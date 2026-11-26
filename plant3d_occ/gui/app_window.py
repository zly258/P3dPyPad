# -*- coding: utf-8 -*-
import os
import sys
import time
import re
import traceback
from PySide6 import QtCore, QtGui, QtWidgets

from OCC.Display.backend import load_backend
load_backend('pyside6')
from OCC.Display.qtDisplay import qtViewer3d
from OCC.Core.Quantity import Quantity_NOC_GRAY50, Quantity_NOC_BLACK, Quantity_Color
from OCC.Core.Aspect import Aspect_TOL_SOLID


class SafeQtViewer3d(qtViewer3d):
    """安全防护型 OpenCASCADE 3D 视口组件，全方位拦截底层 OpenGL 上下文及事件驱动异常，根治闪退。"""

    def InitDriver(self):
        if getattr(self, "_inited", False):
            return
        try:
            super(SafeQtViewer3d, self).InitDriver()
        except Exception:
            pass

    def paintEvent(self, event):
        # 绝不能在这里调用 InitDriver（父类 paintEvent 会在未初始化时这么做）：
        # InitDriver 内部要 winId()+Create() 创建原生 GL 窗口，在 Qt 的绘制过程中
        # 重入会直接触发 "QWidget::repaint: Recursive repaint detected" 与
        # "QBackingStore::endPaint() called with active painter" 并闪退。
        # 初始化一律由窗口的 deferred 回调在 paint 之外完成；未初始化前只画背景。
        if not getattr(self, "_inited", False):
            return
        if not self.isVisible() or self.width() <= 1 or self.height() <= 1:
            return
        if not hasattr(self, "_display") or self._display is None:
            return
        try:
            super(SafeQtViewer3d, self).paintEvent(event)
        except Exception:
            pass

    def resizeEvent(self, event):
        # 初始化前不要碰 OCC 的 View（原生窗口尚未创建）
        if not getattr(self, "_inited", False):
            return
        if not self.isVisible() or self.width() <= 1 or self.height() <= 1:
            return
        if not hasattr(self, "_display") or self._display is None:
            return
        try:
            super(SafeQtViewer3d, self).resizeEvent(event)
        except Exception:
            pass

    def focusInEvent(self, event):
        if not self.isVisible() or self.width() <= 1 or not getattr(self, "_inited", False):
            return
        try:
            super(SafeQtViewer3d, self).focusInEvent(event)
        except Exception:
            pass

    def focusOutEvent(self, event):
        # 失去焦点时绝对禁止触发底层 Repaint，防止 wglMakeCurrent 上下文丢失导致崩溃闪退
        pass

    def wheelEvent(self, event):
        if not self.isVisible() or not getattr(self, "_inited", False):
            return
        try:
            super(SafeQtViewer3d, self).wheelEvent(event)
        except Exception:
            pass

    def mousePressEvent(self, event):
        if not self.isVisible() or not getattr(self, "_inited", False):
            return
        try:
            super(SafeQtViewer3d, self).mousePressEvent(event)
        except Exception:
            pass

    def mouseMoveEvent(self, event):
        if not self.isVisible() or not getattr(self, "_inited", False):
            return
        try:
            super(SafeQtViewer3d, self).mouseMoveEvent(event)
        except Exception:
            pass

    def mouseReleaseEvent(self, event):
        if not self.isVisible() or not getattr(self, "_inited", False):
            return
        try:
            super(SafeQtViewer3d, self).mouseReleaseEvent(event)
        except Exception:
            pass

from .property_grid import PropertyGridWidget
from .file_tree import FileTreeWidget
from .component_publish_page import ComponentPublishPage
from .equipment_publish_page import EquipmentPublishPage
from .catalog_manager_page import CatalogManagerPage
from .spec_manager_page import SpecManagerPage
from .python_highlighter import PythonHighlighter
from .theme import apply_theme, get_app_icon
from .i18n import (
    tr, current_language, set_current_language, register_language_listener,
    LANG_AUTO, LANG_ZH, LANG_EN, detect_system_language, load_configured_language,
    apply_qt_default_translations
)
from ..core.session import OccSession

EDGE_LINE_WIDTH = 1.0


def get_view_modes():
    return (
        ("iso", tr("view_iso", "等轴测"), "1"),
        ("front", tr("view_front", "前视"), "2"),
        ("rear", tr("view_rear", "后视"), "3"),
        ("left", tr("view_left", "左视"), "4"),
        ("right", tr("view_right", "右视"), "5"),
        ("top", tr("view_top", "俯视"), "6"),
        ("bottom", tr("view_bottom", "仰视"), "7"),
    )


def get_display_styles():
    return (
        ("shaded", tr("style_shaded", "着色")),
        ("shaded_with_edges", tr("style_shaded_edges", "着色带边")),
        ("hidden_line", tr("style_hidden_line", "隐藏线")),
        ("wireframe", tr("style_wireframe", "线框")),
    )


VIEW_MODES = get_view_modes()
DISPLAY_STYLES = get_display_styles()
DEFAULT_DISPLAY_STYLE = "shaded_with_edges"
DEFAULT_VIEW = "iso"


def get_app_root():
    """动态获取当前软件运行根目录，支持源码模式、便携免安装版与安装版，杜绝使用依赖终端的 cwd。"""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(here))


def get_default_scripts_dir():
    """动态智能解析构件脚本的默认根目录 (优先级: 环境变量 > 持久化配置 > 相对安装目录 > 用户主目录)。"""
    # 1. 显式环境变量
    env_dir = os.environ.get("P3DPYPAD_SCRIPTS")
    if env_dir and os.path.isdir(env_dir):
        return env_dir

    # 2. 读取用户上次在软件中选择并持久化的配置
    try:
        from ..catalog.manager import load_catalog_config
        cfg = load_catalog_config()
        saved_dir = cfg.get("scripts_dir")
        if saved_dir and os.path.isdir(saved_dir):
            return saved_dir
    except Exception:
        pass

    # 3. 相对于程序根目录动态查找
    app_root = get_app_root()
    candidates = [
        os.path.join(app_root, "pyscripts", "custom_scripts"),
        os.path.join(app_root, "pyscripts"),
        os.path.join(app_root, "custom_scripts"),
    ]
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        candidates.extend([
            os.path.join(sys._MEIPASS, "pyscripts", "custom_scripts"),
            os.path.join(sys._MEIPASS, "pyscripts"),
        ])
    for c in candidates:
        if os.path.isdir(c):
            return c

    # 4. 用户文档目录兜底
    user_dir = os.path.join(os.path.expanduser("~"), "Plant3D_Scripts", "custom_scripts")
    return user_dir


