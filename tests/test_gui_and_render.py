# -*- coding: utf-8 -*-
"""OCC 桌面窗口与渲染管线测试。

覆盖：窗口两种打开方式、视口初始化时序、发布对话框、网格化、
离线渲染、visual_check 命令行入口。
需要一个可用的桌面会话（OCCT 必须拿到真实窗口句柄）；没有就跳过。
"""

import glob
import os
import textwrap
import sys
import tempfile
import unittest

pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)

try:
    from PySide6 import QtWidgets, QtCore
    HAS_PYSIDE6 = True
except ImportError:
    QtWidgets = None
    QtCore = None
    HAS_PYSIDE6 = False

_tests_dir = os.path.dirname(os.path.abspath(__file__))
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

import script_fixtures

SCRIPTS_ROOT = script_fixtures.SCRIPTS_ROOT
HG_SCRIPTS = script_fixtures.hg_scripts()
SAMPLE_SCRIPT = script_fixtures.first_renderable_script()


def _app():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


def _pump(app):
    app.processEvents()
    QtCore.QCoreApplication.processEvents()


class TestAppWindow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not HAS_PYSIDE6:
            raise unittest.SkipTest("PySide6 未安装，跳过桌面窗口用例")
        cls.app = _app()

    def _window(self, default_path=None):
        from plant3d_occ.gui.app_window import Plant3dOccAppWindow
        win = Plant3dOccAppWindow(default_path=default_path)
        self.addCleanup(self._dispose, win)
        return win

    def _dispose(self, win):
        try:
            win.close()
            win.deleteLater()
        finally:
            _pump(self.app)

    def test_construction_does_not_create_viewport(self):
        """构造阶段视口必须是 None：此时 Qt 还没布局，按占位尺寸建 GL 视口会错。

        构造时可能会排队一次首次渲染（目录模式自动选中第一个脚本），
        但绝不能真的去建视口——渲染必须推迟到 showEvent。
        """
        win = self._window()
        self.assertIsNone(win.display, "构造阶段不应创建 OCCT 视口")
        self.assertFalse(win._viewport_synced, "未上屏不应标记为已同步")
        self.assertIsNotNone(win.viewer_widget)

    def test_show_event_initializes_viewport(self):
        win = self._window()
        win.show()
        _pump(self.app)
        self.assertTrue(win._viewport_synced, "showEvent 应把视口标记为已同步")
        self.assertGreater(win.viewer_widget.width(), 100,
                           "控件不应仍是占位宽度")

    def test_switch_mode(self):
        win = self._window()
        win.show()
        _pump(self.app)
        win._switch_mode(0)
        _pump(self.app)
        win._switch_mode(1)
        _pump(self.app)

    def test_opens_on_directory(self):
        """目录浏览模式：main.py 的默认入口就是传一个目录。"""
        win = self._window(SCRIPTS_ROOT)
        win.show()
        _pump(self.app)
        self.assertGreater(win.file_tree.tree.topLevelItemCount(), 0,
                           "目录模式下文件树应有条目")

    def test_opens_on_single_script(self):
        if not SAMPLE_SCRIPT:
            self.skipTest("没有可用脚本")
        win = self._window(SAMPLE_SCRIPT)
        win.show()
        _pump(self.app)
        self.assertGreater(len(win.property_grid.get_values()), 0,
                           "单脚本模式应直接载入参数")

    def test_load_script_and_csv(self):
        if not SAMPLE_SCRIPT:
            self.skipTest("没有可用脚本")
        script = SAMPLE_SCRIPT
        win = self._window()
        win.show()
        _pump(self.app)

        win.load_script_file(script)
        _pump(self.app)
        self.assertTrue(win.property_grid.get_values(), "载入脚本后应有参数值")

        csv_path = os.path.splitext(script)[0] + ".csv"
        if os.path.isfile(csv_path):
            win.load_csv_file(csv_path)
            _pump(self.app)
            self.assertTrue(win._presets, "CSV 应被读成预设列表")
            self.assertGreater(win.preset_combo.count(), 0, "预设下拉应有条目")

    def test_run_before_show_is_deferred(self):
        """未上屏时 run_and_render 只记待渲染标记，不能抛异常。"""
        if not SAMPLE_SCRIPT:
            self.skipTest("没有可用脚本")
        win = self._window()
        win.load_script_file(SAMPLE_SCRIPT)
        _pump(self.app)
        win.run_and_render()
        self.assertTrue(win._pending_render or win.display is not None)


