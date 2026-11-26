# -*- coding: utf-8 -*-
"""CPak Common 路径：下拉列出本机各版本，也可以手改或浏览。"""

import os

from PySide6 import QtCore, QtWidgets

from ..catalog.content_dirs import list_cpak_common_dirs


class ContentDirBox(QtWidgets.QComboBox):
    """可编辑下拉。text()/setText() 与原来的输入框兼容。"""

    editingFinished = QtCore.Signal()

    def __init__(self, current="", parent=None):
        super(ContentDirBox, self).__init__(parent)
        self.setEditable(True)
        self.setFixedHeight(26)
        self.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self._last = None
        self.reload(current)
        line = self.lineEdit()
        line.setPlaceholderText("选择或填写 CPak Common，留空则用本机已安装版本")
        line.editingFinished.connect(self._emit_if_changed)
        self.activated.connect(self._on_activated)

    def reload(self, current=""):
        current = (current or "").strip()
        self.blockSignals(True)
        self.clear()
        paths = []
        for item in list_cpak_common_dirs():
            paths.append(item["path"])
            label = item["path"]
            if item.get("year"):
                label = "%s  (%s)" % (item["path"], item["source"])
            self.addItem(label, item["path"])
            tip = item["source"]
            if item.get("year"):
                tip = "Plant %s，%s" % (item["year"], item["source"])
            self.setItemData(self.count() - 1, tip, QtCore.Qt.ToolTipRole)
        if current and os.path.normcase(current) not in {os.path.normcase(p) for p in paths}:
            self.addItem(current, current)
        if current:
            self._select(current)
        elif self.count():
            self.setCurrentIndex(0)
        self._last = self.text()
        self.blockSignals(False)

    def text(self):
        data = self.currentData()
        if isinstance(data, str) and data.strip() and self.currentText().startswith(data):
            return data.strip()
        # 手改后的文字就是路径；下拉项文字可能带来源后缀，优先用 item data。
        idx = self.currentIndex()
        if idx >= 0:
            stored = self.itemData(idx)
            shown = self.currentText().strip()
            if isinstance(stored, str) and (shown == stored or shown.startswith(stored)):
                return stored.strip()
        return self.currentText().strip()

    def setText(self, value):
        value = (value or "").strip()
        self.blockSignals(True)
        if value and self.findData(value) < 0:
            self.addItem(value, value)
        self._select(value)
        self._last = self.text()
        self.blockSignals(False)

    def _select(self, value):
        idx = self.findData(value)
        if idx < 0:
            idx = self.findText(value)
        if idx >= 0:
            self.setCurrentIndex(idx)
        else:
            self.setEditText(value)

    def _on_activated(self, index):
        stored = self.itemData(index)
        if isinstance(stored, str) and stored.strip():
            self.setEditText(stored)
        self._emit_if_changed()

    def _emit_if_changed(self):
        text = self.text()
        if text == self._last:
            return
        self._last = text
        self.editingFinished.emit()
