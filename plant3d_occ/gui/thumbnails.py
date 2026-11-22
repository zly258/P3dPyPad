# -*- coding: utf-8 -*-
"""CustomScripts 预览缩略图：元件库/等级库表格共用。"""

import os

from PySide6 import QtCore, QtGui, QtWidgets

THUMBNAIL_SIZE = 80
_ICON_CACHE = {}


def find_script_thumbnail(content_dir, stem, explicit_path=""):
    """优先使用 CustomScripts 下最大尺寸的 640 图，保证表格里清晰直观。"""
    if not content_dir or not stem:
        return explicit_path if explicit_path and os.path.isfile(explicit_path) else ""
    for base in (content_dir, os.path.join(content_dir, "CPak Common")):
        cs_dir = os.path.join(base, "CustomScripts")
        if not os.path.isdir(cs_dir):
            continue
        for suffix in ("_640.png", "_200.png", "_64.png", "_32.png"):
            path = os.path.join(cs_dir, stem + suffix)
            if os.path.isfile(path) and os.path.getsize(path) > 0:
                return path
    if explicit_path and os.path.isfile(explicit_path):
        return explicit_path
    return ""


def make_thumbnail_item(image_path, tooltip=""):
    """生成带居中缩略图的只读表格项。"""
    item = QtWidgets.QTableWidgetItem()
    item.setFlags(QtCore.Qt.ItemIsEnabled)
    if image_path and os.path.isfile(image_path):
        icon = _ICON_CACHE.get(image_path)
        if icon is None:
            pix = QtGui.QPixmap(image_path)
            if not pix.isNull():
                scaled = pix.scaled(
                    THUMBNAIL_SIZE, THUMBNAIL_SIZE,
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                icon = QtGui.QIcon(scaled)
                if len(_ICON_CACHE) > 512:
                    _ICON_CACHE.clear()
                _ICON_CACHE[image_path] = icon
        if icon is not None:
            item.setIcon(icon)
    if tooltip:
        item.setToolTip(tooltip)
    return item
