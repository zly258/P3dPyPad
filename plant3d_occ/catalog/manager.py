# -*- coding: utf-8 -*-
"""Plant 3D 元件库、等级库与设备库 (.acat / .pcat / .pspc / .peqx) 真实检索、配置与管理引擎。

直接连接并查询 CPak Common 目录下的真实 SQLite 元件库 (.acat / .pcat)、等级库 (.pspc)
以及设备模板包 (equipment/*.peqx) 与 CustomScripts 注册目录，支持：
1. 元件库路径与目标库映射配置持久化；
2. 真实检索所有已发布构件（支持按“仅自定义已发布”与“含系统原厂库”切换、按分类与关键字过滤）；
3. 查询任意已发布构件的全部规格行明细 (ND, OD, ItemCode, 参数定义串) 与高清预览图；
4. 从元件库/等级库/设备库中安全卸载或重新发布指定构件。
"""

import json
import os
import shutil
import sqlite3
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from typing import Dict, List, Optional, Tuple

from .store import PLANT_CONTENT, guid_text, detect_plant_content_dir
from .equipment import get_equipment_type_display_label

CONFIG_FILE = os.path.expanduser("~/.plant3d_occ_catalog_config.json")

# ---- 进程内扫描缓存 --------------------------------------------------------
# 元件库 (.acat/.pcat) 的族聚合结果与等级库 (.pspc) 的入库计数按
# (路径, 修改时间, 大小) 缓存：同一进程内重复检索直接命中，不再重复开库。
_FAMILY_ROWS_CACHE: Dict[tuple, list] = {}
_SPEC_COUNT_CACHE: Dict[tuple, Dict[str, int]] = {}


def _db_stamp(path: str) -> tuple:
    """数据库文件的缓存键：路径 + 修改时间 + 大小；文件变更后自动失效。"""
    try:
        st = os.stat(path)
        return (os.path.normcase(os.path.abspath(path)), int(st.st_mtime_ns), st.st_size)
    except OSError:
        return (os.path.normcase(os.path.abspath(path)), 0, 0)


def clear_catalog_caches():
    """写库（删除/加入/新建）后调用，丢弃本进程内的检索缓存。"""
    _FAMILY_ROWS_CACHE.clear()
    _SPEC_COUNT_CACHE.clear()


def _read_catalog_family_rows(cat_path: str) -> list:
    """读取元件库每族聚合行；结果按文件指纹缓存，重复检索零开销。"""
    key = _db_stamp(cat_path)
    cached = _FAMILY_ROWS_CACHE.get(key)
    if cached is not None:
        return cached
    rows: list = []
    try:
        con = sqlite3.connect("file:%s?mode=ro" % cat_path.replace("\\", "/"), uri=True)
        try:
            rows = con.execute(
                "SELECT ContentGeometryTemplate, COUNT(*), "
                "MIN(PartFamilyLongDesc), MIN(ShortDescription), "
                "MIN(NominalDiameter), MAX(NominalDiameter), MIN(NominalUnit), "
                "MIN(ContentGeometryParamDefinition), MIN(PartFamilyId) "
                "FROM EngineeringItems "
                "WHERE ContentGeometryTemplate IS NOT NULL AND ContentGeometryTemplate != '' "
                "GROUP BY ContentGeometryTemplate "
                "ORDER BY ContentGeometryTemplate"
            ).fetchall()
        finally:
            con.close()
    except Exception:
        rows = []
    _FAMILY_ROWS_CACHE[key] = rows
    return rows


def _read_spec_template_counts(sp_path: str) -> Dict[str, int]:
    """读取等级库每构件族的行数 {template_upper: count}，按文件指纹缓存。"""
    key = _db_stamp(sp_path)
    cached = _SPEC_COUNT_CACHE.get(key)
    if cached is not None:
        return cached
    counts: Dict[str, int] = {}
    try:
        con = sqlite3.connect("file:%s?mode=ro" % sp_path.replace("\\", "/"), uri=True)
        try:
            for tpl, cnt in con.execute(
                "SELECT ContentGeometryTemplate, COUNT(*) FROM EngineeringItems "
                "WHERE ContentGeometryTemplate IS NOT NULL AND ContentGeometryTemplate != '' "
                "GROUP BY ContentGeometryTemplate"
            ):
                counts[str(tpl).upper()] = int(cnt)
        finally:
            con.close()
    except Exception:
        counts = {}
    _SPEC_COUNT_CACHE[key] = counts
    return counts


def _unit_kind(unit) -> str:
    """长度单位 -> "metric" / "imperial" / ""（无法判定）。"""
    u = str(unit or "").strip().lower()
    if u in ("mm", "cm", "m"):
        return "metric"
    if u in ("in", "inch", "ft", "foot", "feet"):
        return "imperial"
    return ""


def detect_specs_editor_path() -> str:
    """探测 AutoCAD Plant 3D 官方规格与元件库编辑器 (SpecsAndCatalogsEditor.exe) 的路径。"""
    # 1. 优先读取持久化配置
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as fp:
                saved = json.load(fp).get("editor_path")
                if saved and os.path.isfile(saved):
                    return saved
        except Exception:
            pass

    # 2. 按版本号从新到旧探测 (2026 -> 2018)，默认使用最新版本
    for year in ("2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"):
        cand = rf"C:\Program Files\Autodesk\AutoCAD {year}\PLNT3D\SpecsAndCatalogsEditor.exe"
        if os.path.isfile(cand):
            return cand

    return ""


def launch_specs_editor(file_path: Optional[str] = None, editor_path: Optional[str] = None) -> bool:
    """启动外部 AutoCAD Plant 3D 官方 SpecsAndCatalogsEditor.exe，可选直接打开指定元件库或等级库。"""
    exe = editor_path or detect_specs_editor_path()
    if not exe or not os.path.isfile(exe):
        raise RuntimeError("找不到 SpecsAndCatalogsEditor.exe，请检查 AutoCAD Plant 3D 安装路径或手动配置。")

    args = [exe]
    if file_path and os.path.isfile(file_path):
        args.append(os.path.abspath(file_path))

    try:
        subprocess.Popen(args, close_fds=True)
        return True
    except Exception as exc:
        raise RuntimeError(f"启动 SpecsAndCatalogsEditor 失败: {exc}")


def resolve_project_and_spec_dir(input_path: str) -> Tuple[str, str]:
    """智能解析 AutoCAD Plant 3D 工程项目根目录与等级库工作表目录。

    支持输入形式：
    - 项目根目录，如：D:\\zTEMP\\Project 1 -> 自动探测其子目录 等级库工作表 或 Spec Sheets；
    - 等级库工作表目录，如：D:\\zTEMP\\Project 1\\等级库工作表 -> 自动推导项目根目录为父目录；
    """
    if not input_path:
        return "", ""
    norm = os.path.normpath(input_path.strip())
    if not os.path.exists(norm):
        return norm, norm

    base_name = os.path.basename(norm).lower()

    # 1. 如果用户直接选中的就是工作表目录名，或者该目录下直接包含多个 .pspc 文件
    if base_name in ("等级库工作表", "spec sheets") or any(
        f.lower().endswith(".pspc") for f in os.listdir(norm) if os.path.isfile(os.path.join(norm, f))
    ):
        project_dir = os.path.dirname(norm)
        spec_dir = norm
        return project_dir, spec_dir

    # 2. 如果输入的是项目根目录，智能查找下属子目录
    project_dir = norm
    cand_zh = os.path.join(norm, "等级库工作表")
    if os.path.isdir(cand_zh):
        return project_dir, cand_zh

    cand_en = os.path.join(norm, "Spec Sheets")
    if os.path.isdir(cand_en):
        return project_dir, cand_en

    # 如果均不存在，但包含 Project.xml 或 Piping.dcf 等 Plant 3D 项目特征文件，默认设为 "等级库工作表"
    has_proj_marker = any(
        os.path.isfile(os.path.join(norm, m))
        for m in ("Project.xml", "Metric_Project.xml", "Piping.dcf")
    )
    if has_proj_marker:
        return project_dir, cand_zh

    return project_dir, project_dir


