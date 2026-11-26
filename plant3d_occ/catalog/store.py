# -*- coding: utf-8 -*-
"""写入 Plant 3D 元件库和等级库。

功能区「添加支吊架」默认打开 PipeSupportsSpec。规格查看器可以打开任意等级，
例如项目里的 PipeSupports。原厂公制元件库的 Name 是 SUPPORTS Catalog metric，
已有零件靠这个名字找库；新建元件库可以用别的 Name，只要等级行的 CatalogId 一致。
原厂库只追加，不整库替换。

端口行（Plant 3D 2026 原厂 ASME/DIN 已核对，不要改）：
没有 S0。S1 只写在 EngineeringItems.PortName 及口径/端面/外径上。
PartPort 从 S2 起，行数 = ConnectionPortCount - 1。单口零件（支吊架、管帽、
盲板）没有 PartPort 行；支吊架 EndType 用 Undefined_ET。禁止把 S1 补进 PartPort。
配管等级仍必须带有 Port/PartPort 表，否则规格编辑器尺寸列表为空。
"""
import datetime
import math
import os
import shutil
import sqlite3
import uuid
import zipfile

from .model import braced_guid, guid_blob, guid_text, stable_uuid

def detect_plant_content_dir():
    """本机最新一份 CPak Common。先读注册表 PLANTCONTENTFOLDER，再扫磁盘。"""
    from .content_dirs import list_cpak_common_dirs
    found = list_cpak_common_dirs()
    return found[0]["path"] if found else ""


def _default_plant_content():
    env = os.environ.get("PLANT3D_CONTENT_DIR")
    if env and os.path.isdir(env):
        return env
    cfg_file = os.path.expanduser("~/.plant3d_occ_catalog_config.json")
    if os.path.isfile(cfg_file):
        try:
            import json
            with open(cfg_file, "r", encoding="utf-8") as fp:
                saved = json.load(fp).get("content_dir")
                if saved and os.path.isdir(saved):
                    return saved
        except Exception:
            pass
    # 未配置时按版本探测 C 盘安装目录，不要求用户先手动指定
    return detect_plant_content_dir()

PLANT_CONTENT = _default_plant_content()

CATALOG_TYPE = "Autodesk.ProcessPower.PartsRepository.Catalog.PipePartCatalog"
SPEC_TYPE = "Autodesk.ProcessPower.PartsRepository.Specification.PipePartSpecification"

# DIN 管件库的 PnP 架构里有 Valve，但没有物理表。规格编辑器要这张表才能认自定义阀。
_VALVE_SQL = (
    'CREATE TABLE "Valve"("PnPID" integer,"Length" double,'
    '"ValveAlignment" VarChar (255) collate nocase,'
    '"ValveDetail" VarChar (255) collate nocase,'
    '"ValveBodyType" VarChar (255) collate nocase,'
    '"FlowDependent" bit,"Offset" bit,'
    '"ValveBodyFamilyId" GUID,"ValveBodyPartSizeId" GUID,'
    '"ActuatorFamilyName" VarChar (255) collate nocase,'
    '"ActuatorFamilyId" GUID,"ActuatorPartSizeId" GUID,'
    '"OperatorType" VarChar (255) collate nocase,'
    '"ActuatorType" VarChar (255) collate nocase,'
    '"ActuatorHeight" double,"ActuatorWidth" double,'
    '"ControlValve" bit,Primary key ("PnPID"))'
)

