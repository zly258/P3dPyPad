# -*- coding: utf-8 -*-
"""元件库管理：只列出 CustomScripts 目录下已发布的自定义构件。

发布构件时会自动写入对应元件库，因此本页不再提供"发布/加入等级库"等操作，
只保留检索、勾选与从元件库移除。设备模板 (.peqx) 不在这里管理。
"""

import os
from typing import List

from PySide6 import QtCore, QtWidgets

from ..catalog.manager import (
    delete_published_item,
    load_catalog_config,
    query_published_items,
    save_catalog_config,
)
from .i18n import tr
from .page_layout import make_action_bar, make_action_button
from .progress import InlineProgressBar, ThreadTask
from .thumbnails import find_script_thumbnail, make_thumbnail_item


class CatalogManagerPage(QtWidgets.QWidget):
    """自定义构件元件库检索与移除页。"""

    status_message = QtCore.Signal(str)

    def __init__(self, parent=None, scripts_root="", lazy_load=True):
        super(CatalogManagerPage, self).__init__(parent)
        self._scripts_root = scripts_root or ""
        self._config = load_catalog_config()
        self._all_items = []
        self._items = []
        self._checked_keys = set()
        self._loaded = False
        self._query_task = None
        self._delete_task = None
        self._pending_query = False
        self._filling_table = False
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
        self.lbl_summary.setText(tr("status_loading", "正在加载元件库数据..."))
        QtCore.QTimer.singleShot(0, lambda: self.refresh_catalog_data(show_progress=True))

    def _setup_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        # 1. 目录配置行
        cfg = QtWidgets.QHBoxLayout()
        cfg.setSpacing(6)
        self.lbl_content_dir = QtWidgets.QLabel(tr("cat_lbl_content_dir"), self)
        self.lbl_content_dir.setFixedWidth(135)
        self.lbl_content_dir.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        cfg.addWidget(self.lbl_content_dir)

        self.txt_content_dir = QtWidgets.QLineEdit(
            self._config.get("content_dir", ""), self)
        self.txt_content_dir.setFixedHeight(26)
        self.txt_content_dir.setPlaceholderText(tr("cat_txt_placeholder"))
        self.txt_content_dir.editingFinished.connect(self._on_content_dir_changed)
        cfg.addWidget(self.txt_content_dir, stretch=1)

        self.btn_browse = QtWidgets.QPushButton(tr("tree_btn_browse"), self)
        self.btn_browse.setFixedSize(65, 26)
        self.btn_browse.clicked.connect(self._on_browse_content_dir)
        cfg.addWidget(self.btn_browse)
        root.addLayout(cfg)

        # 2. 工具栏
        tools = QtWidgets.QHBoxLayout()
        tools.setSpacing(6)

        self.btn_select_all = QtWidgets.QPushButton("全选", self)
        self.btn_select_all.setFixedHeight(26)
        self.btn_select_all.clicked.connect(self._select_all_items)
        tools.addWidget(self.btn_select_all)

        self.btn_select_none = QtWidgets.QPushButton("全不选", self)
        self.btn_select_none.setFixedHeight(26)
        self.btn_select_none.clicked.connect(self._select_none_items)
        tools.addWidget(self.btn_select_none)

        self.btn_select_invert = QtWidgets.QPushButton("反选", self)
        self.btn_select_invert.setFixedHeight(26)
        self.btn_select_invert.clicked.connect(self._select_invert_items)
        tools.addWidget(self.btn_select_invert)

        tools.addStretch()

        self.txt_search = QtWidgets.QLineEdit(self)
        self.txt_search.setFixedHeight(26)
        self.txt_search.setPlaceholderText(tr("cat_search_placeholder"))
        self.txt_search.textChanged.connect(lambda _text: self._search_timer.start())
        tools.addWidget(self.txt_search, stretch=1)

        self.btn_refresh = QtWidgets.QPushButton(tr("cat_btn_refresh"), self)
        self.btn_refresh.setFixedHeight(26)
        self.btn_refresh.clicked.connect(self._on_refresh_clicked)
        tools.addWidget(self.btn_refresh)
        self.lbl_summary = QtWidgets.QLabel(tr("status_ready"), self)
        tools.addWidget(self.lbl_summary)
        root.addLayout(tools)

        # 3. 操作栏：统一放在表格上方，危险操作靠右
        action_bar = make_action_bar()
        self.lbl_action_hint = QtWidgets.QLabel(
            "只管理和移除 CustomScripts 下的自定义构件；设备请在「发布设备」页移除", self)
        self.lbl_action_hint.setObjectName("actionHint")
        action_bar.addWidget(self.lbl_action_hint)
        self.lbl_checked = QtWidgets.QLabel("", self)
        self.lbl_checked.setObjectName("checkedCount")
        action_bar.addWidget(self.lbl_checked)
        action_bar.addStretch()
        self.btn_remove = make_action_button(
            tr("det_btn_delete", "从元件库移除"), danger=True, min_width=140)
        self.btn_remove.setEnabled(False)
        self.btn_remove.clicked.connect(self._on_remove)
        action_bar.addWidget(self.btn_remove)
        root.addLayout(action_bar)

        # 4. 主列表：勾选 / 图标 / 构件名称 / 类别 / 规格数 / 所属元件库
        self.table_items = QtWidgets.QTableWidget(0, 6, self)
        self.table_items.setIconSize(QtCore.QSize(80, 80))
        self.table_items.verticalHeader().setDefaultSectionSize(88)
        self.table_items.verticalHeader().setVisible(False)
        self.table_items.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_items.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table_items.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_items.setAlternatingRowColors(True)
        self.table_items.itemChanged.connect(self._on_table_item_changed)
        self.table_items.itemSelectionChanged.connect(self._update_checked_label)
        root.addWidget(self.table_items, stretch=1)
        self._apply_header_labels()

        hdr = self.table_items.horizontalHeader()
        hdr.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.table_items.setColumnWidth(0, 48)
        hdr.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.table_items.setColumnWidth(1, 96)
        hdr.setSectionResizeMode(2, QtWidgets.QHeaderView.Interactive)
        self.table_items.setColumnWidth(2, 280)
        hdr.setSectionResizeMode(3, QtWidgets.QHeaderView.Interactive)
        self.table_items.setColumnWidth(3, 150)
        hdr.setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)
        self.table_items.setColumnWidth(4, 85)
        hdr.setSectionResizeMode(5, QtWidgets.QHeaderView.Stretch)

        self.progress_bar_widget = InlineProgressBar(self)
        root.addWidget(self.progress_bar_widget)

    def _apply_header_labels(self):
        self.table_items.setHorizontalHeaderLabels([
            tr("th_select", "勾选"),
            tr("th_icon", "图标"),
            tr("th_script_name", "构件名称"),
            tr("th_category", "类别"),
            tr("th_sizes", "规格数"),
            tr("th_catalog_file", "所属库文件"),
        ])

    def retranslate_ui(self):
        if hasattr(self, "lbl_content_dir"):
            self.lbl_content_dir.setText(tr("cat_lbl_content_dir"))
        if hasattr(self, "btn_browse"):
            self.btn_browse.setText(tr("tree_btn_browse"))
        if hasattr(self, "btn_refresh"):
            self.btn_refresh.setText(tr("cat_btn_refresh"))
        if hasattr(self, "btn_remove"):
            self.btn_remove.setText(tr("det_btn_delete"))
        if hasattr(self, "txt_search"):
            self.txt_search.setPlaceholderText(tr("cat_search_placeholder"))
        if hasattr(self, "table_items"):
            self._apply_header_labels()

    def content_dir(self) -> str:
        return self.txt_content_dir.text().strip()

    def _on_browse_content_dir(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择 CPak Common", self.content_dir())
        if folder:
            self.txt_content_dir.setText(folder)
            save_catalog_config({"content_dir": folder})
            self.refresh_catalog_data(force=True, show_progress=True)

    def _on_content_dir_changed(self):
        folder = self.content_dir()
        if not folder:
            return
        self._config["content_dir"] = folder
        save_catalog_config({"content_dir": folder})
        self.refresh_catalog_data(force=True, show_progress=True)

    def _on_refresh_clicked(self):
        self.refresh_catalog_data(force=True, show_progress=True)

    def _show_progress(self, text, done=0, total=0):
        if total and total > 0:
            self.progress_bar_widget.set_progress(text, done, total)
        else:
            self.progress_bar_widget.set_busy(text)

    def _hide_progress(self):
        self.progress_bar_widget.hide_bar()

    def refresh_catalog_data(self, show_progress=False, force=False):
        """后台查询元件库，只保留 CustomScripts 下真实存在的自定义构件。"""
        if self._query_task is not None and self._query_task.is_running():
            self._pending_query = True
            return
        self.btn_refresh.setEnabled(False)
        if show_progress:
            self._show_progress(tr("cat_scanning", "正在检索元件库..."))

        cdir = self.content_dir()

        def _work(progress, token):
            def _on_prog(done, total, filename):
                token.check()
                progress((done, total, filename))

            rows = query_published_items(
                content_dir=cdir,
                on_progress=_on_prog,
                include_builtin=False,
            )
            token.check()
            custom = [
                it for it in rows
                if it.get("has_py") and it.get("source_type") != "peqx"
            ]
            custom.sort(key=lambda it: (
                (it.get("domain") or "").upper(),
                (it.get("script_name") or "").upper(),
            ))
            return custom

        self._query_task = ThreadTask(_work, parent=self, name="catalog-query")
        self._query_task.progress.connect(self._on_query_progress)
        self._query_task.finished.connect(self._on_query_finished)
        self._query_task.failed.connect(self._on_query_failed)
        self._query_task.start()

    def _on_query_progress(self, payload):
        done, total, filename = payload
        self._show_progress(
            tr("cat_scanning_file", "正在检索元件库 {done}/{total}: {file}").format(
                done=done, total=total, file=filename),
            done, total)

    def _on_query_finished(self, items):
        self._query_task = None
        self.btn_refresh.setEnabled(True)
        self._hide_progress()
        self._all_items = items or []
        self._apply_filter()
        if self._pending_query:
            self._pending_query = False
            self.refresh_catalog_data(show_progress=True, force=True)

    def _on_query_failed(self, detail):
        self._query_task = None
        self.btn_refresh.setEnabled(True)
        self._hide_progress()
        self.lbl_summary.setText("元件库检索失败，请检查目录与数据库是否被占用")
        self.status_message.emit("元件库检索失败: " + detail.strip().splitlines()[-1])

    def _apply_filter(self):
        q = self.txt_search.text().strip().lower()
        if q:
            items = [
                it for it in self._all_items
                if q in (it.get("script_name") or "").lower()
                or q in (it.get("description") or "").lower()
                or q in (it.get("catalog_file") or "").lower()
            ]
        else:
            items = list(self._all_items)
        self._items = items
        self._fill_table()

    @staticmethod
    def _item_key(item):
        return (item.get("script_name", ""), item.get("catalog_path", ""))

    def _fill_table(self):
        self._filling_table = True
        self.table_items.setUpdatesEnabled(False)
        self.table_items.blockSignals(True)
        self.table_items.setRowCount(0)
        self.table_items.setRowCount(len(self._items))
        total_sizes = 0
        for row, item in enumerate(self._items):
            total_sizes += int(item.get("size_count") or 0)
            checked = self._item_key(item) in self._checked_keys
            cell = QtWidgets.QTableWidgetItem()
            cell.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            cell.setCheckState(QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
            self.table_items.setItem(row, 0, cell)

            thumb = find_script_thumbnail(
                self.content_dir(), item.get("script_name") or "",
                item.get("preview_path") or "")
            self.table_items.setItem(
                row, 1, make_thumbnail_item(thumb, item.get("script_name") or ""))

            name_item = QtWidgets.QTableWidgetItem(item.get("script_name") or "")
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            self.table_items.setItem(row, 2, name_item)

            self.table_items.setItem(
                row, 3, QtWidgets.QTableWidgetItem(item.get("domain") or ""))

            cnt_item = QtWidgets.QTableWidgetItem(str(item.get("size_count") or 0))
            cnt_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table_items.setItem(row, 4, cnt_item)

            cat_item = QtWidgets.QTableWidgetItem(item.get("catalog_file") or "")
            cat_item.setToolTip(item.get("catalog_path") or "")
            self.table_items.setItem(row, 5, cat_item)

        self.table_items.blockSignals(False)
        self.table_items.setUpdatesEnabled(True)
        self._filling_table = False
        self.lbl_summary.setText(
            "共 %d 个自定义构件 · %d 条入库规格" % (len(self._items), total_sizes))
        self._update_checked_label()

    def _on_table_item_changed(self, item):
        if self._filling_table or item.column() != 0:
            return
        row = item.row()
        if not (0 <= row < len(self._items)):
            return
        key = self._item_key(self._items[row])
        if item.checkState() == QtCore.Qt.Checked:
            self._checked_keys.add(key)
        else:
            self._checked_keys.discard(key)
        self._update_checked_label()

    def _update_checked_label(self):
        count = len(self._get_checked_items())
        self.lbl_checked.setText("已勾选 %d 项" % count if count else "")
        self.btn_remove.setEnabled(count > 0 or bool(self._get_selected_items()))

    def _select_all_items(self):
        for row in range(self.table_items.rowCount()):
            self.table_items.item(row, 0).setCheckState(QtCore.Qt.Checked)

    def _select_none_items(self):
        for row in range(self.table_items.rowCount()):
            self.table_items.item(row, 0).setCheckState(QtCore.Qt.Unchecked)

    def _select_invert_items(self):
        for row in range(self.table_items.rowCount()):
            item = self.table_items.item(row, 0)
            item.setCheckState(
                QtCore.Qt.Unchecked if item.checkState() == QtCore.Qt.Checked
                else QtCore.Qt.Checked)

    def _get_checked_items(self) -> List[dict]:
        checked = []
        for row in range(self.table_items.rowCount()):
            item = self.table_items.item(row, 0)
            if item and item.checkState() == QtCore.Qt.Checked and row < len(self._items):
                checked.append(self._items[row])
        return checked

    def _get_selected_items(self) -> List[dict]:
        sm = self.table_items.selectionModel()
        if sm is None:
            return []
        rows = sorted({ix.row() for ix in sm.selectedRows()})
        return [self._items[r] for r in rows if 0 <= r < len(self._items)]

    def _get_target_items(self) -> List[dict]:
        return self._get_checked_items() or self._get_selected_items()

    def _on_remove(self):
        targets = self._get_target_items()
        if not targets:
            QtWidgets.QMessageBox.information(self, "从元件库移除", "请先勾选或选中要移除的构件。")
            return
        if self._delete_task is not None and self._delete_task.is_running():
            QtWidgets.QMessageBox.information(self, "正在处理", "上一个移除任务尚未完成，请稍候。")
            return

        names = [it.get("script_name", "") for it in targets]
        shown = "、".join(names[:8]) + (f" 等共 {len(names)} 个构件" if len(names) > 8 else "")
        ans = QtWidgets.QMessageBox.question(
            self, "确认从元件库移除",
            f"确定要从元件库中移除以下 {len(names)} 个构件的全部规格记录吗？\n\n【{shown}】\n\n"
            "CustomScripts 中的脚本文件会保留，可随时重新发布。",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if ans != QtWidgets.QMessageBox.Yes:
            return

        content_dir = self.content_dir()
        self.btn_refresh.setEnabled(False)
        self.btn_remove.setEnabled(False)
        self._show_progress("正在从元件库移除...", 0, len(targets))

        def _work(progress, token):
            total_rows = 0
            deleted = 0
            errors = []
            for i, it in enumerate(targets, 1):
                token.check()
                progress((i, len(targets), it.get("script_name", "")))
                try:
                    out = delete_published_item(
                        content_dir=content_dir,
                        script_name=it.get("script_name", ""),
                        catalog_path=it.get("catalog_path"),
                        remove_custom_script_files=False,
                    )
                    if out.get("ok"):
                        total_rows += out.get("deleted_rows", 0)
                        deleted += 1
                    else:
                        errors.append(
                            f"{it.get('script_name', '')}: {out.get('error') or '未找到库内记录'}")
                except Exception as exc:
                    errors.append(f"{it.get('script_name', '')}: {exc}")
            return {"total_rows": total_rows, "deleted": deleted, "errors": errors}

        self._delete_task = ThreadTask(_work, parent=self, name="catalog-delete")
        self._delete_task.progress.connect(self._on_delete_progress)
        self._delete_task.finished.connect(self._on_delete_finished)
        self._delete_task.failed.connect(self._on_delete_failed)
        self._delete_task.start()

    def _on_delete_progress(self, payload):
        i, total, name = payload
        self.lbl_summary.setText(f"正在移除 {i}/{total}: {name}")
        self._show_progress(f"正在移除 {i}/{total}: {name}", i, total)

    def _on_delete_finished(self, summary):
        self._delete_task = None
        self.btn_refresh.setEnabled(True)
        self.btn_remove.setEnabled(True)
        self._hide_progress()
        self._checked_keys.clear()
        deleted = summary.get("deleted", 0)
        total_rows = summary.get("total_rows", 0)
        errors = summary.get("errors") or []
        self.status_message.emit(
            f"已从元件库移除 {deleted} 个构件（共 {total_rows} 条记录）")
        if errors:
            QtWidgets.QMessageBox.warning(
                self, "部分移除失败", "\n".join(errors[:10]))
        self.refresh_catalog_data(force=True, show_progress=True)

    def _on_delete_failed(self, detail):
        self._delete_task = None
        self.btn_refresh.setEnabled(True)
        self.btn_remove.setEnabled(True)
        self._hide_progress()
        QtWidgets.QMessageBox.critical(
            self, "移除失败", "删除过程中发生异常:\n" + detail[-1200:])

    def shutdown(self):
        for attr in ("_query_task", "_delete_task"):
            task = getattr(self, attr, None)
            if task is not None:
                task.stop(15000)
                setattr(self, attr, None)