class TestDisplayStyleAndViews(unittest.TestCase):
    """显示样式与标准视图：每个档位必须真的改变画面，而不是只改状态。"""

    @classmethod
    def setUpClass(cls):
        if not HAS_PYSIDE6:
            raise unittest.SkipTest("PySide6 未安装，跳过桌面窗口用例")
        cls.app = _app()

    def setUp(self):
        from plant3d_occ.gui.app_window import Plant3dOccAppWindow
        if not SAMPLE_SCRIPT:
            self.skipTest("没有可用脚本")
        self.win = Plant3dOccAppWindow(default_path=SAMPLE_SCRIPT)
        self.win.resize(900, 700)
        self.win.show()
        _pump(self.app)
        if self.win.display is None:
            self.win.close()
            self.skipTest("OCCT 视口不可用（需要桌面会话）")
        if not self.win._ais_objects:
            self.win.close()
            self.skipTest("样板脚本没有渲染出实体")

    def tearDown(self):
        try:
            self.win.close()
            self.win.deleteLater()
        finally:
            _pump(self.app)

    def _dump_hash(self, tag):
        import hashlib
        path = os.path.join(self.tmpdir, tag + ".png")
        self.assertTrue(self.win.display.View.Dump(path), "抓图失败: " + tag)
        with open(path, "rb") as handle:
            return hashlib.md5(handle.read()).hexdigest()

    def test_every_display_style_renders_differently(self):
        import tempfile
        from plant3d_occ.gui.app_window import DISPLAY_STYLES

        self.tmpdir = tempfile.mkdtemp(prefix="p3d_style_")
        self.addCleanup(__import__("shutil").rmtree, self.tmpdir, ignore_errors=True)

        seen = {}
        for value, _label in DISPLAY_STYLES:
            self.win.set_display_style(value)
            _pump(self.app)
            self.assertEqual(self.win._display_style, value)
            seen[value] = self._dump_hash("style_" + value)

        self.assertEqual(len(set(seen.values())), len(seen),
                         "存在画面完全相同的显示样式: " + str(seen))

    def test_every_standard_view_renders_differently(self):
        import shutil
        import tempfile
        from plant3d_occ.gui.app_window import VIEW_MODES

        self.tmpdir = tempfile.mkdtemp(prefix="p3d_view_")
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)

        seen = {}
        for value, _label, _key in VIEW_MODES:
            self.win._set_view(value)
            _pump(self.app)
            self.assertEqual(self.win._current_view, value)
            seen[value] = self._dump_hash("view_" + value)

        self.assertEqual(len(set(seen.values())), len(seen),
                         "存在画面完全相同的标准视图: " + str(seen))

    def test_combos_reflect_programmatic_changes(self):
        """快捷键/代码触发时，下拉框必须同步，不能只改内部状态。"""
        self.win._set_view("top")
        self.assertEqual(self.win.combo_view.currentData(), "top")
        self.win.set_display_style("wireframe")
        self.assertEqual(self.win.combo_style.currentData(), "wireframe")
        # 无效视图名不应改动当前视图
        self.win._set_view("nonsense")
        self.assertEqual(self.win._current_view, "top")

    def test_header_shows_view_and_style(self):
        self.win._set_view("left")
        self.win.set_display_style("hidden_line")
        text = self.win.right_header.text()
        self.assertIn("左视", text)
        self.assertIn("隐藏线", text)

    def test_shortcuts_do_not_hijack_editor_typing(self):
        """在代码编辑器里敲数字/字母是输入内容，不能触发视图或样式切换。"""
        from PySide6 import QtGui, QtCore

        self.win._set_view("iso")
        self.win.set_display_style("shaded_with_edges")
        self.win.code_editor.setFocus()
        _pump(self.app)

        for key in (QtCore.Qt.Key_5, QtCore.Qt.Key_W):
            event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, key, QtCore.Qt.NoModifier)
            self.win.keyPressEvent(event)

        self.assertEqual(self.win._current_view, "iso", "编辑器里按 5 不应切换视图")
        self.assertEqual(self.win._display_style, "shaded_with_edges",
                         "编辑器里按 W 不应切换样式")


