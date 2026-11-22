# -*- coding: utf-8 -*-
"""构件发布对话框：独立窗口形态的发布入口。

发布逻辑已收敛到 `ComponentPublishPage`，这里只负责把它包进一个 QDialog，
供"从某处点开批量发布"的调用点继续使用；需要嵌进主界面时直接用页面类。
"""
import os

from PySide6 import QtCore, QtWidgets

from .component_publish_page import ComponentPublishPage
from .i18n import tr


class PublishDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, scripts_root="", current_script=None, content_dir=None):
        super(PublishDialog, self).__init__(parent)
        self.setWindowTitle(tr("pub_dialog_title"))
        self.resize(1040, 680)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.page = ComponentPublishPage(
            self, scripts_root=scripts_root, content_dir=content_dir)
        layout.addWidget(self.page)

        buttons = QtWidgets.QHBoxLayout()
        buttons.setContentsMargins(10, 0, 10, 10)
        buttons.addStretch()
        btn_close = QtWidgets.QPushButton(tr("pub_btn_close"), self)
        btn_close.clicked.connect(self.accept)
        buttons.addWidget(btn_close)
        layout.addLayout(buttons)

        # 兼容旧调用：这些名字仍指向页面里的真实控件
        self.log = self.page.log
        self.table = self.page.table
        self.btn_run = self.page.btn_run

        if current_script:
            self._select_script(current_script)

    def _select_script(self, script_path):
        """把指定脚本所在行勾选上。"""
        target = os.path.abspath(script_path)
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and os.path.abspath(item.data(QtCore.Qt.UserRole)) == target:
                item.setCheckState(QtCore.Qt.Checked)
                break