_DOMAINS = {
    "support": {
        # 内容目录里的支吊架等级母本仍是 PipeSupportsSpec.pspc。
        # 项目里用哪一份（PipeSupports、PipeSupportsSpec 或其他）由发布时的等级选择决定。
        # 原厂公制元件库 Name 是 SUPPORTS Catalog metric。
        "catalog_name": "SUPPORTS Catalog metric",
        "catalog_file": "SUPPORTS Catalog metric.acat",
        "spec_file": "PipeSupportsSpec.pspc",
        "pspx_file": "PipeSupportsSpec.pspx",
        "catalog_donor": ("CPak Common", "SUPPORTS Catalog metric.acat"),
        "spec_donor": ("CPak Common", "PipeSupportsSpec.pspc"),
        "pspx_donor": ("CPak Common", "PipeSupportsSpec.pspx"),
        "schema_donor": ("CPak Common", "SUPPORTS Catalog metric.acat"),
        "catalog_content": "Pipe Supports",
        "spec_content": "Supports",
        "append": True,
        # 同一个 CPak 里有英制与公制两个支吊架元件库，发布时两份都要写；
        # 等级库只有一份（文件名可由 support_spec 配置覆盖），不重复写。
        "extra_catalogs": [
            {"catalog_file": "SUPPORTS Catalog.acat",
             "catalog_name": "SUPPORTS Catalog",
             "catalog_content": "Pipe Supports"},
        ],
    },
    "instrumentation": {
        # 仪表进 Plant 自带的仪表库，append 模式：在现有库里追加零件 (纯元件库模式)
        "catalog_name": "Instrumentation Metric",
        "catalog_file": "Instrumentation Metric.pcat",
        "spec_file": "Instrumentation Metric.pspc",
        "pspx_file": "Instrumentation Metric.pspx",
        "catalog_donor": ("CPak Common", "Instrumentation Metric.pcat"),
        "spec_donor": ("CPak Common", "Instrumentation Metric.pspc"),
        "pspx_donor": ("CPak Common", "Instrumentation Metric.pspx"),
        "schema_donor": ("CPak Common", "Instrumentation Metric.pcat"),
        "catalog_content": "Standard",
        "spec_content": "Standard",
        "append": True,
        "catalog_only": True,
    },
    "piping": {
        # 官方原生管件/管道/阀门自定义元件库：CustomParts Metric Catalog.pcat，追加模式写入 (纯元件库模式)
        "catalog_name": "CustomParts Metric Catalog",
        "catalog_file": "CustomParts Metric Catalog.pcat",
        "spec_file": "CustomParts Metric.pspc",
        "pspx_file": "CustomParts Metric.pspx",
        "catalog_donor": ("CPak Common", "CustomParts Metric Catalog.pcat"),
        "spec_donor": ("CPak Common", "CustomPartsSpecs", "CustomParts Metric.pspc"),
        "pspx_donor": ("CPak Common", "CustomPartsSpecs", "CustomParts Metric.pspx"),
        "schema_donor": ("CPak Common", "CustomParts Metric Catalog.pcat"),
        "catalog_content": "Custom Parts",
        "spec_content": "Custom Parts",
        "append": True,
        "catalog_only": True,
    },
}


class PublishError(Exception):
    pass


def domain_info(domain):
    info = _DOMAINS.get(domain)
    if info is None:
        raise PublishError("未知库类型: " + str(domain))
    return info


_FALLBACK_DONORS = {
    ("CPak DIN", "DIN Pipes and Fittings Catalog.pcat"): ("CPak Common", "Instrumentation Metric.pcat"),
    ("CPak DIN", "10HC01.pspc"): ("CPak Common", "Instrumentation Metric.pspc"),
}

_FALLBACK_TABLE_SQL = {
    "Elbow": 'CREATE TABLE "Elbow"("PnPID" integer, "Angle" double, "Radius" double, Primary key ("PnPID"))',
    "Pipe": 'CREATE TABLE "Pipe"("PnPID" integer, "Length" double, Primary key ("PnPID"))',
    "SingleBranchFitting": 'CREATE TABLE "SingleBranchFitting"("PnPID" integer, "BranchAngle1" double, Primary key ("PnPID"))',
    "Tee": 'CREATE TABLE "Tee"("PnPID" integer, "Length" double, Primary key ("PnPID"))',
    "Reducer": 'CREATE TABLE "Reducer"("PnPID" integer, "Length" double, Primary key ("PnPID"))',
    "Cross": 'CREATE TABLE "Cross"("PnPID" integer, "Length" double, Primary key ("PnPID"))',
    "Cap": 'CREATE TABLE "Cap"("PnPID" integer, "Length" double, Primary key ("PnPID"))',
    "BlindFlange": 'CREATE TABLE "BlindFlange"("PnPID" integer, "Length" double, Primary key ("PnPID"))',
    "Support": 'CREATE TABLE "Support"("PnPID" integer, "PartSubType" VarChar(255) collate nocase, Primary key ("PnPID"))',
    "Instrument": 'CREATE TABLE "Instrument"("PnPID" integer, "PartSubType" VarChar(255) collate nocase, Primary key ("PnPID"))',
}