def detect_default_project_dir() -> Tuple[str, str]:
    """探测默认的 Plant 3D 工程项目目录及等级库工作表目录。"""
    # 1. 优先从配置读取
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as fp:
                saved = json.load(fp)
                p_dir = saved.get("project_dir", "")
                ps_dir = saved.get("project_spec_dir", "")
                if p_dir and os.path.isdir(p_dir):
                    p_res, ps_res = resolve_project_and_spec_dir(ps_dir or p_dir)
                    return p_res, ps_res
        except Exception:
            pass

    # 2. 优先测试 D:\zTEMP\Project 1 (常见工程测试目录)
    cand_default = r"D:\zTEMP\Project 1"
    if os.path.isdir(cand_default):
        return resolve_project_and_spec_dir(cand_default)

    # 3. 环境变量 PLANT3D_PROJECT_DIR
    env_p = os.environ.get("PLANT3D_PROJECT_DIR")
    if env_p and os.path.isdir(env_p):
        return resolve_project_and_spec_dir(env_p)

    return "", ""


def detect_default_content_dir() -> str:
    """获取用户指定的 CPak Common 目录。用户可在界面上自由指定并持久化。"""
    # 1. 优先读取用户持久化配置
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as fp:
                saved = json.load(fp).get("content_dir")
                if saved and os.path.isdir(saved):
                    return saved
        except Exception:
            pass

    # 2. 环境变量 (如用户外部显式指定)
    env_dir = os.environ.get("PLANT3D_CONTENT_DIR")
    if env_dir:
        if os.path.isfile(os.path.join(env_dir, "SUPPORTS Catalog metric.acat")):
            return env_dir
        sub = os.path.join(env_dir, "CPak Common")
        if os.path.isdir(sub):
            return sub
        if os.path.isdir(env_dir):
            return env_dir

    # 3. 未指定时按版本探测 C 盘安装目录，而不是留空让用户自己找
    return detect_plant_content_dir()


def load_catalog_config() -> dict:
    """加载元件库与等级库配置。"""
    def_pdir, def_pspec_dir = detect_default_project_dir()
    default_cfg = {
        "content_dir": detect_default_content_dir(),
        "project_dir": def_pdir,
        "project_spec_dir": def_pspec_dir,
        "selected_spec": "CS150.pspc",
        "editor_path": detect_specs_editor_path(),
        "sync_to_project_spec": False,
        "support_catalog": "SUPPORTS Catalog metric.acat",
        "support_spec": "PipeSupportsSpec.pspc",
        "piping_catalog": "CustomParts Metric Catalog.pcat",
        "piping_spec": "CustomParts Metric.pspc",
        "instrument_catalog": "Instrumentation Metric.pcat",
        "instrument_spec": "Instrumentation Metric.pspc",
        "equipment_subdir": "equipment",
        "auto_generate_sizes": True,
        "write_preview": True,
        "validate_before_publish": True,
    }
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as fp:
                saved = json.load(fp)
            if isinstance(saved, dict):
                default_cfg.update(saved)
                if not os.path.isdir(default_cfg.get("content_dir", "")):
                    default_cfg["content_dir"] = detect_default_content_dir()
                if not os.path.isdir(default_cfg.get("project_dir", "")):
                    default_cfg["project_dir"] = def_pdir
                if not os.path.isdir(default_cfg.get("project_spec_dir", "")):
                    default_cfg["project_spec_dir"] = def_pspec_dir
                if not default_cfg.get("editor_path") or not os.path.isfile(default_cfg.get("editor_path", "")):
                    default_cfg["editor_path"] = detect_specs_editor_path()
        except Exception:
            pass
    return default_cfg


