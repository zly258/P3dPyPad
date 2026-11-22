# -*- coding: utf-8 -*-
"""AutoCAD Plant 3D OCC 工作台现代工业 CAD (Fluent) 样式系统。

设计规范严格遵循 $wpf-ui-style (Theme/Tokens.xaml):
- 低饱和度工业桌面色板 (WindowBackground #E9EDF2, Surface #FAFBFC, Border #D0D5DB)
- 品牌强调色 (Accent #2F6F9F, Hover #285F88, Pressed #22506F)
- 紧凑排版体系 (12px 正文, 26px 紧凑控件高度, 3px 边距, 3px 统一圆角)
- 状态契约：显式对勾矢量图标 (check_white.png)、显式下拉三角形箭头 (arrow_down.png)
- 盒模型防溢出：紧凑 padding，彻底解决按钮/控件下半部分被布局遮挡裁切的问题
"""

import os
from PySide6 import QtGui, QtWidgets


def get_app_icon() -> QtGui.QIcon:
    """获取程序标准矢量/高清图标。"""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "app_icon.ico"),
        os.path.join(here, "app_icon.png"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return QtGui.QIcon(c)
    return QtGui.QIcon()


def _ensure_icons(icons_dir: str):
    """自动确保 QSS 所需的紧凑矢量/高清 PNG 图标（对勾、下拉箭头等）就绪。"""
    if os.path.isfile(os.path.join(icons_dir, "check_white.png")) and os.path.isfile(os.path.join(icons_dir, "arrow_down.png")):
        return
    try:
        os.makedirs(icons_dir, exist_ok=True)
        from PIL import Image, ImageDraw

        im_chk = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(im_chk)
        d.line([(3, 8), (6, 11)], fill=(255, 255, 255, 255), width=2)
        d.line([(6, 11), (13, 4)], fill=(255, 255, 255, 255), width=2)
        im_chk.save(os.path.join(icons_dir, 'check_white.png'))

        im_ind = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        d = ImageDraw.Draw(im_ind)
        d.line([(4, 8), (12, 8)], fill=(255, 255, 255, 255), width=2)
        im_ind.save(os.path.join(icons_dir, 'check_indeterminate.png'))

        im_ad = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
        d = ImageDraw.Draw(im_ad)
        d.polygon([(2, 4), (10, 4), (6, 8)], fill=(75, 85, 99, 255))
        im_ad.save(os.path.join(icons_dir, 'arrow_down.png'))

        im_adh = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
        d = ImageDraw.Draw(im_adh)
        d.polygon([(2, 4), (10, 4), (6, 8)], fill=(31, 41, 51, 255))
        im_adh.save(os.path.join(icons_dir, 'arrow_down_hover.png'))

        im_add = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
        d = ImageDraw.Draw(im_add)
        d.polygon([(2, 4), (10, 4), (6, 8)], fill=(156, 163, 175, 255))
        im_add.save(os.path.join(icons_dir, 'arrow_down_disabled.png'))

        im_bc = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
        d = ImageDraw.Draw(im_bc)
        d.polygon([(4, 2), (4, 10), (8, 6)], fill=(100, 116, 139, 255))
        im_bc.save(os.path.join(icons_dir, 'branch_closed.png'))

        im_bo = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
        d = ImageDraw.Draw(im_bo)
        d.polygon([(2, 4), (10, 4), (6, 8)], fill=(100, 116, 139, 255))
        im_bo.save(os.path.join(icons_dir, 'branch_open.png'))
    except Exception:
        pass


def get_qss_style() -> str:
    """生成带动态图标正斜杠绝对路径的高品质工业 CAD QSS 样式表。"""
    here = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
    icons = f"{here}/icons"
    _ensure_icons(os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons"))

    return f"""
/* 全局基础重置与字体设置 */
QWidget {{
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 12px;
    color: #1F2933;
    outline: none;
}}

QMainWindow, QDialog {{
    background-color: #E9EDF2;
}}

/* 选项卡 (QTabWidget) - 工业平顶紧凑设计 */
QTabWidget::pane {{
    border: 1px solid #D0D5DB;
    background-color: #FAFBFC;
    top: -1px;
}}

QTabBar::tab {{
    background-color: #E9EDF2;
    color: #4B5563;
    border: 1px solid #D0D5DB;
    border-bottom: none;
    padding: 4px 14px;
    margin-right: 2px;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
    min-height: 22px;
}}

QTabBar::tab:hover {{
    background-color: #F2F4F7;
    color: #1F2933;
}}

QTabBar::tab:selected {{
    background-color: #FAFBFC;
    color: #2F6F9F;
    font-weight: bold;
    border-top: 2px solid #2F6F9F;
    border-bottom: 1px solid #FAFBFC;
}}

/* 标准按钮 (QPushButton) - 紧凑 padding 防裁切 */
QPushButton {{
    background-color: #FAFBFC;
    color: #1F2933;
    border: 1px solid #D0D5DB;
    border-radius: 3px;
    padding: 1px 8px;
    min-height: 18px;
}}

QPushButton:hover {{
    background-color: #F0F3F6;
    border-color: #AEB7C2;
}}

QPushButton:pressed {{
    background-color: #E4E8EE;
    border-color: #2F6F9F;
}}

QPushButton:checked {{
    background-color: #E4EEF5;
    color: #2F6F9F;
    border-color: #2F6F9F;
    font-weight: bold;
}}

QPushButton:disabled {{
    background-color: #F2F4F7;
    color: #667085;
    border-color: #D0D5DB;
}}

/* 主强调按钮 (Primary Button) - 单一行动色 */
QPushButton[primary="true"] {{
    background-color: #2F6F9F;
    color: #FFFFFF;
    border: 1px solid #22506F;
    font-weight: bold;
}}

QPushButton[primary="true"]:hover {{
    background-color: #285F88;
    border-color: #1A3E57;
}}

QPushButton[primary="true"]:pressed {{
    background-color: #22506F;
    border-color: #122B3D;
}}

QPushButton[primary="true"]:disabled {{
    background-color: #D8E6F0;
    color: #8CAABF;
    border-color: #C0D3E2;
}}

/* 危险操作按钮 (Danger Button) - 移除/删除 */
QPushButton[danger="true"] {{
    background-color: #B42318;
    color: #FFFFFF;
    border: 1px solid #8F1D14;
    font-weight: bold;
}}

QPushButton[danger="true"]:hover {{
    background-color: #912018;
    border-color: #731710;
}}

QPushButton[danger="true"]:pressed {{
    background-color: #7A1A13;
    border-color: #5E130E;
}}

QPushButton[danger="true"]:disabled {{
    background-color: #F3D9D6;
    color: #9A5B55;
    border-color: #E3BDB8;
}}

/* 紧凑微型按钮 (如状态栏语言切换) */
QPushButton[compact="true"] {{
    padding: 0px 4px;
    font-size: 11px;
    min-height: 16px;
}}

/* 输入框 (QLineEdit) */
QLineEdit {{
    background-color: #FFFFFF;
    color: #1F2933;
    border: 1px solid #D0D5DB;
    border-radius: 3px;
    padding: 1px 6px;
    min-height: 20px;
    selection-background-color: #E4EEF5;
    selection-color: #1F2933;
}}

QLineEdit:focus {{
    border: 1px solid #2F6F9F;
}}

QLineEdit:read-only {{
    background-color: #F7F8FA;
    color: #4B5563;
}}

/* 下拉选择框 (QComboBox) - 显式下三角箭头与优雅弹层 */
QComboBox {{
    background-color: #FFFFFF;
    color: #1F2933;
    border: 1px solid #D0D5DB;
    border-radius: 3px;
    padding-left: 6px;
    padding-right: 20px;
    padding-top: 1px;
    padding-bottom: 1px;
    min-height: 20px;
    selection-background-color: #E4EEF5;
    selection-color: #1F2933;
}}

QComboBox:hover {{
    border-color: #AEB7C2;
}}

QComboBox:focus {{
    border: 1px solid #2F6F9F;
}}

QComboBox:disabled {{
    background-color: #F2F4F7;
    color: #667085;
    border-color: #D0D5DB;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 18px;
    border-left: 1px solid #E4E8EE;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
    background-color: #FAFBFC;
}}

QComboBox::drop-down:hover {{
    background-color: #F0F3F6;
}}

QComboBox::down-arrow {{
    image: url({icons}/arrow_down.png);
    width: 10px;
    height: 10px;
}}

QComboBox::down-arrow:hover {{
    image: url({icons}/arrow_down_hover.png);
}}

QComboBox::down-arrow:disabled {{
    image: url({icons}/arrow_down_disabled.png);
}}

QComboBox QAbstractItemView {{
    border: 1px solid #AEB7C2;
    background-color: #FFFFFF;
    color: #1F2933;
    selection-background-color: #E4EEF5;
    selection-color: #1F2933;
    padding: 2px;
}}

QComboBox QAbstractItemView::item {{
    min-height: 22px;
    padding: 2px 6px;
}}

/* 复选框 (QCheckBox) - 显式高对比度清晰白对勾 */
QCheckBox {{
    spacing: 6px;
    color: #1F2933;
}}

QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid #AEB7C2;
    border-radius: 2px;
    background-color: #FFFFFF;
}}

QCheckBox::indicator:hover {{
    border-color: #2F6F9F;
    background-color: #F0F3F6;
}}

QCheckBox::indicator:checked {{
    background-color: #2F6F9F;
    border-color: #22506F;
    image: url({icons}/check_white.png);
}}

QCheckBox::indicator:indeterminate {{
    background-color: #2F6F9F;
    border-color: #22506F;
    image: url({icons}/check_indeterminate.png);
}}

QCheckBox::indicator:disabled {{
    border-color: #D0D5DB;
    background-color: #F2F4F7;
}}

/* 单选框 (QRadioButton) */
QRadioButton {{
    spacing: 6px;
    color: #1F2933;
}}

QRadioButton::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid #AEB7C2;
    border-radius: 7px;
    background-color: #FFFFFF;
}}

QRadioButton::indicator:hover {{
    border-color: #2F6F9F;
}}

QRadioButton::indicator:checked {{
    background-color: #2F6F9F;
    border-color: #22506F;
}}

/* 分组框 (QGroupBox) */
QGroupBox {{
    border: 1px solid #D0D5DB;
    border-radius: 3px;
    margin-top: 8px;
    background-color: #FAFBFC;
    padding-top: 8px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    padding: 0 4px;
    color: #2F6F9F;
    font-weight: bold;
    background-color: #FAFBFC;
}}

/* 数据表格 (QTableWidget) 与 树形目录 (QTreeWidget) */
QTableWidget, QTreeWidget {{
    background-color: #FFFFFF;
    alternate-background-color: #F7F8FA;
    border: 1px solid #D0D5DB;
    gridline-color: #E4E8EE;
    color: #1F2933;
    selection-background-color: #E4EEF5;
    selection-color: #1F2933;
}}

QTableWidget::item, QTreeWidget::item {{
    padding: 2px 4px;
    min-height: 22px;
}}

QTableWidget::item:selected, QTreeWidget::item:selected {{
    background-color: #E4EEF5;
    color: #1F2933;
}}

QHeaderView::section {{
    background-color: #F2F4F7;
    color: #1F2933;
    font-weight: bold;
    padding: 3px 6px;
    border: none;
    border-right: 1px solid #D0D5DB;
    border-bottom: 1px solid #D0D5DB;
}}

QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings {{
    border-image: none;
    image: url({icons}/branch_closed.png);
}}

QTreeView::branch:open:has-children:!has-siblings,
QTreeView::branch:open:has-children:has-siblings {{
    border-image: none;
    image: url({icons}/branch_open.png);
}}

/* 日志文本框 (QPlainTextEdit) */
QPlainTextEdit {{
    background-color: #FAFBFC;
    color: #1F2933;
    border: 1px solid #D0D5DB;
    border-radius: 3px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11.5px;
    selection-background-color: #E4EEF5;
    selection-color: #1F2933;
}}

/* 分割器手柄 (QSplitter) */
QSplitter::handle {{
    background-color: #D0D5DB;
}}

QSplitter::handle:horizontal {{
    width: 3px;
}}

QSplitter::handle:vertical {{
    height: 3px;
}}

QSplitter::handle:hover {{
    background-color: #2F6F9F;
}}

/* 紧凑现代滚动条 (QScrollBar) */
QScrollBar:vertical {{
    background-color: #F2F4F7;
    width: 8px;
    margin: 0;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background-color: #C3CAD3;
    min-height: 24px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #A7B0BB;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    height: 0px;
    background: none;
}}

QScrollBar:horizontal {{
    background-color: #F2F4F7;
    height: 8px;
    margin: 0;
    border-radius: 3px;
}}

QScrollBar::handle:horizontal {{
    background-color: #C3CAD3;
    min-width: 24px;
    border-radius: 3px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: #A7B0BB;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    width: 0px;
    background: none;
}}

/* 状态栏 (QStatusBar) - 确保充足垂直裕量 */
QStatusBar {{
    background-color: #F2F4F7;
    border-top: 1px solid #D0D5DB;
    color: #4B5563;
    min-height: 26px;
}}

/* 进度条 (QProgressBar) */
QProgressBar {{
    background-color: #E9EDF2;
    border: 1px solid #D0D5DB;
    border-radius: 2px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: #2F6F9F;
    border-radius: 1px;
}}

/* 批量勾选计数提示 */
QLabel#checkedCount {{
    color: #B54708;
    font-weight: 600;
}}

/* 表格上方操作栏提示文字 */
QLabel#actionHint {{
    color: #475467;
    font-size: 12px;
}}
"""


def apply_theme(app_or_widget: QtWidgets.QWidget = None):
    """为应用程序或顶级窗口应用标准 Fluent 工业风格 QSS。"""
    style_sheet = get_qss_style()
    app = QtWidgets.QApplication.instance()
    if app is not None:
        icon = get_app_icon()
        if not icon.isNull():
            app.setWindowIcon(icon)
        app.setStyleSheet(style_sheet)
    elif app_or_widget is not None:
        icon = get_app_icon()
        if not icon.isNull():
            app_or_widget.setWindowIcon(icon)
        app_or_widget.setStyleSheet(style_sheet)