class TestEditorExecution(unittest.TestCase):
    """GUI 编辑器里的“运行”必须与文件沙箱行为一致。

    这条路径以前自己 exec 了一份代码，沙箱里补的 Python 2 兼容垫片与
    @activate 入口识别都拿不到，编辑器里跑存量脚本会直接 NameError: reload。
    """

    PY2_SCRIPT = textwrap.dedent(
        """        #coding=utf-8
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')

        from varmain.divsub.cnut6_001 import *
        from varmain.divsub.divutil import *

        from aqa.math import *
        from varmain.primitiv import *
        from varmain.var_basic import *
        from varmain.custom import *

        @activate(Group="Support", TooltipShort="门形支撑", Ports="1")
        @param(D=LENGTH, TooltipLong="管径")
        @param(H=LENGTH, TooltipLong="高度")
        def test_support001(s, D=114.3, H=600.0, **kw):
            beam = BOX(s, L=H, W=40.0, H=40.0).translate((0, 0, 0))
            nut = NUT_BOLT_HEAD_6_001(s, W=20.0, H=10.0).translate((20.0, 0, -25.0))
            beam.uniteWith(nut)
            nut.erase()
            s.setPoint((0, 0, 0), (0, 1, 0))
        """
    )

    @classmethod
    def setUpClass(cls):
        if not HAS_PYSIDE6:
            raise unittest.SkipTest("PySide6 未安装，跳过桌面窗口用例")
        cls.app = _app()

    def setUp(self):
        from plant3d_occ.gui.app_window import Plant3dOccAppWindow
        if not SAMPLE_SCRIPT:
            self.skipTest("没有可用脚本")
        self.win = Plant3dOccAppWindow(default_path=SAMPLE_SCRIPT)
        self.win.resize(1000, 720)
        self.win.show()
        _pump(self.app)
        if self.win.display is None:
            self.win.close()
            self.skipTest("OCCT 视口不可用（需要桌面会话）")

    def tearDown(self):
        try:
            self.win.close()
            self.win.deleteLater()
        finally:
            _pump(self.app)

    def _run(self, code, hint):
        self.win.code_editor.setPlainText(code)
        self.win._current_script_path = hint
        self.win.run_and_render()
        _pump(self.app)
        return self.win.log_box.toPlainText(), self.win.lbl_status.text()

    def test_editor_runs_python2_header_script(self):
        log, status = self._run(self.PY2_SCRIPT, "test_support001.py")
        self.assertNotIn("执行失败", log, "编辑器执行报错：" + log)
        self.assertNotIn("NameError", log)
        self.assertTrue(self.win._shapes, "应生成实体")
        self.assertIn("test_support001", status)

    def test_editor_entry_not_tied_to_filename(self):
        """文件名与函数名不一致时也要能跑（靠 @activate 识别）。"""
        log, status = self._run(self.PY2_SCRIPT, "完全不相干的名字.py")
        self.assertNotIn("执行失败", log, "编辑器执行报错：" + log)
        self.assertIn("test_support001", status)

    def test_editor_reports_missing_entry_clearly(self):
        log, _status = self._run("x = 1", "")
        self.assertIn("未在代码中找到", log)


class TestRenderPipeline(unittest.TestCase):

    def test_mesh_and_bounds(self):
        from plant3d_occ.renderer.mesher import extract_mesh_and_bounds
        from plant3d_occ.runner.sandbox import run_script_in_sandbox

        if not SAMPLE_SCRIPT:
            self.skipTest("没有可用脚本")
        _session, _entry, shapes = run_script_in_sandbox(SAMPLE_SCRIPT)
        self.assertTrue(shapes, "脚本应生成实体")

        triangles, bounds = extract_mesh_and_bounds(shapes)
        self.assertGreater(len(triangles), 0, "应提取到三角面片")
        self.assertEqual(len(bounds), 6, "包围盒应有 6 个分量")
        xmin, ymin, zmin, xmax, ymax, zmax = bounds
        self.assertLess(xmin, xmax)
        self.assertLess(ymin, ymax)
        self.assertLess(zmin, zmax)
        for triangle in triangles[:5]:
            self.assertEqual(len(triangle), 3, "每个面片应有 3 个顶点")
            for vertex in triangle:
                self.assertEqual(len(vertex), 3, "每个顶点应有 3 个坐标")

    def test_offscreen_render_writes_png(self):
        from plant3d_occ.renderer.offscreen import render_occt_viewer
        from plant3d_occ.runner.sandbox import run_script_in_sandbox

        if not SAMPLE_SCRIPT:
            self.skipTest("没有可用脚本")
        _session, _entry, shapes = run_script_in_sandbox(SAMPLE_SCRIPT)
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "shot.png")
            render_occt_viewer(shapes, out, show_gui=False)
            self.assertTrue(os.path.isfile(out), "应生成 PNG")
            self.assertGreater(os.path.getsize(out), 1000, "渲染图不应为空")

    def test_visual_check_entry_point(self):
        from plant3d_occ.runner.visual_check import visual_check

        if not SAMPLE_SCRIPT:
            self.skipTest("没有可用脚本")
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "check.png")
            ok = visual_check(SAMPLE_SCRIPT, output_png=out, show_gui=False)
            self.assertTrue(ok, "visual_check 应返回 True")
            self.assertTrue(os.path.isfile(out))
            self.assertGreater(os.path.getsize(out), 1000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