def save_catalog_config(cfg: dict) -> dict:
    """保存元件库配置。"""
    merged = load_catalog_config()
    merged.update(cfg or {})
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as fp:
            json.dump(merged, fp, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return merged


def list_catalog_databases(content_dir: str) -> List[dict]:
    """扫描 content_dir 下的所有 .acat / .pcat / .pspc 数据库文件及 equipment 目录状态。"""
    if not content_dir or not os.path.isdir(content_dir):
        return []
    items = []
    for fn in sorted(os.listdir(content_dir)):
        full = os.path.join(content_dir, fn)
        if not os.path.isfile(full):
            continue
        ext = os.path.splitext(fn)[1].lower()
        if ext not in (".acat", ".pcat", ".pspc"):
            continue
        size_kb = round(os.path.getsize(full) / 1024.0, 1)
        row_cnt = 0
        family_cnt = 0
        if os.path.getsize(full) > 0:
            try:
                con = sqlite3.connect(full)
                cur = con.cursor()
                cur.execute(
                    "SELECT COUNT(*), COUNT(DISTINCT ContentGeometryTemplate) "
                    "FROM EngineeringItems WHERE ContentGeometryTemplate IS NOT NULL AND ContentGeometryTemplate != ''"
                )
                r = cur.fetchone()
                if r:
                    row_cnt, family_cnt = int(r[0] or 0), int(r[1] or 0)
                con.close()
            except Exception:
                pass
        items.append({
            "file": fn,
            "path": full,
            "type": "元件库" if ext in (".acat", ".pcat") else "等级库",
            "size_kb": size_kb,
            "families": family_cnt,
            "rows": row_cnt,
        })
    eq_dir = os.path.join(content_dir, "equipment")
    if os.path.isdir(eq_dir):
        peqx_files = [f for f in os.listdir(eq_dir) if f.lower().endswith(".peqx")]
        items.append({
            "file": "equipment/*.peqx",
            "path": eq_dir,
            "type": "设备模板库",
            "size_kb": round(sum(os.path.getsize(os.path.join(eq_dir, f)) for f in peqx_files) / 1024.0, 1),
            "families": len(peqx_files),
            "rows": len(peqx_files),
        })
    return items


def _preview_search_dirs(content_dir: str) -> List[str]:
    """构件预览图的候选目录（含 CustomScripts 的每个子目录）。"""
    here_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    search_dirs = [
        os.path.join(content_dir, "CustomScripts"),
        os.path.join(content_dir, "CPak Common", "CustomScripts"),
        os.path.join(here_root, "test_output"),
        os.path.join(here_root, "cad_renders"),
        os.path.join(here_root, "pyscripts", "rendered_previews"),
        os.path.join(here_root, "pyscripts", "custom_scripts"),
    ]
    cs_root = os.path.join(here_root, "pyscripts", "custom_scripts")
    if os.path.isdir(cs_root):
        try:
            for sub in os.listdir(cs_root):
                sub_p = os.path.join(cs_root, sub)
                if os.path.isdir(sub_p):
                    search_dirs.append(sub_p)
        except OSError:
            pass

    # 去重且保持顺序
    seen = set()
    unique = []
    for d in search_dirs:
        norm = os.path.normcase(os.path.abspath(d))
        if norm in seen:
            continue
        seen.add(norm)
        unique.append(d)
    return unique


class _PreviewIndex(object):
    """一次性列出候选目录中的文件名，之后按文件名 O(1) 命中。

    此前每个构件都要对每个候选目录 listdir + isfile，N 个构件 x M 个目录
    的文件系统遍历是"检索元件库很慢"的主要来源。
    """

    def __init__(self, dirs: List[str]):
        self._dirs = []   # [(dir, {lower_name: full_path})]
        for d in dirs:
            if not d or not os.path.isdir(d):
                continue
            try:
                names = {}
                for fn in os.listdir(d):
                    names.setdefault(fn.lower(), os.path.join(d, fn))
            except OSError:
                continue
            if names:
                self._dirs.append((d, names))
        self._pngs = [
            (d, [(n, p) for n, p in names.items() if n.endswith(".png")])
            for d, names in self._dirs
        ]

    def find(self, candidates: List[str]) -> str:
        """按目录优先、候选名次优先返回第一个存在的非空文件。"""
        for _d, names in self._dirs:
            for cand in candidates:
                p = names.get(cand.lower())
                if p:
                    try:
                        if os.path.getsize(p) > 0:
                            return p
                    except OSError:
                        continue
        return ""

    def find_prefix(self, prefix: str) -> str:
        """模糊兜底：返回第一个以 prefix 开头的有效 png。"""
        prefix = prefix.lower()
        for _d, pngs in self._pngs:
            for name, p in pngs:
                if name.startswith(prefix):
                    try:
                        if os.path.getsize(p) > 0:
                            return p
                    except OSError:
                        continue
        return ""


def _resolve_preview_image(content_dir: str, catalog_file: str, script_name: str,
                           part_family_id_blob=None, preview_index=None) -> str:
    """智能检索构件的带标注工程图或普通预览图。

    策略：优先显示带尺寸标注的大图（_iso_dim / 640 / 600 / 400 / 200 等）；
    若没有标注图，则自动使用普通 3D 轴测预览图（_iso / _views / 200 / 400 / 600 / .png 等）进行坚实兜底。
    """
    index = preview_index or _PreviewIndex(_preview_search_dirs(content_dir))

    # 1. 第一梯队：优先检索带尺寸标注的大图 (iso_dim, 640, 600, 400, 200, dim)
    found = index.find([
        f"{script_name}_iso_dim.png",
        f"{script_name}_640.png",
        f"{script_name}_600.png",
        f"{script_name}_400.png",
        f"{script_name}_200.png",
        f"{script_name}_dim.png",
        f"{script_name}_annotated.png",
    ])
    if found:
        return found

    # 元件库标准 UUID 图标目录检索 (优先 640/600/400/200/64/32)
    if catalog_file and part_family_id_blob:
        stem = os.path.splitext(catalog_file)[0]
        try:
            import uuid
            u = uuid.UUID(bytes_le=bytes(part_family_id_blob))
            g_txt = guid_text(u)
            for sz in (640, 600, 400, 200, 64, 32):
                cand = os.path.join(content_dir, stem, str(sz), f"{script_name}_{g_txt}_{sz}.png")
                if os.path.isfile(cand) and os.path.getsize(cand) > 0:
                    return cand
        except Exception:
            pass

    # 2. 第二梯队：若没有标注图，使用普通 3D 预览图兜底
    found = index.find([
        f"{script_name}_iso.png",
        f"{script_name}_views.png",
        f"{script_name}_360.png",
        f"{script_name}.png",
        f"{script_name}_preview.png",
    ])
    if found:
        return found

    # 3. 第三梯队：模糊匹配任何以 script_name 开头的有效 png 兜底
    return index.find_prefix(script_name)



def _extract_peqx_preview(peqx_path: str, script_name: str) -> str:
    """从 .peqx 压缩包内提取或定位预览图。"""
    try:
        with zipfile.ZipFile(peqx_path, "r") as zf:
            pngs = [n for n in zf.namelist() if n.lower().endswith(".png")]
            if pngs:
                cache_dir = os.path.join(tempfile.gettempdir(), "p3d_peqx_previews")
                os.makedirs(cache_dir, exist_ok=True)
                out_p = os.path.join(cache_dir, f"{script_name}_peqx.png")
                with open(out_p, "wb") as fp:
                    fp.write(zf.read(pngs[0]))
                return out_p
    except Exception:
        pass
    return ""


def _infer_domain(catalog_file: str, script_name: str) -> str:
    cf = catalog_file.lower()
    su = script_name.upper()
    if "support" in cf or su.startswith(("CSG", "SUPPORT_")):
        return "Support (支吊架)"
    if "instrument" in cf or su.startswith(("CPI0", "INSTRUMENT_")):
        return "Instrument (仪表)"
    if "actuator" in cf or su.startswith("CPVX"):
        return "Actuator (执行机构)"
    if "nozzle" in cf or su == "CMANHOLE":
        return "Nozzle (管嘴/人孔)"
    if cf.endswith(".peqx") or "equipment" in cf:
        return "Equipment (设备)"
    return "Piping (管道/管件/阀门)"


def query_published_items(
    content_dir: str = None,
    include_builtin: bool = False,
    domain_filter: str = "ALL",
    search_text: str = "",
    on_progress=None,
    catalog_files: Optional[List[str]] = None,
    include_spec_counts: bool = False,
) -> List[dict]:
    """从真实的元件库 (.acat/.pcat)、等级库 (.pspc) 与设备库 (.peqx) 中检索所有已发布构件。

    on_progress(done, total, filename)：逐库进度回调，供 GUI 在后台线程里
    显示已计算的进度条；不传则静默。
    catalog_files：可选的库文件白名单（完整路径或文件名）。给出时只检索这些
    元件库/设备库，用于"用户自选库范围"场景；None 表示搜索全部。
    include_spec_counts：是否统计每个构件已进入多少行等级库。等级库扫描代价
    高且主列表已不再展示该列，默认关闭；需要时显式打开。
    """
    content_dir = content_dir or detect_default_content_dir()
    if not os.path.isdir(content_dir):
        return []

    # Check both content_dir and content_dir/CPak Common if nested
    scan_dirs = [content_dir]
    nested_cpak = os.path.join(content_dir, "CPak Common")
    if os.path.isdir(nested_cpak):
        scan_dirs.append(nested_cpak)

    custom_scripts_set = set()
    custom_py_stems = set()      # CustomScripts 下已部署的 .py 脚本名（大写 stem）
    custom_xml_stems = set()     # 同名 .xml 定义文件
    for d in scan_dirs:
        cs_d = os.path.join(d, "CustomScripts")
        if os.path.isdir(cs_d):
            try:
                for fn in os.listdir(cs_d):
                    low = fn.lower()
                    if low.endswith(".py"):
                        stem = os.path.splitext(fn)[0].upper()
                        custom_scripts_set.add(stem)
                        custom_py_stems.add(stem)
                    elif low.endswith(".xml"):
                        custom_xml_stems.add(os.path.splitext(fn)[0].upper())
            except OSError:
                pass

    # 补充当前项目开发工作区中的真实自定义构件集合（严格排除 system_defaults 避免混入原厂未发布零件）
    try:
        from .model import iter_scripts
        here_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        cand_custom = os.path.join(here_root, "pyscripts", "custom_scripts")
        if os.path.isdir(cand_custom):
            for sp in iter_scripts(cand_custom):
                custom_scripts_set.add(os.path.splitext(os.path.basename(sp))[0].upper())
    except Exception:
        pass

    # Map spec counts across .pspc files（仅在显式要求时统计，避免每次检索都全量扫等级库）
    spec_counts: Dict[str, int] = {}
    if include_spec_counts:
        for d in scan_dirs:
            try:
                psps = sorted(fn for fn in os.listdir(d) if fn.lower().endswith(".pspc"))
            except OSError:
                continue
            for fn in psps:
                sp_path = os.path.join(d, fn)
                if not (os.path.isfile(sp_path) and os.path.getsize(sp_path) > 0):
                    continue
                for tpl, cnt in _read_spec_template_counts(sp_path).items():
                    spec_counts[tpl] = max(spec_counts.get(tpl, 0), cnt)

    results: List[dict] = []
    seen_keys = set()

    # 预览图索引：每个 base 目录只 listdir 一次，供全部构件复用
    preview_indexes: Dict[str, _PreviewIndex] = {}

    def _preview_index_for(base_dir: str) -> _PreviewIndex:
        idx = preview_indexes.get(base_dir)
        if idx is None:
            dirs = _preview_search_dirs(base_dir)
            if os.path.normcase(os.path.abspath(base_dir)) != os.path.normcase(os.path.abspath(content_dir)):
                dirs += _preview_search_dirs(content_dir)
            idx = _PreviewIndex(dirs)
            preview_indexes[base_dir] = idx
        return idx


    # 1. Query all .acat and .pcat SQLite catalog databases（或仅用户选定的范围）
    allow = None
    if catalog_files:
        allow = {os.path.normcase(os.path.abspath(p)) for p in catalog_files}
        allow.update({os.path.normcase(os.path.basename(p)) for p in catalog_files})
    catalog_files = []
    for d in scan_dirs:
        for fn in sorted(os.listdir(d)):
            ext = os.path.splitext(fn)[1].lower()
            if ext not in (".acat", ".pcat"):
                continue
            cat_path = os.path.join(d, fn)
            if not (os.path.isfile(cat_path) and os.path.getsize(cat_path) > 0):
                continue
            if allow is not None:
                if (os.path.normcase(os.path.abspath(cat_path)) not in allow
                        and os.path.normcase(fn) not in allow):
                    continue
            catalog_files.append((d, fn, cat_path))
    total_catalogs = len(catalog_files)
    for done, (d, fn, cat_path) in enumerate(catalog_files, 1):
        if on_progress:
            on_progress(done, total_catalogs, fn)
        rows = _read_catalog_family_rows(cat_path)
        if not rows:
            continue
        preview_index = _preview_index_for(d)

        for tpl, cnt, fam_desc, short_desc, min_nd, max_nd, nd_unit, sample_param, fam_blob in rows:
            if not tpl:
                continue
            tu = tpl.upper()
            # 只有真正属于用户开发发布的自定义构件脚本才标记为 is_custom，避免原厂库自带内置零件污染
            is_custom = (
                tu in custom_scripts_set
                or tpl.startswith(("SUPPORT_", "ELBOW_", "PIPE_", "VALVE_", "INSTRUMENT_", "EQUIPMENT_"))
            )
            if not is_custom:
                continue

            dedup_key = (fn, tu)
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            domain_label = _infer_domain(fn, tpl)
            if domain_filter and domain_filter != "ALL" and domain_filter.lower() not in domain_label.lower():
                continue

            desc_str = fam_desc or short_desc or tpl
            if search_text:
                q = search_text.strip().lower()
                if q not in tpl.lower() and q not in desc_str.lower() and q not in fn.lower():
                    continue

            has_py = tu in custom_py_stems
            has_xml = tu in custom_xml_stems
            preview_img = _resolve_preview_image(d, fn, tpl, fam_blob, preview_index=preview_index)

            nd_range = f"{min_nd:g}~{max_nd:g} {nd_unit or 'mm'}" if min_nd is not None and max_nd is not None else "-"
            results.append({
                "script_name": tpl,
                "description": desc_str,
                "domain": domain_label,
                "catalog_file": fn,
                "catalog_path": cat_path,
                "size_count": int(cnt),
                "spec_count": spec_counts.get(tu, 0),
                "nd_range": nd_range,
                "sample_params": sample_param or "",
                "is_custom": is_custom,
                "has_py": has_py,
                "has_xml": has_xml,
                "preview_path": preview_img,
                "source_type": "catalog_db",
            })

    # 2. Query all .peqx Equipment packages in equipment/
    for d in scan_dirs:
        eq_dir = os.path.join(d, "equipment")
        if not os.path.isdir(eq_dir):
            continue
        for fn in sorted(os.listdir(eq_dir)):
            if not fn.lower().endswith(".peqx"):
                continue
            peqx_path = os.path.join(eq_dir, fn)
            stem = os.path.splitext(fn)[0]
            tu = stem.upper()
            is_custom = tu in custom_scripts_set or stem.startswith("EQUIPMENT_")
            if not is_custom:
                continue

            dedup_key = ("equipment", tu)
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)

            disp_name = stem
            part_type = "Equipment"
            part_sub_type = ""
            param_defs = []
            try:
                with zipfile.ZipFile(peqx_path, "r") as zf:
                    if "content/EquipmentType.xml" in zf.namelist():
                        xml_bytes = zf.read("content/EquipmentType.xml")
                        root = ET.fromstring(xml_bytes)
                        part_type = root.attrib.get("PartType", "Equipment")
                        part_sub_type = root.attrib.get("PartSubType", "")
                        for child in root:
                            tag = child.tag.split("}")[-1]
                            if tag == "DisplayName" and child.text:
                                disp_name = child.text.strip()
                            elif tag == "Parameters":
                                for pnode in child:
                                    if pnode.tag.split("}")[-1] == "ParameterInfo":
                                        pn = pnode.attrib.get("Name", "")
                                        dv = pnode.attrib.get("DefaultValue", "")
                                        if pn:
                                            param_defs.append(f"{pn}={dv}")
            except Exception:
                pass

            eq_cn_type = get_equipment_type_display_label(part_type, part_sub_type)
            domain_label = f"设备 · {eq_cn_type}"
            if domain_filter and domain_filter != "ALL" and domain_filter.lower() not in domain_label.lower() and domain_filter.lower() not in "equipment":
                continue

            if search_text:
                q = search_text.strip().lower()
                if q not in stem.lower() and q not in disp_name.lower() and q not in part_type.lower() and q not in eq_cn_type.lower():
                    continue

            has_py = tu in custom_py_stems
            has_xml = tu in custom_xml_stems
            preview_img = _resolve_preview_image(
                d, fn, stem, preview_index=_preview_index_for(d)) or _extract_peqx_preview(peqx_path, stem)

            results.append({
                "script_name": stem,
                "description": f"{disp_name} ({part_type}/{part_sub_type})" if part_sub_type else disp_name,
                "domain": domain_label,
                "part_type": part_type,
                "part_sub_type": part_sub_type,
                "catalog_file": f"equipment/{fn}",
                "catalog_path": peqx_path,
                "size_count": len(param_defs) or 1,
                "spec_count": 1,
                "nd_range": "PEQX 设备模板",
                "sample_params": ",".join(param_defs[:10]),
                "is_custom": is_custom,
                "has_py": has_py,
                "has_xml": has_xml,
                "preview_path": preview_img,
                "source_type": "peqx",
            })

    # Sort custom published items first, then by domain & script_name
    results.sort(key=lambda r: (0 if r["is_custom"] else 1, r["domain"], r["script_name"]))
    return results


