# -*- coding: utf-8 -*-
"""等级库管理：选择元件库 + 等级库，批量加入/移除 CustomScripts 构件。

页面只做一件事：把 CustomScripts 下的自定义构件在"元件库 -> 等级库"之间
批量搬运，不涉及发布、预览或设备模板。所有数据库读写都在后台线程执行。
"""

import os
import sqlite3
from typing import List

from PySide6 import QtCore, QtGui, QtWidgets

from ..catalog.manager import (
    add_catalog_item_to_spec,
    list_spec_files,
    load_catalog_config,
    remove_item_from_spec,
    resolve_project_and_spec_dir,
    save_catalog_config,
)
from ..catalog.model import inspect_script
from .i18n import tr
from .page_layout import make_action_bar, make_action_button
from .progress import InlineProgressBar, ThreadTask
from .thumbnails import find_script_thumbnail, make_thumbnail_item


def _list_catalog_files(content_dir):
    """列出 content_dir 及其 CPak Common 子目录下的 .acat/.pcat。"""
    found = []
    seen = set()
    for base in (content_dir, os.path.join(content_dir, "CPak Common")):
        if not base or not os.path.isdir(base):
            continue
        for fn in sorted(os.listdir(base)):
            if not fn.lower().endswith((".acat", ".pcat")):
                continue
            path = os.path.join(base, fn)
            if not os.path.isfile(path):
                continue
            key = os.path.normcase(os.path.abspath(path))
            if key in seen:
                continue
            seen.add(key)
            found.append({"file": fn, "path": path})
    return found


def _custom_script_paths(content_dir):
    """CustomScripts 下的 .py 脚本，按 stem 去重。"""
    paths = []
    seen = set()
    for base in (content_dir, os.path.join(content_dir, "CPak Common")):
        cs_dir = os.path.join(base, "CustomScripts") if base else ""
        if not cs_dir or not os.path.isdir(cs_dir):
            continue
        for fn in sorted(os.listdir(cs_dir)):
            if not fn.lower().endswith(".py") or fn.startswith("__"):
                continue
            stem = os.path.splitext(fn)[0]
            key = stem.upper()
            if key in seen:
                continue
            seen.add(key)
            paths.append(os.path.join(cs_dir, fn))
    return paths


def _read_template_counts(db_path):
    """读取元件库/等级库中每个构件族的规格行数。"""
    counts = {}
    if not db_path or not os.path.isfile(db_path) or os.path.getsize(db_path) == 0:
        return counts
    uri = "file:%s?mode=ro" % db_path.replace("\\", "/")
    try:
        con = sqlite3.connect(uri, uri=True, timeout=5)
        try:
            cur = con.execute(
                "SELECT UPPER(ContentGeometryTemplate), COUNT(*) "
                "FROM EngineeringItems WHERE ContentGeometryTemplate IS NOT NULL "
                "AND ContentGeometryTemplate != '' GROUP BY UPPER(ContentGeometryTemplate)")
            for tpl, cnt in cur.fetchall():
                if tpl:
                    counts[tpl] = int(cnt or 0)
        finally:
            con.close()
    except Exception:
        pass
    return counts