class Plant3dOccAppWindow(QtWidgets.QMainWindow):
    """Plant 3D OCC 独立交互式 3D 构件设计工作台。"""

    def __init__(self, default_path=None):
        super(Plant3dOccAppWindow, self).__init__()
        apply_qt_default_translations()
        self._current_script_path = None
        self._current_csv_path = None
        self._presets = []
        self._shapes = []
        self._viewport_synced = False
        self._display_style = DEFAULT_DISPLAY_STYLE
        self._current_view = DEFAULT_VIEW
        self._ais_objects = []

        self.setWindowTitle(tr("app_title"))
        icon = get_app_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)
        apply_theme(self)

        self.resize(1440, 880)
        self._center_on_screen()

        self._setup_ui()
        self._setup_viewer()
        self.retranslate_ui()

        init_target = default_path or get_default_scripts_dir()
        if os.path.isdir(init_target):
            self.file_tree.load_directory(init_target)
        elif os.path.isfile(init_target):
            parent_dir = os.path.dirname(init_target)
            self.file_tree.load_directory(parent_dir)
            self.load_script_file(init_target)

    def _center_on_screen(self):
        screen = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(max(0, x), max(0, y))

    def _setup_ui(self):
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)

        outer_layout = QtWidgets.QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # 四条链路各占一个 Tab：构件设计 / 发布构件 / 发布设备 / 元件库管理。
        # 发布构件与发布设备必须分开——前者写 .acat/.pcat 并依赖规格表，
        # 后者写 .peqx 且由设备类型决定菜单归类，两者的校验与参数语义都不同。
        self.main_tabs = QtWidgets.QTabWidget(central_widget)
        outer_layout.addWidget(self.main_tabs)

        design_page = QtWidgets.QWidget(self.main_tabs)
        main_layout = QtWidgets.QVBoxLayout(design_page)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(6)

        # 1. 顶部紧凑工具栏 (纯粹构件设计工作台)
        toolbar_widget = QtWidgets.QWidget(self)
        toolbar_widget.setFixedHeight(40)
        tb_layout = QtWidgets.QHBoxLayout(toolbar_widget)
        tb_layout.setContentsMargins(6, 4, 6, 4)
        tb_layout.setSpacing(6)

        # 左上角不显示节点名称（窗口标题栏和左侧目录树已有清晰指示），保留对象兼容
        self.lbl_script_path = QtWidgets.QLabel("", toolbar_widget)
        self.lbl_script_path.setVisible(False)

        self.btn_save_code = QtWidgets.QPushButton("保存源码 (Ctrl+S)", toolbar_widget)
        self.btn_save_code.setFixedHeight(26)
        self.btn_save_code.clicked.connect(self._on_save_script)
        tb_layout.addWidget(self.btn_save_code)

        self.btn_reload = QtWidgets.QPushButton("重载", toolbar_widget)
        self.btn_reload.setFixedHeight(26)
        self.btn_reload.clicked.connect(self._on_reload_script)
        tb_layout.addWidget(self.btn_reload)

        self.btn_csv = QtWidgets.QPushButton("规格表...", toolbar_widget)
        self.btn_csv.setFixedHeight(26)
        self.btn_csv.clicked.connect(self._on_select_csv)
        tb_layout.addWidget(self.btn_csv)

        self.lbl_csv_path = QtWidgets.QLabel("", self)
        self.lbl_csv_path.setVisible(False)

        # 语言切换三按钮单选组 (Auto / 中文 / EN)，将放置在右下角任务栏
        lang_widget = QtWidgets.QWidget(self)
        lang_layout = QtWidgets.QHBoxLayout(lang_widget)
        lang_layout.setContentsMargins(0, 0, 4, 0)
        lang_layout.setSpacing(2)

        self.lang_group = QtWidgets.QButtonGroup(self)
        self.lang_group.setExclusive(True)

        self.btn_lang_auto = QtWidgets.QPushButton("Auto", lang_widget)
        self.btn_lang_auto.setCheckable(True)
        self.btn_lang_auto.setFixedHeight(20)
        self.btn_lang_auto.setProperty("compact", "true")
        self.btn_lang_auto.setToolTip("跟随系统语言")

        self.btn_lang_zh = QtWidgets.QPushButton("中文", lang_widget)
        self.btn_lang_zh.setCheckable(True)
        self.btn_lang_zh.setFixedHeight(20)
        self.btn_lang_zh.setProperty("compact", "true")
        self.btn_lang_zh.setToolTip("简体中文界面")

        self.btn_lang_en = QtWidgets.QPushButton("EN", lang_widget)
        self.btn_lang_en.setCheckable(True)
        self.btn_lang_en.setFixedHeight(20)
        self.btn_lang_en.setProperty("compact", "true")
        self.btn_lang_en.setToolTip("English Interface")

        self.lang_group.addButton(self.btn_lang_auto, 0)
        self.lang_group.addButton(self.btn_lang_zh, 1)
        self.lang_group.addButton(self.btn_lang_en, 2)

        lang_layout.addWidget(self.btn_lang_auto)
        lang_layout.addWidget(self.btn_lang_zh)
        lang_layout.addWidget(self.btn_lang_en)

        cur_lang_cfg = load_configured_language()
        if cur_lang_cfg == LANG_ZH:
            self.btn_lang_zh.setChecked(True)
        elif cur_lang_cfg == LANG_EN:
            self.btn_lang_en.setChecked(True)
        else:
            self.btn_lang_auto.setChecked(True)

        self.btn_lang_auto.clicked.connect(lambda: self._set_language(LANG_AUTO))
        self.btn_lang_zh.clicked.connect(lambda: self._set_language(LANG_ZH))
        self.btn_lang_en.clicked.connect(lambda: self._set_language(LANG_EN))

        tb_layout.addStretch()

        self.btn_run = QtWidgets.QPushButton("运行建模 (F5)", toolbar_widget)
        self.btn_run.setFixedHeight(28)
        self.btn_run.setProperty("primary", "true")
        self.btn_run.clicked.connect(self.run_and_render)
        tb_layout.addWidget(self.btn_run)

        main_layout.addWidget(toolbar_widget)

        # 2. 中间主体区域：3D 构件设计工作台 (三栏清爽布局：左目录、中参数与代码、右 3D 视口)
        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, central_widget)

        # 栏 1 (左)：构件目录树与关键字检索 (始终显示，单击即可即时切换，默认优先打开 custom_scripts)
        self.file_tree = FileTreeWidget(default_dir=get_default_scripts_dir(), parent=self.main_splitter)
        self.file_tree.script_selected.connect(self._on_tree_script_selected)
        self.file_tree.directory_changed.connect(self._on_tree_dir_changed)
        self.main_splitter.addWidget(self.file_tree)

        # 兼容性包装容器 (防止历史脚本调用报错)
        self.left_stack = QtWidgets.QStackedWidget(self)
        self.left_stack.setVisible(False)

        # 栏 2 (中)：预设切换栏 + 参数属性网格 (PropertyGrid) + 源码编辑器 (CodeEditor)
        edit_container = QtWidgets.QWidget(self.main_splitter)
        edit_layout = QtWidgets.QVBoxLayout(edit_container)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.setSpacing(4)

        preset_bar = QtWidgets.QWidget(edit_container)
        preset_bar.setFixedHeight(30)
        preset_layout = QtWidgets.QHBoxLayout(preset_bar)
        preset_layout.setContentsMargins(4, 2, 4, 2)
        preset_layout.setSpacing(4)

        self.lbl_spec = QtWidgets.QLabel("规格:", preset_bar)
        preset_layout.addWidget(self.lbl_spec)

        self.preset_combo = QtWidgets.QComboBox(preset_bar)
        self.preset_combo.setFixedHeight(24)
        self.preset_combo.setEditable(True)
        self.preset_combo.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        preset_layout.addWidget(self.preset_combo, stretch=1)

        self.btn_reset_defaults = QtWidgets.QPushButton("还原默认", preset_bar)
        self.btn_reset_defaults.setFixedHeight(24)
        self.btn_reset_defaults.clicked.connect(self._on_reset_defaults)
        preset_layout.addWidget(self.btn_reset_defaults)

        edit_layout.addWidget(preset_bar)

        self.edit_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, edit_container)
        self.property_grid = PropertyGridWidget(self.edit_splitter)
        self.edit_splitter.addWidget(self.property_grid)

        code_box = QtWidgets.QWidget(self.edit_splitter)
        code_layout = QtWidgets.QVBoxLayout(code_box)
        code_layout.setContentsMargins(0, 0, 0, 0)
        code_layout.setSpacing(2)

        code_header_bar = QtWidgets.QWidget(code_box)
        code_header_bar.setFixedHeight(26)
        ch_layout = QtWidgets.QHBoxLayout(code_header_bar)
        ch_layout.setContentsMargins(4, 2, 4, 2)
        ch_layout.setSpacing(6)

        self.code_header = QtWidgets.QLabel("Python 源码", code_header_bar)
        ch_layout.addWidget(self.code_header, stretch=1)

        self.btn_toggle_code = QtWidgets.QPushButton("收起源码 ▲", code_header_bar)
        self.btn_toggle_code.setFixedHeight(22)
        self.btn_toggle_code.setToolTip("折叠或展开下方的 Python 源码编辑器")
        self.btn_toggle_code.clicked.connect(self._toggle_code_editor)
        ch_layout.addWidget(self.btn_toggle_code)

        code_layout.addWidget(code_header_bar)

        self.code_editor = QtWidgets.QPlainTextEdit(code_box)
        self.code_editor.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        # 语法高亮：挂在编辑器文档上，QPlainTextEdit 本身也能着色
        self._highlighter = PythonHighlighter(self.code_editor.document())
        code_layout.addWidget(self.code_editor)

        self.edit_splitter.addWidget(code_box)
        self.edit_splitter.setStretchFactor(0, 6)
        self.edit_splitter.setStretchFactor(1, 4)

        edit_layout.addWidget(self.edit_splitter)
        self.main_splitter.addWidget(edit_container)

        # 右侧 OCCT 3D 视口
        right_container = QtWidgets.QWidget(self.main_splitter)
        right_layout = QtWidgets.QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        view_bar = QtWidgets.QWidget(right_container)
        view_bar.setFixedHeight(32)
        view_layout = QtWidgets.QHBoxLayout(view_bar)
        view_layout.setContentsMargins(4, 2, 4, 2)
        view_layout.setSpacing(6)

        self.right_header = QtWidgets.QLabel("3D 视口", view_bar)
        view_layout.addWidget(self.right_header, stretch=1)

        self.lbl_style = QtWidgets.QLabel("显示:", view_bar)
        view_layout.addWidget(self.lbl_style)

        self.combo_style = QtWidgets.QComboBox(view_bar)
        self.combo_style.setFixedHeight(24)
        self.combo_style.setMinimumWidth(96)
        for value, label in DISPLAY_STYLES:
            self.combo_style.addItem(label, value)
        self.combo_style.setCurrentIndex(self._style_index(self._display_style))
        self.combo_style.setToolTip("显示样式，快捷键 S 着色(无边线) / E 着色带边 / H 隐藏线 / W 线框")
        self.combo_style.currentIndexChanged.connect(self._on_style_changed)
        view_layout.addWidget(self.combo_style)

        self.lbl_view = QtWidgets.QLabel("视图:", view_bar)
        view_layout.addWidget(self.lbl_view)

        self.combo_view = QtWidgets.QComboBox(view_bar)
        self.combo_view.setFixedHeight(24)
        self.combo_view.setMinimumWidth(84)
        for index, (value, label, key) in enumerate(VIEW_MODES):
            self.combo_view.addItem(label, value)
            self.combo_view.setItemData(index, "快捷键 " + key, QtCore.Qt.ToolTipRole)
        self.combo_view.setCurrentIndex(self._view_index(self._current_view))
        self.combo_view.setToolTip("标准视图，快捷键 1-7")
        self.combo_view.currentIndexChanged.connect(self._on_view_changed)
        view_layout.addWidget(self.combo_view)

        self.btn_fit = QtWidgets.QPushButton("适应窗口", view_bar)
        self.btn_fit.setFixedHeight(24)
        self.btn_fit.setToolTip("缩放至全部实体 (快捷键 0)")
        self.btn_fit.clicked.connect(lambda: self._set_view('fit'))
        view_layout.addWidget(self.btn_fit)

        self.btn_dim_preview = QtWidgets.QPushButton("轴测预览", view_bar)
        self.btn_dim_preview.setFixedHeight(24)
        self.btn_dim_preview.setToolTip(
            "生成当前构件的轴测预览图（支吊架/设备含尺寸标注，管件等仅着色）")
        self.btn_dim_preview.clicked.connect(self._on_show_annotated_preview)
        view_layout.addWidget(self.btn_dim_preview)

        right_layout.addWidget(view_bar)

        self.viewer_widget = SafeQtViewer3d(right_container)
        right_layout.addWidget(self.viewer_widget)

        self.file_tree.setMinimumWidth(260)
        edit_container.setMinimumWidth(340)
        right_container.setMinimumWidth(500)

        self.main_splitter.addWidget(right_container)
        self.main_splitter.setSizes([280, 380, 780])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 0)
        self.main_splitter.setStretchFactor(2, 1)

        main_layout.addWidget(self.main_splitter, stretch=1)

        # 3. 底部日志区
        bottom_widget = QtWidgets.QWidget(design_page)
        bottom_widget.setFixedHeight(82)
        bottom_layout = QtWidgets.QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(2)

        self.lbl_log = QtWidgets.QLabel("执行与调试日志", bottom_widget)
        bottom_layout.addWidget(self.lbl_log)

        self.log_box = QtWidgets.QPlainTextEdit(bottom_widget)
        self.log_box.setReadOnly(True)
        bottom_layout.addWidget(self.log_box)

        main_layout.addWidget(bottom_widget)

        # 4. 主窗口底部全局任务栏/状态栏 (跨所有标签页常驻，右下角为语言切换)
        status_bar = self.statusBar()
        status_bar.setSizeGripEnabled(False)
        status_bar.setFixedHeight(30)

        self.lbl_status = QtWidgets.QLabel("就绪", self)
        self.lbl_status.setContentsMargins(6, 0, 6, 0)
        status_bar.addWidget(self.lbl_status)

        self.loading_bar = QtWidgets.QProgressBar(self)
        self.loading_bar.setFixedSize(140, 12)
        self.loading_bar.setRange(0, 0)
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setVisible(False)
        status_bar.addWidget(self.loading_bar)

        # 语言切换常驻右下角任务栏
        status_bar.addPermanentWidget(lang_widget)

        # ---- 注册各 Tab ----
        self.main_tabs.addTab(design_page, tr("tab_design", "构件设计"))

        scripts_root = get_default_scripts_dir()
        self.publish_page = ComponentPublishPage(self.main_tabs, scripts_root=scripts_root)
        self.equipment_publish_page = EquipmentPublishPage(self.main_tabs, scripts_root=scripts_root)
        self.catalog_page = CatalogManagerPage(self.main_tabs, scripts_root=scripts_root)
        self.spec_page = SpecManagerPage(self.main_tabs, scripts_root=scripts_root)

        self.main_tabs.addTab(self.publish_page, tr("tab_publish_component", "发布构件"))
        self.main_tabs.addTab(self.equipment_publish_page, tr("tab_publish_equipment", "发布设备"))
        self.main_tabs.addTab(self.catalog_page, tr("tab_manage_catalog", "元件库管理"))
        self.main_tabs.addTab(self.spec_page, tr("tab_manage_spec", "等级库管理"))
        self.main_tabs.currentChanged.connect(self._on_tab_changed)
        for page in (self.catalog_page, self.spec_page):
            if hasattr(page, "status_message"):
                page.status_message.connect(self._on_page_status)

    def _on_tab_changed(self, idx: int):
        """Tab 切换时按需惰性加载数据，切回 3D 视口时平滑同步尺寸，防止任何卡顿与闪退。"""
        if idx == 0:
            # 切回 3D 页：延后一拍，等 Qt 完成本帧布局/绘制后再同步视口
            QtCore.QTimer.singleShot(0, self._ensure_viewport_ready)
        elif idx == 1:
            if hasattr(self, "publish_page") and hasattr(self.publish_page, "ensure_loaded"):
                self.publish_page.ensure_loaded()
        elif idx == 2:
            if hasattr(self, "equipment_publish_page") and hasattr(self.equipment_publish_page, "ensure_loaded"):
                self.equipment_publish_page.ensure_loaded()
        elif idx == 3:
            if hasattr(self, "catalog_page") and hasattr(self.catalog_page, "ensure_loaded"):
                self.catalog_page.ensure_loaded()
        elif idx == 4:
            if hasattr(self, "spec_page") and hasattr(self.spec_page, "ensure_loaded"):
                self.spec_page.ensure_loaded()

    def closeEvent(self, event):
        """关窗前先停止各页后台任务，避免 QThread 在窗口析构后仍在运行导致闪退。"""
        preview_proc = getattr(self, "_preview_proc", None)
        if preview_proc is not None and preview_proc.state() != QtCore.QProcess.NotRunning:
            try:
                preview_proc.kill()
                preview_proc.waitForFinished(1500)
            except Exception:
                pass
        for attr in ("publish_page", "equipment_publish_page",
                     "catalog_page", "spec_page"):
            page = getattr(self, attr, None)
            if page is not None and hasattr(page, "shutdown"):
                try:
                    page.shutdown()
                except Exception:
                    pass
        super(Plant3dOccAppWindow, self).closeEvent(event)

    def _scripts_root(self):
        """发布/管理页共用的脚本根目录。"""
        return get_default_scripts_dir()

    def _on_page_status(self, message: str):
        """各页操作结果都进窗口左下角任务栏，不跟当前 Tab 走。"""
        text = str(message or "").strip()
        if text:
            self.lbl_status.setText(text)

    def _begin_loading(self, message: str, done: int = None, total: int = None):
        """开启底部任务状态栏与窗口 Loading；总量已知时显示确定进度百分比，未知时流动条。"""
        self.lbl_status.setText(message)
        if done is not None and total:
            self.loading_bar.setRange(0, 100)
            self.loading_bar.setValue(int(done * 100.0 / max(1, total)))
            self.loading_bar.setVisible(True)
            self.setWindowTitle("[%d%% %s] - %s" % (
                int(done * 100.0 / max(1, total)), message, tr("app_title")))
        else:
            self.loading_bar.setRange(0, 0)
            self.loading_bar.setVisible(True)
            self.setWindowTitle(f"[{message}] - {tr('app_title')}")
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

    def _update_loading(self, message: str, done: int, total: int):
        """进行中更新：不重复压光标，只刷新进度。"""
        if total:
            self.lbl_status.setText(message)
            pct = int(done * 100.0 / max(1, total))
            self.loading_bar.setRange(0, 100)
            self.loading_bar.setValue(pct)
            self.setWindowTitle("[%d%% %s] - %s" % (pct, message, tr("app_title")))

    def _end_loading(self, message: str = "就绪"):
        """结束 Loading 指示并恢复状态栏与任务栏标题。"""
        self.loading_bar.setVisible(False)
        self.lbl_status.setText(message)
        script_tag = f" - {os.path.basename(self._current_script_path)}" if self._current_script_path else ""
        self.setWindowTitle(f"{tr('app_title')}{script_tag}")
        while QtWidgets.QApplication.overrideCursor() is not None:
            QtWidgets.QApplication.restoreOverrideCursor()

    def _setup_viewer(self):
        self.display = None
        self._pending_render = False

    def _configure_smooth_drawer(self, show_edges: bool = False):
        """配置 OCCT 默认 Drawer：主色不带边线 (FaceBoundaryDraw=False) + 高精度平滑曲面细分 (禁止网格化)。"""
        if not self.display:
            return
        try:
            ctx = getattr(self.display, "Context", None)
            if ctx is not None and hasattr(ctx, "DefaultDrawer"):
                drawer = ctx.DefaultDrawer()
                if hasattr(drawer, "SetFaceBoundaryDraw"):
                    drawer.SetFaceBoundaryDraw(bool(show_edges))
                if show_edges and hasattr(drawer, "FaceBoundaryAspect"):
                    aspect = drawer.FaceBoundaryAspect()
                    aspect.SetColor(Quantity_Color(Quantity_NOC_BLACK))
                    aspect.SetWidth(EDGE_LINE_WIDTH)
                    aspect.SetTypeOfLine(Aspect_TOL_SOLID)
                if hasattr(drawer, "SetDeviationCoefficient"):
                    drawer.SetDeviationCoefficient(0.002)
                if hasattr(drawer, "SetDeviationAngle"):
                    drawer.SetDeviationAngle(0.2)
        except Exception:
            pass

    def _ensure_display(self):
        if self.display is not None and getattr(self.viewer_widget, "_inited", False):
            return True
        if not self.viewer_widget.isVisible() or self.viewer_widget.width() <= 1:
            return False

        try:
            self.viewer_widget.InitDriver()
            if not getattr(self.viewer_widget, "_inited", False):
                self.display = None
                return False
            self.display = getattr(self.viewer_widget, "_display", None)
            if self.display is None:
                return False
            self.display.set_bg_gradient_color([245, 247, 250], [235, 238, 242])

            # 使用 OCCT 原生平滑 Phong 着色（禁止 Unlit 扁平化与网格棱线）
            try:
                from OCC.Core.Graphic3d import Graphic3d_TypeOfShadingModel_Phong
                self.display.View.SetShadingModel(Graphic3d_TypeOfShadingModel_Phong)
            except Exception:
                pass
            try:
                if hasattr(self.display.View, "SetAntialiasingOn"):
                    self.display.View.SetAntialiasingOn()
            except Exception:
                pass

            self._configure_smooth_drawer(show_edges=(self._display_style == "shaded_with_edges"))
            self.display.View_Iso()
            self._update_view_header()
            return True
        except Exception:
            return False

    def showEvent(self, event):
        super(Plant3dOccAppWindow, self).showEvent(event)
        if self._viewport_synced:
            return
        self._viewport_synced = True
        try:
            # 显式绑定 Windows 原生大图标 (48x48) 与小图标 (24x24) 到 HWND，确保任务栏高清无裁切
            if sys.platform == "win32":
                try:
                    import ctypes
                    hwnd = int(self.winId())
                    icon_path = os.path.join(os.path.dirname(__file__), "app_icon.ico")
                    if os.path.isfile(icon_path):
                        IMAGE_ICON = 1
                        LR_LOADFROMFILE = 0x00000010
                        hicon_big = ctypes.windll.user32.LoadImageW(0, icon_path, IMAGE_ICON, 48, 48, LR_LOADFROMFILE)
                        hicon_small = ctypes.windll.user32.LoadImageW(0, icon_path, IMAGE_ICON, 24, 24, LR_LOADFROMFILE)
                        WM_SETICON = 0x0080
                        if hicon_big:
                            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 1, hicon_big)
                        if hicon_small:
                            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, 0, hicon_small)
                except Exception:
                    pass

            self.main_splitter.setSizes([280, 380, 780])
            # 关键：InitDriver / 首次渲染 / Repaint 都不能在 showEvent（Qt 正在
            # 处理显示与绘制）里同步执行——会与 GL 窗口的 backing store 冲突，
            # 触发 "QWidget::repaint: Recursive repaint detected" 与
            # "QBackingStore::endPaint() called with active painter"。
            self._viewport_init_retries = 0
            QtCore.QTimer.singleShot(0, self._ensure_viewport_ready)
        except Exception:
            pass

    def _ensure_viewport_ready(self):
        """在 paint 事件之外完成 3D 视口初始化；视口暂不可见时短暂重试。"""
        try:
            if self.display is not None:
                self._sync_viewport()
                return
            if not self._ensure_display():
                if getattr(self, "_viewport_init_retries", 0) < 40:
                    self._viewport_init_retries = getattr(self, "_viewport_init_retries", 0) + 1
                    QtCore.QTimer.singleShot(50, self._ensure_viewport_ready)
                return
            self._viewport_init_retries = 0
            if self._pending_render:
                self._pending_render = False
                self.run_and_render()
            else:
                self._sync_viewport()
        except Exception:
            pass

    def _sync_viewport(self):
        if self.display is None or not getattr(self.viewer_widget, "_inited", False):
            return
        try:
            self.display.View.MustBeResized()
            self.display.Repaint()
        except Exception:
            pass

    def _switch_mode(self, mode_idx=0):
        """仅保留构件设计工作台单一视图 (保持接口兼容)。"""
        pass

    def _on_tree_script_selected(self, py_path):
        self._begin_loading(f"正在切换脚本: {os.path.basename(py_path)}...")
        try:
            self.load_script_file(py_path)
        finally:
            self._end_loading(self.lbl_status.text())

    def _on_tree_dir_changed(self, folder_path):
        """文件树切换根目录后，同步发布构件/发布设备两个 tab 的扫描目录。"""
        for page_attr in ("publish_page", "equipment_publish_page"):
            page = getattr(self, page_attr, None)
            if page is not None and hasattr(page, "set_scripts_root"):
                page.set_scripts_root(folder_path)

    _STYLE_KEYS = {
        QtCore.Qt.Key_W: "wireframe",
        QtCore.Qt.Key_S: "shaded",
        QtCore.Qt.Key_E: "shaded_with_edges",
        QtCore.Qt.Key_H: "hidden_line",
    }

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F5:
            self.run_and_render()
            event.accept()
            return
        if (event.modifiers() & QtCore.Qt.ControlModifier) and event.key() == QtCore.Qt.Key_S:
            self._on_save_script()
            event.accept()
            return

        focus = QtWidgets.QApplication.focusWidget()
        editing = isinstance(focus, (QtWidgets.QPlainTextEdit, QtWidgets.QLineEdit, QtWidgets.QTextEdit))
        if editing:
            super(Plant3dOccAppWindow, self).keyPressEvent(event)
            return

        for _value, _label, key in VIEW_MODES:
            if event.key() == getattr(QtCore.Qt, "Key_" + key):
                self._set_view(_value)
                event.accept()
                return
        if event.key() == QtCore.Qt.Key_0:
            self._set_view("fit")
            event.accept()
            return

        style = self._STYLE_KEYS.get(event.key())
        if style is not None:
            self.set_display_style(style)
            event.accept()
            return

        super(Plant3dOccAppWindow, self).keyPressEvent(event)

    @staticmethod
    def _style_index(style):
        for index, (value, _label) in enumerate(DISPLAY_STYLES):
            if value == style:
                return index
        return 0

    @staticmethod
    def _view_index(view):
        for index, (value, _label, _key) in enumerate(VIEW_MODES):
            if value == view:
                return index
        return 0

    def _view_label(self, view):
        for value, label, _key in get_view_modes():
            if value == view:
                return label
        return tr("view_iso")

    def _style_label(self, style):
        for value, label in get_display_styles():
            if value == style:
                return label
        return tr("style_shaded")

    def _toggle_code_editor(self):
        is_vis = self.code_editor.isVisible()
        self.code_editor.setVisible(not is_vis)
        if is_vis:
            self.btn_toggle_code.setText("展开源码 ▼" if current_language() == "zh" else "Expand Code ▼")
            self.edit_splitter.setSizes([1000, 26])
        else:
            self.btn_toggle_code.setText("收起源码 ▲" if current_language() == "zh" else "Collapse Code ▲")
            self.edit_splitter.setSizes([550, 450])

    def _set_language(self, code):
        set_current_language(code, persist=True)
        self.retranslate_ui()

    def _on_language_changed(self, index_or_code):
        if isinstance(index_or_code, str):
            code = index_or_code
        elif hasattr(self, "combo_lang") and self.combo_lang is not None:
            code = self.combo_lang.itemData(index_or_code)
        else:
            code = None
        if code:
            self._set_language(code)

    def retranslate_ui(self):
        script_tag = f" - {os.path.basename(self._current_script_path)}" if self._current_script_path else ""
        self.setWindowTitle(f"{tr('app_title')}{script_tag}")

        if not self._current_script_path:
            self.lbl_script_path.setText(tr("lbl_no_script"))
        else:
            self.lbl_script_path.setText(f"📄 {os.path.basename(self._current_script_path)}")

        self.btn_save_code.setText(tr("btn_save_code"))
        self.btn_reload.setText(tr("btn_reload"))
        self.btn_csv.setText(tr("btn_preset"))
        self.btn_run.setText(tr("btn_run"))

        self.lbl_spec.setText(tr("lbl_spec"))
        self.btn_reset_defaults.setText(tr("btn_reset_defaults"))
        self.code_header.setText(tr("code_header", "Python 源码"))
        if hasattr(self, "btn_toggle_code"):
            is_vis = self.code_editor.isVisible()
            self.btn_toggle_code.setText(("收起源码 ▲" if is_vis else "展开源码 ▼") if current_language() == "zh" else ("Collapse Code ▲" if is_vis else "Expand Code ▼"))

        self.right_header.setText(tr("lbl_3d_model", "3D 视口"))
        self.lbl_style.setText(tr("lbl_style"))
        self.lbl_view.setText(tr("lbl_view"))
        self.btn_fit.setText(tr("btn_fit"))
        self.btn_dim_preview.setText(tr("btn_dim_preview"))
        self.btn_dim_preview.setToolTip(tr("btn_dim_preview_tip"))

        self.lbl_log.setText(tr("lbl_log_title"))
        if self.lbl_status.text() in ("就绪", "Ready"):
            self.lbl_status.setText(tr("status_ready"))

        cur_style = self._display_style
        self.combo_style.blockSignals(True)
        self.combo_style.clear()
        for val, lbl in get_display_styles():
            self.combo_style.addItem(lbl, val)
        self.combo_style.setCurrentIndex(self._style_index(cur_style))
        self.combo_style.blockSignals(False)

        cur_view = self._current_view
        self.combo_view.blockSignals(True)
        self.combo_view.clear()
        for idx, (val, lbl, key) in enumerate(get_view_modes()):
            self.combo_view.addItem(lbl, val)
            tip_str = ("快捷键 " if current_language() == "zh" else "Shortcut ") + key
            self.combo_view.setItemData(idx, tip_str, QtCore.Qt.ToolTipRole)
        self.combo_view.setCurrentIndex(self._view_index(cur_view))
        self.combo_view.blockSignals(False)

        self._update_view_header()

        if hasattr(self, "file_tree"):
            self.file_tree.retranslate_ui()
        if hasattr(self, "property_grid"):
            self.property_grid.retranslate_ui()

        # 业务页各自刷新文案（未实现 retranslate_ui 的页跳过）
        for attr in ("publish_page", "equipment_publish_page", "catalog_page", "spec_page"):
            page = getattr(self, attr, None)
            if page is not None and hasattr(page, "retranslate_ui"):
                page.retranslate_ui()

        # Tab 标题
        if hasattr(self, "main_tabs"):
            self.main_tabs.setTabText(0, tr("tab_design", "构件设计"))
            self.main_tabs.setTabText(1, tr("tab_publish_component", "发布构件"))
            self.main_tabs.setTabText(2, tr("tab_publish_equipment", "发布设备"))
            self.main_tabs.setTabText(3, tr("tab_manage_catalog", "元件库管理"))
            self.main_tabs.setTabText(4, tr("tab_manage_spec", "等级库管理"))

    def _on_style_changed(self, index):
        style = self.combo_style.itemData(index)
        if style:
            self.set_display_style(style)

    def _on_view_changed(self, index):
        view = self.combo_view.itemData(index)
        if view:
            self._set_view(view)

    def set_display_style(self, style):
        self._display_style = style
        expected = self._style_index(style)
        if self.combo_style.currentIndex() != expected:
            self.combo_style.blockSignals(True)
            self.combo_style.setCurrentIndex(expected)
            self.combo_style.blockSignals(False)
        self._apply_display_style()
        self._update_view_header()

    def _apply_display_style(self):
        if not self.display:
            return
        style = self._display_style
        context = getattr(self.display, "Context", None)
        try:
            if style == "wireframe":
                self._configure_smooth_drawer(show_edges=False)
                self.display.SetModeWireFrame()
            elif style == "hidden_line":
                self._configure_smooth_drawer(show_edges=False)
                self.display.SetModeHLR()
            else:
                show_edges = (style == "shaded_with_edges")
                self._configure_smooth_drawer(show_edges=show_edges)
                self.display.SetModeShaded()
                if context is not None:
                    for ais in self._ais_objects:
                        try:
                            context.Redisplay(ais, False)
                        except Exception:
                            pass
            self.display.Repaint()
        except Exception:
            pass

    def _set_face_boundaries(self, enabled):
        self._configure_smooth_drawer(show_edges=bool(enabled))
        context = getattr(self.display, "Context", None)
        if context is not None:
            for ais in self._ais_objects:
                try:
                    context.Redisplay(ais, False)
                except Exception:
                    pass

    def _set_view(self, view_type, repaint=True):
        if view_type == "fit":
            if not self.display:
                return
            self.display.FitAll()
            if repaint:
                self.display.Repaint()
            return

        if view_type not in [value for value, _l, _k in VIEW_MODES]:
            return

        self._current_view = view_type
        expected = self._view_index(view_type)
        if self.combo_view.currentIndex() != expected:
            self.combo_view.blockSignals(True)
            self.combo_view.setCurrentIndex(expected)
            self.combo_view.blockSignals(False)

        if not self.display:
            return
        if view_type == "iso":
            self.display.View_Iso()
        elif view_type == "front":
            self.display.View_Front()
        elif view_type == "rear":
            self.display.View_Rear()
        elif view_type == "left":
            self.display.View_Left()
        elif view_type == "right":
            self.display.View_Right()
        elif view_type == "top":
            self.display.View_Top()
        elif view_type == "bottom":
            self.display.View_Bottom()
        self.display.FitAll()
        if repaint:
            self.display.Repaint()
        self._update_view_header()

    def _update_view_header(self):
        if not hasattr(self, "right_header"):
            return
        tag = "(平滑无网格着色)" if current_language() == "zh" else "(Smooth Shaded)"
        self.right_header.setText(
            f" {tr('lbl_3d_model')} · {self._view_label(self._current_view)} · {self._style_label(self._display_style)} {tag}"
        )

    def _clear_viewport(self):
        """彻底清除上一个脚本在视口和交互上下文中遗留的所有 3D 实体与 HLR 投影线。"""
        if self.display is not None:
            try:
                ctx = getattr(self.display, "Context", None)
                if ctx is not None:
                    ctx.RemoveAll(True)
                else:
                    self.display.EraseAll()
                self._ais_objects = []
                self._shapes = []
            except Exception:
                pass

    def load_script_file(self, path):
        if not os.path.exists(path):
            return
        self._clear_viewport()
        self._begin_loading(f"正在加载脚本 {os.path.basename(path)}...")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
            self._current_script_path = path
            self.lbl_script_path.setText(os.path.basename(path))
            self.lbl_script_path.setToolTip(path)
            self.code_editor.setPlainText(code)

            auto_csv = os.path.splitext(path)[0] + ".csv"
            if os.path.exists(auto_csv):
                self.load_csv_file(auto_csv)
            else:
                self.lbl_csv_path.setText("无预设表")
                self.lbl_csv_path.setToolTip(None)
                self._current_csv_path = None
                self._parse_and_update_grid()

            self.run_and_render()
        except Exception as e:
            self.log_box.setPlainText("加载脚本失败: " + str(e))
            self._end_loading("加载脚本失败")
        else:
            self._end_loading(self.lbl_status.text())

    def load_csv_file(self, path):
        if not os.path.exists(path):
            return
        try:
            self._presets.clear()
            self.preset_combo.blockSignals(True)
            self.preset_combo.clear()

            with open(path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            if lines:
                header = [c.strip() for c in lines[0].split(',')]
                for line in lines[1:]:
                    cells = [c.strip() for c in line.split(',')]
                    if len(cells) >= 2 and any(any(ch.isdigit() for ch in c) for c in cells):
                        name = cells[0]
                        row_dict = {header[i]: (cells[i] if i < len(cells) else '') for i in range(len(header))}
                        summary = ", ".join([f"{k}={v}" for k, v in list(row_dict.items())[1:4] if v])
                        display_text = f"{name}  [{summary}]" if summary else name
                        self._presets.append({'name': name, 'display': display_text, 'values': row_dict})
                        self.preset_combo.addItem(display_text, row_dict)

            self.preset_combo.blockSignals(False)
            self._current_csv_path = path
            self.lbl_csv_path.setText(os.path.basename(path))
            self.lbl_csv_path.setToolTip(path)

            self._parse_and_update_grid()
            if self._presets:
                self.preset_combo.blockSignals(True)
                self.preset_combo.setCurrentIndex(0)
                self.preset_combo.blockSignals(False)
                self.property_grid.set_values(self._presets[0]['values'])
        except Exception as e:
            self.log_box.setPlainText("加载 CSV 失败: " + str(e))

    def _parse_and_update_grid(self):
        code = self.code_editor.toPlainText()
        param_list = []
        for line in code.split('\n'):
            line = line.strip()
            if line.startswith('@param(') and line.endswith(')'):
                inner = line[7:-1]
                m = re.match(r'([A-Za-z0-9_]+)\s*=\s*([A-Za-z0-9_]+)', inner)
                if m:
                    p_name, p_type = m.group(1), m.group(2)
                    tooltip = ""
                    long_desc = ""
                    m_tt = re.search(r'TooltipShort\s*=\s*["\']([^"\']+)["\']', inner)
                    if m_tt:
                        tooltip = m_tt.group(1)
                    m_ttl = re.search(r'TooltipLong\s*=\s*["\']([^"\']+)["\']', inner)
                    if m_ttl:
                        long_desc = m_ttl.group(1)
                    param_list.append({
                        'name': p_name,
                        'type': p_type,
                        'tooltip': tooltip,
                        'tooltip_long': long_desc,
                        'default': '0.0'
                    })

        m_def = re.search(r'def\s+([A-Za-z0-9_]+)\s*\((.*?)\):', code, re.S)
        if m_def:
            args_str = m_def.group(2)
            for part in args_str.split(','):
                if '=' in part:
                    k, v = part.split('=', 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    for p in param_list:
                        if p['name'] == k:
                            p['default'] = v

        self.property_grid.load_parameters(param_list)

    def run_and_render(self):
        if not self._ensure_display():
            self._pending_render = True
            return

        t0 = time.time()
        self._begin_loading("正在运行模型并计算 CSG 几何拓扑...")

        code = self.code_editor.toPlainText()
        if not code.strip():
            self.log_box.setPlainText("编辑器中无代码。")
            self._end_loading("无代码")
            return

        values = self.property_grid.get_values()
        from ..runner.sandbox import execute_script_source

        try:
            filename_base = ""
            if self._current_script_path:
                filename_base = os.path.splitext(os.path.basename(self._current_script_path))[0]

            mod_globals, entry_name = execute_script_source(
                code, filename_hint=filename_base, origin="<editor_script>"
            )
            if not entry_name:
                self.log_box.setPlainText("未在代码中找到可执行的自定义构件 def 函数入口。")
                return

            entry_fn = mod_globals[entry_name]

            import inspect

            def clean_arg(arg_val):
                if not isinstance(arg_val, str):
                    return arg_val
                s_val = arg_val.strip()
                if not s_val:
                    return None
                m_b = re.match(r'^[Mm](\d+(?:\.\d+)?)$', s_val)
                if m_b:
                    return float(m_b.group(1))
                m_n = re.match(r'^([+-]?\d+(?:\.\d+)?)\s*[\u4e00-\u9fa5a-zA-Z]*$', s_val)
                if m_n:
                    return float(m_n.group(1))
                return s_val

            try:
                sig = inspect.signature(entry_fn)
                call_args = {}
                has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
                for k, v in values.items():
                    if has_var_kw or k in sig.parameters:
                        c_val = clean_arg(v)
                        if c_val is not None:
                            call_args[k] = c_val
            except Exception:
                call_args = {}
                for k, v in values.items():
                    c_val = clean_arg(v)
                    if c_val is not None:
                        call_args[k] = c_val

            s = OccSession()
            entry_fn(s, **call_args)

            shapes = s.get_final_shapes()
            self._shapes = list(shapes)
            t_calc = time.time() - t0

            if not shapes:
                self.log_box.setPlainText(f"脚本 {entry_name} 执行完毕，但未产生任何 3D 实体！")
                return

            # 预先配置 Drawer（避免显示后再二次 Redisplay 触发重复网格剖分卡顿）
            show_edges = (self._display_style == "shaded_with_edges")
            self._configure_smooth_drawer(show_edges=show_edges)

            # 安全从 OCCT 交互上下文释放历史 3D 实体，防止野指针闪退与外形堆叠
            try:
                if hasattr(self.display, "Context") and self.display.Context is not None:
                    self.display.EraseAll()
                    for ais in self._ais_objects:
                        try:
                            self.display.Context.Remove(ais, False)
                        except Exception:
                            pass
                else:
                    self.display.EraseAll()
            except Exception:
                pass
            self._ais_objects = []
            steel_gray = Quantity_Color(Quantity_NOC_GRAY50)

            for sp in shapes:
                shape = sp.shape if hasattr(sp, 'shape') else sp
                if shape and not shape.IsNull():
                    ais_list = self.display.DisplayShape(shape, update=False, color=steel_gray, transparency=0.0)
                    if ais_list is None:
                        continue
                    self._ais_objects.extend(ais_list)

            if self._display_style == "wireframe":
                self.display.SetModeWireFrame()
            elif self._display_style == "hidden_line":
                self.display.SetModeHLR()
            else:
                self.display.SetModeShaded()

            self._set_view(self._current_view, repaint=True)
            self._update_view_header()

            msg = (
                f"已成功生成 {len(shapes)} 个有效 3D 实体。\n"
                f"入口函数: {entry_name}  |  端口数: {len(s.ports)}  |  标注尺寸数: {len(s.grips)}\n"
                f"CSG 建模与平滑着色耗时: {t_calc*1000:.1f}ms"
            )
            self.log_box.setPlainText(msg)
            self._end_loading(f"{entry_name} 渲染完成 ({t_calc*1000:.1f}ms)")
        except Exception:
            err = traceback.format_exc()
            self.log_box.setPlainText("执行失败:\n" + err)
            self._end_loading("执行出错")

    def _apply_edge_style(self, ais):
        drawer = ais.Attributes()
        drawer.SetFaceBoundaryDraw(True)
        aspect = drawer.FaceBoundaryAspect()
        aspect.SetColor(Quantity_Color(Quantity_NOC_BLACK))
        aspect.SetWidth(EDGE_LINE_WIDTH)
        aspect.SetTypeOfLine(Aspect_TOL_SOLID)
        ais.SetAttributes(drawer)
        context = getattr(self.display, "Context", None)
        if context is not None:
            context.Redisplay(ais, False)

    def _on_save_script(self):
        if not self._current_script_path:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "保存 Python 构件脚本", "pyscripts", "Python 脚本 (*.py)"
            )
            if not file_path:
                return
            self._current_script_path = file_path
        try:
            with open(self._current_script_path, "w", encoding="utf-8") as fp:
                fp.write(self.code_editor.toPlainText())
            self._parse_and_update_grid()
            self.lbl_status.setText(f"已保存: {os.path.basename(self._current_script_path)}")
        except Exception as exc:
            self.log_box.appendPlainText("保存失败: " + str(exc))

    def _on_show_annotated_preview(self):
        """异步生成当前构件的着色+边线轴测大图。

        OCC 离屏视口只能在进程主线程创建，和主窗口实时 3D 视口共用显卡上下文
        时容易触发 wglMakeCurrent 冲突闪退。这里用 QProcess 把整次渲染放到独立
        子进程：界面不阻塞，子进程异常也不会带走主程序。

        支吊架和设备生成带尺寸标注图；管件、阀门、仪表只生成轴测着色图。
        """
        if not self._current_script_path or not os.path.isfile(self._current_script_path):
            QtWidgets.QMessageBox.information(self, "提示", "请先选择一个构件脚本。")
            return
        import json
        import tempfile
        from ..catalog.model import inspect_script, needs_dimension_annotation

        job = inspect_script(self._current_script_path, auto_generate_sizes=True)
        values = self.property_grid.get_values()
        call_params = {}
        for k, v in values.items():
            try:
                call_params[k] = float(v)
            except Exception:
                call_params[k] = v

        out_dir = os.path.join(tempfile.gettempdir(), "p3d_occ_live_preview")
        os.makedirs(out_dir, exist_ok=True)
        clean_path = os.path.join(out_dir, "%s_clean.png" % job["stem"])
        param_text = json.dumps(call_params, ensure_ascii=False)
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        if getattr(sys, "frozen", False):
            program = sys.executable
            args = ["--render-preview", self._current_script_path,
                    "--output-dir", out_dir, "--params-json", param_text,
                    "--clean-preview", clean_path]
        else:
            program = sys.executable
            args = ["-u", "-m", "plant3d_occ", "--render-preview", self._current_script_path,
                    "--output-dir", out_dir, "--params-json", param_text,
                    "--clean-preview", clean_path]

        proc = QtCore.QProcess(self)
        proc.setProcessChannelMode(QtCore.QProcess.SeparateChannels)
        proc.setWorkingDirectory(root)
        env = QtCore.QProcessEnvironment.systemEnvironment()
        old_path = env.value("PYTHONPATH", "")
        env.insert("PYTHONPATH", root + (os.pathsep + old_path if old_path else ""))
        env.insert("PYTHONIOENCODING", "utf-8")
        env.insert("PYTHONUNBUFFERED", "1")
        proc.setProcessEnvironment(env)
        self._preview_proc = proc
        proc.finished.connect(
            lambda code, _status: self._on_annotated_preview_finished(
                proc, code, job, clean_path))
        proc.errorOccurred.connect(lambda _err: self._on_annotated_preview_error(proc))
        if needs_dimension_annotation(job):
            self._begin_loading("正在异步生成着色+边线标注预览图...")
        else:
            self._begin_loading("正在异步生成轴测着色预览图...")
        proc.start(program, args)

    def _on_annotated_preview_error(self, proc):
        if proc is not self._preview_proc or getattr(proc, "_p3d_error_reported", False):
            return
        proc._p3d_error_reported = True
        self._end_loading("预览生成失败")
        QtWidgets.QMessageBox.warning(self, "生成轴测预览图失败", "预览渲染子进程启动失败。")

    def _on_annotated_preview_finished(self, proc, exit_code, job, clean_path):
        if proc is not self._preview_proc or getattr(proc, "_p3d_error_reported", False):
            return
        import json

        out_text = bytes(proc.readAllStandardOutput()).decode("utf-8", "replace")
        err_text = bytes(proc.readAllStandardError()).decode("utf-8", "replace")
        paths = {}
        for line in out_text.splitlines():
            line = line.strip()
            if not line.startswith("{"):
                continue
            try:
                data = json.loads(line)
            except Exception:
                continue
            raw_paths = data.get("paths") if isinstance(data, dict) else None
            if isinstance(raw_paths, dict):
                for key, value in raw_paths.items():
                    try:
                        paths[int(key)] = value
                    except (TypeError, ValueError):
                        pass

        if exit_code != 0 or not paths.get(640):
            self._end_loading("预览生成失败")
            detail = err_text.strip()[-1500:] or out_text.strip()[-1500:] \
                or ("渲染子进程退出代码 %s" % exit_code)
            QtWidgets.QMessageBox.warning(self, "生成轴测预览图失败", detail)
            return

        self._end_loading("已生成轴测预览图")
        self._show_annotated_preview_dialog(job, paths, clean_path)

    def _show_annotated_preview_dialog(self, job, paths, clean_path):
        from ..catalog.model import needs_dimension_annotation

        annotate = needs_dimension_annotation(job)
        dlg = QtWidgets.QDialog(self)
        if annotate:
            dlg.setWindowTitle(f"着色+边线 外形与轴测尺寸标注大图 — {job['stem']}")
            dlg.resize(1200, 640)
            images = (
                ("1. 着色+边线 外形 + 轴测尺寸标注图 (发布图)", paths.get(640, ""), 560),
                ("2. 着色+边线 3D 外形图 (无标注)", clean_path, 560),
            )
        else:
            dlg.setWindowTitle(f"着色+边线 轴测图 — {job['stem']}")
            dlg.resize(760, 700)
            images = (
                ("着色+边线 轴测图", paths.get(640, "") or clean_path, 680),
            )
        lay = QtWidgets.QHBoxLayout(dlg)
        for title_txt, img_file, max_px in images:
            box = QtWidgets.QGroupBox(title_txt, dlg)
            blay = QtWidgets.QVBoxLayout(box)
            lbl = QtWidgets.QLabel(box)
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            if img_file and os.path.isfile(img_file):
                pix = QtGui.QPixmap(img_file).scaled(
                    max_px, max_px, QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation)
                lbl.setPixmap(pix)
            blay.addWidget(lbl)
            lay.addWidget(box)
        dlg.exec()

    def _on_reload_script(self):
        if self._current_script_path and os.path.exists(self._current_script_path):
            self.load_script_file(self._current_script_path)

    def _on_select_csv(self):
        start_dir = os.path.dirname(self._current_script_path) if self._current_script_path else get_default_scripts_dir()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "选择 CSV 预设表", start_dir, "CSV 规格表 (*.csv);;所有文件 (*.*)"
        )
        if file_path:
            self.load_csv_file(file_path)

    def _on_clear_csv(self):
        self._presets.clear()
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        self.preset_combo.blockSignals(False)
        self.lbl_csv_path.setText("无预设表")
        self.lbl_csv_path.setToolTip(None)
        self._current_csv_path = None

    def _on_preset_changed(self, idx):
        if 0 <= idx < len(self._presets):
            self.property_grid.set_values(self._presets[idx]['values'])
            self.run_and_render()

    def _on_reset_defaults(self):
        self.property_grid.reset_defaults()
        self.run_and_render()