def query_item_sizes_detail(catalog_path: str, script_name: str) -> List[dict]:
    """查询指定构件在数据库 (.acat/.pcat) 或设备包 (.peqx) 中的全部规格行详情。"""
    if not catalog_path or not os.path.isfile(catalog_path):
        return []
    if catalog_path.lower().endswith(".peqx"):
        rows = []
        try:
            with zipfile.ZipFile(catalog_path, "r") as zf:
                if "content/EquipmentType.xml" in zf.namelist():
                    root = ET.fromstring(zf.read("content/EquipmentType.xml"))
                    for idx, pnode in enumerate(root.iter(), 1):
                        if pnode.tag.split("}")[-1] == "ParameterInfo":
                            tip = ""
                            for ch in pnode:
                                if ch.tag.split("}")[-1] == "Tooltip" and ch.text:
                                    tip = ch.text.strip()
                            rows.append({
                                "PnPID": idx,
                                "NominalDiameter": "-",
                                "MatchingPipeOd": "-",
                                "ItemCode": pnode.attrib.get("Name", ""),
                                "PartSizeLongDesc": tip or pnode.attrib.get("Type", ""),
                                "ContentGeometryParamDefinition": f"DefaultValue={pnode.attrib.get('DefaultValue', '')}",
                            })
        except Exception:
            pass
        return rows

    rows = []
    try:
        con = sqlite3.connect(catalog_path)
        cur = con.cursor()
        cur.execute(
            "SELECT PnPID, NominalDiameter, MatchingPipeOd, ItemCode, PartSizeLongDesc, ContentGeometryParamDefinition "
            "FROM EngineeringItems WHERE UPPER(ContentGeometryTemplate) = UPPER(?) "
            "ORDER BY NominalDiameter ASC, PnPID ASC",
            (script_name,),
        )
        for pnp_id, nd, od, code, desc, pdef in cur.fetchall():
            rows.append({
                "PnPID": pnp_id,
                "NominalDiameter": nd if nd is not None else "",
                "MatchingPipeOd": od if od is not None else "",
                "ItemCode": code or "",
                "PartSizeLongDesc": desc or "",
                "ContentGeometryParamDefinition": pdef or "",
            })
        con.close()
    except Exception:
        pass
    return rows


