# -*- coding: utf-8 -*-
"""业务页统一样式：所有页面使用相同高度的操作栏与主/危险按钮。"""

from PySide6 import QtWidgets

ACTION_BUTTON_HEIGHT = 30


def make_action_button(text, primary=False, danger=False, min_width=120):
    button = QtWidgets.QPushButton(text)
    button.setFixedHeight(ACTION_BUTTON_HEIGHT)
    button.setMinimumWidth(min_width)
    if primary:
        button.setProperty("primary", "true")
    if danger:
        button.setProperty("danger", "true")
    return button


def make_action_bar(margins=(0, 2, 0, 2), spacing=8):
    bar = QtWidgets.QHBoxLayout()
    bar.setContentsMargins(*margins)
    bar.setSpacing(spacing)
    return bar