def donor_file(plant_root, parts, content_dir=None):
    """智能解析模板库真实路径，优先命中当前 content_dir，杜绝 CPak Common 重复拼接。"""
    target_fn = parts[-1]

    # 1. 优先直接在当前使用的 content_dir 根目录下寻找
    if content_dir and os.path.isfile(os.path.join(content_dir, target_fn)):
        return os.path.join(content_dir, target_fn)

    # 2. 如果当前 content_dir 带有子目录 (如 CustomPartsSpecs/)
    if content_dir and len(parts) > 1 and parts[0] == "CPak Common":
        sub_cand = os.path.join(content_dir, *parts[1:])
        if os.path.isfile(sub_cand):
            return sub_cand

    # 3. 如果 plant_root 自身就是 CPak Common，去除重复的 parts[0]
    if plant_root:
        if os.path.isfile(os.path.join(plant_root, target_fn)):
            return os.path.join(plant_root, target_fn)
        base = os.path.basename(os.path.normpath(plant_root)).lower()
        if len(parts) > 1 and base == parts[0].lower():
            cand = os.path.join(plant_root, *parts[1:])
            if os.path.isfile(cand):
                return cand

        cand = os.path.join(plant_root, *parts)
        if os.path.isfile(cand):
            return cand

        # 4. 如果 plant_root 是 Content 根目录的子级，尝试退回父级拼接
        parent_d = os.path.dirname(os.path.normpath(plant_root))
        parent_cand = os.path.join(parent_d, *parts)
        if os.path.isfile(parent_cand):
            return parent_cand

    alt = _FALLBACK_DONORS.get(tuple(parts))
    if alt and plant_root:
        alt_cand = os.path.join(plant_root, *alt)
        if os.path.isfile(alt_cand):
            return alt_cand

    return os.path.join(content_dir or plant_root or "", target_fn)


def copy_family_previews(src_root, src_guid, dst_root, dst_guid, prefix):
    """把元件库预览图复制到规格编辑器按零件族 GUID 查找的目录。

    文件名是 ``{类名}_{guid}_{尺寸}.png``，尺寸目录为 32/64/200/640。
    规格编辑器用等级里的 PartFamilyId，不是元件库的 CatalogPartFamilyId。
    """
    src_guid = str(src_guid).strip("{}")
    dst_guid = str(dst_guid).strip("{}")
    copied = 0
    for size in (32, 64, 200, 640):
        folder = os.path.join(src_root, str(size))
        want = "%s_%s_%d.png" % (prefix, src_guid, size)
        src = os.path.join(folder, want)
        if not os.path.isfile(src) and os.path.isdir(folder):
            want_l = want.lower()
            for name in os.listdir(folder):
                if name.lower() == want_l:
                    src = os.path.join(folder, name)
                    break
        if not os.path.isfile(src):
            continue
        out_dir = os.path.join(dst_root, str(size))
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        dst = os.path.join(out_dir, "%s_%s_%d.png" % (prefix, dst_guid, size))
        if not os.path.isfile(dst):
            shutil.copy2(src, dst)
        copied += 1
    return copied


def preview_paths(content_dir, catalog_file, image_prefix, family_uuid):
    stem = os.path.splitext(catalog_file)[0]
    text = guid_text(family_uuid)
    paths = {}
    for size in (640, 200, 64, 32):
        name = "%s_%s_%d.png" % (image_prefix, text, size)
        paths[size] = os.path.join(content_dir, stem, str(size), name)
    return paths


def _factory_database(path):
    """原厂库（描述里没有 P3dPyPad）只能追加，不能清空重写。"""
    if not path or not os.path.isfile(path):
        return False
    try:
        con = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)
        try:
            row = con.execute("SELECT Description FROM RepositoryDescriptor").fetchone()
        finally:
            con.close()
    except sqlite3.Error:
        return True
    text = row[0] if row and row[0] else ""
    return "P3dPyPad" not in str(text)