def delete_published_item(
    content_dir: str,
    script_name: str,
    catalog_path: Optional[str] = None,
    remove_custom_script_files: bool = False,
) -> dict:
    """从元件库 (.acat/.pcat)、等级库 (.pspc) 或设备库 (.peqx) 中真实删除指定构件记录。"""
    deleted_rows = 0
    touched_files = []

    if catalog_path and catalog_path.lower().endswith(".peqx"):
        if os.path.isfile(catalog_path):
            os.remove(catalog_path)
            deleted_rows += 1
            touched_files.append(os.path.basename(catalog_path))
    else:
        # Delete from target catalog and any paired .pspc / extra .acat in content_dir
        scan_dirs = [content_dir]
        nested = os.path.join(content_dir, "CPak Common")
        if os.path.isdir(nested):
            scan_dirs.append(nested)

        db_targets = []
        if catalog_path and os.path.isfile(catalog_path):
            db_targets.append(catalog_path)
        for d in scan_dirs:
            if not os.path.isdir(d):
                continue
            for fn in os.listdir(d):
                if fn.lower().endswith((".acat", ".pcat", ".pspc")):
                    p = os.path.join(d, fn)
                    if p not in db_targets:
                        db_targets.append(p)

        for db_p in db_targets:
            if os.path.getsize(db_p) == 0:
                continue
            try:
                con = sqlite3.connect(db_p)
                cur = con.cursor()
                cur.execute(
                    "SELECT PnPID FROM EngineeringItems WHERE UPPER(ContentGeometryTemplate) = UPPER(?)",
                    (script_name,),
                )
                ids = [r[0] for r in cur.fetchall()]
                if ids:
                    placeholders = ",".join("?" for _ in ids)
                    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = [r[0] for r in cur.fetchall()]
                    for tbl in tables:
                        if tbl.startswith("PnP") and tbl != "PnPBase":
                            continue
                        try:
                            cur.execute(f'DELETE FROM "{tbl}" WHERE PnPID IN ({placeholders})', ids)
                        except Exception:
                            pass
                    con.commit()
                    deleted_rows += len(ids)
                    touched_files.append(os.path.basename(db_p))
                con.close()
            except Exception:
                pass

    if remove_custom_script_files:
        for d in [content_dir, os.path.join(content_dir, "CPak Common")]:
            cs_dir = os.path.join(d, "CustomScripts")
            if not os.path.isdir(cs_dir):
                continue
            for ext in (".py", ".xml", "_640.png", "_200.png", "_64.png", "_32.png"):
                fp = os.path.join(cs_dir, f"{script_name}{ext}")
                if os.path.isfile(fp):
                    try:
                        os.remove(fp)
                    except Exception:
                        pass

    clear_catalog_caches()
    return {
        "ok": deleted_rows > 0,
        "deleted_rows": deleted_rows,
        "touched_files": touched_files,
    }


def list_project_specs(spec_dir: str) -> List[dict]:
    """列出项目等级库工作表目录 (spec_dir) 下的所有真实等级库 (.pspc) 文件状态。"""
    if not spec_dir or not os.path.isdir(spec_dir):
        return []
    results = []
    for fn in sorted(os.listdir(spec_dir)):
        if not fn.lower().endswith(".pspc"):
            continue
        full_pspc = os.path.join(spec_dir, fn)
        if not os.path.isfile(full_pspc) or os.path.getsize(full_pspc) == 0:
            continue
        stem = os.path.splitext(fn)[0]
        full_pspx = os.path.join(spec_dir, stem + ".pspx")
        has_pspx = os.path.isfile(full_pspx)
        size_kb = round(os.path.getsize(full_pspc) / 1024.0, 1)

        part_count = 0
        family_count = 0
        spec_desc = ""
        try:
            con = sqlite3.connect(full_pspc)
            cur = con.cursor()
            cur.execute("SELECT Description FROM RepositoryDescriptor LIMIT 1")
            r = cur.fetchone()
            if r and r[0]:
                spec_desc = str(r[0])
            cur.execute(
                "SELECT COUNT(*), COUNT(DISTINCT ContentGeometryTemplate) FROM EngineeringItems "
                "WHERE ContentGeometryTemplate IS NOT NULL AND ContentGeometryTemplate != ''"
            )
            r2 = cur.fetchone()
            if r2:
                part_count, family_count = int(r2[0] or 0), int(r2[1] or 0)
            con.close()
        except Exception:
            pass

        results.append({
            "file": fn,
            "path": full_pspc,
            "stem": stem,
            "pspx_path": full_pspx if has_pspx else "",
            "has_pspx": has_pspx,
            "size_kb": size_kb,
            "part_count": part_count,
            "family_count": family_count,
            "description": spec_desc,
            "unit": detect_spec_unit(full_pspc),
        })
    return results


