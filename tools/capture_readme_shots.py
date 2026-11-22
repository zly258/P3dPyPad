# -*- coding: utf-8 -*-
"""README UI 截图采集脚本：启动真实工作台窗口，逐 Tab 截屏到 docs/images/。

用法：python tools/capture_readme_shots.py
只覆盖 README 引用的 UI 截图（构件设计/发布构件/发布设备/元件库管理），
关于窗口 (03_csharp_about.png) 不在此采集，保持原样。
"""
import os
import sys

PKG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG_ROOT)

OUT_DIR = os.path.join(PKG_ROOT, "docs", "images")


def composite_viewport(win, shot_path):
    """把 OCCT 视口的真实 GL 画面合成到整窗截图上。

    qtViewer3d 是 WA_PaintOnScreen 原生 GL 窗口，win.grab() 抓不到 GL 内容
    （该区域是黑的）。用 View.Dump 抓 GL 后备缓冲，再贴回 grab 图中视口的
    实际几何矩形。
    """
    from PIL import Image
    display = getattr(win, "display", None)
    if display is None or getattr(display, "View", None) is None:
        return
    import tempfile
    vp_png = os.path.join(tempfile.gettempdir(), "p3dpypad_shot_viewport.png")
    try:
        if not display.View.Dump(vp_png):
            return
        if not os.path.isfile(vp_png) or os.path.getsize(vp_png) < 100:
            return
        base = Image.open(shot_path).convert("RGB")
        vp = Image.open(vp_png).convert("RGB")
        if vp.size[0] < 10 or vp.size[1] < 10:
            return
        # 视口 widget 在整窗中的物理矩形（DPI 缩放已由 win.grab 的设备像素体现）
        from PySide6 import QtCore
        tl = win.viewer_widget.mapTo(win, QtCore.QPoint(0, 0))
        dpr = win.devicePixelRatioF()
        x, y = int(tl.x() * dpr), int(tl.y() * dpr)
        w = int(win.viewer_widget.width() * dpr)
        h = int(win.viewer_widget.height() * dpr)
        if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > base.width or y + h > base.height:
            return
        base.paste(vp.resize((w, h), Image.LANCZOS), (x, y))
        base.save(shot_path, "PNG")
    except Exception as exc:
        print("composite warn:", exc)


def main():
    from PySide6 import QtWidgets, QtCore
    from plant3d_occ.main import _install_global_exception_hooks
    from plant3d_occ.gui.app_window import Plant3dOccAppWindow
    from plant3d_occ.gui.theme import apply_theme

    QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
        QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    _install_global_exception_hooks()
    apply_theme(app)

    win = Plant3dOccAppWindow()
    win.resize(1600, 900)
    win.show()
    app.processEvents()

    # 等待首屏 3D 场景与惰性加载就绪，然后真实跑一次 F5 建模让视口里有构件
    for _ in range(30):
        app.processEvents()
        QtCore.QThread.msleep(100)
    try:
        win.run_and_render()
    except Exception as exc:
        print("run_and_render warn:", exc)
    for _ in range(60):
        app.processEvents()
        QtCore.QThread.msleep(100)
    QtCore.QThread.msleep(800)
    for _ in range(10):
        app.processEvents()

    tabs = [
        (0, "04_python_workbench.png"),      # 构件设计（工作台主界面）
        (1, "06_publish_component.png"),     # 发布构件
        (2, "07_publish_equipment.png"),     # 发布设备
        (3, "08_catalog_manager.png"),       # 元件库管理
    ]
    for idx, filename in tabs:
        win.main_tabs.setCurrentIndex(idx)
        # 给当前页的惰性加载与渲染留时间
        for _ in range(50):
            app.processEvents()
            QtCore.QThread.msleep(100)
        QtCore.QThread.msleep(800)
        for _ in range(10):
            app.processEvents()
        pix = win.grab()
        out = os.path.join(OUT_DIR, filename)
        ok = pix.save(out, "PNG")
        print(("OK " if ok else "FAIL ") + out, pix.width(), "x", pix.height())
        if idx == 0:
            # 构件设计页：把 OCCT 视口真实 GL 画面合进去
            composite_viewport(win, out)

    win.close()
    QtCore.QThread.msleep(200)
    print("done")


if __name__ == "__main__":
    main()
