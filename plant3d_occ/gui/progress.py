# -*- coding: utf-8 -*-
"""可计算进度的内嵌进度条组件（无图标，纯文本 + 百分比 + 进度条）。

所有页面的 loading 统一用这个：底部一行"说明文字 + 进度条 + 百分比"，
总工作量已知时显示确定进度，未知时显示流动条。
"""
import threading
import traceback

from PySide6 import QtCore, QtWidgets

from .i18n import tr


class InlineProgressBar(QtWidgets.QWidget):
    """一行内嵌进度条。set_progress(text, done, total) 或 set_busy(text)。"""

    def __init__(self, parent=None):
        super(InlineProgressBar, self).__init__(parent)
        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(2, 0, 2, 0)
        lay.setSpacing(8)
        self.label = QtWidgets.QLabel(self)
        self.bar = QtWidgets.QProgressBar(self)
        self.bar.setFixedHeight(14)
        self.bar.setTextVisible(False)
        self.pct = QtWidgets.QLabel(self)
        self.pct.setFixedWidth(48)
        self.pct.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        lay.addWidget(self.label, stretch=1)
        lay.addWidget(self.bar, stretch=2)
        lay.addWidget(self.pct)
        self.setVisible(False)

    def set_progress(self, text: str, done: int, total: int):
        """确定进度：done/total 可计算百分比。"""
        self.setVisible(True)
        self.label.setText(text)
        self.bar.setRange(0, 100)
        pct = int(done * 100.0 / max(1, total))
        self.bar.setValue(pct)
        self.pct.setText("%d%%" % pct)

    def set_busy(self, text: str):
        """总工作量未知：流动条 + 纯文字。"""
        self.setVisible(True)
        self.label.setText(text)
        self.bar.setRange(0, 0)
        self.pct.setText("")

    def hide_bar(self):
        self.setVisible(False)


class TaskCancelled(Exception):
    """后台任务被主动取消时抛出，线程会安静退出。"""


class _CancelToken(object):
    """线程安全的取消令牌；被取消后 check() 立即抛 TaskCancelled。"""

    def __init__(self):
        self._event = threading.Event()

    def cancel(self):
        self._event.set()

    @property
    def cancelled(self):
        return self._event.is_set()

    def check(self):
        if self._event.is_set():
            raise TaskCancelled()


class _TaskWorker(QtCore.QObject):
    progress = QtCore.Signal(object)
    finished = QtCore.Signal(object)
    failed = QtCore.Signal(str)

    def __init__(self, fn, token):
        super(_TaskWorker, self).__init__()
        self._fn = fn
        self._token = token

    def run(self):
        try:
            result = self._fn(
                lambda payload: self.progress.emit(payload), self._token)
            if not self._token.cancelled:
                self.finished.emit(result)
        except TaskCancelled:
            pass
        except BaseException:
            self.failed.emit(traceback.format_exc())


class ThreadTask(QtCore.QObject):
    """可取消的后台任务：函数在独立 QThread 执行，结果/异常排队回 UI 线程。

    用法：
        task = ThreadTask(self._work, parent=self)
        task.progress.connect(self._on_progress)   # payload 为任意 Python 对象
        task.finished.connect(self._on_finished)
        task.failed.connect(self._on_failed)
        task.start()

    `_work(progress, token)` 必须定期调用 `token.check()`，取消后尽快返回。
    任务完成后线程自动退出并清理，不需要调用方再手工 quit/wait。
    """

    progress = QtCore.Signal(object)
    finished = QtCore.Signal(object)
    failed = QtCore.Signal(str)

    def __init__(self, fn, parent=None, name="p3d-task"):
        super(ThreadTask, self).__init__(parent)
        self._token = _CancelToken()
        self._done = False
        self._thread = QtCore.QThread()
        self._thread.setObjectName(name)
        self._worker = _TaskWorker(fn, self._token)
        self._worker.moveToThread(self._thread)
        self._worker.progress.connect(self.progress)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.failed.connect(self._on_worker_failed)
        # 直接在工作线程里退出事件循环：即使 UI 线程正卡在 wait()，
        # 线程也能正常结束，避免“QThread destroyed while running”闪退。
        self._worker.finished.connect(
            self._thread.quit, QtCore.Qt.ConnectionType.DirectConnection)
        self._worker.failed.connect(
            self._thread.quit, QtCore.Qt.ConnectionType.DirectConnection)
        self._thread.started.connect(self._worker.run)
        self._thread.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

    def start(self):
        if self._done or self._thread.isRunning():
            return
        self._thread.start()

    def cancel(self):
        self._token.cancel()
        if not self._done and self._thread.isRunning():
            self._thread.quit()

    def is_running(self):
        if self._done or self._thread is None:
            return False
        try:
            return bool(self._thread.isRunning())
        except RuntimeError:
            return False

    def wait(self, msec=5000):
        """等待后台函数返回；仅用于窗口关闭/销毁前的安全收尾。"""
        if self._done or self._thread is None:
            return True
        try:
            return bool(self._thread.wait(msec))
        except RuntimeError:
            return True

    def stop(self, msec=5000):
        self.cancel()
        return self.wait(msec)

    def _on_worker_finished(self, result):
        self._done = True
        try:
            self._thread.quit()
        except RuntimeError:
            pass
        self.finished.emit(result)

    def _on_worker_failed(self, detail):
        self._done = True
        try:
            self._thread.quit()
        except RuntimeError:
            pass
        self.failed.emit(detail)

