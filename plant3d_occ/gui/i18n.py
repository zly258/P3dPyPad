# -*- coding: utf-8 -*-
"""Plant 3D OCC 独立工作台双语 (中/英) 本地化国际化 (i18n) 引擎。

支持：
1. 默认按操作系统区域自动匹配语言 (中文系统使用 zh_CN, 其余默认 en_US)；
2. 用户在界面手动切换并持久化保存至 ~/.plant3d_occ_catalog_config.json；
3. 全界面动态刷新 (标题栏、工具栏按钮、表头、下拉列表、状态与工程提示)。
"""

import json
import locale
import os
from typing import Callable, Dict, List, Optional
from PySide6 import QtCore

CONFIG_FILE = os.path.expanduser("~/.plant3d_occ_catalog_config.json")

# 语言定义
LANG_AUTO = "auto"
LANG_ZH = "zh"
LANG_EN = "en"

_CURRENT_LANG = LANG_ZH
_LISTENERS: List[Callable[[str], None]] = []
_QT_TRANSLATORS: List[QtCore.QTranslator] = []


def apply_qt_default_translations(lang: Optional[str] = None) -> None:
    """根据当前语言，动态加载 Qt 官方标准翻译文件 (qtbase_zh_CN.qm, qt_zh_CN.qm 等)。

    彻底实现 QMessageBox (Ok/Cancel/Yes/No/Save/Discard)、QFileDialog (Open/Save/Cancel) 等所有 PySide 默认组件语言原生自动切换，
    完全基于 Qt 国际化翻译机制，杜绝任何硬编码替换！
    """
    app = QtCore.QCoreApplication.instance()
    if app is None:
        return

    global _QT_TRANSLATORS
    for t in _QT_TRANSLATORS:
        try:
            app.removeTranslator(t)
        except Exception:
            pass
    _QT_TRANSLATORS = []

    target_lang = lang or _CURRENT_LANG
    if target_lang == LANG_ZH:
        trans_dir = QtCore.QLibraryInfo.path(QtCore.QLibraryInfo.LibraryPath.TranslationsPath)
        for qm_name in ("qtbase_zh_CN.qm", "qt_zh_CN.qm"):
            qm_path = os.path.join(trans_dir, qm_name)
            if os.path.isfile(qm_path):
                tr_inst = QtCore.QTranslator(app)
                if tr_inst.load(qm_path):
                    app.installTranslator(tr_inst)
                    _QT_TRANSLATORS.append(tr_inst)


def detect_system_language() -> str:
    """检测当前操作系统首选语言。"""
    try:
        sys_loc = QtCore.QLocale.system().name().lower()
        if sys_loc.startswith("zh"):
            return LANG_ZH
    except Exception:
        pass

    try:
        def_loc, _ = locale.getdefaultlocale()
        if def_loc and def_loc.lower().startswith("zh"):
            return LANG_ZH
    except Exception:
        pass

    return LANG_EN


def load_configured_language() -> str:
    """从本地配置文件读取语言偏好；若未设置或为 auto，则返回自动探测的系统语言。"""
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as fp:
                cfg = json.load(fp)
            if isinstance(cfg, dict):
                saved = cfg.get("ui_language")
                if saved in (LANG_ZH, LANG_EN):
                    return saved
                if saved == LANG_AUTO:
                    return detect_system_language()
        except Exception:
            pass
    return detect_system_language()


def save_configured_language(lang: str) -> None:
    """持久化保存语言偏好至配置文件。"""
    cfg = {}
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as fp:
                cfg = json.load(fp)
            if not isinstance(cfg, dict):
                cfg = {}
        except Exception:
            cfg = {}
    cfg["ui_language"] = lang
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as fp:
            json.dump(cfg, fp, ensure_ascii=False, indent=2)
    except Exception:
        pass


def current_language() -> str:
    return _CURRENT_LANG


def set_current_language(lang: str, persist: bool = True) -> None:
    global _CURRENT_LANG
    resolved = detect_system_language() if lang == LANG_AUTO else lang
    if resolved not in (LANG_ZH, LANG_EN):
        resolved = LANG_ZH
    _CURRENT_LANG = resolved
    apply_qt_default_translations(resolved)
    if persist:
        save_configured_language(lang)
    for cb in list(_LISTENERS):
        try:
            cb(_CURRENT_LANG)
        except Exception:
            pass


