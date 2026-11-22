# -*- coding: utf-8 -*-
"""设备发布页：设备脚本 -> 设备模板 (.peqx)。

与构件发布分开的原因：
  1. 产物不同：构件写元件库 (.acat/.pcat)，设备写设备模板包 (.peqx)；
  2. 设备在 Plant 3D 设备菜单里的归类由 PartType/PartSubType 决定，
     必须能显式指定，写错类型设备不显示；
  3. 设备没有规格表 CSV 的概念，不需要"自动推导多规格"。
"""
import os

from PySide6 import QtCore, QtWidgets

from ..catalog.equipment import (
    EQUIPMENT_TYPE_CHOICES,
    resolve_equipment_type,
    get_equipment_type_display_label,
)
from ..catalog.manager import (
    delete_published_item,
    load_catalog_config,
    save_catalog_config,
)
from ..catalog.model import inspect_script, iter_scripts
from ..catalog.publish import REGISTER_HINT
from .i18n import tr
from .page_layout import make_action_bar, make_action_button
from .progress import ThreadTask
from .publish_process import PublishProcess


class EquipmentPublishPage(QtWidgets.QWidget):
    """只处理 domain == equipment 的脚本。"""

    def __init__(self, parent=None, scripts_root="", content_dir=None, lazy_load=True):
        super(EquipmentPublishPage, self).__init__(parent)
        self._scripts_root = scripts_root
        self._cfg = load_catalog_config()
        if content_dir:
            self._cfg["content_dir"] = content_dir
        self._jobs = []
        self._job_map = {}
        self._scan_task = None
        self._scan_gen = 0
        self._publish_task = None
        self._remove_task = None
        self._loaded = False
        self._search_timer = QtCore.QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(250)
        self._search_timer.timeout.connect(self._fill_table)
        self._setup_ui()
        if not lazy_load:
            self.ensure_loaded()

    def ensure_loaded(self):
        if not self._loaded:
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

        # 1. 目录配置行
        row = QtWidgets.QHBoxLayout()
        self.lbl_content_dir = QtWidgets.QLabel(tr("cat_lbl_content_dir"), self)
        self.lbl_content_dir.setFixedWidth(135)
        self.lbl_content_dir.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        row.addWidget(self.lbl_content_dir)
        self.txt_content = QtWidgets.QLineEdit(self._cfg.get("content_dir", ""), self)
        self.txt_content.setFixedHeight(26)
        row.addWidget(self.txt_content, stretch=1)
        self.btn_browse = QtWidgets.QPushButton(tr("tree_btn_browse"), self)
        self.btn_browse.setFixedSize(65, 26)
        self.btn_browse.clicked.connect(self._browse_content)
        row.addWidget(self.btn_browse)
        box.addLayout(row)

        # 2. 工具栏：设备类型下拉框不独占一行，与操作按钮紧凑排在同一行
        tools = QtWidgets.QHBoxLayout()
        tools.setSpacing(6)

        self.lbl_type = QtWidgets.QLabel(tr("pub_eq_type_label", "设备类型:"), self)
        tools.addWidget(self.lbl_type)

        self.combo_type = QtWidgets.QComboBox(self)
        self.combo_type.setFixedHeight(26)
        for label, part_type, part_sub in EQUIPMENT_TYPE_CHOICES:
            self.combo_type.addItem(label, (part_type, part_sub) if part_type else None)
        self.combo_type.currentIndexChanged.connect(self._fill_table)
        tools.addWidget(self.combo_type)

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
        self.btn_check_unpublished.setToolTip("勾选所有尚未发布且可正常发布的设备")
        self.btn_check_unpublished.clicked.connect(self._check_unpublished)
        tools.addWidget(self.btn_check_unpublished)

        tools.addStretch()

        self.txt_search = QtWidgets.QLineEdit(self)
        self.txt_search.setFixedHeight(26)
        self.txt_search.setPlaceholderText("实时过滤设备名称或说明...")
        self.txt_search.textChanged.connect(lambda _text: self._search_timer.start())
        tools.addWidget(self.txt_search, stretch=1)

        self.btn_reload = QtWidgets.QPushButton(tr("pub_btn_reload", "重新扫描"), self)
        self.btn_reload.setFixedHeight(26)
        self.btn_reload.clicked.connect(self.reload_scripts)
        tools.addWidget(self.btn_reload)

        self.lbl_count = QtWidgets.QLabel("", self)
        tools.addWidget(self.lbl_count)
        box.addLayout(tools)

        # 3. 操作栏：发布与移除统一放在表格上方
        action_bar = make_action_bar()
        self.lbl_action_hint = QtWidgets.QLabel(
            "发布生成 .peqx 设备模板；移除只删除已发布模板，不动脚本", self)
        self.lbl_action_hint.setObjectName("actionHint")
        action_bar.addWidget(self.lbl_action_hint)
        action_bar.addStretch()
        self.btn_run = make_action_button(
            tr("pub_eq_btn_run", "发布勾选设备"), primary=True, min_width=150)
        self.btn_run.clicked.connect(self._publish)
        action_bar.addWidget(self.btn_run)
        self.btn_remove = make_action_button(
            tr("pub_eq_btn_remove", "移除已发布设备"), danger=True, min_width=150)
        self.btn_remove.clicked.connect(self._remove_published)
        action_bar.addWidget(self.btn_remove)
        box.addLayout(action_bar)

        # 4. 设备明细列表 (第 2 列明确展示中文设备大类与子分类)
        self.table = QtWidgets.QTableWidget(0, 5, self)
        self.table.setHorizontalHeaderLabels([
            tr("pub_th_check"), tr("pub_th_name"), tr("pub_th_category", "设备类别 (大类·子类)"),
            tr("pub_eq_th_target", "目标设备模板"), tr("pub_th_desc"),
        ])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        head = self.table.horizontalHeader()
        for col in range(4):
            head.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeToContents)
        head.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        box.addWidget(self.table, stretch=1)

        # 5. 发布输出日志
        self.log = QtWidgets.QPlainTextEdit(self)
        self.log.setFixedHeight(85)
        self.log.setReadOnly(True)
        box.addWidget(self.log)

    def retranslate_ui(self):
        from .i18n import tr
        if hasattr(self, "lbl_content_dir"):
            self.lbl_content_dir.setText(tr("cat_lbl_content_dir"))
        if hasattr(self, "btn_browse"):
            self.btn_browse.setText(tr("tree_btn_browse"))
        if hasattr(self, "lbl_type"):
            self.lbl_type.setText(tr("pub_eq_type_label", "设备类型:"))
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
            self.btn_run.setText(tr("pub_eq_btn_run", "发布勾选设备"))
        if hasattr(self, "btn_remove"):
            self.btn_remove.setText(tr("pub_eq_btn_remove", "移除已发布设备"))
        if hasattr(self, "table"):
            self.table.setHorizontalHeaderLabels([
                tr("pub_th_check"), tr("pub_th_name"), tr("pub_th_group"),
                tr("pub_eq_th_target", "目标设备模板"), tr("pub_th_desc"),
            ])

    def reload_scripts(self):
        """只收设备脚本：非 equipment 一律不列。

        扫描+解析放到后台线程，避免脚本多时切换 Tab 假死。
        """
        if self._scan_task is not None and self._scan_task.is_running():
            self._scan_task.cancel()
        self._scan_gen += 1
        gen = self._scan_gen
        self.lbl_count.setText(tr("pub_loading", "正在扫描脚本..."))
        self.btn_reload.setEnabled(False)
        root = self._scripts_root
        self._scan_task = ThreadTask(
            lambda progress, token: self._scan_worker(root, gen, progress, token),
            parent=self, name="equipment-script-scan")
        self._scan_task.progress.connect(self._on_scan_progress)
        self._scan_task.finished.connect(self._on_scan_finished)
        self._scan_task.failed.connect(self._on_scan_failed)
        self._scan_task.start()

    def _scan_worker(self, root, gen, progress, token):
        jobs = []
        for path in iter_scripts(root):
            token.check()
            job = inspect_script(path, auto_generate_sizes=False)
            if (job.get("domain") or "") != "equipment":
                continue
            # 没有 @activate(Group=...) 的脚本不是可发布构件，直接不列
            if not (job.get("group") or "").strip():
                continue
            jobs.append(job)
            if len(jobs) % 20 == 0:
                progress("正在扫描设备脚本... 已解析 %d 个" % len(jobs))
        # 优化排序：根据 分类 (Group) + 名称 (stem) 升序排列
        jobs.sort(key=lambda j: (
            (j.get("group") or "ZZZ").strip().upper(),
            (j.get("stem") or "").strip().upper()
        ))
        return gen, jobs

    def _on_scan_progress(self, text):
        self.lbl_count.setText(str(text))

    def _on_scan_finished(self, result):
        gen, jobs = result
        if gen != self._scan_gen:
            return
        self._loaded = True
        self._jobs = jobs
        self._job_map = {job["path"]: job for job in jobs}
        ready = sum(1 for j in jobs if not j["skip_reason"])
        self.lbl_count.setText("可发布 %d / %d" % (ready, len(jobs)))
        self.btn_reload.setEnabled(True)
        self._fill_table()
        self._scan_task = None

    def _on_scan_failed(self, detail):
        if self.sender() is not self._scan_task:
            return
        self.lbl_count.setText("设备脚本扫描失败")
        self.btn_reload.setEnabled(True)
        self.log.appendPlainText("设备脚本扫描失败:\n" + detail)
        self._scan_task = None

    @staticmethod
    def _published_equipment(content):
        """一次 listdir 得到 equipment/ 下全部 .peqx，避免逐行 isfile。"""
        eq_dir = os.path.join(content, "equipment") if content else ""
        if not eq_dir or not os.path.isdir(eq_dir):
            return set()
        try:
            return {fn.lower() for fn in os.listdir(eq_dir)
                    if fn.lower().endswith(".peqx")}
        except OSError:
            return set()

    def _fill_table(self):
        if not hasattr(self, "table"):
            return
        content = self.txt_content.text().strip()
        from PySide6 import QtGui
        color_published = QtGui.QColor("#2A704E")
        color_unpublished = QtGui.QColor("#1F2933")
        published_files = self._published_equipment(content)

        sel_type = self.combo_type.currentData()
        search_kw = self.txt_search.text().strip().lower() if hasattr(self, "txt_search") else ""
        display_jobs = []
        for job in self._jobs:
            resolved = resolve_equipment_type(job)
            if sel_type and (sel_type[0] != resolved[0] or (sel_type[1] and sel_type[1] != resolved[1])):
                continue
            if search_kw:
                haystack = " ".join([
                    job.get("stem") or "", job.get("group") or "",
                    job.get("tooltip_short") or "",
                ]).lower()
                if search_kw not in haystack:
                    continue
            display_jobs.append((job, resolved))

        self.table.setUpdatesEnabled(False)
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.table.setRowCount(len(display_jobs))

        for i, (job, resolved) in enumerate(display_jobs):
            stem_name = job.get("stem", "")
            target = os.path.join(content, "equipment", stem_name + ".peqx")
            is_pub = (stem_name + ".peqx").lower() in published_files

            cell = QtWidgets.QTableWidgetItem()
            cell.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            cell.setCheckState(QtCore.Qt.Unchecked)
            cell.setData(QtCore.Qt.UserRole, job["path"])
            self.table.setItem(i, 0, cell)

            name_item = QtWidgets.QTableWidgetItem(stem_name)
            if is_pub:
                name_item.setForeground(color_published)
            self.table.setItem(i, 1, name_item)

            # 第 2 列：清晰展示中文设备大类与细分类别 (如 '泵 · 离心泵')
            type_label = get_equipment_type_display_label(resolved[0], resolved[1])
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(type_label))

            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(target))

            if is_pub:
                status_prefix = "【已发布】"
            else:
                status_prefix = "【未发布】"

            raw_desc = job["skip_reason"] or job.get("tooltip_short") or "就绪"
            detail_item = QtWidgets.QTableWidgetItem(f"{status_prefix} {raw_desc}")
            if is_pub:
                detail_item.setForeground(color_published)
            else:
                detail_item.setForeground(color_unpublished)
            self.table.setItem(i, 4, detail_item)
        self.table.blockSignals(False)
        self.table.setUpdatesEnabled(True)

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
        """一键勾选未发布且可发布的设备。"""
        published = self._published_equipment(self.txt_content.text().strip())
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            job = self._job_by_path(item.data(QtCore.Qt.UserRole))
            if not job or job.get("skip_reason"):
                item.setCheckState(QtCore.Qt.Unchecked)
                continue
            stem = (job.get("stem") or "").strip()
            item.setCheckState(
                QtCore.Qt.Unchecked if (stem + ".peqx").lower() in published
                else QtCore.Qt.Checked)

    def _selected_paths(self):
        return [self.table.item(r, 0).data(QtCore.Qt.UserRole)
                for r in range(self.table.rowCount())
                if self.table.item(r, 0).checkState() == QtCore.Qt.Checked]

    def _browse_content(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择 CPak Common", self.txt_content.text())
        if folder:
            self.txt_content.setText(folder)
            save_catalog_config({"content_dir": folder})
            self._fill_table()

    def _publish(self):
        paths = self._selected_paths()
        if not paths:
            self.log.appendPlainText("请先勾选至少一个要发布的设备脚本。")
            return
        content = self.txt_content.text().strip()
        if not content:
            self.log.appendPlainText("请填写 CPak Common 内容目录。")
            return
        save_catalog_config({
            "content_dir": content,
            "write_preview": True,
        })

        equip_type = self.combo_type.currentData()
        self.btn_run.setEnabled(False)
        self.log.clear()

        win = self.window()
        if hasattr(win, "_begin_loading"):
            win._begin_loading(f"正在打包发布 {len(paths)} 个设备模板 (.peqx)...")
        # 发布与设备预览图都在独立子进程里完成，避免 OCC 离屏视口在线程里闪退。
        self._publish_task = PublishProcess(
            paths, content, include_equipment=True,
            auto_generate_sizes=False, equipment_type=equip_type,
            write_preview=True, parent=self)
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

        self.btn_run.setEnabled(True)
        if hasattr(win, "_end_loading"):
            win._end_loading(f"设备发布完成 (成功 {ok}, 失败 {bad})")
        self._fill_table()
        self._publish_task = None

    def _on_publish_failed(self, detail):
        self.log.appendPlainText("设备发布中断:\n" + detail)
        self.btn_run.setEnabled(True)
        win = self.window()
        if hasattr(win, "_end_loading"):
            win._end_loading("设备发布中断")
        self._publish_task = None

    def _remove_targets(self):
        """勾选优先，其次当前多选行；只返回确实存在的 .peqx 模板。"""
        content = self.txt_content.text().strip()
        rows = set()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == QtCore.Qt.Checked:
                rows.add(row)
        if not rows:
            sm = self.table.selectionModel()
            if sm is not None:
                rows = {ix.row() for ix in sm.selectedRows()}
        targets = []
        for row in sorted(rows):
            item = self.table.item(row, 0)
            job = self._job_by_path(item.data(QtCore.Qt.UserRole)) if item else None
            if not job:
                continue
            stem = (job.get("stem") or "").strip()
            peqx = os.path.join(content, "equipment", stem + ".peqx")
            if os.path.isfile(peqx):
                targets.append((stem, peqx))
        return targets

    def _remove_published(self):
        targets = self._remove_targets()
        if not targets:
            QtWidgets.QMessageBox.information(
                self, "移除已发布设备",
                "请先勾选或选中已经发布的设备行（未发布的行会被忽略）。")
            return
        if self._remove_task is not None and self._remove_task.is_running():
            QtWidgets.QMessageBox.information(self, "正在处理", "上一个移除任务尚未完成，请稍候。")
            return

        names = "、".join([name for name, _path in targets[:8]])
        if len(targets) > 8:
            names += " 等共 %d 个设备" % len(targets)
        ans = QtWidgets.QMessageBox.question(
            self, "确认移除已发布设备",
            "确定要删除以下 %d 个已发布设备模板 (.peqx) 吗？\n\n【%s】\n\n"
            "设备脚本和 CustomScripts 文件会保留，可随时重新发布。" % (len(targets), names),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if ans != QtWidgets.QMessageBox.Yes:
            return

        content = self.txt_content.text().strip()
        self.btn_run.setEnabled(False)
        self.btn_remove.setEnabled(False)
        win = self.window()
        if hasattr(win, "_begin_loading"):
            win._begin_loading("正在移除已发布设备模板...")

        def _work(progress, token):
            removed = 0
            rows = 0
            errors = []
            for i, (stem, peqx) in enumerate(targets, 1):
                token.check()
                progress((i, len(targets), stem))
                try:
                    out = delete_published_item(
                        content_dir=content,
                        script_name=stem,
                        catalog_path=peqx,
                        remove_custom_script_files=False,
                    )
                    if out.get("ok"):
                        removed += 1
                        rows += out.get("deleted_rows", 0)
                    else:
                        errors.append("%s: 未找到已发布模板" % stem)
                except Exception as exc:
                    errors.append("%s: %s" % (stem, exc))
            return {"removed": removed, "rows": rows, "errors": errors}

        self._remove_task = ThreadTask(_work, parent=self, name="equipment-remove")
        self._remove_task.progress.connect(self._on_remove_progress)
        self._remove_task.finished.connect(self._on_remove_finished)
        self._remove_task.failed.connect(self._on_remove_failed)
        self._remove_task.start()

    def _on_remove_progress(self, payload):
        i, total, stem = payload
        self.log.appendPlainText("正在移除设备 %d/%d: %s" % (i, total, stem))

    def _on_remove_finished(self, summary):
        self._remove_task = None
        self.btn_run.setEnabled(True)
        self.btn_remove.setEnabled(True)
        win = self.window()
        removed = summary.get("removed", 0)
        errors = summary.get("errors") or []
        if hasattr(win, "_end_loading"):
            win._end_loading("已移除 %d 个设备模板" % removed)
        self.log.appendPlainText("移除完成：成功 %d 个设备模板。" % removed)
        if errors:
            self.log.appendPlainText("\n".join(errors[:10]))
            QtWidgets.QMessageBox.warning(self, "部分移除失败", "\n".join(errors[:10]))
        self._fill_table()

    def _on_remove_failed(self, detail):
        self._remove_task = None
        self.btn_run.setEnabled(True)
        self.btn_remove.setEnabled(True)
        win = self.window()
        if hasattr(win, "_end_loading"):
            win._end_loading("移除设备失败")
        self.log.appendPlainText("移除设备失败:\n" + detail)

    def shutdown(self):
        if self._scan_task is not None:
            self._scan_task.stop(3000)
            self._scan_task = None
        if self._publish_task is not None:
            if not self._publish_task.wait(60000):
                self._publish_task.stop(3000)
            self._publish_task = None
        if self._remove_task is not None:
            self._remove_task.stop(5000)
            self._remove_task = None
