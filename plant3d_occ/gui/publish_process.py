# -*- coding: utf-8 -*-
"""发布子进程：把 OCC 渲染与数据库写入隔离到独立进程。

PyOCC 的离屏视口必须在进程主线程创建；塞进 QThread 会触发原生
access violation（0xC0000005）。这里用 QProcess 启动一个发布子进程：
- GUI 线程只负责读进度和结果，永不创建 OCC 视口；
- 渲染完全异步，界面保持可交互；
- 子进程崩溃不会带走主程序。
"""

import json
import os
import sys
import tempfile

from PySide6 import QtCore


def _package_root():
    """源码模式下的仓库根目录；frozen 模式返回可执行文件目录。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(here))


class PublishProcess(QtCore.QObject):
    """异步发布任务。信号：progress(str) / finished(list) / failed(str)。"""

    progress = QtCore.Signal(str)
    finished = QtCore.Signal(object)
    failed = QtCore.Signal(str)

    def __init__(self, paths, content_dir, include_equipment=True,
                 auto_generate_sizes=True, equipment_type=None,
                 write_preview=True, validate=True, parent=None):
        super(PublishProcess, self).__init__(parent)
        self._paths = list(paths or [])
        self._content_dir = content_dir or ""
        self._include_equipment = bool(include_equipment)
        self._auto_generate_sizes = bool(auto_generate_sizes)
        self._equipment_type = equipment_type
        self._write_preview = bool(write_preview)
        self._validate = bool(validate)
        self._proc = None
        self._buffer = ""
        self._done = False
        self._result = None
        self._job_file = ""
        self._result_file = ""
        self._stderr_tail = ""
        self._exit_code = -1

    def start(self):
        if self._done or (self._proc is not None and self._proc.state() != QtCore.QProcess.NotRunning):
            return

        handle, self._job_file = tempfile.mkstemp(
            prefix="p3d_publish_", suffix=".json")
        os.close(handle)
        handle, self._result_file = tempfile.mkstemp(
            prefix="p3d_publish_result_", suffix=".json")
        os.close(handle)
        os.remove(self._result_file)

        job = {
            "paths": self._paths,
            "content_dir": self._content_dir,
            "include_equipment": self._include_equipment,
            "auto_generate_sizes": self._auto_generate_sizes,
            "equipment_type": list(self._equipment_type) if self._equipment_type else None,
            "write_preview": self._write_preview,
            "validate": self._validate,
            "result_path": self._result_file,
        }
        with open(self._job_file, "w", encoding="utf-8") as fp:
            json.dump(job, fp, ensure_ascii=False)

        self._proc = QtCore.QProcess(self)
        self._proc.setProcessChannelMode(QtCore.QProcess.SeparateChannels)
        root = _package_root()
        self._proc.setWorkingDirectory(root)
        env = QtCore.QProcessEnvironment.systemEnvironment()
        old_path = env.value("PYTHONPATH", "")
        env.insert("PYTHONPATH", root + (os.pathsep + old_path if old_path else ""))
        env.insert("PYTHONIOENCODING", "utf-8")
        env.insert("PYTHONUNBUFFERED", "1")
        self._proc.setProcessEnvironment(env)

        if getattr(sys, "frozen", False):
            program = sys.executable
            args = ["--publish-json", self._job_file]
        else:
            program = sys.executable
            args = ["-u", "-m", "plant3d_occ", "--publish-json", self._job_file]

        self._proc.readyReadStandardOutput.connect(self._on_stdout)
        self._proc.readyReadStandardError.connect(self._on_stderr)
        self._proc.finished.connect(self._on_finished)
        self._proc.errorOccurred.connect(self._on_error)
        self._proc.start(program, args)

    def cancel(self):
        if self._proc is not None:
            try:
                self._proc.kill()
            except Exception:
                pass

    def is_running(self):
        if self._done or self._proc is None:
            return False
        try:
            return self._proc.state() != QtCore.QProcess.NotRunning
        except RuntimeError:
            return False

    def wait(self, msec=60000):
        if self._done or self._proc is None:
            return True
        try:
            return bool(self._proc.waitForFinished(msec))
        except RuntimeError:
            return True

    def stop(self, msec=5000):
        self.cancel()
        return self.wait(msec)

    def _on_stdout(self):
        if self._proc is None:
            return
        chunk = bytes(self._proc.readAllStandardOutput()).decode("utf-8", "replace")
        self._buffer += chunk
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._handle_line(line.strip())

    def _on_stderr(self):
        if self._proc is None:
            return
        chunk = bytes(self._proc.readAllStandardError()).decode("utf-8", "replace")
        self._stderr_tail = (self._stderr_tail + chunk)[-4000:]

    def _handle_line(self, line):
        if not line:
            return
        if line.startswith("@P3D@PROGRESS "):
            try:
                self.progress.emit(str(json.loads(line[len("@P3D@PROGRESS "):])))
            except Exception:
                self.progress.emit(line[len("@P3D@PROGRESS "):])
        elif line.startswith("@P3D@RESULT "):
            try:
                self._result = json.loads(line[len("@P3D@RESULT "):])
            except Exception:
                self._result = None

    def _on_error(self, _error):
        # 进程未能启动时 finished 不一定触发，这里主动收尾。
        if self._proc is not None and self._proc.state() == QtCore.QProcess.NotRunning:
            QtCore.QTimer.singleShot(0, self._finish)

    def _on_finished(self, exit_code, _exit_status):
        self._on_stdout()
        self._on_stderr()
        self._exit_code = exit_code
        self._finish()

    def _finish(self):
        if self._done:
            return
        self._done = True
        result = self._result
        if result is None and self._result_file and os.path.isfile(self._result_file):
            try:
                with open(self._result_file, "r", encoding="utf-8") as fp:
                    result = json.load(fp)
            except Exception:
                result = None
        self._cleanup_files()
        if result is not None:
            self.finished.emit(result)
        else:
            detail = "发布进程异常退出（代码 %s）" % self._exit_code
            if self._stderr_tail.strip():
                detail += "\n" + self._stderr_tail.strip()[-1500:]
            self.failed.emit(detail)

    def _cleanup_files(self):
        for path in (self._job_file, self._result_file):
            if path:
                try:
                    os.remove(path)
                except OSError:
                    pass
        self._job_file = ""
        self._result_file = ""