def create_project_spec(
    spec_dir: str,
    spec_name: str,
    donor_spec_path: Optional[str] = None,
    description: str = "",
    include_pipe: bool = True,
) -> dict:
    """在项目等级库工作表目录下创建全新的等级库 (.pspc) 及配对的打包外壳 (.pspx)。"""
    from .store import SPEC_TYPE, _stamp, _wipe_parts, _write_pspx

    if not spec_dir:
        raise ValueError("请指定等级库工作表目录。")
    os.makedirs(spec_dir, exist_ok=True)

    clean_name = spec_name.strip()
    if clean_name.lower().endswith((".pspc", ".pspx")):
        clean_name = os.path.splitext(clean_name)[0]
    if not clean_name:
        raise ValueError("等级库名称不能为空。")

    target_pspc = os.path.join(spec_dir, clean_name + ".pspc")
    target_pspx = os.path.join(spec_dir, clean_name + ".pspx")

    if os.path.isfile(target_pspc):
        raise RuntimeError(f"等级库文件已存在: {clean_name}.pspc")

    # 1. 寻找可用的 donor 模板
    donor = None
    if donor_spec_path and os.path.isfile(donor_spec_path):
        donor = donor_spec_path
    else:
        # 优先在当前项目目录找包含完整 Pipe + Port + PartPort 表的管道等级作为模板（跳过纯支吊架等级）
        fallback_donor = None
        for cand_fn in sorted(os.listdir(spec_dir)):
            if not cand_fn.lower().endswith(".pspc"):
                continue
            c_p = os.path.join(spec_dir, cand_fn)
            if not (os.path.isfile(c_p) and os.path.getsize(c_p) > 0):
                continue
            if fallback_donor is None:
                fallback_donor = c_p
            try:
                chk = sqlite3.connect("file:%s?mode=ro" % c_p.replace("\\", "/"), uri=True)
                try:
                    tset = {r[0] for r in chk.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                finally:
                    chk.close()
                if {"Pipe", "Port", "PartPort"}.issubset(tset):
                    donor = c_p
                    break
            except Exception:
                continue
        if not donor:
            donor = fallback_donor
        if not donor:
            # 其次在 CPak Common 找
            c_dir = detect_default_content_dir()
            for cand_fn in ("CustomParts Metric.pspc", "PipeSupportsSpec.pspc", "Instrumentation Metric.pspc"):
                c_p = os.path.join(c_dir, cand_fn)
                if os.path.isfile(c_p):
                    donor = c_p
                    break

    if not donor or not os.path.isfile(donor):
        raise RuntimeError("未找到用于创建新等级库的模板库 (.pspc)，请确保项目目录或 CPak Common 中存在基准等级库。")

    donor_pspx = os.path.splitext(donor)[0] + ".pspx"

    # 2. 复制 donor 数据库并初始化
    shutil.copy2(donor, target_pspc)
    con = sqlite3.connect(target_pspc)
    try:
        _wipe_parts(con)
        spec_desc = description.strip() or f"P3dPyPad Specification {clean_name}"
        _stamp(con, clean_name, SPEC_TYPE, "Standard", "spec")
        con.execute("UPDATE RepositoryDescriptor SET Description=? WHERE 1=1", (spec_desc,))
        con.commit()
        try:
            con.execute("VACUUM")
        except Exception:
            pass
    finally:
        con.close()

    clear_catalog_caches()

    # 3. 生成配对的 .pspx
    if donor_pspx and os.path.isfile(donor_pspx):
        try:
            _write_pspx(target_pspx, donor_pspx, clean_name + ".pspc")
        except Exception:
            pass
    else:
        # 如果 donor 旁没有 .pspx，尝试在 spec_dir 或 CPak Common 找任意 .pspx 借用外壳
        alt_pspx = None
        for fn in os.listdir(spec_dir):
            if fn.lower().endswith(".pspx"):
                alt_pspx = os.path.join(spec_dir, fn)
                break
        if not alt_pspx:
            c_dir = detect_default_content_dir()
            for fn in os.listdir(c_dir):
                if fn.lower().endswith(".pspx"):
                    alt_pspx = os.path.join(c_dir, fn)
                    break
        if alt_pspx and os.path.isfile(alt_pspx):
            try:
                _write_pspx(target_pspx, alt_pspx, clean_name + ".pspc")
            except Exception:
                pass

    pipe_rows = 0
    pipe_note = ""
    if include_pipe:
        pipe_rows, pipe_note = _seed_metric_pipes(target_pspc)
    return {
        "ok": True,
        "spec_name": clean_name,
        "spec_file": clean_name + ".pspc",
        "spec_path": target_pspc,
        "pspx_path": target_pspx,
        "pipe_rows": pipe_rows,
        "pipe_note": pipe_note,
    }


def _seed_metric_pipes(spec_path: str):
    """把公制直管 CPP 从 CustomParts Metric 元件库抄进新等级，否则无法布管。"""
    content = detect_default_content_dir()
    candidates = [
        os.path.join(content or "", "CustomParts Metric Catalog.pcat"),
        os.path.join(content or "", "CustomPartsSpecs", "CustomParts Metric.pspc"),
    ]
    catalog = next((path for path in candidates if path and os.path.isfile(path)), "")
    if not catalog:
        return 0, "未找到公制管子库 CustomParts Metric Catalog.pcat，等级里没有管子"
    try:
        added = add_catalog_item_to_spec(catalog, spec_path, "CPP")
    except Exception as exc:
        return 0, "写入默认管子失败: " + str(exc)
    rows = int(added.get("added_rows") or 0)
    if rows <= 0:
        return 0, "公制管子库里没有 CPP 直管"
    # 清除 CustomParts 带来的 Custom 标记与 Universal_ET，确保 Plant 3D Ribbon 管径下拉正常显示
    try:
        con = sqlite3.connect(spec_path)
        try:
            con.execute(
                "UPDATE EngineeringItems SET ComponentDesignation = NULL, "
                "EndType = CASE WHEN EndType = 'Universal_ET' OR EndType IS NULL OR EndType = '' THEN 'PL' ELSE EndType END "
                "WHERE ContentGeometryTemplate = 'CPP' AND PartCategory = 'Pipe'"
            )
            con.commit()
        finally:
            con.close()
    except Exception:
        pass
    return rows, "已写入 %d 条公制直管（CPP，mm）" % rows


def create_user_catalog(content_dir: str, catalog_name: str, kind: str = "piping") -> dict:
    """在 CPak Common 里新建元件库。固定库名拒绝覆盖。

    配管/阀门用 CustomParts Metric Catalog 做表结构；仪表用 Instrumentation Metric。
    新建库是空的，内部 Name 等于文件名（不含扩展名），等级行的 CatalogId 就写这个名字。
    """
    from .destinations import catalog_filename
    from .store import CATALOG_TYPE, _stamp, _wipe_parts

    if not content_dir or not os.path.isdir(content_dir):
        raise ValueError("请先指定 CPak Common 目录。")
    filename, stem = catalog_filename(catalog_name, kind=kind)
    target = os.path.join(content_dir, filename)
    if os.path.isfile(target):
        raise RuntimeError("元件库已存在: " + filename)

    if kind == "instrumentation":
        donor_names = ("Instrumentation Metric.pcat",)
        content_type = "Standard"
    else:
        donor_names = ("CustomParts Metric Catalog.pcat", "Instrumentation Metric.pcat")
        content_type = "Custom Parts"
    donor = ""
    for cand in donor_names:
        path = os.path.join(content_dir, cand)
        if os.path.isfile(path):
            donor = path
            break
    if not donor:
        raise RuntimeError("找不到用作表结构的原厂元件库（CustomParts Metric Catalog.pcat）。")

    shutil.copy2(donor, target)
    con = sqlite3.connect(target)
    try:
        _wipe_parts(con)
        _stamp(con, stem, CATALOG_TYPE, content_type, "catalog")
        con.commit()
    finally:
        con.close()
    clear_catalog_caches()
    return {"ok": True, "catalog_file": filename, "catalog_name": stem, "catalog_path": target}


def ensure_project_spec_copy(spec_dir: str, content_dir: str, spec_file: str) -> str:
    """项目等级表里没有这份固定等级时，从 CPak Common 原样复制，不清空零件。"""
    if not spec_dir:
        return ""
    os.makedirs(spec_dir, exist_ok=True)
    dest = os.path.join(spec_dir, spec_file)
    if os.path.isfile(dest) and os.path.getsize(dest) > 0:
        return dest
    src = os.path.join(content_dir or "", spec_file)
    if not os.path.isfile(src):
        nested = os.path.join(content_dir or "", "CPak Common", spec_file)
        if os.path.isfile(nested):
            src = nested
    if not os.path.isfile(src):
        return ""
    shutil.copy2(src, dest)
    src_pspx = os.path.splitext(src)[0] + ".pspx"
    if os.path.isfile(src_pspx):
        shutil.copy2(src_pspx, os.path.splitext(dest)[0] + ".pspx")
    return dest


def detect_spec_unit(spec_path: str, script_name: str = "") -> str:
    """判定等级库 (.pspc) 的单位制，返回 "metric" / "imperial" / ""。

    判定顺序：
    1. 文件名含 imperial / 英制 -> imperial；含 metric / 公制 -> metric；
       其余文件（PipeSupports / CS 系列等无标注命名）按数据实测；
    2. 传 script_name 时优先看该构件自己数据行的 LengthUnit（同一库里
       可能内置件英制、自定义件公制混合，行级单位才是构件的真实单位制）；
    3. 不传 script_name 时取全表主导单位（mm 为主 -> 公制，in/ft -> 英制）。
    """
    name = os.path.basename(spec_path or "").lower()
    if "imperial" in name or "英制" in name:
        return "imperial"
    if "metric" in name or "公制" in name:
        return "metric"
    if not spec_path or not os.path.isfile(spec_path):
        return ""
    try:
        con = sqlite3.connect("file:%s?mode=ro" % spec_path.replace("\\", "/"), uri=True)
        cur = con.cursor()
        if script_name:
            cur.execute(
                "SELECT LengthUnit, COUNT(*) AS c FROM EngineeringItems "
                "WHERE UPPER(ContentGeometryTemplate)=UPPER(?) "
                "AND LengthUnit IS NOT NULL AND LengthUnit != '' "
                "GROUP BY LengthUnit ORDER BY c DESC",
                (script_name,),
            )
        else:
            cur.execute(
                "SELECT LengthUnit, COUNT(*) AS c FROM EngineeringItems "
                "WHERE LengthUnit IS NOT NULL AND LengthUnit != '' "
                "GROUP BY LengthUnit ORDER BY c DESC"
            )
        rows = cur.fetchall()
        con.close()
    except Exception:
        return ""
    if not rows:
        return ""
    return _unit_kind(rows[0][0])


def spec_unit_label(unit: str) -> str:
    """单位制代号 -> 中文标签；空串返回空。"""
    return {"metric": "公制", "imperial": "英制"}.get(unit, "")


def build_spec_membership_index(dirs: List[str], on_progress=None,
                               files: Optional[List[str]] = None) -> Dict[str, dict]:
    """一次性扫描若干目录下的全部等级库，建立构件 -> 成员资格 的总索引。

    返回 {template_upper: {spec_path: {"file","count","unit"}}}。每个库只开一次，
    单条 GROUP BY 同时取行数与长度单位，单位随索引一起返回——这样「同时存在于」
    列与单位列都不必再逐对 (构件 x 等级库) 开库查询。
    on_progress(done, total, filename) 用于进度显示。
    """
    index: Dict[str, dict] = {}
    spec_paths = []
    seen = set()
    allow = None
    if files:
        allow = {os.path.normcase(os.path.abspath(f)) for f in files}
        allow.update({os.path.normcase(os.path.basename(f)) for f in files})
    for d in dirs:
        if not d or not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.lower().endswith(".pspc"):
                continue
            p = os.path.join(d, fn)
            if not os.path.isfile(p) or os.path.getsize(p) == 0:
                continue
            norm = os.path.normcase(os.path.abspath(p))
            if norm in seen:
                continue
            if allow is not None and norm not in allow and os.path.normcase(fn) not in allow:
                continue
            seen.add(norm)
            spec_paths.append(p)

    total = len(spec_paths)
    for done, path in enumerate(spec_paths, 1):
        if on_progress:
            on_progress(done, total, os.path.basename(path))
        fn = os.path.basename(path)
        # per_template: {tpl: {unit_kind: rows}}
        per_template: Dict[str, Dict[str, int]] = {}
        try:
            con = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)
            try:
                for tpl, unit, cnt in con.execute(
                    "SELECT ContentGeometryTemplate, LengthUnit, COUNT(*) FROM EngineeringItems "
                    "WHERE ContentGeometryTemplate IS NOT NULL AND ContentGeometryTemplate != '' "
                    "GROUP BY ContentGeometryTemplate, LengthUnit"
                ):
                    if not tpl:
                        continue
                    bucket = per_template.setdefault(str(tpl).upper(), {})
                    kind = _unit_kind(unit) or ""
                    bucket[kind] = bucket.get(kind, 0) + int(cnt)
            finally:
                con.close()
        except Exception:
            continue
        for tpl_u, kinds in per_template.items():
            count = sum(kinds.values())
            # 该构件行在库内的主导单位制（空串表示无法判定）
            dominant = ""
            if kinds:
                best = max(kinds.items(), key=lambda kv: kv[1])
                dominant = best[0] or ""
            entry = index.setdefault(tpl_u, {})
            entry[path] = {"file": fn, "count": count, "unit": dominant}
    return index