class SpecManagerPage(QtWidgets.QWidget):
    """元件库 -> 等级库批量成员管理。"""

    status_message = QtCore.Signal(str)

    def __init__(self, parent=None, scripts_root="", lazy_load=True):
        super(SpecManagerPage, self).__init__(parent)
        self._scripts_root = scripts_root or ""
        self._config = load_catalog_config()
        self._project_dir = self._config.get("project_dir", "")
        self._project_spec_dir = self._config.get("project_spec_dir", "")
        self._rows = []
        self._visible_rows = []
        self._checked_stems = set()
        self._scan_task = None
        self._write_task = None
        self._scan_gen = 0
        self._loaded = False
        self._filling = False
        self._search_timer = QtCore.QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)
        self._search_timer.timeout.connect(self._apply_filter)
        self._setup_ui()
        if not lazy_load:
            self.ensure_loaded()

    def ensure_loaded(self):
        if self._loaded:
            return
        self._loaded = True
        self._populate_selectors()
        self.reload_items()

    def _setup_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        cfg = QtWidgets.QHBoxLayout()
        cfg.setSpacing(6)
        self.lbl_content_dir = QtWidgets.QLabel(tr("cat_lbl_content_dir"), self)
        self.lbl_content_dir.setFixedWidth(135)
        self.lbl_content_dir.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        cfg.addWidget(self.lbl_content_dir)
        self.txt_content_dir = QtWidgets.QLineEdit(
            self._config.get("content_dir", ""), self)
        self.txt_content_dir.setFixedHeight(26)
        self.txt_content_dir.editingFinished.connect(self._on_content_dir_changed)
        cfg.addWidget(self.txt_content_dir, stretch=1)
        self.btn_browse = QtWidgets.QPushButton(tr("tree_btn_browse"), self)
        self.btn_browse.setFixedSize(65, 26)
        self.btn_browse.clicked.connect(self._on_browse_content_dir)
        cfg.addWidget(self.btn_browse)
        root.addLayout(cfg)

        project_row = QtWidgets.QHBoxLayout()
        project_row.setSpacing(6)
        self.lbl_project_dir = QtWidgets.QLabel(
            tr("spec_lbl_project_dir", "项目路径:"), self)
        self.lbl_project_dir.setFixedWidth(135)
        self.lbl_project_dir.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        project_row.addWidget(self.lbl_project_dir)
        self.txt_project_dir = QtWidgets.QLineEdit(self._project_dir, self)
        self.txt_project_dir.setFixedHeight(26)
        self.txt_project_dir.setPlaceholderText(
            tr("spec_project_placeholder", "选择 Plant 3D 项目根目录或等级库工作表目录..."))
        self.txt_project_dir.setToolTip(
            "设置后，等级库列表会优先显示该项目的 Spec Sheets / 等级库工作表")
        self.txt_project_dir.editingFinished.connect(self._on_project_dir_changed)
        project_row.addWidget(self.txt_project_dir, stretch=1)
        self.btn_project_browse = QtWidgets.QPushButton(tr("tree_btn_browse"), self)
        self.btn_project_browse.setFixedSize(65, 26)
        self.btn_project_browse.clicked.connect(self._on_browse_project_dir)
        project_row.addWidget(self.btn_project_browse)
        root.addLayout(project_row)

        tools = QtWidgets.QHBoxLayout()
        tools.setSpacing(6)
        self.lbl_catalog = QtWidgets.QLabel(tr("spec_lbl_catalog", "元件库:"), self)
        tools.addWidget(self.lbl_catalog)
        self.combo_catalog = QtWidgets.QComboBox(self)
        self.combo_catalog.setFixedHeight(26)
        self.combo_catalog.setMinimumWidth(230)
        self.combo_catalog.currentIndexChanged.connect(self._on_selector_changed)
        tools.addWidget(self.combo_catalog)

        self.lbl_spec = QtWidgets.QLabel(tr("spec_lbl_spec", "等级库:"), self)
        tools.addWidget(self.lbl_spec)
        self.combo_spec = QtWidgets.QComboBox(self)
        self.combo_spec.setFixedHeight(26)
        self.combo_spec.setMinimumWidth(230)
        self.combo_spec.currentIndexChanged.connect(self._on_selector_changed)
        tools.addWidget(self.combo_spec)

        self.btn_select_all = QtWidgets.QPushButton("全选", self)
        self.btn_select_all.setFixedHeight(26)
        self.btn_select_all.clicked.connect(self._select_all)
        tools.addWidget(self.btn_select_all)
        self.btn_select_none = QtWidgets.QPushButton("全不选", self)
        self.btn_select_none.setFixedHeight(26)
        self.btn_select_none.clicked.connect(self._select_none)
        tools.addWidget(self.btn_select_none)
        self.btn_select_invert = QtWidgets.QPushButton("反选", self)
        self.btn_select_invert.setFixedHeight(26)
        self.btn_select_invert.clicked.connect(self._select_invert)
        tools.addWidget(self.btn_select_invert)

        tools.addStretch()
        self.txt_search = QtWidgets.QLineEdit(self)
        self.txt_search.setFixedHeight(26)
        self.txt_search.setPlaceholderText(tr("spec_search_placeholder", "搜索脚本名称或类别..."))
        self.txt_search.textChanged.connect(lambda _text: self._search_timer.start())
        tools.addWidget(self.txt_search, stretch=1)
        self.btn_refresh = QtWidgets.QPushButton(tr("cat_btn_refresh"), self)
        self.btn_refresh.setFixedHeight(26)
        self.btn_refresh.clicked.connect(self.reload_items)
        tools.addWidget(self.btn_refresh)
        self.lbl_count = QtWidgets.QLabel("", self)
        tools.addWidget(self.lbl_count)
        root.addLayout(tools)

        action_bar = make_action_bar()
        self.lbl_action_hint = QtWidgets.QLabel(
            "勾选构件后，可批量加入所选等级库或从等级库移除", self)
        self.lbl_action_hint.setObjectName("actionHint")
        action_bar.addWidget(self.lbl_action_hint)
        action_bar.addStretch()
        self.btn_add = make_action_button(
            tr("spec_btn_add", "批量添加到等级库"), primary=True, min_width=160)
        self.btn_add.clicked.connect(self._batch_add)
        action_bar.addWidget(self.btn_add)
        self.btn_remove = make_action_button(
            tr("spec_btn_remove", "从等级库移除"), danger=True, min_width=140)
        self.btn_remove.clicked.connect(self._batch_remove)
        action_bar.addWidget(self.btn_remove)
        root.addLayout(action_bar)

        self.table = QtWidgets.QTableWidget(0, 6, self)
        self.table.setIconSize(QtCore.QSize(80, 80))
        self.table.verticalHeader().setDefaultSectionSize(88)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemChanged.connect(self._on_item_changed)
        root.addWidget(self.table, stretch=1)
        self._apply_headers()

        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.table.setColumnWidth(0, 48)
        hdr.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.table.setColumnWidth(1, 96)
        hdr.setSectionResizeMode(2, QtWidgets.QHeaderView.Interactive)
        self.table.setColumnWidth(2, 320)
        hdr.setSectionResizeMode(3, QtWidgets.QHeaderView.Interactive)
        self.table.setColumnWidth(3, 160)
        hdr.setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)
        self.table.setColumnWidth(4, 110)
        hdr.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)

        self.progress_bar_widget = InlineProgressBar(self)
        root.addWidget(self.progress_bar_widget)

    def _apply_headers(self):
        self.table.setHorizontalHeaderLabels([
            tr("th_select", "勾选"),
            tr("th_icon", "图标"),
            tr("th_script_name", "构件名称"),
            tr("th_category", "类别"),
            tr("spec_th_catalog_rows", "元件库规格数"),
            tr("spec_th_spec_status", "等级库状态"),
        ])

    def retranslate_ui(self):
        if hasattr(self, "lbl_content_dir"):
            self.lbl_content_dir.setText(tr("cat_lbl_content_dir"))
        if hasattr(self, "btn_browse"):
            self.btn_browse.setText(tr("tree_btn_browse"))
        if hasattr(self, "lbl_project_dir"):
            self.lbl_project_dir.setText(tr("spec_lbl_project_dir", "项目路径:"))
        if hasattr(self, "btn_project_browse"):
            self.btn_project_browse.setText(tr("tree_btn_browse"))
        if hasattr(self, "txt_project_dir"):
            self.txt_project_dir.setPlaceholderText(
                tr("spec_project_placeholder", "选择 Plant 3D 项目根目录或等级库工作表目录..."))
        if hasattr(self, "lbl_catalog"):
            self.lbl_catalog.setText(tr("spec_lbl_catalog", "元件库:"))
        if hasattr(self, "lbl_spec"):
            self.lbl_spec.setText(tr("spec_lbl_spec", "等级库:"))
        if hasattr(self, "btn_refresh"):
            self.btn_refresh.setText(tr("cat_btn_refresh"))
        if hasattr(self, "btn_add"):
            self.btn_add.setText(tr("spec_btn_add", "批量添加到等级库"))
        if hasattr(self, "btn_remove"):
            self.btn_remove.setText(tr("spec_btn_remove", "从等级库移除"))
        if hasattr(self, "txt_search"):
            self.txt_search.setPlaceholderText(
                tr("spec_search_placeholder", "搜索脚本名称或类别..."))
        if hasattr(self, "table"):
            self._apply_headers()

    def _content_dir(self):
        return self.txt_content_dir.text().strip()

    def _on_browse_content_dir(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择 CPak Common", self._content_dir())
        if folder:
            self.txt_content_dir.setText(folder)
            self._on_content_dir_changed()

    def _on_content_dir_changed(self):
        folder = self._content_dir()
        if not folder:
            return
        save_catalog_config({"content_dir": folder})
        self._populate_selectors()
        self.reload_items()

    def _on_browse_project_dir(self):
        start = self.txt_project_dir.text().strip() or self._project_dir
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择 Plant 3D 项目目录", start)
        if folder:
            self.txt_project_dir.setText(folder)
            self._on_project_dir_changed()

    def _on_project_dir_changed(self):
        value = self.txt_project_dir.text().strip()
        if not value:
            self._project_dir = ""
            self._project_spec_dir = ""
        else:
            self._project_dir, self._project_spec_dir = resolve_project_and_spec_dir(value)
            self.txt_project_dir.setText(self._project_dir or value)
        self._config["project_dir"] = self._project_dir
        self._config["project_spec_dir"] = self._project_spec_dir
        save_catalog_config({
            "project_dir": self._project_dir,
            "project_spec_dir": self._project_spec_dir,
        })
        self._populate_selectors()
        self.reload_items()

    def _populate_selectors(self):
        content = self._content_dir()
        catalogs = _list_catalog_files(content)
        prev_catalog = self.combo_catalog.currentData()
        self.combo_catalog.blockSignals(True)
        self.combo_catalog.clear()
        for item in catalogs:
            self.combo_catalog.addItem(item["file"], item["path"])
        if prev_catalog:
            idx = self.combo_catalog.findData(prev_catalog)
            if idx >= 0:
                self.combo_catalog.setCurrentIndex(idx)
        self.combo_catalog.blockSignals(False)

        specs = list_spec_files(
            content_dir=content,
            project_spec_dir=self._project_spec_dir)
        prev_spec = self.combo_spec.currentData()
        self.combo_spec.blockSignals(True)
        self.combo_spec.clear()
        for item in specs:
            label = item["file"]
            if item.get("is_project"):
                label += "  (项目)"
            self.combo_spec.addItem(label, item["path"])
        if prev_spec:
            idx = self.combo_spec.findData(prev_spec)
            if idx >= 0:
                self.combo_spec.setCurrentIndex(idx)
        self.combo_spec.blockSignals(False)

    def _on_selector_changed(self, _index):
        if self._loaded:
            self.reload_items()

    def reload_items(self):
        content = self._content_dir()
        catalog_path = self.combo_catalog.currentData() or ""
        spec_path = self.combo_spec.currentData() or ""
        if not content or not os.path.isdir(content):
            self._rows = []
            self._apply_filter()
            self.lbl_count.setText("请先选择 CPak Common 目录")
            return

        if self._scan_task is not None and self._scan_task.is_running():
            self._scan_task.cancel()
        self._scan_gen += 1
        gen = self._scan_gen
        self.btn_refresh.setEnabled(False)
        self.lbl_count.setText("正在检索...")
        self._show_progress("正在检索 CustomScripts 与所选元件库/等级库...")

        self._scan_task = ThreadTask(
            lambda progress, token: self._scan_worker(
                content, catalog_path, spec_path, gen, progress, token),
            parent=self, name="spec-scan")
        self._scan_task.finished.connect(self._on_scan_finished)
        self._scan_task.failed.connect(self._on_scan_failed)
        self._scan_task.start()

    def _scan_worker(self, content, catalog_path, spec_path, gen, progress, token):
        catalog_counts = _read_template_counts(catalog_path)
        token.check()
        spec_counts = _read_template_counts(spec_path)
        token.check()

        rows = []
        for index, path in enumerate(_custom_script_paths(content), 1):
            token.check()
            job = inspect_script(path, auto_generate_sizes=False)
            if (job.get("domain") or "") == "equipment":
                continue
            stem = job.get("stem") or os.path.splitext(os.path.basename(path))[0]
            key = stem.upper()
            catalog_rows = catalog_counts.get(key, 0)
            # 等级库管理只显示所选元件库中真实已发布的构件，而不是所有脚本
            if catalog_rows <= 0:
                continue
            rows.append({
                "stem": stem,
                "path": path,
                "group": job.get("group") or "",
                "catalog_rows": catalog_rows,
                "spec_rows": spec_counts.get(key, 0),
            })
            if index % 20 == 0:
                progress("正在解析 CustomScripts... 已处理 %d 个" % index)
        rows.sort(key=lambda r: ((r["group"] or "ZZZ").upper(), r["stem"].upper()))
        return gen, rows

    def _on_scan_finished(self, result):
        gen, rows = result
        if gen != self._scan_gen:
            return
        self._scan_task = None
        self.btn_refresh.setEnabled(True)
        self._hide_progress()
        self._rows = rows
        self._apply_filter()

    def _on_scan_failed(self, detail):
        self._scan_task = None
        self.btn_refresh.setEnabled(True)
        self._hide_progress()
        self.lbl_count.setText("检索失败")
        self.status_message.emit("等级库检索失败: " + detail.strip().splitlines()[-1])

    def _apply_filter(self):
        q = self.txt_search.text().strip().lower()
        if q:
            rows = [
                r for r in self._rows
                if q in r["stem"].lower() or q in (r["group"] or "").lower()
            ]
        else:
            rows = list(self._rows)
        self._visible_rows = rows
        self._fill_table()

    def _fill_table(self):
        self._filling = True
        self.table.setUpdatesEnabled(False)
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.table.setRowCount(len(self._visible_rows))
        for row, item in enumerate(self._visible_rows):
            checked = item["stem"].upper() in self._checked_stems
            cell = QtWidgets.QTableWidgetItem()
            cell.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            cell.setCheckState(QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
            self.table.setItem(row, 0, cell)

            thumb = find_script_thumbnail(self._content_dir(), item["stem"])
            self.table.setItem(
                row, 1, make_thumbnail_item(thumb, item["stem"]))

            name_item = QtWidgets.QTableWidgetItem(item["stem"])
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            self.table.setItem(row, 2, name_item)
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(item["group"]))

            cnt_item = QtWidgets.QTableWidgetItem(str(item["catalog_rows"]))
            cnt_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(row, 4, cnt_item)

            if item["spec_rows"] > 0:
                status = "已加入（%d 行）" % item["spec_rows"]
                color = QtGui.QColor("#2A704E")
            elif item["catalog_rows"] > 0:
                status = "未加入（可从元件库添加）"
                color = QtGui.QColor("#B54708")
            else:
                status = "元件库中无此构件"
                color = QtGui.QColor("#667085")
            status_item = QtWidgets.QTableWidgetItem(status)
            status_item.setForeground(color)
            self.table.setItem(row, 5, status_item)

        self.table.blockSignals(False)
        self.table.setUpdatesEnabled(True)
        self._filling = False
        self.lbl_count.setText("共 %d 个自定义构件" % len(self._visible_rows))

    def _on_item_changed(self, item):
        if self._filling or item.column() != 0:
            return
        row = item.row()
        if not (0 <= row < len(self._visible_rows)):
            return
        stem = self._visible_rows[row]["stem"].upper()
        if item.checkState() == QtCore.Qt.Checked:
            self._checked_stems.add(stem)
        else:
            self._checked_stems.discard(stem)

    def _set_checked(self, predicate):
        self.table.blockSignals(True)
        for row, item in enumerate(self._visible_rows):
            cell = self.table.item(row, 0)
            if cell is None:
                continue
            state = QtCore.Qt.Checked if predicate(item) else QtCore.Qt.Unchecked
            cell.setCheckState(state)
            key = item["stem"].upper()
            if state == QtCore.Qt.Checked:
                self._checked_stems.add(key)
            else:
                self._checked_stems.discard(key)
        self.table.blockSignals(False)

    def _select_all(self):
        self._set_checked(lambda _item: True)

    def _select_none(self):
        self._set_checked(lambda _item: False)

    def _select_invert(self):
        current = {}
        for row, item in enumerate(self._visible_rows):
            cell = self.table.item(row, 0)
            current[item["stem"].upper()] = bool(
                cell and cell.checkState() == QtCore.Qt.Checked)
        self._set_checked(lambda item: not current.get(item["stem"].upper(), False))

    def _checked_rows(self):
        return [r for r in self._visible_rows if r["stem"].upper() in self._checked_stems]

    def _selector_error(self, need_catalog=True):
        if not self._content_dir() or not os.path.isdir(self._content_dir()):
            return "请先选择有效的 CPak Common 目录。"
        if need_catalog and not (self.combo_catalog.currentData() or ""):
            return "请先选择一个元件库 (.acat/.pcat)。"
        if not (self.combo_spec.currentData() or ""):
            return "请先选择一个等级库 (.pspc)。"
        return ""

    def _batch_add(self):
        error = self._selector_error(need_catalog=True)
        if error:
            QtWidgets.QMessageBox.information(self, "批量添加到等级库", error)
            return
        rows = self._checked_rows()
        if not rows:
            QtWidgets.QMessageBox.information(self, "批量添加到等级库", "请先勾选要添加的构件。")
            return
        if self._write_task is not None and self._write_task.is_running():
            QtWidgets.QMessageBox.information(self, "正在处理", "上一个写入任务尚未完成，请稍候。")
            return

        catalog_path = self.combo_catalog.currentData()
        spec_path = self.combo_spec.currentData()
        ans = QtWidgets.QMessageBox.question(
            self, "确认批量添加到等级库",
            "将 %d 个勾选构件写入等级库：\n%s\n\n元件库：%s" % (
                len(rows), os.path.basename(spec_path), os.path.basename(catalog_path)),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if ans != QtWidgets.QMessageBox.Yes:
            return

        def _work(progress, token):
            ok = skipped = 0
            rows_written = 0
            errors = []
            for i, item in enumerate(rows, 1):
                token.check()
                progress((i, len(rows), item["stem"]))
                if item["catalog_rows"] <= 0:
                    skipped += 1
                    continue
                try:
                    out = add_catalog_item_to_spec(
                        catalog_path, spec_path, item["stem"])
                    ok += 1
                    rows_written += int(out.get("added_rows") or 0)
                except Exception as exc:
                    errors.append("%s: %s" % (item["stem"], exc))
            return ok, skipped, rows_written, errors

        self._start_write(_work, "正在写入等级库...")

    def _batch_remove(self):
        error = self._selector_error(need_catalog=False)
        if error:
            QtWidgets.QMessageBox.information(self, "从等级库移除", error)
            return
        rows = [r for r in self._checked_rows() if r["spec_rows"] > 0]
        if not rows:
            QtWidgets.QMessageBox.information(
                self, "从等级库移除", "请勾选已加入当前等级库的构件。")
            return
        if self._write_task is not None and self._write_task.is_running():
            QtWidgets.QMessageBox.information(self, "正在处理", "上一个写入任务尚未完成，请稍候。")
            return

        spec_path = self.combo_spec.currentData()
        names = "、".join(r["stem"] for r in rows[:8])
        if len(rows) > 8:
            names += " 等共 %d 个构件" % len(rows)
        ans = QtWidgets.QMessageBox.question(
            self, "确认从等级库移除",
            "确定要从等级库 %s 中移除以下 %d 个构件吗？\n\n【%s】\n\n"
            "元件库中的记录不会受影响。" % (os.path.basename(spec_path), len(rows), names),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if ans != QtWidgets.QMessageBox.Yes:
            return

        def _work(progress, token):
            ok = 0
            removed_rows = 0
            errors = []
            for i, item in enumerate(rows, 1):
                token.check()
                progress((i, len(rows), item["stem"]))
                try:
                    out = remove_item_from_spec(spec_path, item["stem"])
                    if out.get("ok"):
                        ok += 1
                        removed_rows += int(out.get("removed_rows") or 0)
                except Exception as exc:
                    errors.append("%s: %s" % (item["stem"], exc))
            return ok, 0, removed_rows, errors

        self._start_write(_work, "正在从等级库移除...")

    def _start_write(self, work, text):
        self.btn_add.setEnabled(False)
        self.btn_remove.setEnabled(False)
        self.btn_refresh.setEnabled(False)
        self._show_progress(text, 0, 0)

        def _wrapped(progress, token):
            return work(progress, token)

        self._write_task = ThreadTask(_wrapped, parent=self, name="spec-write")
        self._write_task.progress.connect(self._on_write_progress)
        self._write_task.finished.connect(self._on_write_finished)
        self._write_task.failed.connect(self._on_write_failed)
        self._write_task.start()

    def _on_write_progress(self, payload):
        i, total, stem = payload
        self._show_progress("正在处理 %d/%d: %s" % (i, total, stem), i, total)

    def _on_write_finished(self, result):
        self._write_task = None
        self.btn_add.setEnabled(True)
        self.btn_remove.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self._hide_progress()
        ok, skipped, rows, errors = result
        msg = "完成：成功 %d 个构件，共 %d 行" % (ok, rows)
        if skipped:
            msg += "，跳过 %d 个" % skipped
        self.status_message.emit(msg)
        if errors:
            QtWidgets.QMessageBox.warning(
                self, "部分操作失败", "\n".join(errors[:10]))
        self._checked_stems.clear()
        self.reload_items()

    def _on_write_failed(self, detail):
        self._write_task = None
        self.btn_add.setEnabled(True)
        self.btn_remove.setEnabled(True)
        self.btn_refresh.setEnabled(True)
        self._hide_progress()
        QtWidgets.QMessageBox.critical(
            self, "操作失败", "等级库写入失败:\n" + detail[-1200:])

    def _show_progress(self, text, done=0, total=0):
        if total and total > 0:
            self.progress_bar_widget.set_progress(text, done, total)
        else:
            self.progress_bar_widget.set_busy(text)

    def _hide_progress(self):
        self.progress_bar_widget.hide_bar()

    def shutdown(self):
        if self._scan_task is not None:
            self._scan_task.stop(5000)
            self._scan_task = None
        if self._write_task is not None:
            self._write_task.stop(5000)
            self._write_task = None