def register_language_listener(callback: Callable[[str], None]) -> None:
    if callback not in _LISTENERS:
        _LISTENERS.append(callback)


# 初始化当前语言
_CURRENT_LANG = load_configured_language()


# ============================================================================
# 双语词典 (Bilingual Dictionary)
# ============================================================================

STRINGS: Dict[str, Dict[str, str]] = {
    # 窗口标题与导航
    "app_title": {
        "zh": "AutoCAD Plant 3D OCC 参数化构件设计工作台",
        "en": "AutoCAD Plant 3D OCC Parametric Component Design Workbench",
    },
    "tab_browse": {"zh": "1. 目录浏览", "en": "1. Script Browser"},
    "tab_edit": {"zh": "2. 脚本调试", "en": "2. Script Editor"},
    "tab_workbench": {"zh": "1. 构件设计工作台", "en": "1. Component Workbench"},
    "tab_catalogs_specs": {"zh": "2. 元件库与项目等级库", "en": "2. Catalogs & Project Specs"},
    "tab_equipment_peqx": {"zh": "3. 设备模板管理 (.peqx)", "en": "3. Equipment Templates (.peqx)"},
    "tab_catalog": {"zh": "3. 已发布库检索与管理", "en": "3. Published Catalogs"},
    # 主窗口五个 Tab：构件设计 / 发布构件 / 发布设备 / 元件库管理 / 等级库管理
    "tab_design": {"zh": "构件设计", "en": "Component Design"},
    "tab_publish_component": {"zh": "发布构件", "en": "Publish Components"},
    "tab_publish_equipment": {"zh": "发布设备", "en": "Publish Equipment"},
    "tab_manage_catalog": {"zh": "元件库管理", "en": "Catalog Manager"},
    "tab_manage_spec": {"zh": "等级库管理", "en": "Spec Manager"},
    "tab_catalog_tip": {
        "zh": "真实检索 .acat / .pcat / .pspc / .peqx 软件库中所有已发布构件与设备",
        "en": "Inspect published parts and equipment in .acat / .pcat / .pspc / .peqx databases",
    },
    "lbl_view_mode": {"zh": "工作台页面:", "en": "Workbench View:"},
    "lbl_no_script": {"zh": "未选脚本", "en": "No Script"},
    "btn_save_code": {"zh": "保存源码 (Ctrl+S)", "en": "Save (Ctrl+S)"},
    "btn_reload": {"zh": "重载", "en": "Reload"},
    "btn_preset": {"zh": "预设...", "en": "Presets..."},
    "lbl_no_preset": {"zh": "无预设表", "en": "No Preset Table"},
    "btn_quick_publish": {"zh": "一键发布当前", "en": "Quick Publish"},
    "btn_quick_publish_tip": {
        "zh": "直接将当前脚本自动生成尺寸表与 PyOCC 3D 外形+标注图并发布入库",
        "en": "Publish current script, auto-generating sizes and PyOCC 3D shape + dimension diagrams",
    },
    "btn_batch_publish": {"zh": "批量发布...", "en": "Batch Publish..."},
    "btn_run": {"zh": "运行建模 (F5)", "en": "Run Model (F5)"},
    "lbl_spec": {"zh": "规格:", "en": "Preset:"},
    "btn_reset_defaults": {"zh": "还原默认", "en": "Reset Defaults"},
    "code_header": {
        "zh": " Python 脚本源码 (可直接修改代码，Ctrl+S 保存，F5 运行)",
        "en": " Python Script Source (Ctrl+S to save, F5 to run & render)",
    },
    "lbl_3d_model": {"zh": "3D 实体模型", "en": "3D Solid Model"},
    "lbl_style": {"zh": "显示:", "en": "Style:"},
    "lbl_view": {"zh": "视图:", "en": "View:"},
    "btn_fit": {"zh": "适应窗口", "en": "Fit View"},
    "btn_dim_preview": {"zh": "轴测预览", "en": "Isometric Preview"},
    "btn_dim_preview_tip": {
        "zh": "使用 PyOCC 生成当前构件的轴测预览图；支吊架和设备带尺寸标注，管件等仅着色",
        "en": "Preview current component in isometric view; supports and equipment include dimensions, other parts are shaded only",
    },
    "lbl_language": {"zh": "语言:", "en": "Language:"},
    "lbl_log_title": {"zh": "执行与调试日志", "en": "Execution & Debug Logs"},
    "status_ready": {"zh": "就绪", "en": "Ready"},
    "status_loading": {"zh": "正在加载元件库数据...", "en": "Loading catalog data..."},

    # 视口与显示模式
    "style_shaded": {"zh": "着色", "en": "Shaded"},
    "style_shaded_edges": {"zh": "着色带边", "en": "Shaded with Edges"},
    "style_hidden_line": {"zh": "隐藏线", "en": "Hidden Line"},
    "style_wireframe": {"zh": "线框", "en": "Wireframe"},

    "view_iso": {"zh": "等轴测", "en": "Isometric"},
    "view_front": {"zh": "前视", "en": "Front"},
    "view_rear": {"zh": "后视", "en": "Rear"},
    "view_left": {"zh": "左视", "en": "Left"},
    "view_right": {"zh": "右视", "en": "Right"},
    "view_top": {"zh": "俯视", "en": "Top"},
    "view_bottom": {"zh": "仰视", "en": "Bottom"},

    # 属性网格与文件树
    "grid_prop_name": {"zh": "属性 (参数名)", "en": "Property (Parameter)"},
    "grid_prop_val": {"zh": "取值 (数值/表达式)", "en": "Value (Number/Expr)"},
    "grid_no_param": {"zh": "未定义任何参数 (@param)", "en": "No @param parameters defined"},
    "tree_search_placeholder": {
        "zh": "搜索脚本或型号 (如: 101, clamp, bend)...",
        "en": "Filter script or model (e.g. 101, clamp, bend)...",
    },
    "tree_btn_browse": {"zh": "浏览...", "en": "Browse..."},
    "tree_found_prefix": {"zh": "共找到", "en": "Found"},
    "tree_found_suffix": {
        "zh": "个构件脚本 (单击任意脚本即时查看 3D 外形)",
        "en": "scripts (click any to view 3D shape)",
    },

    # 已发布库管理页面 (CatalogManagerPage)
    # 设备模板独立管理 (EquipmentManagerPage)
    "eq_cfg_group": {
        "zh": "设备模板库与脚本路径 (Autodesk PD1746 规范)",
        "en": "Equipment Package & Script Configuration (Autodesk PD1746)",
    },
    "eq_lbl_peqx_dir": {"zh": "设备模板目录 (equipment):", "en": "Equipment Dir (equipment):"},
    "eq_lbl_custom_dir": {"zh": "自定义脚本目录 (CustomScripts):", "en": "CustomScripts Dir:"},
    "eq_filter_placeholder": {"zh": "输入设备名称、描述或类型实时检索...", "en": "Search equipment by name, description or type..."},
    "eq_btn_refresh": {"zh": "刷新设备列表", "en": "Refresh Equipment"},
    "eq_btn_publish": {"zh": "发布设备为 .peqx 模板包...", "en": "Publish Equipment .peqx..."},
    "eq_th_template": {"zh": "设备模板名称", "en": "Template Name"},
    "eq_th_display": {"zh": "显示名称", "en": "Display Name"},
    "eq_th_subtype": {"zh": "设备子类型 (PartSubType)", "en": "Equipment Sub-Type"},
    "eq_th_param_cnt": {"zh": "参数数", "en": "Params"},
    "eq_th_port_cnt": {"zh": "管嘴端口", "en": "Ports"},
    "eq_th_script_status": {"zh": "关联 Python 脚本", "en": "Linked Python Script"},
    "eq_det_title": {"zh": "设备模板详情 (EquipmentType.xml & 预览图)", "en": "Equipment Details (EquipmentType.xml & Preview)"},
    "eq_btn_load_3d": {"zh": "在 3D 视口加载调试", "en": "Load in 3D View"},
    "eq_btn_delete": {"zh": "从设备库中删除", "en": "Remove from Equipment"},
    "eq_th_pname": {"zh": "参数代号", "en": "Param Name"},
    "eq_th_ptype": {"zh": "类型 (d/d0/a/r/b)", "en": "Type (d/d0/a/r/b)"},
    "eq_th_pdefault": {"zh": "默认值", "en": "Default Value"},
    "eq_th_pdesc": {"zh": "参数说明 / 提示", "en": "Description / Tooltip"},
    "cat_cfg_group": {
        "zh": "元件库与设备库路径配置 (CPak Common)",
        "en": "Content && Catalog Path Configuration (CPak Common)",
    },
    "cat_lbl_content_dir": {"zh": "CPak Common 目录:", "en": "CPak Common Dir:"},
    "cat_txt_placeholder": {
        "zh": "下拉选择已安装版本的 CPak Common，或手动填写路径...",
        "en": "Select CPak Common folder under AutoCAD Plant 3D Content...",
    },
    "cat_btn_save_cfg": {"zh": "保存配置", "en": "Save Config"},
    "cat_btn_db_status": {"zh": "库文件状态...", "en": "Catalog Status..."},
    "cat_chk_auto_sizes": {
        "zh": "缺失 CSV 时自动推导多规格尺寸 (--auto-sizes)",
        "en": "Auto-infer size matrix when CSV is missing (--auto-sizes)",
    },
    "cat_chk_preview": {
        "zh": "自动生成 PyOCC 3D 外形 + 轴测尺寸标注图",
        "en": "Auto-generate PyOCC 3D Shape + CAD Dimension Diagrams",
    },
    "cat_lbl_domain": {"zh": "构件分类:", "en": "Category:"},
    "cat_opt_all": {"zh": "全部类别 (ALL)", "en": "All Categories (ALL)"},
    "cat_opt_support": {"zh": "支吊架 (Support .acat)", "en": "Supports (Support .acat)"},
    "cat_opt_piping": {"zh": "管道/管件/阀门 (Piping .pcat)", "en": "Piping/Fittings/Valves (.pcat)"},
    "cat_opt_instrument": {"zh": "仪表 (Instrument .pcat)", "en": "Instrumentation (.pcat)"},
    "cat_opt_equipment": {"zh": "设备与泵 (Equipment .peqx)", "en": "Equipment & Pumps (.peqx)"},
    "cat_opt_actuator": {"zh": "执行机构 (Actuator .acat)", "en": "Actuators (.acat)"},
    "cat_opt_nozzle": {"zh": "管嘴/人孔 (Nozzle .acat)", "en": "Nozzles/Manholes (.acat)"},
    "cat_search_placeholder": {
        "zh": "输入脚本名、描述或元件库文件名实时检索...",
        "en": "Search by script name, description or catalog file...",
    },
    "cat_lbl_scope": {"zh": "元件库:", "en": "Catalog:"},
    "cat_scope_all": {"zh": "全部元件库（较慢）", "en": "All Catalogs (slow)"},
    "spec_lbl_scope": {"zh": "索引范围:", "en": "Index Scope:"},
    "spec_scope_all": {"zh": "全部等级库（索引较慢）", "en": "All Specs (slow index)"},
    "spec_scope_tip": {"zh": "只影响后台构件成员索引的扫描范围；左侧列表始终显示全部等级库",
                       "en": "Only controls the background membership index scan; the list always shows all specs"},
    "cat_btn_refresh": {"zh": "从软件库刷新", "en": "Refresh Catalogs"},
    "cat_btn_batch_pub": {"zh": "批量发布脚本/设备...", "en": "Batch Publish..."},
    "cat_btn_batch_delete": {"zh": "批量从元件库移除", "en": "Batch Remove Parts"},
    # 表头
    "th_select": {"zh": "勾选", "en": "Select"},
    "th_icon": {"zh": "图标", "en": "Icon"},
    "th_script_name": {"zh": "构件名称", "en": "Component Name"},
    "th_category": {"zh": "类别", "en": "Category"},
    "th_sizes": {"zh": "规格数", "en": "Sizes"},
    "th_spec_status": {"zh": "所在等级库", "en": "Specs Containing"},
    "th_catalog_file": {"zh": "所属库文件", "en": "Catalog / Package"},
    "th_sizes": {"zh": "库内规格数", "en": "Sizes"},
    "th_in_spec": {"zh": "等级库数", "en": "In Specs"},
    "th_nd_range": {"zh": "管径范围 / 类型", "en": "Size Range / Type"},
    "th_status": {"zh": "状态", "en": "Status"},

    # 详情抽屉
    "det_no_selection": {"zh": "未选择构件", "en": "No Part Selected"},
    "det_btn_load_3d": {"zh": "在 3D 视口加载调试", "en": "Load in 3D View"},
    "det_btn_republish": {"zh": "重新发布更新", "en": "Republish"},
    "det_btn_delete": {"zh": "从元件库移除", "en": "Remove from Catalog"},
    "det_lbl_target_spec": {"zh": "目标等级库:", "en": "Target Spec:"},
    "cat_lbl_project_dir": {"zh": "工程项目目录:", "en": "Project Root Dir:"},
    "cat_project_dir_placeholder": {
        "zh": "例如 D:\\zTEMP\\Project 1 (自动识别 等级库工作表 / Spec Sheets)...",
        "en": "e.g. D:\\zTEMP\\Project 1 (Auto-resolves Spec Sheets)...",
    },
    "cat_lbl_project_spec_dir": {"zh": "项目等级库工作表 (*.pspc):", "en": "Project Spec Sheets Dir (*.pspc):"},
    "cat_project_spec_placeholder": {
        "zh": "选择具体项目下的 等级库工作表 / Spec Sheets 目录...",
        "en": "Select project's Spec Sheets directory...",
    },
    "cat_lbl_current_spec": {"zh": "当前项目等级库:", "en": "Project Spec:"},
    "cat_btn_new_spec": {"zh": "新建等级库...", "en": "New Spec..."},
    "cat_btn_open_editor": {"zh": "规格编辑器", "en": "Specs Editor"},
    "cat_btn_open_editor_tip": {
        "zh": "启动 AutoCAD Plant 3D 官方 SpecsAndCatalogsEditor.exe",
        "en": "Launch AutoCAD Plant 3D SpecsAndCatalogsEditor.exe",
    },
    "cat_btn_open_in_editor": {"zh": "在官方编辑器中打开", "en": "Open in Specs Editor"},
    "det_btn_add_spec": {"zh": "加入项目等级库", "en": "Add to Project Spec"},
    "det_btn_remove_spec": {"zh": "从项目等级库移除", "en": "Remove from Project Spec"},
    "pub_chk_sync_spec": {"zh": "发布后同步加入项目等级库", "en": "Sync into project spec upon publishing"},
    "pub_lbl_target_spec": {"zh": "目标项目等级库:", "en": "Target Project Spec:"},
    "th_spec_status": {"zh": "所在等级库", "en": "Specs Containing"},
    "det_spec_header": {
        "zh": "软件库内真实存储规格明细 (EngineeringItems / EquipmentType.xml):",
        "en": "Database Specification Rows (EngineeringItems / EquipmentType.xml):",
    },
    "det_th_pnpid": {"zh": "PnPID", "en": "PnPID"},
    "det_th_nd": {"zh": "公称直径 ND", "en": "Nominal Diameter ND"},
    "det_th_od": {"zh": "管外径 OD", "en": "Matching Pipe OD"},
    "det_th_code": {"zh": "编码 / 参数名", "en": "Item Code / Param"},
    "det_th_param_def": {
        "zh": "几何参数定义 (ContentGeometryParamDefinition)",
        "en": "Geometry Parameter Definition (ContentGeometryParamDefinition)",
    },

    # 批量发布对话框 (PublishDialog)
    "pub_dialog_title": {
        "zh": "自动发布到元件库 / 等级库 / 设备模板库 (.acat / .pcat / .pspc / .peqx)",
        "en": "Auto-Publish to Catalogs, Specs & Equipment Packages (.acat / .pcat / .pspc / .peqx)",
    },
    "pub_hint": {
        "zh": (
            "• 支吊架元件库写入 SUPPORTS Catalog metric.acat；等级跟界面选择走（如 PipeSupports）。没选等级时才回退 PipeSupportsSpec\n"
            "• 管件/阀门/仪表可写入已有或新建的元件库（放在 CPak Common），等级可新建或加入已有\n"
            "• 设备与泵 (Equipment) → 自动打包生成 CPak Common/equipment/<脚本名>.peqx 模板包 + CustomScripts/<脚本名>.py\n"
            "• 自动生成 PyOCC 3D 外形 + 轴测字母尺寸标注图 (640/200/64/32px) 及 CustomScripts 注册 XML。"
        ),
        "en": (
            "• Support → Auto-written to SUPPORTS Catalog metric.acat\n"
            "• Piping / Fittings / Valves → Auto-written to CustomParts Metric Catalog.pcat  |  Instrumentation → Instrumentation Metric.pcat\n"
            "• Equipment & Pumps → Auto-packaged into CPak Common/equipment/<name>.peqx + CustomScripts/<name>.py\n"
            "• Auto-generates PyOCC 3D Shaded Shape + CAD Isometric Dimension Diagrams (640/200/64/32px) and CustomScripts XML."
        ),
    },
    # 构件真实类型
    "type_all": {"zh": "全部类型 (ALL)", "en": "All Types (ALL)"},
    "type_support": {"zh": "支吊架 (Support)", "en": "Support (Support)"},
    "type_elbow": {"zh": "弯头 (Elbow)", "en": "Elbow (Elbow)"},
    "type_tee": {"zh": "三通 (Tee)", "en": "Tee (Tee)"},
    "type_reducer": {"zh": "异径管 (Reducer)", "en": "Reducer (Reducer)"},
    "type_cross": {"zh": "四通 (Cross)", "en": "Cross (Cross)"},
    "type_valve": {"zh": "阀门 (Valve)", "en": "Valve (Valve)"},
    "type_flange": {"zh": "法兰 (Flange)", "en": "Flange (Flange)"},
    "type_blind": {"zh": "盲板 (Blind)", "en": "Blind (Blind)"},
    "type_cap": {"zh": "管帽/封头 (Cap)", "en": "Cap (Cap)"},
    "type_instrument": {"zh": "仪表 (Instrument)", "en": "Instrument (Instrument)"},
    "type_pipe": {"zh": "管段/管道 (Pipe)", "en": "Pipe (Pipe)"},

    "pub_filter_ready": {"zh": "只看可发布脚本", "en": "Publishable scripts only"},
    "pub_filter_equipment": {"zh": "只看设备与泵 (Equipment .peqx)", "en": "Equipment & Pumps only (.peqx)"},
    "pub_filter_support": {"zh": "只看支吊架 (Support .acat)", "en": "Supports only (.acat)"},
    "pub_filter_all": {"zh": "全部脚本", "en": "All scripts"},
    "pub_btn_check_all": {"zh": "全选", "en": "Select All"},
    "pub_btn_check_none": {"zh": "全不选", "en": "Deselect All"},
    "pub_btn_check_invert": {"zh": "反选", "en": "Invert"},
    "pub_btn_check_unpublished": {"zh": "一键勾选未发布", "en": "Check Unpublished"},
    "pub_eq_btn_remove": {"zh": "移除已发布设备", "en": "Remove Published Equipment"},
    "spec_lbl_catalog": {"zh": "元件库:", "en": "Catalog:"},
    "spec_lbl_spec": {"zh": "等级库:", "en": "Spec:"},
    "spec_lbl_project_dir": {"zh": "项目路径:", "en": "Project:"},
    "spec_project_placeholder": {
        "zh": "选择 Plant 3D 项目根目录或等级库工作表目录...",
        "en": "Select a Plant 3D project root or Spec Sheets directory...",
    },
    "spec_search_placeholder": {"zh": "搜索脚本名称或类别...", "en": "Search script or category..."},
    "spec_btn_add": {"zh": "批量添加到等级库", "en": "Add Checked to Spec"},
    "spec_btn_remove": {"zh": "从等级库移除", "en": "Remove from Spec"},
    "spec_th_catalog_rows": {"zh": "元件库规格数", "en": "Catalog Rows"},
    "spec_th_spec_status": {"zh": "等级库状态", "en": "Spec Status"},
    "pub_loading": {"zh": "正在扫描脚本...", "en": "Scanning scripts..."},
    "pub_th_check": {"zh": "勾选", "en": "Select"},
    "pub_th_name": {"zh": "脚本名称", "en": "Script Name"},
    "pub_th_group": {"zh": "Group 类别", "en": "Group Category"},
    "pub_th_target": {"zh": "目标元件库 / 设备模板", "en": "Target Catalog / Package"},
    "pub_th_sizes": {"zh": "规格数", "en": "Sizes"},
    "pub_th_desc": {"zh": "说明 / 尺寸来源", "en": "Description / Source"},
    "pub_btn_run": {"zh": "开始发布勾选构件", "en": "Publish Selected Parts"},
    "pub_btn_close": {"zh": "关闭", "en": "Close"},
}


def tr(key: str, default: Optional[str] = None) -> str:
    """获取指定 key 在当前语言环境下的文本。"""
    entry = STRINGS.get(key)
    if entry:
        val = entry.get(_CURRENT_LANG)
        if val:
            return val
        val_en = entry.get(LANG_EN)
        if val_en:
            return val_en
    return default if default is not None else key