def query_item_spec_membership(spec_dir: str, script_name: str, extra_dirs: Optional[List[str]] = None) -> List[dict]:
    """查询指定构件在哪些等级库 (.pspc) 中已入库。

    默认扫项目等级库工作表目录；extra_dirs 里的目录（如 CPak Common——发布时
    支吊架/仪表固定等级的追加副本所在处）也一并扫，按目录去重。
    批量场景请用 build_spec_membership_index 一次建索引，避免逐构件全库扫描。
    """
    if not script_name:
        return []
    dirs = []
    for d in ([spec_dir] + list(extra_dirs or [])):
        if d and os.path.isdir(d) and d not in dirs:
            dirs.append(d)
    if not dirs:
        return []
    membership = []
    seen = set()
    for d in dirs:
        for fn in sorted(os.listdir(d)):
            if not fn.lower().endswith(".pspc"):
                continue
            p = os.path.join(d, fn)
            if not os.path.isfile(p) or os.path.getsize(p) == 0 or p.lower() in seen:
                continue
            seen.add(p.lower())
            try:
                con = sqlite3.connect(p)
                cur = con.cursor()
                cur.execute(
                    "SELECT COUNT(*) FROM EngineeringItems WHERE UPPER(ContentGeometryTemplate)=UPPER(?)",
                    (script_name,),
                )
                r = cur.fetchone()
                cnt = int(r[0] or 0) if r else 0
                con.close()
                if cnt > 0:
                    membership.append({
                        "file": fn,
                        "path": p,
                        "count": cnt,
                        # 库整体单位制（按主导行单位/文件名）
                        "unit": detect_spec_unit(p),
                        # 该构件自己数据行的单位制（混合库里与库整体可能不同）
                        "row_unit": detect_spec_unit(p, script_name),
                    })
            except Exception:
                pass
    return membership


def list_spec_files(content_dir: str = None, project_spec_dir: str = None,
                    include_content_dir: bool = True) -> List[dict]:
    """列出项目等级库目录 (project_spec_dir) 与 content_dir 下所有可用的等级库 (.pspc) 文件。

    include_content_dir=False 时只扫 project_spec_dir（供页面按目录逐个枚举，
    避免每个目录都重复扫一遍 CPak Common）。
    """
    specs = []
    seen = set()

    # 1. 优先列出具体工程项目 Spec Sheets 目录下的项目等级库
    if project_spec_dir and os.path.isdir(project_spec_dir):
        for fn in sorted(os.listdir(project_spec_dir)):
            if not fn.lower().endswith(".pspc"):
                continue
            full = os.path.join(project_spec_dir, fn)
            if not os.path.isfile(full) or os.path.getsize(full) == 0:
                continue
            norm = os.path.normcase(os.path.abspath(full))
            if norm in seen:
                continue
            seen.add(norm)
            specs.append({"file": fn, "path": full, "is_project": True})

    if not include_content_dir:
        return specs

    # 2. 补充标准 CPak Common 下的系统/通用等级库
    content_dir = content_dir or detect_default_content_dir()
    scan_dirs = [content_dir]
    nested = os.path.join(content_dir, "CPak Common")
    if os.path.isdir(nested):
        scan_dirs.append(nested)

    for d in scan_dirs:
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.lower().endswith(".pspc"):
                continue
            full = os.path.join(d, fn)
            if not os.path.isfile(full) or os.path.getsize(full) == 0:
                continue
            norm = os.path.normcase(os.path.abspath(full))
            if norm in seen:
                continue
            seen.add(norm)
            specs.append({"file": fn, "path": full, "is_project": False})

    return specs


def default_spec_for_catalog(content_dir: str, catalog_file: str) -> str:
    """根据元件库文件名自动匹配对应的默认等级库 (.pspc) 路径。

    支吊架功能区命令默认找 PipeSupportsSpec.pspc。规格查看器不限制等级名。
    """
    cf = (catalog_file or "").lower()
    if "support" in cf:
        targets = ["PipeSupportsSpec.pspc"]
    elif "instrument" in cf:
        targets = ["Instrumentation Metric.pspc"]
    else:
        targets = ["CustomParts Metric.pspc"]
    for target in targets:
        if not target:
            continue
        for d in [content_dir, os.path.join(content_dir, "CPak Common")]:
            cand = os.path.join(d, target)
            if os.path.isfile(cand):
                return cand
    specs = list_spec_files(content_dir)
    if "support" in cf:
        # 兜底：目录里任意含 support 字样的等级
        for sp in specs:
            if "support" in sp["file"].lower():
                return sp["path"]
    return specs[0]["path"] if specs else os.path.join(content_dir, targets[0] or "")


