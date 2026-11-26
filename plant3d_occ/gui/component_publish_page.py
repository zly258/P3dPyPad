# -*- coding: utf-8 -*-
"""构件发布页：自定义构件脚本 -> 元件库 (.acat/.pcat) 及项目等级库 (.pspc)。

设计原则：
1. 极简专业布局：去除冗余杂乱复选框与多余列，宽幅展示核心主要列表；
2. 像素级标签与输入框对齐：标签统一 135px 宽度，与元件库管理页绝对一致；
3. 支持一键同步写入项目等级库工作表 (.pspc + .pspx)。
"""

import os
from PySide6 import QtCore, QtGui, QtWidgets

from ..catalog.destinations import (
    LOCKED_SUPPORT_CATALOG_FILE,
    LOCKED_SUPPORT_SPEC_FILE,
    PREFERRED_SUPPORT_SPEC_FILE,
    is_support_catalog,
    locked_catalog_reason,
    locked_spec_reason,
    spec_filename,
)
from ..catalog.manager import (
    create_project_spec,
    create_user_catalog,
    list_spec_files,
    load_catalog_config,
    save_catalog_config,
)
from ..catalog.model import inspect_script, iter_scripts
from ..catalog.publish import REGISTER_HINT
from .content_dir_box import ContentDirBox
from .i18n import tr
from .new_spec_dialog import ask_new_spec
from .page_layout import make_action_bar, make_action_button
from .progress import ThreadTask
from .publish_process import PublishProcess


def get_standard_component_types():
    return [
        ("ALL", tr("type_all", "全部类型 (ALL)")),
        ("Support", tr("type_support", "支吊架 (Support)")),
        ("Elbow", tr("type_elbow", "弯头 (Elbow)")),
        ("Tee", tr("type_tee", "三通 (Tee)")),
        ("Reducer", tr("type_reducer", "异径管 (Reducer)")),
        ("Cross", tr("type_cross", "四通 (Cross)")),
        ("Valve", tr("type_valve", "阀门 (Valve)")),
        ("Flange", tr("type_flange", "法兰 (Flange)")),
        ("Blind", tr("type_blind", "盲板 (Blind)")),
        ("Cap", tr("type_cap", "管帽/封头 (Cap)")),
        ("Instrument", tr("type_instrument", "仪表 (Instrument)")),
        ("Pipe", tr("type_pipe", "管段/管道 (Pipe)")),
    ]