class LibrarySession(object):
    """一次发布里打开的一对元件库和等级库。

    spec_file_override：可选，覆盖该领域的等级库文件名。支吊架不要改，
    Plant 只打开 PipeSupportsSpec。
    catalog_file_override：配管/仪表可写入用户自建元件库。支吊架忽略这个参数，
    避免把支吊架写进没有 Support 表的管件库。
    """

    def __init__(self, content_dir, plant_root, domain, spec_file_override=None,
                 catalog_file_override=None, catalog_name_override=None,
                 catalog_only=None):
        info = dict(domain_info(domain))
        if catalog_only is not None:
            info["catalog_only"] = bool(catalog_only)
        if spec_file_override:
            info["spec_file"] = spec_file_override
            info["pspx_file"] = os.path.splitext(spec_file_override)[0] + ".pspx"
        if catalog_file_override and domain != "support":
            info["catalog_file"] = catalog_file_override
            info["catalog_name"] = catalog_name_override or os.path.splitext(catalog_file_override)[0]
            dest = os.path.join(content_dir or "", info["catalog_file"])
            # 原厂库没有 P3dPyPad 印记，只能追加；新建或本工具建的库走复制/续写。
            info["append"] = _factory_database(dest)
            info["catalog_only"] = True
        self.info = info
        self.domain = domain
        self.catalog_path = os.path.join(content_dir, info["catalog_file"])
        self.spec_path = os.path.join(content_dir, info["spec_file"])
        self.pspx_path = os.path.join(content_dir, info["pspx_file"])
        self.catalog_donor = donor_file(plant_root, info["catalog_donor"], content_dir)
        self.spec_donor = donor_file(plant_root, info.get("spec_donor", info["catalog_donor"]), content_dir)
        self.pspx_donor = donor_file(plant_root, info.get("pspx_donor", info["catalog_donor"]), content_dir)
        self.schema_donor = donor_file(plant_root, info["schema_donor"], content_dir)
        self._schema_sql = {}
        self.catalog = None
        self.spec = None
        self.catalog_ids = None
        self.spec_ids = None

    def open(self):
        try:
            append = bool(self.info.get("append"))
            self.catalog = _ensure_database(
                self.catalog_path,
                self.catalog_donor,
                self.info["catalog_name"],
                CATALOG_TYPE,
                self.info["catalog_content"],
                "catalog",
                append,
            )
            if self.info.get("catalog_only"):
                # 只写元件库（额外的 .acat），等级库由主会话负责
                self.spec = None
                self._load_schema_sql()
                self.catalog.execute("BEGIN IMMEDIATE")
                self.catalog_ids = _IdAllocator(self.catalog)
                return

            self.spec = _ensure_database(
                self.spec_path,
                self.spec_donor,
                self.info["catalog_name"],
                SPEC_TYPE,
                self.info["spec_content"],
                "spec",
                append,
            )
            if not append:
                _write_pspx(self.pspx_path, self.pspx_donor, self.info["spec_file"])
            self._load_schema_sql()
            self.catalog.execute("BEGIN IMMEDIATE")
            self.spec.execute("BEGIN IMMEDIATE")
            self.catalog_ids = _IdAllocator(self.catalog)
            self.spec_ids = _IdAllocator(self.spec)
        except Exception:
            self._abort()
            raise

    def _abort(self):
        for con in (self.catalog, self.spec):
            if con is None:
                continue
            try:
                con.close()
            except sqlite3.Error:
                pass
        self.catalog = None
        self.spec = None

    def close(self):
        for con, alloc in ((self.catalog, self.catalog_ids), (self.spec, self.spec_ids)):
            if con is None:
                continue
            try:
                if alloc is not None:
                    alloc.flush(con)
                con.execute("COMMIT")
            except sqlite3.Error:
                try:
                    con.execute("ROLLBACK")
                except sqlite3.Error:
                    pass
            finally:
                con.close()
        self.catalog = None
        self.spec = None

    def mark(self):
        self.catalog.execute("SAVEPOINT fam")
        if self.spec is not None:
            self.spec.execute("SAVEPOINT fam")

    def release(self):
        self.catalog.execute("RELEASE fam")
        if self.spec is not None:
            self.spec.execute("RELEASE fam")

    def undo(self):
        for con in (self.catalog, self.spec):
            if con is None:
                continue
            con.execute("ROLLBACK TO fam")
            con.execute("RELEASE fam")

    def write_family(self, job):
        family = stable_uuid("catalog:%s:%s" % (self.domain, job["stem"]))
        spec_family = stable_uuid("spec:%s:%s" % (self.domain, job["stem"]))
        self._write_one(self.catalog, self.catalog_ids, job, family, None, False)
        if self.spec is not None:
            self._write_one(self.spec, self.spec_ids, job, spec_family, family, True)
        return family

    def _write_one(self, con, alloc, job, family_uuid, catalog_family, is_spec):
        _ensure_chain(con, job["chain"], self._schema_sql)
        if job["ports"] > 1 and not _table_exists(con, "Port"):
            raise PublishError("该库没有端口表，不能写入多端口零件")
        _delete_template(con, job["stem"])
        for size in job["sizes"]:
            part_id = alloc.next_base()
            size_uuid = stable_uuid(
                "%s:%s:%s:%s" % ("specsize" if is_spec else "size", self.domain, job["stem"], size["preset"])
            )
            _insert_part(con, job, size, part_id, family_uuid, size_uuid, catalog_family, is_spec, self.info["catalog_name"])
            # Plant 没有 S0。主端口 S1 写在 EngineeringItems（PortName/口径/端面），
            # 不进 PartPort。PartPort 从 S2 起，和原厂 ASME/DIN 等级库一致。
            # 单端口零件（支吊架、管帽、盲板）因此没有 PartPort 行，这是对的。
            if job["ports"] <= 1:
                continue
            for index in range(2, job["ports"] + 1):
                port_id = alloc.next_base()
                rel_id = alloc.next_rel()
                port_uuid = stable_uuid(
                    "port:%s:%s:%s:%s:S%d" % (
                        "spec" if is_spec else "cat", self.domain, job["stem"], size["preset"], index,
                    )
                )
                _insert_port(con, job, size, part_id, port_id, rel_id, index, port_uuid)

    def _load_schema_sql(self):
        if not os.path.isfile(self.schema_donor):
            raise PublishError("找不到表结构来源: " + self.schema_donor)
        src = sqlite3.connect(self.schema_donor)
        try:
            for name, sql in src.execute("SELECT name, sql FROM sqlite_master WHERE type='table'"):
                if sql:
                    self._schema_sql[name] = sql
        finally:
            src.close()
        for k, v in _FALLBACK_TABLE_SQL.items():
            self._schema_sql.setdefault(k, v)
        self._schema_sql["Valve"] = _VALVE_SQL


