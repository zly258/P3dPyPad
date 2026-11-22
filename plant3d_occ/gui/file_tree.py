# -*- coding: utf-8 -*-
import os
import re
from PySide6 import QtCore, QtGui, QtWidgets

class FileTreeWidget(QtWidgets.QWidget):
    """支持递归扫描、模糊搜索与单击即时预览的脚本目录浏览器组件。"""

    script_selected = QtCore.Signal(str) # 发射当前选中的 .py 物理全路径
    directory_changed = QtCore.Signal(str) # 发射当前浏览的根目录物理全路径

    def __init__(self, default_dir=None, parent=None):
        super(FileTreeWidget, self).__init__(parent)
        self._root_dir = default_dir or ""
        self._setup_ui()

        if self._root_dir and os.path.exists(self._root_dir):
            self.load_directory(self._root_dir)

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # 1. 顶部目录选择条
        dir_box = QtWidgets.QWidget(self)
        dir_layout = QtWidgets.QHBoxLayout(dir_box)
        dir_layout.setContentsMargins(0, 0, 0, 0)
        dir_layout.setSpacing(4)

        self.txt_dir = QtWidgets.QLineEdit(self._root_dir, dir_box)
        self.txt_dir.setFixedHeight(26)
        self.txt_dir.setReadOnly(True)
        self.txt_dir.setToolTip(self._root_dir)
        dir_layout.addWidget(self.txt_dir, stretch=1)

        from .i18n import tr
        self.btn_browse = QtWidgets.QPushButton(tr("tree_btn_browse"), dir_box)
        self.btn_browse.setFixedHeight(26)
        self.btn_browse.clicked.connect(self._on_browse_dir)
        dir_layout.addWidget(self.btn_browse)

        layout.addWidget(dir_box)

        # 2. 搜索过滤框
        self.txt_search = QtWidgets.QLineEdit(self)
        self.txt_search.setFixedHeight(26)
        self.txt_search.setPlaceholderText(tr("tree_search_placeholder"))
        self.txt_search.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.txt_search)

        # 3. 目录树形控件
        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.currentItemChanged.connect(self._on_item_changed)
        layout.addWidget(self.tree, stretch=1)

        # 4. 底部统计
        self.lbl_count = QtWidgets.QLabel("未加载目录", self)
        layout.addWidget(self.lbl_count)

    def load_directory(self, folder_path):
        """递归加载指定目录中的所有 Python 构件脚本。"""
        if not os.path.exists(folder_path):
            return

        self._root_dir = folder_path
        self.txt_dir.setText(os.path.basename(folder_path) or folder_path)
        self.txt_dir.setToolTip(folder_path)
        self.directory_changed.emit(folder_path)

        self.tree.blockSignals(True)
        self.tree.clear()

        total_py_count = [0]
        self._populate_tree(self.tree.invisibleRootItem(), folder_path, total_py_count)
        self.tree.blockSignals(False)

        self._total_count = total_py_count[0]
        self.retranslate_ui()

        # 默认选中第一个脚本
        first_item = self._find_first_script_item(self.tree.invisibleRootItem())
        if first_item:
            self.tree.setCurrentItem(first_item)

    def retranslate_ui(self):
        from .i18n import tr, current_language
        if hasattr(self, "btn_browse"):
            self.btn_browse.setText(tr("tree_btn_browse"))
        if hasattr(self, "txt_search"):
            self.txt_search.setPlaceholderText(tr("tree_search_placeholder"))
        cnt = getattr(self, "_total_count", 0)
        if current_language() == "zh":
            self.lbl_count.setText(f"共 {cnt} 个构件脚本")
        else:
            self.lbl_count.setText(f"{cnt} scripts")

    def _populate_tree(self, parent_item, dir_path, counter):
        try:
            entries = sorted(os.listdir(dir_path))
        except Exception:
            return

        dirs = []
        files = []
        for name in entries:
            if name.startswith('.') or name.startswith('__') or name.startswith('_'):
                continue
            full_path = os.path.join(dir_path, name)
            if os.path.isdir(full_path):
                dirs.append((name, full_path))
            elif name.endswith('.py') and not name.startswith('dev_') and name != 'setup.py':
                files.append((name, full_path))

        # 添加子目录
        dir_labels = {
            "01_pipe_fittings": "管件",
            "02_flanges_gaskets": "法兰垫片",
            "03_valves": "阀门",
            "04_instruments": "仪器仪表",
            "05_supports": "支吊架",
            "06_equipment": "工艺设备",
            "custom_scripts": "自定义构件库",
            "supports": "标准支吊架库",
            "system_defaults": "原厂反编译脚本",
        }
        for name, full_path in dirs:
            dir_item = QtWidgets.QTreeWidgetItem(parent_item)
            zh_dir = dir_labels.get(name, "")
            dir_item.setText(0, f"{zh_dir} ({name})" if zh_dir else name)
            dir_item.setData(0, QtCore.Qt.UserRole, "") # 空表示文件夹
            dir_item.setExpanded(True)
            self._populate_tree(dir_item, full_path, counter)

        # 添加脚本文件
        for name, full_path in files:
            file_item = QtWidgets.QTreeWidgetItem(parent_item)
            # 嗅探中文名称，优先显示在左侧避免长英文文件名截断中文
            short_title = self._quick_sniff_title(full_path)
            display_text = f"{short_title} ({name})" if short_title else name
            file_item.setText(0, display_text)
            file_item.setData(0, QtCore.Qt.UserRole, full_path)
            file_item.setToolTip(0, f"{short_title}\n{full_path}" if short_title else full_path)
            counter[0] += 1

    def _quick_sniff_title(self, py_path):
        try:
            with open(py_path, 'r', encoding='utf-8', errors='ignore') as f:
                head = "".join(f.readline() for _ in range(40))
            m = re.search(r'TooltipShort\s*=\s*[uU]?["\']([^"\']+)["\']', head)
            if m:
                return m.group(1).strip()
            # 兜底：匹配首部中文注释行（跳过 coding 声明）
            for line in head.splitlines():
                s = line.strip()
                if not s.startswith('#') or 'coding' in s:
                    continue
                comment = s.lstrip('#').strip()
                if re.search(r'[\u4e00-\u9fff]', comment):
                    # 去掉常见前缀如 "FLANGE_WN: "
                    comment = re.sub(r'^[A-Za-z0-9_]+\s*[:：]\s*', '', comment)
                    return comment[:28] + ('…' if len(comment) > 28 else '')
        except Exception:
            pass
        return ""

    def _find_first_script_item(self, item):
        for i in range(item.childCount()):
            child = item.child(i)
            path = child.data(0, QtCore.Qt.UserRole)
            if path and path.endswith('.py'):
                return child
            res = self._find_first_script_item(child)
            if res:
                return res
        return None

    def _on_item_changed(self, current, previous):
        if not current: return
        path = current.data(0, QtCore.Qt.UserRole)
        if path and path.endswith('.py'):
            self.script_selected.emit(path)

    def _on_search_changed(self, query):
        q = query.strip().lower()
        self._filter_tree(self.tree.invisibleRootItem(), q)

    def _filter_tree(self, item, q):
        has_visible_child = False
        for i in range(item.childCount()):
            child = item.child(i)
            path = child.data(0, QtCore.Qt.UserRole)
            text = child.text(0).lower()

            if path and path.endswith('.py'):
                matches = not q or (q in text) or (q in os.path.basename(path).lower())
                child.setHidden(not matches)
                if matches:
                    has_visible_child = True
            else:
                # 文件夹递归过滤
                sub_visible = self._filter_tree(child, q)
                child.setHidden(not sub_visible)
                if sub_visible:
                    has_visible_child = True

        return has_visible_child

    def _on_browse_dir(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "选择脚本根目录", self._root_dir or "pyscripts")
        if folder:
            self.load_directory(folder)
