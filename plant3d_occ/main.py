# -*- coding: utf-8 -*-
"""Plant 3D OCC 独立交互式桌面开发视窗主入口 (脱离 AutoCAD 的轻量级 PyPad)。

用法：
    python plant3d_occ/main.py                          # 默认打开 pyscripts/ 根目录
    python plant3d_occ/main.py pyscripts/05_supports    # 打开指定构件目录，树形列出所有子脚本
    python plant3d_occ/main.py .../SUPPORT_PIPE_CLAMP.py # 打开指定单件脚本并渲染
"""

import argparse
import json
import os
import sys
import tempfile
import time

pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)


def _run_cli(argv):
    parser = argparse.ArgumentParser(description="Plant 3D OCC CLI & Desktop Workbench")
    parser.add_argument("--render-preview", metavar="SCRIPT",
                        help="使用 PyOCC 渲染指定脚本的轴测预览图（支吊架/设备含尺寸标注，其他仅着色）")
    parser.add_argument("--output-dir", metavar="DIR", default="", help="预览图输出目录")
    parser.add_argument("--params-json", metavar="JSON", default="", help="参数 JSON 字符串")
    parser.add_argument("--clean-preview", metavar="FILE", default="",
                        help="额外输出一张无标注的着色+边线大图")
    parser.add_argument("--publish", metavar="TARGET", help="发布单个脚本或目录到元件库/等级库/设备包")
    parser.add_argument("--publish-json", metavar="FILE", default="",
                        help="GUI 子进程发布任务 JSON（含 paths/content_dir/include_equipment 等）")
    parser.add_argument("--content-dir", metavar="DIR", default="", help="CPak Common 目录")
    parser.add_argument("--auto-sizes", action="store_true", default=True, help="缺失 CSV 时自动生成多规格尺寸")
    parser.add_argument("--add-to-spec", action="store_true", help="将元件库中的构件快速添加到等级库")
    parser.add_argument("--remove-from-spec", action="store_true", help="将构件从指定等级库中移除")
    parser.add_argument("--delete-published", action="store_true",
                        help="从元件库/等级库/设备包中真实删除指定构件")
    parser.add_argument("--remove-custom-script-files", action="store_true",
                        help="删除构件时同时清理 CustomScripts 下的脚本与预览图")
    parser.add_argument("--catalog", metavar="FILE", default="", help="源元件库 (.acat/.pcat) 路径")
    parser.add_argument("--spec", metavar="FILE", default="", help="目标等级库 (.pspc) 路径")
    parser.add_argument("--script-name", metavar="NAME", default="", help="构件脚本名 (ContentGeometryTemplate)")
    parser.add_argument("--equipment-type", metavar="PARTTYPE/PARTSUBTYPE", default="",
                        help="发布设备时显式指定设备类型，格式 PartType/PartSubType，"
                             "例如 Tank/VerticalVessel")

    args, unknown = parser.parse_known_args(argv)

    if args.publish_json:
        return _run_publish_job(args.publish_json)

    if args.render_preview:
        from plant3d_occ.catalog.model import inspect_script, needs_dimension_annotation
        from plant3d_occ.catalog.preview import close_display, open_offscreen_display, render_custom_script_previews
        from plant3d_occ.runner.sandbox import run_script_in_sandbox

        script_path = os.path.abspath(args.render_preview)
        job = inspect_script(script_path, auto_generate_sizes=True)
        params = {}
        if job.get("sizes"):
            params = dict(job["sizes"][len(job["sizes"]) // 2].get("call") or {})
        elif job.get("defaults"):
            params = dict(job["defaults"])
        if args.params_json:
            try:
                override = json.loads(args.params_json)
                if isinstance(override, dict):
                    for k, v in override.items():
                        try:
                            params[k] = float(v) if "." in str(v) else int(v)
                        except Exception:
                            params[k] = v
            except Exception:
                pass
        session, _entry, shapes = run_script_in_sandbox(script_path, params)
        out_dir = args.output_dir or os.path.dirname(script_path)
        disp = open_offscreen_display()
        try:
            paths = render_custom_script_previews(
                disp,
                shapes,
                out_dir,
                job["stem"],
                session=session,
                params_meta=job.get("params_meta") or job.get("params"),
                call_values=params,
                clean_path=(args.clean_preview or None),
                annotate=needs_dimension_annotation(job),
            )
            print(json.dumps({"ok": True, "paths": {str(k): v for k, v in paths.items()}}, ensure_ascii=False))
        finally:
            close_display(disp)
        return 0

    if args.publish:
        from plant3d_occ.catalog.manager import load_catalog_config
        from plant3d_occ.catalog.model import iter_scripts
        from plant3d_occ.catalog.publish import publish_scripts

        target = os.path.abspath(args.publish)
        scripts = list(iter_scripts(target)) if os.path.isdir(target) else [target]
        cfg = load_catalog_config()
        cdir = args.content_dir or cfg.get("content_dir")

        equipment_type = None
        if args.equipment_type:
            parts = args.equipment_type.split("/")
            if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                equipment_type = (parts[0].strip(), parts[1].strip())

        results = publish_scripts(
            scripts,
            content_dir=cdir,
            write_preview=True,
            auto_generate_sizes=args.auto_sizes,
            validate=True,
            equipment_type=equipment_type,
        )
        out = [
            {"script": r.script, "status": r.status, "message": r.message, "catalog": r.catalog}
            for r in results
        ]
        print(json.dumps({"ok": True, "results": out}, ensure_ascii=False))
        return 0

    if args.add_to_spec:
        from plant3d_occ.catalog.manager import add_catalog_item_to_spec
        res = add_catalog_item_to_spec(args.catalog, args.spec, args.script_name)
        print(json.dumps(res, ensure_ascii=False))
        return 0

    if args.remove_from_spec:
        from plant3d_occ.catalog.manager import remove_item_from_spec
        res = remove_item_from_spec(args.spec, args.script_name)
        print(json.dumps(res, ensure_ascii=False))
        return 0

    if args.delete_published:
        from plant3d_occ.catalog.manager import delete_published_item, load_catalog_config
        cfg = load_catalog_config()
        cdir = args.content_dir or cfg.get("content_dir")
        res = delete_published_item(
            cdir,
            args.script_name,
            catalog_path=(args.catalog or None),
            remove_custom_script_files=bool(args.remove_custom_script_files),
        )
        print(json.dumps(res, ensure_ascii=False))
        return 0

    return None


def _run_publish_job(job_file):
    """在独立进程中执行 GUI 发起的发布任务。

    OCC 的离屏视口只能在进程主线程创建；放进 QThread 会直接
    0xC0000005 闪退。GUI 通过 QProcess 调用这里，渲染与数据库写入都在
    子进程主线程完成，即使底层驱动崩溃也只影响子进程。
    """
    from plant3d_occ.catalog.publish import publish_scripts

    with open(job_file, "r", encoding="utf-8") as fp:
        job = json.load(fp)

    def _tell(message):
        line = "@P3D@PROGRESS " + json.dumps(str(message), ensure_ascii=False)
        sys.stdout.write(line + "\n")
        sys.stdout.flush()

    equipment_type = job.get("equipment_type")
    if equipment_type:
        equipment_type = (equipment_type[0], equipment_type[1])
    results = publish_scripts(
        job.get("paths") or [],
        content_dir=job.get("content_dir") or None,
        write_preview=bool(job.get("write_preview", True)),
        auto_generate_sizes=bool(job.get("auto_generate_sizes", True)),
        validate=bool(job.get("validate", True)),
        include_equipment=bool(job.get("include_equipment", True)),
        equipment_type=equipment_type,
        catalog_file=job.get("catalog_file") or None,
        catalog_name=job.get("catalog_name") or None,
        project_spec=job.get("project_spec") or None,
        project_spec_dir=job.get("project_spec_dir") or None,
        on_progress=_tell,
    )
    payload = [
        {"script": r.script, "status": r.status, "message": r.message,
         "catalog": r.catalog}
        for r in results
    ]
    result_path = job.get("result_path") or ""
    if result_path:
        tmp_path = result_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as fp:
            json.dump(payload, fp, ensure_ascii=False)
        os.replace(tmp_path, result_path)
    sys.stdout.write("@P3D@RESULT " + json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    return 0


def _log_exception(exc_type, exc_value, exc_tb):
    """把未捕获异常写入崩溃日志并打印到 stderr。"""
    import traceback
    text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    try:
        with open(os.path.join(tempfile.gettempdir(), "p3dpypad_crash.log"),
                  "a", encoding="utf-8") as fp:
            fp.write("\n[uncaught %s]\n%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), text))
    except Exception:
        pass
    try:
        sys.stderr.write(text)
    except Exception:
        pass


def _install_global_exception_hooks():
    """全局异常兜底。

    - sys.excepthook：主线程未捕获异常（main() 之外的顶层）。
    - threading.excepthook：工作线程未捕获异常。
    - QApplication.notify 覆写：Qt 事件循环里槽函数抛出的异常默认会打印后
      继续运行甚至中止，这里统一拦截 → 记日志 + 弹错误对话框（仅 GUI 已就绪时）。
    """
    sys.excepthook = _log_exception
    try:
        import threading
        threading.excepthook = lambda args: _log_exception(
            args.exc_type, args.exc_value, args.exc_traceback)
    except Exception:
        pass

    from PySide6 import QtWidgets, QtCore

    _app = QtWidgets.QApplication.instance()
    if _app is None:
        return

    _base_notify = QtWidgets.QApplication.notify

    def _safe_notify(obj, receiver, event):
        try:
            return _base_notify(obj, receiver, event)
        except SystemExit:
            raise
        except BaseException:
            _log_exception(*sys.exc_info())
            # 尽量弹窗提示，但弹窗本身出错绝不能二次崩溃
            try:
                QtWidgets.QMessageBox.critical(
                    None, "程序内部错误",
                    "发生未处理的异常，详情已记录到:\n%s\n\n%s" % (
                        os.path.join(tempfile.gettempdir(), "p3dpypad_crash.log"),
                        str(sys.exc_info()[1])[:500]))
            except Exception:
                pass
            return True  # 吞掉异常，保持事件循环存活

    QtWidgets.QApplication.notify = _safe_notify


def main():
    # 原生崩溃 (0xc0000005) 时把 Python 调用栈写入日志，便于定位闪退
    try:
        import faulthandler
        _crash_log = os.path.join(tempfile.gettempdir(), "p3dpypad_crash.log")
        _crash_fp = open(_crash_log, "a", encoding="utf-8", buffering=1)
        faulthandler.enable(file=_crash_fp, all_threads=True)
    except Exception:
        pass

    cli_flags = ("--render-preview", "--publish", "--publish-json",
                 "--add-to-spec", "--remove-from-spec")
    if any(f in sys.argv[1:] for f in cli_flags):
        code = _run_cli(sys.argv[1:])
        if code is not None:
            sys.exit(code)

    # 注册 Windows 专属应用 UserModelID，确保任务栏精准显示原生大尺寸 CAD 构件图标而非缩小副图标
    if sys.platform == "win32":
        try:
            import ctypes
            myappid = "Autodesk.AutoCAD.Plant3D.PyPad.Workbench"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    from PySide6 import QtWidgets, QtCore
    from plant3d_occ.gui.app_window import Plant3dOccAppWindow
    from plant3d_occ.gui.theme import apply_theme, get_app_icon

    QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
        QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)

    # 全局异常兜底：未捕获异常记入崩溃日志并弹窗提示，避免直接闪退
    _install_global_exception_hooks()

    # 应用严格遵循 $wpf-ui-style 工业CAD规范的 QSS 样式与图标
    apply_theme(app)

    # 默认加载目录或脚本 (优先使用命令行参数，未指定时由窗口内部动态推导)
    default_target = None
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        default_target = os.path.abspath(sys.argv[1])

    win = Plant3dOccAppWindow(default_path=default_target)
    win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