def copy_script(content_dir, script_path):
    folder = os.path.join(content_dir, "CustomScripts")
    if not os.path.isdir(folder):
        os.makedirs(folder)
    dest = os.path.join(folder, os.path.basename(script_path))
    shutil.copy2(script_path, dest)
    return dest


def _ensure_database(dest, donor, name, repo_type, content_type, kind, append=False):
    if append:
        if not os.path.isfile(dest):
            raise PublishError("找不到软件指定的库: " + dest)
        _backup_once(dest)
        con = _connect(dest)
        con.execute("COMMIT")
        return con
    if _same_path(dest, donor):
        raise PublishError("拒绝覆盖原始库: " + donor)
    if not os.path.isfile(donor):
        raise PublishError("找不到原始库: " + donor)
    brand_new = not os.path.isfile(dest)
    if brand_new:
        folder = os.path.dirname(dest)
        if folder and not os.path.isdir(folder):
            os.makedirs(folder)
        shutil.copy2(donor, dest)
    else:
        _backup(dest)
    con = _connect(dest)
    try:
        desc = con.execute("SELECT Description FROM RepositoryDescriptor").fetchone()
        text = desc[0] if desc and desc[0] else ""
        if not brand_new and "P3dPyPad" not in text:
            con.close()
            raise PublishError("目标已存在但不是本工具生成的库，已停止: " + dest)
        if brand_new:
            _wipe_parts(con)
            _stamp(con, name, repo_type, content_type, kind)
            con.execute("COMMIT")
            try:
                con.execute("VACUUM")
            except sqlite3.Error:
                pass
        else:
            con.execute("COMMIT")
        return con
    except PublishError:
        raise
    except Exception:
        try:
            con.close()
        except sqlite3.Error:
            pass
        raise


def _connect(path):
    try:
        con = sqlite3.connect(path, timeout=5, isolation_level=None)
        con.execute("PRAGMA busy_timeout=5000")
        con.execute("BEGIN IMMEDIATE")
    except sqlite3.OperationalError as exc:
        raise PublishError("文件被占用，请关闭规格编辑器后再发布: " + path + " (" + str(exc) + ")")
    return con


def _backup(path):
    try:
        shutil.copy2(path, path + ".bak")
    except OSError:
        pass


def _backup_once(path):
    """原厂库只在第一次追加前留一份，避免每次发布都覆盖备份。"""
    kept = path + ".pypad-orig"
    if os.path.isfile(kept):
        return
    shutil.copy2(path, kept)