class ComponentPublishPage(QtWidgets.QWidget):
    """只处理 domain 不是 equipment 的脚本。"""

    def __init__(self, parent=None, scripts_root="", content_dir=None, lazy_load=True):
        super(ComponentPublishPage, self).__init__(parent)
        self._scripts_root = scripts_root
        self._cfg = load_catalog_config()
        if content_dir:
            self._cfg["content_dir"] = content_dir
        self._jobs = []
        self._job_map = {}
        self._published_set = set()
        self._scan_task = None
        self._scan_gen = 0
        self._publish_task = None
        self._search_timer = QtCore.QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)
        self._search_timer.timeout.connect(self._fill_table)
        self._loaded = False
        self._setup_ui()
        if not lazy_load:
            self.ensure_loaded()

    def ensure_loaded(self):
        if not self._loaded:
            self._refresh_destinations()
            self.reload_scripts()

    def set_scripts_root(self, root_dir: str):
        """同步文件树当前浏览目录：立即重扫脚本列表。"""
        root_dir = root_dir or ""
        if not root_dir or root_dir == self._scripts_root:
            return
        self._scripts_root = root_dir
        self.reload_scripts()

    def _setup_ui(self):
        box = QtWidgets.QVBoxLayout(self)
        box.setContentsMargins(8, 8, 8, 8)
        box.setSpacing(6)

        # 1. 目录配置行 (固定标签宽度 135px 与设备发布页统一对齐)
        row = QtWidgets.QHBoxLayout()
        self.lbl_content_dir = QtWidgets.QLabel(tr("cat_lbl_content_dir"), self)
        self.lbl_content_dir.setFixedWidth(135)
        self.lbl_content_dir.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row.addWidget(self.lbl_content_dir)

        self.txt_content = ContentDirBox(self._cfg.get("content_dir", ""), self)
        self.txt_content.editingFinished.connect(self._on_content_changed)
        row.addWidget(self.txt_content, stretch=1)

        self.btn_browse = QtWidgets.QPushButton(tr("tree_btn_browse"), self)
        self.btn_browse.setFixedSize(65, 26)
        self.btn_browse.clicked.connect(self._browse_content)
        row.addWidget(self.btn_browse)
        box.addLayout(row)

        dest = QtWidgets.QHBoxLayout()
        dest.setSpacing(6)
        self.lbl_catalog = QtWidgets.QLabel("元件库:", self)
        dest.addWidget(self.lbl_catalog)
        self.combo_catalog = QtWidgets.QComboBox(self)
        self.combo_catalog.setFixedHeight(26)
        self.combo_catalog.setMinimumWidth(220)
        self.combo_catalog.currentIndexChanged.connect(self._update_dest_hint)
        dest.addWidget(self.combo_catalog, stretch=1)
        self.btn_new_catalog = QtWidgets.QPushButton("新建元件库", self)
        self.btn_new_catalog.setFixedHeight(26)
        self.btn_new_catalog.clicked.connect(self._new_catalog)
        dest.addWidget(self.btn_new_catalog)
        self.lbl_spec = QtWidgets.QLabel("等级库:", self)
        dest.addWidget(self.lbl_spec)
        self.combo_spec = QtWidgets.QComboBox(self)
        self.combo_spec.setFixedHeight(26)
        self.combo_spec.setMinimumWidth(220)
        self.combo_spec.currentIndexChanged.connect(self._update_dest_hint)
        dest.addWidget(self.combo_spec, stretch=1)
        self.btn_new_spec = QtWidgets.QPushButton("新建等级库", self)
        self.btn_new_spec.setFixedHeight(26)
        self.btn_new_spec.clicked.connect(self._new_spec)
        dest.addWidget(self.btn_new_spec)
        box.addLayout(dest)

        self.lbl_dest_hint = QtWidgets.QLabel("", self)
        self.lbl_dest_hint.setWordWrap(True)
        self.lbl_dest_hint.setObjectName("actionHint")
        box.addWidget(self.lbl_dest_hint)

        # 2. 紧凑工具栏：构件类型筛选 + 全选/全不选/反选 + 实时搜索 + 重新扫描
        #    (全选/全不选/反选位置与发布设备页一致)
        tools = QtWidgets.QHBoxLayout()
        tools.setSpacing(6)

        self.lbl_type = QtWidgets.QLabel(tr("cat_lbl_domain", "构件类型:"), self)
        tools.addWidget(self.lbl_type)

        self.filter_box = QtWidgets.QComboBox(self)
        self.filter_box.setFixedHeight(26)
        self._populate_type_combo()
        self.filter_box.currentIndexChanged.connect(self._fill_table)
        tools.addWidget(self.filter_box)

        self.btn_check_all = QtWidgets.QPushButton(tr("pub_btn_check_all"), self)
        self.btn_check_all.setFixedHeight(26)
        self.btn_check_all.clicked.connect(self._check_ready)
        tools.addWidget(self.btn_check_all)

        self.btn_check_none = QtWidgets.QPushButton(tr("pub_btn_check_none"), self)
        self.btn_check_none.setFixedHeight(26)
        self.btn_check_none.clicked.connect(self._check_none)
        tools.addWidget(self.btn_check_none)

        self.btn_check_invert = QtWidgets.QPushButton(tr("pub_btn_check_invert", "反选"), self)
        self.btn_check_invert.setFixedHeight(26)
        self.btn_check_invert.clicked.connect(self._check_invert)
        tools.addWidget(self.btn_check_invert)

        self.btn_check_unpublished = QtWidgets.QPushButton(
            tr("pub_btn_check_unpublished", "一键勾选未发布"), self)
        self.btn_check_unpublished.setFixedHeight(26)
        self.btn_check_unpublished.setToolTip("勾选所有尚未发布且可正常发布的构件")
        self.btn_check_unpublished.clicked.connect(self._check_unpublished)
        tools.addWidget(self.btn_check_unpublished)

        tools.addStretch()

        self.txt_search = QtWidgets.QLineEdit(self)
        self.txt_search.setFixedHeight(26)
        self.txt_search.setPlaceholderText("实时过滤脚本名称或说明...")
        self.txt_search.textChanged.connect(lambda _text: self._search_timer.start())
        tools.addWidget(self.txt_search, stretch=1)

        self.btn_reload = QtWidgets.QPushButton(tr("pub_btn_reload", "重新扫描"), self)
        self.btn_reload.setFixedHeight(26)
        self.btn_reload.clicked.connect(self.reload_scripts)
        tools.addWidget(self.btn_reload)

        self.lbl_count = QtWidgets.QLabel("", self)
        tools.addWidget(self.lbl_count)
        box.addLayout(tools)

        # 3. 操作栏：所有页面统一放在表格上方，主操作按钮固定在右侧
        action_bar = make_action_bar()
        self.lbl_action_hint = QtWidgets.QLabel(
            "支吊架元件库仍进 SUPPORTS Catalog metric；等级跟上面的选择走，例如 PipeSupports", self)
        self.lbl_action_hint.setObjectName("actionHint")
        action_bar.addWidget(self.lbl_action_hint)
        action_bar.addStretch()
        self.btn_run = make_action_button(tr("pub_btn_run"), primary=True, min_width=150)
        self.btn_run.clicked.connect(self._publish)
        action_bar.addWidget(self.btn_run)
        box.addLayout(action_bar)

        # 4. 构件明细主要列表 (5 列主要宽幅布局：勾选、构件名称、类别、规格数、发布状态/说明)
        self.table = QtWidgets.QTableWidget(0, 5, self)
        self.table.setHorizontalHeaderLabels([
            tr("th_select", "勾选"),
            tr("th_script_name", "构件名称"),
            tr("th_category", "类别"),
            tr("th_sizes", "规格数"),
            tr("pub_th_desc", "发布状态 / 说明"),
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)

        head = self.table.horizontalHeader()
        head.setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.table.setColumnWidth(0, 48)

        head.setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
        self.table.setColumnWidth(1, 260)  # 构件名称宽幅舒展

        head.setSectionResizeMode(2, QtWidgets.QHeaderView.Interactive)
        self.table.setColumnWidth(2, 140)  # 类别舒展

        head.setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        self.table.setColumnWidth(3, 85)   # 规格数紧凑居中

        head.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)  # 说明列拉伸
        box.addWidget(self.table, stretch=1)

        # 5. 发布输出日志
        self.log = QtWidgets.QPlainTextEdit(self)
        self.log.setFixedHeight(85)
        self.log.setReadOnly(True)
        box.addWidget(self.log)
        self._refresh_destinations()

    def _populate_type_combo(self):
        cur_data = self.filter_box.currentData() if self.filter_box.count() > 0 else "ALL"
        self.filter_box.blockSignals(True)
        self.filter_box.clear()

        known_codes = set()
        for code, name in get_standard_component_types():
            known_codes.add(code.lower())
            self.filter_box.addItem(name, code)

        for job in self._jobs:
            grp = (job.get("group") or "").strip()
            if grp and grp.lower() not in known_codes and grp.lower() != "equipment":
                known_codes.add(grp.lower())
                self.filter_box.addItem(f"{grp} (自定义类型)", grp)

        idx = self.filter_box.findData(cur_data)
        if idx >= 0:
            self.filter_box.setCurrentIndex(idx)
        else:
            self.filter_box.setCurrentIndex(0)
        self.filter_box.blockSignals(False)

    def reload_scripts(self):
        """只收构件脚本：设备脚本与系统默认内置构件一律不列。

        扫描+解析全部放到后台线程，主界面不再因为脚本数量多而假死。
        """
        if self._scan_task is not None and self._scan_task.is_running():
            self._scan_task.cancel()
        self._scan_gen += 1
        gen = self._scan_gen
        self.lbl_count.setText(tr("pub_loading", "正在扫描脚本..."))
        self.btn_reload.setEnabled(False)
        root = self._scripts_root
        content = self.txt_content.text().strip()
        self._scan_task = ThreadTask(
            lambda progress, token: self._scan_worker(
                root, content, gen, progress, token),
            parent=self, name="component-script-scan")
        self._scan_task.progress.connect(self._on_scan_progress)
        self._scan_task.finished.connect(self._on_scan_finished)
        self._scan_task.failed.connect(self._on_scan_failed)
        self._scan_task.start()

    def _scan_worker(self, root, content, gen, progress, token):
        jobs = []
        total_hint = 0
        for path in iter_scripts(root):
            token.check()
            # 严格过滤原厂系统内置构件
            if "system_defaults" in path.replace("\\", "/"):
                continue
            job = inspect_script(path, auto_generate_sizes=True)
            if (job.get("domain") or "") == "equipment":
                continue
            if not (job.get("group") or "").strip():
                continue
            jobs.append(job)
            total_hint += 1
            if total_hint % 20 == 0:
                progress(("正在扫描脚本... 已解析 %d 个" % total_hint, 0, 0))

        token.check()
        jobs.sort(key=lambda j: (
            (j.get("group") or "ZZZ").strip().upper(),
            (j.get("stem") or "").strip().upper()
        ))
        published = self._query_published_set(content, token)
        return gen, jobs, published

    def _on_scan_progress(self, payload):
        text = payload[0] if isinstance(payload, tuple) else str(payload)
        self.lbl_count.setText(text)

    def _on_scan_finished(self, result):
        gen, jobs, published = result
        if gen != self._scan_gen:
            return
        self._loaded = True
        self._jobs = jobs
        self._published_set = published
        self._job_map = {job["path"]: job for job in jobs}
        ready = sum(1 for j in jobs if not j["skip_reason"])
        self.lbl_count.setText("可发布 %d / %d" % (ready, len(jobs)))
        self.btn_reload.setEnabled(True)
        self._populate_type_combo()
        self._fill_table()
        self._scan_task = None

    def _on_scan_failed(self, detail):
        if self.sender() is not self._scan_task:
            return
        self.lbl_count.setText("脚本扫描失败")
        self.btn_reload.setEnabled(True)
        self.log.appendPlainText("脚本扫描失败:\n" + detail)
        self._scan_task = None

    def _query_published_set(self, content=None, token=None):
        content = content if content is not None else self.txt_content.text().strip()
        if not content or not os.path.isdir(content):
            return set()
        published = set()
        import sqlite3
        scan_dirs = [content]
        nested = os.path.join(content, "CPak Common")
        if os.path.isdir(nested):
            scan_dirs.append(nested)
        for d in scan_dirs:
            try:
                for fn in os.listdir(d):
                    if token is not None:
                        token.check()
                    if fn.lower().endswith((".pcat", ".acat")):
                        db_p = os.path.join(d, fn)
                        try:
                            con = sqlite3.connect("file:%s?mode=ro" % db_p.replace("\\", "/"), uri=True)
                            cur = con.cursor()
                            cur.execute("SELECT DISTINCT ContentGeometryTemplate FROM EngineeringItems WHERE ContentGeometryTemplate IS NOT NULL")
                            for r in cur.fetchall():
                                if r[0]:
                                    published.add(r[0].strip().upper())
                            con.close()
                        except Exception:
                            pass
            except Exception:
                pass
        return published

    def _fill_table(self):
        if not hasattr(self, "table"):
            return
        sel_type = self.filter_box.currentData() or "ALL"
        search_kw = self.txt_search.text().strip().lower() if hasattr(self, "txt_search") else ""
        rows = []
        for job in self._jobs:
            grp = (job.get("group") or "").strip()
            stem = (job.get("stem") or "").strip()
            desc = (job.get("tooltip_short") or "").strip()

            if sel_type != "ALL":
                if sel_type.lower() == "other":
                    known = {code.lower() for code, _ in get_standard_component_types() if code != "ALL"}
                    if grp.lower() in known:
                        continue
                elif grp.lower() != sel_type.lower():
                    continue

            if search_kw:
                if search_kw not in stem.lower() and search_kw not in grp.lower() and search_kw not in desc.lower():
                    continue

            rows.append(job)

        published_set = self._published_set
        color_published = QtGui.QColor("#2A704E")
        color_unpublished = QtGui.QColor("#1F2933")

        self.table.setUpdatesEnabled(False)
        self.table.blockSignals(True)
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        self.table.setRowCount(len(rows))
        for i, job in enumerate(rows):
            # 列 0：勾选
            cell = QtWidgets.QTableWidgetItem()
            cell.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            cell.setCheckState(QtCore.Qt.Unchecked)
            cell.setData(QtCore.Qt.UserRole, job["path"])
            self.table.setItem(i, 0, cell)

            # 列 1：构件名称 (加粗宽幅)
            stem_name = job.get("stem", "")
            is_pub = stem_name.upper() in published_set
            name_item = QtWidgets.QTableWidgetItem(stem_name)
            font = name_item.font()
            font.setBold(True)
            name_item.setFont(font)
            if is_pub:
                name_item.setForeground(color_published)
            self.table.setItem(i, 1, name_item)

            # 列 2：类别
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(job.get("group") or ""))

            # 列 3：规格数 (居中)
            cnt_item = QtWidgets.QTableWidgetItem(str(len(job.get("sizes") or [])))
            cnt_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(i, 3, cnt_item)

            # 列 4：状态与说明
            status_prefix = "【已发布】" if is_pub else "【未发布】"
            raw_desc = (job["skip_reason"]
                        or "；".join(job.get("warnings") or [])
                        or job.get("tooltip_short")
                        or "就绪")
            detail_item = QtWidgets.QTableWidgetItem(f"{status_prefix} {raw_desc}")
            if is_pub:
                detail_item.setForeground(color_published)
            else:
                detail_item.setForeground(color_unpublished)
            self.table.setItem(i, 4, detail_item)
        self.table.blockSignals(False)
        self.table.setUpdatesEnabled(True)

    def retranslate_ui(self):
        if hasattr(self, "lbl_content_dir"):
            self.lbl_content_dir.setText(tr("cat_lbl_content_dir"))
        if hasattr(self, "btn_browse"):
            self.btn_browse.setText(tr("tree_btn_browse"))
        if hasattr(self, "lbl_type"):
            self.lbl_type.setText(tr("cat_lbl_domain", "构件类型:"))
        if hasattr(self, "btn_check_all"):
            self.btn_check_all.setText(tr("pub_btn_check_all"))
        if hasattr(self, "btn_check_none"):
            self.btn_check_none.setText(tr("pub_btn_check_none"))
        if hasattr(self, "btn_check_invert"):
            self.btn_check_invert.setText(tr("pub_btn_check_invert", "反选"))
        if hasattr(self, "btn_check_unpublished"):
            self.btn_check_unpublished.setText(tr("pub_btn_check_unpublished", "一键勾选未发布"))
        if hasattr(self, "btn_reload"):
            self.btn_reload.setText(tr("pub_btn_reload", "重新扫描"))
        if hasattr(self, "btn_run"):
            self.btn_run.setText(tr("pub_btn_run"))
        if hasattr(self, "table"):
            self.table.setHorizontalHeaderLabels([
                tr("th_select", "勾选"),
                tr("th_script_name", "构件名称"),
                tr("th_category", "类别"),
                tr("th_sizes", "规格数"),
                tr("pub_th_desc", "发布状态 / 说明"),
            ])
        self._populate_type_combo()

    def _job_by_path(self, path):
        return self._job_map.get(path)

    def _check_ready(self):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            job = self._job_by_path(item.data(QtCore.Qt.UserRole))
            if job and not job["skip_reason"]:
                item.setCheckState(QtCore.Qt.Checked)

    def _check_none(self):
        for row in range(self.table.rowCount()):
            self.table.item(row, 0).setCheckState(QtCore.Qt.Unchecked)

    def _check_invert(self):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            job = self._job_by_path(item.data(QtCore.Qt.UserRole))
            if job and job["skip_reason"]:
                continue  # 不可发布行不参与反选
            item.setCheckState(
                QtCore.Qt.Unchecked if item.checkState() == QtCore.Qt.Checked
                else QtCore.Qt.Checked)

    def _check_unpublished(self):
        """一键勾选未发布且可发布的构件。"""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            job = self._job_by_path(item.data(QtCore.Qt.UserRole))
            if not job or job.get("skip_reason"):
                item.setCheckState(QtCore.Qt.Unchecked)
                continue
            stem = (job.get("stem") or "").strip().upper()
            item.setCheckState(
                QtCore.Qt.Unchecked if stem in self._published_set
                else QtCore.Qt.Checked)

    def _selected_paths(self):
        return [self.table.item(r, 0).data(QtCore.Qt.UserRole)
                for r in range(self.table.rowCount())
                if self.table.item(r, 0).checkState() == QtCore.Qt.Checked]

    def _content_dir(self):
        return self.txt_content.text().strip()

    def _project_spec_dir(self):
        cfg = load_catalog_config()
        return cfg.get("project_spec_dir") or ""

    def _refresh_destinations(self):
        content = self._content_dir()
        prev_catalog = self.combo_catalog.currentData()
        prev_spec = self.combo_spec.currentData()
        self.combo_catalog.blockSignals(True)
        self.combo_spec.blockSignals(True)
        self.combo_catalog.clear()
        if content and os.path.isdir(content):
            for fn in sorted(os.listdir(content)):
                if not fn.lower().endswith((".pcat", ".acat")):
                    continue
                path = os.path.join(content, fn)
                if not os.path.isfile(path):
                    continue
                label = fn
                reason = locked_catalog_reason(fn)
                if reason:
                    label += "  （固定）"
                self.combo_catalog.addItem(label, path)
        preferred = os.path.join(content, "CustomParts Metric Catalog.pcat") if content else ""
        idx = self.combo_catalog.findData(prev_catalog) if prev_catalog else -1
        if idx < 0 and preferred:
            idx = self.combo_catalog.findData(preferred)
        if idx >= 0:
            self.combo_catalog.setCurrentIndex(idx)

        self.combo_spec.clear()
        self.combo_spec.addItem("不加入等级库", "")
        spec_dir = self._project_spec_dir()
        for item in list_spec_files(content, spec_dir, include_content_dir=False):
            label = item["file"]
            if locked_spec_reason(item["file"]):
                label += "  （固定）"
            self.combo_spec.addItem(label, item["path"])
        if prev_spec is None:
            for prefer in (PREFERRED_SUPPORT_SPEC_FILE, LOCKED_SUPPORT_SPEC_FILE):
                for i in range(self.combo_spec.count()):
                    path = self.combo_spec.itemData(i) or ""
                    if os.path.basename(path).lower() == prefer.lower():
                        self.combo_spec.setCurrentIndex(i)
                        prefer = ""
                        break
                if not prefer:
                    break
        else:
            idx = self.combo_spec.findData(prev_spec)
            if idx >= 0:
                self.combo_spec.setCurrentIndex(idx)
        self.combo_catalog.blockSignals(False)
        self.combo_spec.blockSignals(False)
        self._update_dest_hint()

    def _update_dest_hint(self, _index=0):
        catalog = os.path.basename(self.combo_catalog.currentData() or "")
        spec = os.path.basename(self.combo_spec.currentData() or "") or "不加入"
        spec_dir = self._project_spec_dir()
        where = spec_dir or "（还没选项目，请先到等级库页指定）"
        self.lbl_dest_hint.setText(
            "元件库只放在 CPak Common。固定库不能改名，可以另建。"
            "等级只放在项目等级表：%s。当前：元件库 %s，等级 %s。"
            "支吊架元件库始终写入 %s，不跟元件库下拉走。等级用当前选择；"
            "选「不加入」时，支吊架才回退到项目里的 %s。"
            % (where, catalog or "未选", spec, LOCKED_SUPPORT_CATALOG_FILE, LOCKED_SUPPORT_SPEC_FILE)
        )

    def _new_catalog(self):
        content = self._content_dir()
        if not content or not os.path.isdir(content):
            self.log.appendPlainText("请先填写 CPak Common 目录。")
            return
        name, ok = QtWidgets.QInputDialog.getText(
            self, "新建元件库", "名称（放在 CPak Common，不要用原厂固定名）:")
        if not ok or not name.strip():
            return
        kind = "instrumentation" if "instrument" in name.lower() else "piping"
        try:
            info = create_user_catalog(content, name.strip(), kind=kind)
        except Exception as exc:
            QtWidgets.QMessageBox.warning(self, "新建元件库", str(exc))
            return
        self._refresh_destinations()
        idx = self.combo_catalog.findData(info["catalog_path"])
        if idx >= 0:
            self.combo_catalog.setCurrentIndex(idx)
        self.log.appendPlainText("已新建元件库 " + info["catalog_file"])

    def _new_spec(self):
        spec_dir = self._project_spec_dir()
        if not spec_dir or not os.path.isdir(spec_dir):
            QtWidgets.QMessageBox.information(
                self, "新建等级库", "请先在「等级库管理」页指定项目或等级库工作表目录。")
            return
        asked = ask_new_spec(self)
        if not asked:
            return
        name, include_pipe = asked
        try:
            spec_filename(name)
            info = create_project_spec(spec_dir, name, include_pipe=include_pipe)
        except Exception as exc:
            QtWidgets.QMessageBox.warning(self, "新建等级库", str(exc))
            return
        self._refresh_destinations()
        idx = self.combo_spec.findData(info["spec_path"])
        if idx >= 0:
            self.combo_spec.setCurrentIndex(idx)
        note = "已新建等级库 " + info["spec_file"]
        if info.get("pipe_note"):
            note += "。" + info["pipe_note"]
        self.log.appendPlainText(note)

    def _on_content_changed(self):
        folder = self._content_dir()
        if not folder:
            return
        save_catalog_config({"content_dir": folder})
        self._refresh_destinations()
        self.reload_scripts()

    def _browse_content(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择 CPak Common", self.txt_content.text())
        if folder:
            self.txt_content.setText(folder)
            self._on_content_changed()

    def _publish(self):
        paths = self._selected_paths()
        if not paths:
            self.log.appendPlainText("请先勾选至少一个要发布的构件脚本。")
            return
        content = self.txt_content.text().strip()
        if not content:
            self.log.appendPlainText("请填写 CPak Common 内容目录。")
            return
        catalog_path = self.combo_catalog.currentData() or ""
        catalog_file = os.path.basename(catalog_path)
        catalog_name = os.path.splitext(catalog_file)[0]
        if is_support_catalog(catalog_file):
            catalog_file = ""
            catalog_name = ""
        project_spec = self.combo_spec.currentData() or ""
        spec_dir = self._project_spec_dir()
        save_catalog_config({
            "content_dir": content,
            "auto_generate_sizes": True,
            "write_preview": True,
            "piping_catalog": catalog_file or "CustomParts Metric Catalog.pcat",
        })

        self.btn_run.setEnabled(False)
        self.log.clear()
        win = self.window()
        if hasattr(win, "_begin_loading"):
            win._begin_loading(f"正在发布 {len(paths)} 个构件到元件库...")
        # 发布 + 预览渲染放到独立子进程：OCC 离屏视口不能在 QThread 里创建，
        # 否则会原生 access violation 闪退。
        self._publish_task = PublishProcess(
            paths, content, include_equipment=False,
            auto_generate_sizes=True, write_preview=True, parent=self,
            catalog_file=catalog_file, catalog_name=catalog_name,
            project_spec=project_spec, project_spec_dir=spec_dir)
        self._publish_task.progress.connect(self._on_publish_progress)
        self._publish_task.finished.connect(self._on_publish_finished)
        self._publish_task.failed.connect(self._on_publish_failed)
        self._publish_task.start()

    def _on_publish_progress(self, message):
        self.log.appendPlainText(str(message))
        win = self.window()
        if hasattr(win, "lbl_status"):
            win.lbl_status.setText(str(message))
        if hasattr(win, "loading_bar"):
            win.loading_bar.setRange(0, 0)

    def _on_publish_finished(self, results):
        win = self.window()
        ok = sum(1 for i in results if i.get("status") == "published")
        sk = sum(1 for i in results if i.get("status") == "skipped")
        bad = sum(1 for i in results if i.get("status") == "failed")
        self.log.appendPlainText("结果汇总：成功 %d，跳过 %d，失败 %d。" % (ok, sk, bad))
        if ok:
            self.log.appendPlainText(REGISTER_HINT)
        for item in results:
            if item.get("status") == "published":
                self.log.appendPlainText(
                    os.path.basename(item.get("script", "")) + " — " + item.get("message", ""))
                self._published_set.add(
                    os.path.splitext(os.path.basename(item.get("script", "")))[0].upper())
        # 等级库 (.pspc) 操作不在这里做：发布只写元件库 (.acat/.pcat)，
        # "加入/移除项目等级库"统一在元件库管理页操作（支吊架/仪表自动匹配固定等级）。

        self.btn_run.setEnabled(True)
        if hasattr(win, "_end_loading"):
            win._end_loading(f"发布完成 (成功 {ok}, 失败 {bad})")
        self._fill_table()
        self._publish_task = None

    def _on_publish_failed(self, detail):
        self.log.appendPlainText("发布中断:\n" + detail)
        self.btn_run.setEnabled(True)
        win = self.window()
        if hasattr(win, "_end_loading"):
            win._end_loading("发布中断")
        self._publish_task = None

    def shutdown(self):
        """窗口关闭前停止可取消的后台扫描，避免 QThread 析构时闪退。"""
        if self._scan_task is not None:
            self._scan_task.stop(3000)
            self._scan_task = None
        if self._publish_task is not None:
            if not self._publish_task.wait(60000):
                self._publish_task.stop(3000)
            self._publish_task = None
