# -*- coding: utf-8 -*-
"""新建等级库：名称，以及是否带上默认公制管子。"""

from PySide6 import QtWidgets


def ask_new_spec(parent=None):
    """返回 (名称, 是否包含管子)；取消时返回 None。"""
    dialog = QtWidgets.QDialog(parent)
    dialog.setWindowTitle("新建等级库")
    layout = QtWidgets.QVBoxLayout(dialog)
    layout.addWidget(QtWidgets.QLabel(
        "名称放在项目等级表。不要用 PipeSupportsSpec 等固定名。", dialog))
    name_edit = QtWidgets.QLineEdit(dialog)
    name_edit.setPlaceholderText("例如 MySpec")
    layout.addWidget(name_edit)
    pipe_check = QtWidgets.QCheckBox(
        "包含默认管子（公制直管 CPP，不勾选则不能布管）", dialog)
    pipe_check.setChecked(True)
    layout.addWidget(pipe_check)
    buttons = QtWidgets.QDialogButtonBox(
        QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, dialog)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)
    if dialog.exec() != QtWidgets.QDialog.Accepted:
        return None
    name = name_edit.text().strip()
    if not name:
        return None
    return name, pipe_check.isChecked()