def _wipe_parts(con):
    tables = [row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    if "PnPRowRelations" in tables:
        con.execute("DELETE FROM PnPRowRelations")
    if "PnPTombstone" in tables:
        con.execute("DELETE FROM PnPTombstone")
    for name in tables:
        if name.startswith("PnP") or name.startswith("sqlite") or name == "RepositoryDescriptor":
            continue
        con.execute('DELETE FROM "%s"' % name.replace('"', ""))
    con.execute("DELETE FROM PnPBase WHERE PnPClassName!='RepositoryDescriptor'")
    _set_counter(con, "PnPSys_PnPBase_PnPID", 2)
    _set_counter(con, "PnPSys_RelationshipSystem_PnPID", 1)


def _stamp(con, name, repo_type, content_type, kind):
    repo = uuid.uuid4()
    description = "P3dPyPad %s %s" % (kind, name)
    con.execute(
        "UPDATE RepositoryDescriptor SET Name=?, RepositoryID=?, Description=?, Type=?, ContentType=?, Version='5_0', OriginalVersion='5_0'",
        (name, braced_guid(repo), description, repo_type, content_type),
    )
    cols = _columns(con, "PnPDatabase")
    if cols:
        try:
            con.execute('UPDATE PnPDatabase SET "%s"=?' % cols[0], (uuid.uuid4().bytes_le,))
        except sqlite3.Error:
            pass


def _ensure_chain(con, chain, schema_sql):
    for name in chain:
        if _table_exists(con, name):
            continue
        sql = schema_sql.get(name)
        if not sql:
            raise PublishError("目标库缺少表 " + name + "，原始库里也没有这张表")
        con.execute(sql)


def _delete_template(con, template):
    """只删这个脚本自己的尺寸和它的端口。

    零件 PnPID 和 PartPort.PnPID 是两套编号，不能拿零件号去 Port/PartPort 里一刀切。
    """
    columns = _columns(con, "EngineeringItems")
    if "ContentGeometryTemplate" not in columns:
        return
    _delete_orphan_ports(con)
    part_ids = [row[0] for row in con.execute(
        "SELECT PnPID FROM EngineeringItems WHERE ContentGeometryTemplate=?", (template,)
    )]
    if not part_ids:
        return
    marks = ",".join("?" for _ in part_ids)
    port_ids = []
    if _table_exists(con, "PartPort"):
        rel_ids = [row[0] for row in con.execute(
            "SELECT PnPID FROM PartPort WHERE Part IN (%s)" % marks, part_ids
        )]
        port_ids = [row[0] for row in con.execute(
            "SELECT Port FROM PartPort WHERE Part IN (%s)" % marks, part_ids
        )]
        if rel_ids:
            rel_marks = ",".join("?" for _ in rel_ids)
            con.execute(
                "DELETE FROM PnPRowRelations WHERE RelationshipTypeName='PartPort' AND RELID IN (%s)" % rel_marks,
                rel_ids,
            )
        con.execute("DELETE FROM PartPort WHERE Part IN (%s)" % marks, part_ids)
    if port_ids:
        port_marks = ",".join("?" for _ in port_ids)
        if _table_exists(con, "Port"):
            con.execute("DELETE FROM Port WHERE PnPID IN (%s)" % port_marks, port_ids)
        con.execute(
            "DELETE FROM PnPBase WHERE PnPClassName='Port' AND PnPID IN (%s)" % port_marks,
            port_ids,
        )
    for name in _pnpid_tables(con):
        if name in ("RepositoryDescriptor", "PnPBase", "Port", "PartPort") or name.startswith("PnP"):
            continue
        con.execute('DELETE FROM "%s" WHERE PnPID IN (%s)' % (name, marks), part_ids)
    con.execute(
        "DELETE FROM PnPBase WHERE PnPClassName!='RepositoryDescriptor' AND PnPClassName!='Port' AND PnPID IN (%s)" % marks,
        part_ids,
    )


def _delete_orphan_ports(con):
    """清掉残缺的端口关系，避免 SizeRecordId 唯一约束被残留行挡住。

    两类残留都要清：
    1. Port 没有 PartPort 指向（纯粹的孤儿端口）；
    2. PartPort 指向的 Part 已不在 PnPBase 里（半孤儿——以前发布中途失败或
       端口写入成功但零件行丢失留下的）。这类 Port 仍在 PartPort 里，
       只按第 1 类清理永远删不掉，其 SizeRecordId 会永久挡住同一构件的
       重新发布 (UNIQUE constraint failed: Port.SizeRecordId)。
    """
    if not _table_exists(con, "Port") or not _table_exists(con, "PartPort"):
        return
    # 先清半孤儿 PartPort（指向的 Part 已不存在），连带其 Port 与关系行
    half = [row[0] for row in con.execute(
        "SELECT PnPID FROM PartPort "
        "WHERE Part IS NOT NULL AND Part NOT IN (SELECT PnPID FROM PnPBase)"
    )]
    if half:
        marks = ",".join("?" for _ in half)
        orphan_port_ids = [row[0] for row in con.execute(
            "SELECT Port FROM PartPort WHERE PnPID IN (%s) AND Port IS NOT NULL" % marks, half
        )]
        con.execute("DELETE FROM PartPort WHERE PnPID IN (%s)" % marks, half)
        if orphan_port_ids:
            pm = ",".join("?" for _ in orphan_port_ids)
            con.execute("DELETE FROM Port WHERE PnPID IN (%s)" % pm, orphan_port_ids)
            con.execute(
                "DELETE FROM PnPBase WHERE PnPClassName='Port' AND PnPID IN (%s)" % pm,
                orphan_port_ids,
            )
        con.execute(
            "DELETE FROM PnPRowRelations WHERE RelationshipTypeName='PartPort' AND RELID IN (%s)" % marks,
            half,
        )
    # 再清没有 PartPort 指向的 Port
    con.execute("DELETE FROM Port WHERE PnPID NOT IN (SELECT Port FROM PartPort WHERE Port IS NOT NULL)")
    con.execute("DELETE FROM PnPBase WHERE PnPClassName='Port' AND PnPID NOT IN (SELECT PnPID FROM Port)")
    con.execute(
        "DELETE FROM PnPRowRelations WHERE RelationshipTypeName='PartPort' AND RELID NOT IN (SELECT PnPID FROM PartPort)"
    )


def _face_length(call):
    """端面到端面的长度。和原厂规格里 Valve/Reducer.Length 用的是同一个数。"""
    if not isinstance(call, dict):
        return None
    for key in ("L", "L_FACE", "H_LEN", "L_LEN", "L_BODY", "L_TOT", "H_TOT"):
        if key not in call:
            continue
        try:
            value = float(call[key])
        except (TypeError, ValueError):
            continue
        if value > 0.0:
            return value
    if "L_OUT" in call and "H_IN" in call:
        try:
            return math.hypot(float(call["L_OUT"]), float(call["H_IN"]))
        except (TypeError, ValueError):
            pass
    if "C_LEN" in call:
        try:
            return 2.0 * float(call["C_LEN"])
        except (TypeError, ValueError):
            pass
    return None


def _insert_part(con, job, size, part_id, family_uuid, size_uuid, catalog_family, is_spec, catalog_name):
    now = _ticks()
    part_guid = stable_uuid("pnp:%s:%s" % (job["stem"], size["preset"] if not is_spec else "spec:" + size["preset"]))
    _insert(con, "PnPBase", {
        "PnPID": part_id,
        "PnPClassName": job["pnp_class"],
        "PnPStatus": 0,
        "PnPRevision": 0,
        "PnPGuid": guid_blob(part_guid),
        "PnPTimestamp": now,
    })
    values = {
        "PnPID": part_id,
        "PartFamilyId": guid_blob(family_uuid),
        "PartFamilyLongDesc": job["tooltip"][:255],
        "PartSizeLongDesc": size["long"],
        "ShortDescription": size["short"],
        "ItemCode": size["item_code"],
        "Material": size["material"] or None,
        "CompatibleStandard": size["standard"] or None,
        "Weight": size["weight"],
        "WeightUnit": "kg" if size["weight"] is not None else None,
        "ConnectionPortCount": job["ports"],
        "SizeRecordId": guid_blob(size_uuid),
        "PortName": "S1",
        "NominalDiameter": size["nominals"][0],
        "NominalUnit": "mm",
        "MatchingPipeOd": size["ods"][0],
        "EndType": size["ends"][0],
        "EngagementLength": 0.0,
        "LengthUnit": "mm",
        "PartCategory": job["category"],
        "ContentDomain": "P3D",
        "ContentGeometryParamDefinition": size["param_def"],
        "ContentIsoSymbolDefinition": size["iso"],
        "ContentGeometryTemplate": job["stem"],
        "PartVersion": "4_0",
        "PressureClass": size["pressure"] or None,
        "Facing": size["facing"] or None,
        "Schedule": size["schedule"] or None,
    }
    if is_spec:
        values["CatalogPartFamilyId"] = guid_blob(catalog_family)
        values["CatalogId"] = catalog_name
    _insert(con, "EngineeringItems", values)
    subtype = size["subtype"] or ("Support" if job["pnp_class"] == "Support" else None)
    # 原厂 CS150：Valve.Length / Reducer.Length 等于脚本端面距离（参数 L）。
    # 空着时 Plant 按 0 缩放，阀门退回系统手轮，大小头被压成对尖双锥。
    length = _face_length(size.get("call") or {})
    for table in job["chain"]:
        extra = {"PnPID": part_id}
        cols = _columns(con, table)
        if table == "Support" and subtype and "PartSubType" in cols:
            extra["PartSubType"] = subtype
        if table == "Valve" and subtype and "ValveBodyType" in cols:
            extra["ValveBodyType"] = subtype
        if "Length" in cols and isinstance(length, (int, float)):
            extra["Length"] = float(length)
        if table == "SingleBranchFitting" and "BranchAngle1" in cols and "A" in size["call"]:
            try:
                extra["BranchAngle1"] = float(size["call"]["A"])
            except (TypeError, ValueError):
                pass
        _insert(con, table, extra)


def _insert_port(con, job, size, part_id, port_id, rel_id, index, port_uuid):
    now = _ticks()
    _insert(con, "PnPBase", {
        "PnPID": port_id,
        "PnPClassName": "Port",
        "PnPStatus": 0,
        "PnPRevision": 0,
        "PnPGuid": guid_blob(stable_uuid("pnpport:%s:%s:S%d" % (job["stem"], size["preset"], index))),
        "PnPTimestamp": now,
    })
    _insert(con, "Port", {
        "PnPID": port_id,
        "SizeRecordId": guid_blob(port_uuid),
        "PortName": "S%d" % index,
        "NominalDiameter": size["nominals"][index - 1],
        "NominalUnit": "mm",
        "MatchingPipeOd": size["ods"][index - 1],
        "EndType": size["ends"][index - 1],
        "EngagementLength": 0.0,
        "LengthUnit": "mm",
        "PressureClass": size["pressure"] or None,
        "Facing": size["facing"] or None,
        "Schedule": size["schedule"] or None,
    })
    _insert(con, "PartPort", {
        "PnPID": rel_id,
        "PnPGuid": guid_blob(stable_uuid("rel:%s:%s:S%d" % (job["stem"], size["preset"], index))),
        "PnPTimestamp": now,
        "Part": part_id,
        "Port": port_id,
        "Name": "S%d" % index,
    })
    con.execute(
        'INSERT INTO PnPRowRelations ("ROWID", RELID, RelationshipTypeName) VALUES (?,?,?)',
        (part_id, rel_id, "PartPort"),
    )
    con.execute(
        'INSERT INTO PnPRowRelations ("ROWID", RELID, RelationshipTypeName) VALUES (?,?,?)',
        (port_id, rel_id, "PartPort"),
    )


def _insert(con, table, values):
    cols = _columns(con, table)
    keys = [key for key in values if key in cols and values[key] is not None]
    if not keys:
        raise PublishError("表 " + table + " 没有可写的列")
    sql = 'INSERT INTO "%s" (%s) VALUES (%s)' % (
        table,
        ",".join('"%s"' % key for key in keys),
        ",".join("?" for _ in keys),
    )
    con.execute(sql, [values[key] for key in keys])


def _write_pspx(dest, donor, spec_file):
    if not os.path.isfile(donor):
        raise PublishError("找不到等级库外壳: " + donor)
    folder = os.path.dirname(dest)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    source = zipfile.ZipFile(donor, "r")
    target = zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED)
    try:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename.replace("\\", "/").endswith("_rels/.rels"):
                text = data.decode("utf-8")
                import re
                text = re.sub(r'Target="[^"]+\.pspc"', 'Target="%s"' % spec_file, text, count=1)
                data = text.encode("utf-8")
            target.writestr(info, data)
    finally:
        source.close()
        target.close()


