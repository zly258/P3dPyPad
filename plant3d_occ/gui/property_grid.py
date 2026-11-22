# -*- coding: utf-8 -*-
from PySide6 import QtCore, QtGui, QtWidgets

class PropertyGridWidget(QtWidgets.QWidget):
    """类似 AutoCAD 特性面板 / Visual Studio 属性网格的紧凑双列参数编辑器。"""

    def __init__(self, parent=None):
        super(PropertyGridWidget, self).__init__(parent)
        self._param_rows = {} # {param_name: {'box': QLineEdit, 'default': str}}
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 表头栏
        header_widget = QtWidgets.QWidget(self)
        header_widget.setFixedHeight(26)
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(8, 0, 8, 0)

        from .i18n import tr
        self.lbl_prop = QtWidgets.QLabel(tr("grid_prop_name"), header_widget)
        self.lbl_prop.setFixedWidth(130)
        header_layout.addWidget(self.lbl_prop)

        self.lbl_val = QtWidgets.QLabel(tr("grid_prop_val"), header_widget)
        header_layout.addWidget(self.lbl_val)

        main_layout.addWidget(header_widget)

        # 滚动区
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        self.container = QtWidgets.QWidget()
        self.container_layout = QtWidgets.QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        self.container_layout.addStretch()

        self.scroll_area.setWidget(self.container)
        main_layout.addWidget(self.scroll_area)

    def load_parameters(self, param_list):
        """动态载入并生成参数行。"""
        # 清空原有项
        for i in reversed(range(self.container_layout.count())):
            item = self.container_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        self._param_rows.clear()

        if not param_list:
            empty_lbl = QtWidgets.QLabel("未定义任何参数 (@param)")
            self.container_layout.insertWidget(0, empty_lbl)
            return

        labels = []
        for p in param_list:
            name = p.get('name', '')
            default_val = str(p.get('default', ''))
            tooltip = p.get('tooltip', '')
            long_desc = p.get('tooltip_long', '')
            type_name = p.get('type', 'LENGTH')

            row_widget = QtWidgets.QWidget()
            row_widget.setFixedHeight(28)
            row_layout = QtWidgets.QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(0)

            # 左列：属性名 + 中文
            left_lbl = QtWidgets.QLabel(f" {name}  {tooltip}", row_widget)
            tip_text = f"{name} ({type_name})\n说明: {tooltip}"
            if long_desc:
                tip_text += f"\n详细: {long_desc}"
            left_lbl.setToolTip(tip_text)
            row_layout.addWidget(left_lbl)
            labels.append(left_lbl)

            # 右列：紧凑输入框
            edit_box = QtWidgets.QLineEdit(default_val, row_widget)
            edit_box.setFixedHeight(24)
            edit_box.setToolTip(tip_text)
            row_layout.addWidget(edit_box)

            self.container_layout.insertWidget(self.container_layout.count() - 1, row_widget)
            self._param_rows[name] = {
                'box': edit_box,
                'default': default_val
            }

        # 标签列统一取"最长标签"的宽度：这样每行输入框的左边缘严格对齐，
        # 不会出现不同参数行输入框左右错开的情况。表头同宽。
        if labels:
            col_w = max(l.sizeHint().width() for l in labels)
            col_w = max(col_w, self.lbl_prop.sizeHint().width())
            for l in labels:
                l.setFixedWidth(col_w)
            self.lbl_prop.setFixedWidth(col_w)

    def get_values(self):
        """返回所有参数的当前输入值字典。"""
        return {name: row['box'].text().strip() for name, row in self._param_rows.items()}

    def set_values(self, values_dict):
        """更新填入匹配的参数值。"""
        if not values_dict:
            return
        for name, row in self._param_rows.items():
            # 精确匹配
            if name in values_dict:
                row['box'].setText(str(values_dict[name]))
                continue
            # 别名映射
            upper = name.upper()
            aliases = [upper]
            if upper == 'D': aliases += ['OD', '管径', '管外径']
            elif upper == 'SH': aliases += ['SUPPORT_H', 'H']
            elif upper == 'SL': aliases += ['L_BODY', 'L']
            elif upper == 'SW': aliases += ['W_BODY', 'W']
            elif upper == 'ST': aliases += ['T', '板厚']
            elif upper == 'L': aliases += ['L_SPAN', 'L_TOTAL', 'L_BODY', 'L_MIN']
            elif upper == 'H': aliases += ['H_FREE', 'H_BODY', 'H_SECTION']
            elif upper == 'W': aliases += ['W_BODY', 'B']
            elif upper == 'B': aliases += ['W', '板宽']
            elif upper == 'T': aliases += ['ST', '壁厚', '厚度']

            matched = False
            for k, v in values_dict.items():
                if k.upper() in aliases:
                    row['box'].setText(str(v))
                    matched = True
                    break

    def reset_defaults(self):
        """还原为脚本默认值。"""
        for row in self._param_rows.values():
            row['box'].setText(row['default'])

    def retranslate_ui(self):
        from .i18n import tr
        if hasattr(self, "lbl_prop"):
            self.lbl_prop.setText(tr("grid_prop_name"))
        if hasattr(self, "lbl_val"):
            self.lbl_val.setText(tr("grid_prop_val"))