def add_catalog_item_to_spec(
    catalog_path: str,
    spec_path: str,
    script_name: str,
    pnp_ids: Optional[List[int]] = None,
) -> dict:
    """将元件库 (.acat/.pcat) 中的指定构件族（或指定规格行）快速自动添加到等级库 (.pspc)。"""
    from .model import guid_blob, stable_uuid
    from .store import _IdAllocator, _columns, _delete_template, _insert, _table_exists, _ticks

    if not catalog_path or not os.path.isfile(catalog_path):
        raise RuntimeError(f"找不到源元件库: {catalog_path}")
    if not spec_path or not os.path.isfile(spec_path):
        raise RuntimeError(f"找不到目标等级库: {spec_path}")

    cat_con = sqlite3.connect(catalog_path)
    cat_con.row_factory = sqlite3.Row
    spec_con = sqlite3.connect(spec_path, timeout=5, isolation_level=None)
    spec_con.execute("PRAGMA busy_timeout=5000")
    spec_con.execute("BEGIN IMMEDIATE")

    try:
        desc_row = cat_con.execute("SELECT Name FROM RepositoryDescriptor LIMIT 1").fetchone()
        catalog_name = desc_row["Name"] if desc_row and desc_row["Name"] else os.path.splitext(os.path.basename(catalog_path))[0]

        if pnp_ids:
            marks = ",".join("?" for _ in pnp_ids)
            cat_rows = cat_con.execute(
                f"SELECT * FROM EngineeringItems WHERE UPPER(ContentGeometryTemplate)=UPPER(?) AND PnPID IN ({marks}) ORDER BY PnPID",
                [script_name] + list(pnp_ids),
            ).fetchall()
        else:
            cat_rows = cat_con.execute(
                "SELECT * FROM EngineeringItems WHERE UPPER(ContentGeometryTemplate)=UPPER(?) ORDER BY PnPID",
                (script_name,),
            ).fetchall()

        if not cat_rows:
            raise RuntimeError(f"在元件库 {os.path.basename(catalog_path)} 中未找到构件 {script_name}")

        # 收集元件库中的附加子类表结构与名称
        cat_tables = {}
        for name, sql in cat_con.execute("SELECT name, sql FROM sqlite_master WHERE type='table'"):
            if sql and not name.startswith(("PnP", "sqlite")) and name not in ("RepositoryDescriptor", "EngineeringItems", "Port", "PartPort"):
                cat_tables[name] = sql

        # 先清理等级库中该构件的旧记录（若未指定部分 pnp_ids 则全族更新）
        if not pnp_ids:
            _delete_template(spec_con, script_name)

        alloc = _IdAllocator(spec_con)
        spec_family_blob = guid_blob(stable_uuid(f"spec:{catalog_name}:{script_name}"))
        now = _ticks()
        added_count = 0

        spec_ei_cols = set(_columns(spec_con, "EngineeringItems"))

        for crow in cat_rows:
            cat_pid = crow["PnPID"]
            base_row = cat_con.execute("SELECT PnPClassName FROM PnPBase WHERE PnPID=?", (cat_pid,)).fetchone()
            pnp_class = base_row["PnPClassName"] if base_row else "Support"

            new_pid = alloc.next_base()
            part_guid = stable_uuid(f"specpnp:{catalog_name}:{script_name}:{cat_pid}")
            _insert(spec_con, "PnPBase", {
                "PnPID": new_pid,
                "PnPClassName": pnp_class,
                "PnPStatus": 0,
                "PnPRevision": 0,
                "PnPGuid": guid_blob(part_guid),
                "PnPTimestamp": now,
            })

            ei_vals = dict(crow)
            ei_vals["PnPID"] = new_pid
            cat_fam_blob = crow["PartFamilyId"] if "PartFamilyId" in crow.keys() else spec_family_blob
            ei_vals["PartFamilyId"] = spec_family_blob
            ei_vals["SizeRecordId"] = guid_blob(stable_uuid(f"specsize:{catalog_name}:{script_name}:{cat_pid}"))
            if "CatalogPartFamilyId" in spec_ei_cols:
                ei_vals["CatalogPartFamilyId"] = cat_fam_blob
            if "CatalogId" in spec_ei_cols:
                ei_vals["CatalogId"] = catalog_name

            filtered_ei = {k: v for k, v in ei_vals.items() if k in spec_ei_cols and v is not None}
            _insert(spec_con, "EngineeringItems", filtered_ei)

            # 同步子类表 (PipeRunComponent / Support / Valve / Elbow / ...)
            for tbl_name, tbl_sql in cat_tables.items():
                sub_row = cat_con.execute(f'SELECT * FROM "{tbl_name}" WHERE PnPID=?', (cat_pid,)).fetchone()
                if sub_row is None:
                    continue
                if not _table_exists(spec_con, tbl_name):
                    spec_con.execute(tbl_sql)
                sub_vals = dict(sub_row)
                sub_vals["PnPID"] = new_pid
                _insert(spec_con, tbl_name, sub_vals)

            # 同步多端口记录 (PartPort & Port)
            if _table_exists(cat_con, "PartPort") and _table_exists(cat_con, "Port") and _table_exists(spec_con, "PartPort") and _table_exists(spec_con, "Port"):
                port_rels = cat_con.execute("SELECT Port, Name FROM PartPort WHERE Part=? ORDER BY PnPID", (cat_pid,)).fetchall()
                # 源库里的附加端口本来就从 S2 起；Name 为空时才用 S2、S3… 补名，不要写成 S1。
                for idx_p, prel in enumerate(port_rels, 2):
                    cat_port_id = prel["Port"]
                    p_name = prel["Name"] or f"S{idx_p}"
                    p_row = cat_con.execute("SELECT * FROM Port WHERE PnPID=?", (cat_port_id,)).fetchone()
                    if p_row is None:
                        continue
                    new_port_id = alloc.next_base()
                    new_rel_id = alloc.next_rel()
                    _insert(spec_con, "PnPBase", {
                        "PnPID": new_port_id,
                        "PnPClassName": "Port",
                        "PnPStatus": 0,
                        "PnPRevision": 0,
                        "PnPGuid": guid_blob(stable_uuid(f"specport:{catalog_name}:{script_name}:{cat_pid}:{p_name}")),
                        "PnPTimestamp": now,
                    })
                    p_vals = dict(p_row)
                    p_vals["PnPID"] = new_port_id
                    p_vals["SizeRecordId"] = guid_blob(stable_uuid(f"specportsize:{catalog_name}:{script_name}:{cat_pid}:{p_name}"))
                    _insert(spec_con, "Port", p_vals)
                    _insert(spec_con, "PartPort", {
                        "PnPID": new_rel_id,
                        "PnPGuid": guid_blob(stable_uuid(f"specrel:{catalog_name}:{script_name}:{cat_pid}:{p_name}")),
                        "PnPTimestamp": now,
                        "Part": new_pid,
                        "Port": new_port_id,
                        "Name": p_name,
                    })
                    if _table_exists(spec_con, "PnPRowRelations"):
                        spec_con.execute(
                            'INSERT INTO PnPRowRelations ("ROWID", RELID, RelationshipTypeName) VALUES (?,?,?)',
                            (new_pid, new_rel_id, "PartPort"),
                        )
                        spec_con.execute(
                            'INSERT INTO PnPRowRelations ("ROWID", RELID, RelationshipTypeName) VALUES (?,?,?)',
                            (new_port_id, new_rel_id, "PartPort"),
                        )
            added_count += 1

        alloc.flush(spec_con)
        spec_con.execute("COMMIT")
        clear_catalog_caches()

        # 确保配套的 .pspx 外壳存在
        pspx_path = os.path.splitext(spec_path)[0] + ".pspx"
        if not os.path.isfile(pspx_path):
            from .store import _write_pspx
            spec_dir = os.path.dirname(spec_path)
            alt_pspx = None
            if os.path.isdir(spec_dir):
                for f in os.listdir(spec_dir):
                    if f.lower().endswith(".pspx"):
                        alt_pspx = os.path.join(spec_dir, f)
                        break
            if not alt_pspx:
                c_dir = detect_default_content_dir()
                if os.path.isdir(c_dir):
                    for f in os.listdir(c_dir):
                        if f.lower().endswith(".pspx"):
                            alt_pspx = os.path.join(c_dir, f)
                            break
            if alt_pspx and os.path.isfile(alt_pspx):
                try:
                    _write_pspx(pspx_path, alt_pspx, os.path.basename(spec_path))
                except Exception:
                    pass

        return {
            "ok": True,
            "added_rows": added_count,
            "spec_file": os.path.basename(spec_path),
            "spec_path": spec_path,
            "pspx_path": pspx_path if os.path.isfile(pspx_path) else "",
            "catalog_file": os.path.basename(catalog_path),
            "script_name": script_name,
        }
    except Exception:
        try:
            spec_con.execute("ROLLBACK")
        except Exception:
            pass
        raise
    finally:
        cat_con.close()
        spec_con.close()


def remove_item_from_spec(
    spec_path: str,
    script_name: str,
) -> dict:
    """从指定等级库 (.pspc) 中移除指定构件的所有规格记录（保留元件库 .acat/.pcat 中的记录）。"""
    from .store import _delete_template

    if not spec_path or not os.path.isfile(spec_path):
        raise RuntimeError(f"找不到目标等级库: {spec_path}")

    con = sqlite3.connect(spec_path, timeout=5, isolation_level=None)
    con.execute("PRAGMA busy_timeout=5000")
    con.execute("BEGIN IMMEDIATE")
    try:
        cnt_row = con.execute(
            "SELECT COUNT(*) FROM EngineeringItems WHERE UPPER(ContentGeometryTemplate)=UPPER(?)",
            (script_name,),
        ).fetchone()
        cnt = int(cnt_row[0] or 0) if cnt_row else 0
        if cnt > 0:
            # Find exact template case
            tpl_row = con.execute(
                "SELECT ContentGeometryTemplate FROM EngineeringItems WHERE UPPER(ContentGeometryTemplate)=UPPER(?) LIMIT 1",
                (script_name,),
            ).fetchone()
            exact_tpl = tpl_row[0] if tpl_row else script_name
            _delete_template(con, exact_tpl)
        con.execute("COMMIT")
        clear_catalog_caches()
        return {
            "ok": cnt > 0,
            "removed_rows": cnt,
            "spec_file": os.path.basename(spec_path),
            "script_name": script_name,
        }
    except Exception:
        try:
            con.execute("ROLLBACK")
        except Exception:
            pass
        raise
    finally:
        con.close()