def _columns(con, table):
    return [row[1] for row in con.execute('PRAGMA table_info("%s")' % table.replace('"', ""))]


def _table_exists(con, name):
    return con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None


def _pnpid_tables(con):
    found = []
    for (name,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        if name.startswith("sqlite"):
            continue
        cols = _columns(con, name)
        if "PnPID" in cols:
            found.append(name)
    return found


def _set_counter(con, table, value):
    if not _table_exists(con, table):
        return
    con.execute("UPDATE %s SET cnt=?" % table, (value,))


def _ticks():
    epoch = datetime.datetime(1, 1, 1)
    return int((datetime.datetime.utcnow() - epoch).total_seconds() * 10000000)


def _same_path(left, right):
    return os.path.normcase(os.path.abspath(left)) == os.path.normcase(os.path.abspath(right))


class _IdAllocator(object):
    def __init__(self, con):
        self.base = con.execute("SELECT COALESCE(MAX(PnPID),0) FROM PnPBase").fetchone()[0] or 0
        if _table_exists(con, "PartPort"):
            self.rel = con.execute("SELECT COALESCE(MAX(PnPID),0) FROM PartPort").fetchone()[0] or 0
        else:
            self.rel = 0

    def next_base(self):
        self.base += 1
        return self.base

    def next_rel(self):
        self.rel += 1
        return self.rel

    def flush(self, con):
        _set_counter(con, "PnPSys_PnPBase_PnPID", self.base + 1)
        _set_counter(con, "PnPSys_RelationshipSystem_PnPID", self.rel + 1)
