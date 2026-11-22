# -*- coding: utf-8 -*-
"""设备（equipment）发布：生成 .peqx 模板包。

设备与管道/支吊架不同，**不走 .acat 元件库**。按 PD1746《Scripting Components for
AutoCAD Plant 3D》：

    CPak Common\\equipment\\<名字>.peqx     ← 设备模板包（OPC/ZIP）
    CPak Common\\CustomScripts\\<名字>.py   ← 脚本本身，名字必须与 peqx 里的 Name 一致

peqx 内部结构（照 Autodesk 自带模板，如 CentrifugalPump.peqx）：

    [Content_Types].xml                    xml / png / rels 三种默认类型
    _rels/.rels                            EquipmentType 关系 + 每个预览图一条关系
    content/EquipmentType.xml              Name / Type=C / PartType / PartSubType / GUID
                                           + <Parameters> + <Categories>
    preview/*.png                          参数示意图（200×200）

关键约束（漏了 Plant 就看不到这台设备）：
- `EquipmentType/@Name` 必须等于脚本名（不含 .py）；
- `@Type="C"`（C = 完全由脚本定义；F = 只用基本体拼、I = 块转换）；
- `@GUID` 每台设备唯一，这里按脚本名做 uuid5，保证可重复生成、同脚本不变；
- `@PartType` / `@PartSubType` 决定它出现在设备菜单的哪一类；
- 参数类型：LENGTH→d、LENGTH0→d0、ANGLE→a、INT→r、BOOL→b；
  STRING 在 peqx 里没有对应类型，直接跳过（脚本默认值仍然生效）。
"""

from __future__ import print_function

import io
import os
import re
import uuid
import zipfile

from .model import activate_body

# Group → (PartType, PartSubType)。PartType/PartSubType 必须取自自带模板的分类，
# 写错的话 Plant 3D 的设备菜单里根本不会出现这台设备。
# 取值来自 CPak Common\equipment\*.peqx 里 EquipmentType.xml 的实际组合。
EQUIPMENT_TYPES = {
    "Equipment": ("Vessel", "GeneralVessel"),
    "Vessel": ("Vessel", "GeneralVessel"),
    "Tank": ("Tank", "GeneralVessel"),
    "Pump": ("Pump", "HorizontalCentrifugalPump"),
    "HeatExchanger": ("HeatExchanger", "ShellTubeHeatExchanger"),
    "Heater": ("Heater", "FiredHeater"),
    "Strainer": ("StrainerEquipment", "General"),
}

# AutoCAD Plant 3D 官方原生设备大类与子分类中英对照字典
EQUIPMENT_CATEGORY_LABELS = {
    "Pump": u"泵 (Pump)",
    "Tank": u"储罐 (Tank)",
    "Vessel": u"容器 (Vessel)",
    "HeatExchanger": u"换热器 (HeatExchanger)",
    "Heater": u"加热炉 (Heater)",
    "StrainerEquipment": u"过滤器 (Strainer)",
}

EQUIPMENT_SUBTYPE_LABELS = {
    ("Pump", "HorizontalCentrifugalPump"): u"离心泵 (Centrifugal Pump)",
    ("Pump", "VerticalInlinePump"): u"立式管道泵 (Vertical Inline Pump)",
    ("Pump", "CentrifugalSumpPump"): u"潜污泵 (Sump Pump)",
    ("Tank", "VerticalVessel"): u"立式储罐 (Vertical Tank)",
    ("Tank", "GeneralVessel"): u"卧式储罐 (Horizontal Tank/Drum)",
    ("Vessel", "GeneralVessel"): u"工艺容器/反应器 (Vessel/Reactor)",
    ("HeatExchanger", "ShellTubeHeatExchanger"): u"管壳式换热器 (Shell & Tube HX)",
    ("HeatExchanger", "PlateAndFrameExchanger"): u"板式换热器 (Plate & Frame HX)",
    ("HeatExchanger", "Reboiler"): u"重沸器 (Reboiler)",
    ("Heater", "FiredHeater"): u"管式加热炉 (Fired Heater)",
    ("StrainerEquipment", "General"): u"工艺过滤器 (Strainer)",
}


def get_equipment_type_display_label(part_type: str, part_sub_type: str) -> str:
    """获取设备大类+子类的格式化中文显示标签，如 '泵 · 离心泵 (Pump)'。"""
    cat_cn = EQUIPMENT_CATEGORY_LABELS.get(part_type, part_type)
    sub_cn = EQUIPMENT_SUBTYPE_LABELS.get((part_type, part_sub_type))
    if sub_cn:
        c_short = cat_cn.split()[0]
        s_short = sub_cn.split()[0]
        return f"{c_short} · {s_short}"
    return cat_cn

# 供界面下拉框使用的可选设备类型：(显示名, PartType, PartSubType)
# 严格遵循官方自带 peqx 模板的标准枚举，杜绝任何非法未知分类
EQUIPMENT_TYPE_CHOICES = [
    (u"全部设备大类 (ALL)", "", ""),
    (u"离心泵 (Centrifugal Pump)", "Pump", "HorizontalCentrifugalPump"),
    (u"立式管道泵 (Vertical Inline Pump)", "Pump", "VerticalInlinePump"),
    (u"潜污泵 (Sump Pump)", "Pump", "CentrifugalSumpPump"),
    (u"立式容器 / 储罐 (Vertical Vessel)", "Tank", "VerticalVessel"),
    (u"卧式容器 / 储罐 (Horizontal Vessel)", "Tank", "GeneralVessel"),
    (u"通用工艺容器 (General Vessel)", "Vessel", "GeneralVessel"),
    (u"管壳式换热器 (Shell & Tube HX)", "HeatExchanger", "ShellTubeHeatExchanger"),
    (u"板式换热器 (Plate & Frame HX)", "HeatExchanger", "PlateAndFrameExchanger"),
    (u"重沸器 / 再沸器 (Reboiler)", "HeatExchanger", "Reboiler"),
    (u"加热炉 (Fired Heater)", "Heater", "FiredHeater"),
    (u"过滤器 (Strainer)", "StrainerEquipment", "General"),
]

# @param 类型 → peqx 的 ParameterInfo @Type
PARAM_TYPES = {
    "LENGTH": "d",
    "LENGTH0": "d0",
    "ANGLE": "a",
    "INT": "r",
    "BOOL": "b",
}

CONTENT_TYPES = u"""<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="xml" ContentType="text/xml" />
<Default Extension="png" ContentType="image/png" />
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />
</Types>
"""

REL_NS = u"http://schemas.openxmlformats.org/package/2006/relationships"

_PARAM_RE = re.compile(
    r'@param\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z0-9_]+)'
    r'(?:\s*,[^)]*?TooltipShort\s*=\s*(u?"[^"]*"|u?\'[^\']*\'))?[^)]*\)')
_GROUP_RE = re.compile(r'@group\s*\(\s*"([^"]*)"\s*(?:,\s*TooltipLong\s*=\s*"[^"]*")?\s*\)')


def _unquote(text):
    if not text:
        return u""
    text = text.strip()
    if text[:1] in (u"u", u"U") and text[1:2] in (u'"', u"'"):
        text = text[1:].strip()
    if text[:1] in (u'"', u"'") and text[-1:] == text[:1]:
        text = text[1:-1]
    return text


def parse_script(path):
    """读脚本的 @activate / @group / @param，返回设备模板需要的信息。

    返回 dict：
        name        脚本名（= peqx 的 Name）
        length_unit @activate 里的 LengthUnit（默认 mm）
        tooltip     显示名用 TooltipShort
        groups      [(分组名, [ (参数名, 类型, 默认值字符串) ... ])]，第一项是主分组
    """
    with io.open(path, encoding="utf-8") as handle:
        text = handle.read()

    name = os.path.splitext(os.path.basename(path))[0]
    info = {"name": name, "length_unit": u"mm", "tooltip": u"",
            "tooltip_long": u"", "groups": [], "ports": 1, "group": u""}
    body = activate_body(text)
    for key, field in ((r'LengthUnit\s*=\s*u?["\']([^"\']*)["\']', "length_unit"),
                       (r'TooltipShort\s*=\s*u?["\']([^"\']*)["\']', "tooltip"),
                       (r'TooltipLong\s*=\s*u?["\']([^"\']*)["\']', "tooltip_long"),
                       (r'Group\s*=\s*u?["\']([^"\']*)["\']', "group")):
        found = re.search(key, body)
        if found:
            info[field] = found.group(1)
    # 与 model._parse_activate 一致，接受 Ports=3 和 Ports="3" 两种写法
    ports = re.search(r'Ports\s*=\s*["\']?(\d+)["\']?', body)
    if ports:
        info["ports"] = max(1, int(ports.group(1)))

    # 默认值从 def 签名里取（@param 通常不带 Value）
    defaults = _signature_defaults(text)

    # 按出现顺序扫 @group / @param，把参数分配到所属分组
    events = []
    for item in _GROUP_RE.finditer(text):
        events.append((item.start(), "group", item.group(1)))
    for item in _PARAM_RE.finditer(text):
        events.append((item.start(), "param",
                       (item.group(1), item.group(2), _unquote(item.group(3)))))
    events.sort(key=lambda e: e[0])

    main = (u"MainDimensions", [])
    current = main
    for _pos, kind, payload in events:
        if kind == "group":
            if payload == main[0]:
                continue
            current = (payload, [])
            info["groups"].append(current)
        else:
            pname, ptype, tip = payload
            current[1].append((pname, ptype, defaults.get(pname, u""), tip))

    info["groups"].insert(0, main)
    return info


def _signature_defaults(text):
    """从 def 签名取默认值：覆盖多行签名。"""
    match = re.search(r"def\s+[A-Za-z_]\w*\s*\((.*?)\)\s*:", text, re.S)
    if not match:
        return {}
    defaults = {}
    for part in match.group(1).split(","):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = key.strip()
        if not re.match(r"^[A-Za-z_]\w*$", key):
            continue
        value = value.strip()
        if value[:1] in (u"u", u"U") and value[1:2] in (u'"', u"'"):
            value = value[1:]
        value = _unquote(value)
        try:
            number = float(value)
            value = ("%g" % number)
        except ValueError:
            pass
        defaults[key] = value
    return defaults


def _xml_attr(value):
    return (value or u"").replace(u"&", u"&amp;").replace(u'"', u"&quot;") \
                         .replace(u"<", u"&lt;").replace(u">", u"&gt;")


DEFAULT_NOZZLE_SIZE_ID = u"4b77a031-115e-53ce-affc-6aa39b8177f1"


def resolve_equipment_subtype(part_type, part_sub_type, stem, info=None):
    """推导设备的 SubType: 'H' (Horizontal 卧式) 或 'V' (Vertical 立式)。

    Plant 3D 的 PnP3dEquipmentUI.dll 在执行 _PLANTEQUIPMENTMODIFY 时，
    必须依据 SubType 进行卧式/立式上下文初始化，缺失该属性会导致图纸实体选择校验失败。
    """
    text = (stem + " " + (part_type or "") + " " + (part_sub_type or "")).upper()
    if any(k in text for k in ("VERTICAL", "STAND", "TOWER", "REACTOR", "COLUMN")):
        return "V"
    if any(k in text for k in ("HORIZONTAL", "DRUM", "HEATEX", "EXCHANGER", "REBOILER")):
        return "H"
    if part_type == "HeatExchanger":
        if "PLATE" in text or "VDN" in text or "VUP" in text:
            return "V"
        return "H"
    if part_type in ("Vessel", "Tank"):
        if "VERTICAL" in text or "REACTOR" in text:
            return "V"
        return "H"
    if part_type == "Heater":
        return "V"
    if part_type == "Pump":
        if "VERTICAL" in text or "INLINE" in text:
            return "V"
        return "H"
    return "H"


def resolve_display_name(stem, display_name=None, script_tooltip=None):
    """解析设备在 Plant 3D 界面中的友好中文显示名称。

    Plant 3D 界面菜单与创建/修改对话框由 .NET (PnP3dEquipmentUI.dll) 渲染，
    原生采用 UTF-16/Unicode，完全支持 UTF-8 中文显示。
    注意：EquipmentType/@Name 保持纯 ASCII 脚本标识，DisplayName 使用中文友好名。
    """
    raw = (display_name or script_tooltip or u"").strip()
    if raw:
        return raw

    st_up = stem.upper()
    if "CENTRIFUGAL_PUMP" in st_up:
        return u"化工标准离心泵 (ISO 2858)"
    if "HORIZONTAL_DRUM" in st_up:
        return u"卧式储罐/容器 (NB/T 47042)"
    if "JACKETED_REACTOR" in st_up:
        return u"标准夹套反应釜 (HG/T 20569)"
    if "SHELL_TUBE_EXCHANGER" in st_up:
        return u"化工固定管板列管换热器 (GB/T 151 BEM)"
    if "VERTICAL_VESSEL" in st_up:
        return u"立式工艺容器 (GB 150)"
    if "PUMP" in st_up:
        return u"自定义工艺泵"
    if "TANK" in st_up or "DRUM" in st_up:
        return u"自定义储罐"
    if "HEAT" in st_up or "EXCH" in st_up:
        return u"自定义换热器"
    if "VESSEL" in st_up or "REACTOR" in st_up:
        return u"自定义工艺容器"
    return stem


def _param_xml(pname, ptype, default, tip, indent):
    peqx_type = PARAM_TYPES.get(ptype)
    if peqx_type is None:
        return None          # STRING / ENUM 在 peqx 里没有直接对应，跳过
    default = default if default not in (u"", None) else u"0"
    attrs = u'Name="%s" DefaultValue="%s" Type="%s"' % (
        _xml_attr(pname), _xml_attr(default), peqx_type)
    if tip:
        return (u'%s<ParameterInfo %s>\n%s  <Tooltip>%s</Tooltip>\n%s</ParameterInfo>'
                % (indent, attrs, indent, _xml_attr(tip), indent))
    return u"%s<ParameterInfo %s />" % (indent, attrs)


def _build_nozzles_xml(info, part_type, indent=u"  "):
    """生成 Type="C" 脚本设备的 <Nozzles> 节点（官方 SumpPump/CAPS1a 风格）。

    三条硬约束（均为实测踩坑结论）：
    1. 严禁 Name="LOC" (Type="List")：LOC 是 Type="F" 基本体设备用来把管口
       吸附到第 N 个基本体的参数；Type="C" 脚本设备没有基本体列表
       (m_primitiveList == null)，带 LOC 会让 EquBaseDlg.RefreshNozzleProperties
       抛出 System.NullReferenceException。
    2. <Nozzles> 不能为空容器：官方所有 Type=C 模板（SumpPump/CAPS1a/Strainer…）
       都至少带一个 NozzleInfo；空 Nozzles 只出现在 Type=F 的 _TEMPLATE-H/V 里。
       Type=C + 空 Nozzles 会让 _PLANTEQUIPMENTMODIFY 的选择校验失败，
       命令行报"选择无效。只能选择一个设备项。"。
    3. NozzleInfo 引用的参数名必须以 "." 开头表示只读引用脚本真实参数
       （如 .DN_SHELL），并带 PortProperties/.SizeRecordId 指向 NOZZLE Catalog
       的真实法兰记录，供放置后挂接真实管口。
    """
    ports = max(1, int(info.get("ports", 1)))
    # 从主参数组里挑一个直径类参数作为管口公称尺寸引用（没有就用默认值）
    main_params = [p[0] for p in info["groups"][0][1]]
    dia_param = next((p for p in main_params if p.upper().startswith(("DN", "D_"))), None)

    lines = [u"%s<Nozzles>" % indent]
    sub = indent + u"  "
    for idx in range(1, ports + 1):
        lines.append(u'%s<NozzleInfo Name="Nozzle %d" PortName="S%d" PortIndex="%d">'
                     % (sub, idx, idx, idx))
        lines.append(u'%s  <DisplayName>Nozzle %d</DisplayName>' % (sub, idx))
        lines.append(u'%s  <Tooltip />' % sub)
        lines.append(u'%s  <NozzleTypes>' % sub)
        lines.append(u'%s    <NozzleType PartType="Nozzle" PartSubType="StraightNozzle" EndType="FL" />' % sub)
        lines.append(u'%s  </NozzleTypes>' % sub)
        lines.append(u'%s  <Parameters>' % sub)
        if dia_param:
            lines.append(u'%s    <ParameterInfo Name=".%s" DefaultValue="0" Type="d" Source="" />' % (sub, dia_param))
        else:
            lines.append(u'%s    <ParameterInfo Name=".NOZ_D" DefaultValue="100" Type="d" Source="" />' % sub)
        lines.append(u'%s  </Parameters>' % sub)
        lines.append(u'%s  <PortProperties>' % sub)
        lines.append(u'%s    <PropertyInfo Name=".SizeRecordId" DefaultValue="%s" />' % (sub, DEFAULT_NOZZLE_SIZE_ID))
        lines.append(u'%s  </PortProperties>' % sub)
        lines.append(u'%s</NozzleInfo>' % sub)
    lines.append(u"%s</Nozzles>" % indent)
    return u"\n".join(lines)


def build_equipment_xml(info, display_name=None, part_type=None, part_sub_type=None, guid=None):
    """生成 content/EquipmentType.xml 的文本 (UTF-8 编码，包含 SubType、安全 Nozzles 与中文 DisplayName)。"""
    if guid is None:
        guid = uuid.uuid5(uuid.NAMESPACE_URL, u"plant3d-occ:equipment:" + info["name"])
    # 类型推断统一走 resolve_equipment_type，避免两处各写一套关键词规则而漂移。
    part_type, part_sub_type = resolve_equipment_type(info, part_type, part_sub_type)
    sub_type = resolve_equipment_subtype(part_type, part_sub_type, info["name"], info)
    safe_disp = resolve_display_name(info["name"], display_name, info.get("tooltip"))

    lines = [
        u'<?xml version="1.0" encoding="utf-8"?>',
        u'<EquipmentType',
        u'\txmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        u'\txmlns:xsd="http://www.w3.org/2001/XMLSchema"',
        u'\tLengthUnit="%s"' % _xml_attr(info.get("length_unit") or u"mm"),
        u'\tName="%s"' % _xml_attr(info["name"]),
        u'\tType="C"',
        u'\tSubType="%s"' % _xml_attr(sub_type),
        u'\tPartType="%s"' % _xml_attr(part_type),
        u'\tPartSubType="%s"' % _xml_attr(part_sub_type),
        u'\tGUID="{%s}">' % str(guid).upper(),
        u'  <DisplayName>%s</DisplayName>' % _xml_attr(safe_disp),
    ]

    main = info["groups"][0]
    lines.append(u"  <Parameters>")
    for pname, ptype, default, tip in main[1]:
        node = _param_xml(pname, ptype, default, tip, u"    ")
        if node:
            lines.append(node)
    lines.append(u"  </Parameters>")

    categories = [g for g in info["groups"][1:] if g[1]]
    if categories:
        lines.append(u"  <Categories>")
        for gname, params in categories:
            lines.append(u'    <CategoryInfo Name="%s">' % _xml_attr(gname))
            lines.append(u"      <DisplayName>%s</DisplayName>" % _xml_attr(gname))
            lines.append(u"      <Tooltip />")
            lines.append(u"      <Parameters>")
            for pname, ptype, default, tip in params:
                node = _param_xml(pname, ptype, default, tip, u"        ")
                if node:
                    lines.append(node)
            lines.append(u"      </Parameters>")
            lines.append(u"    </CategoryInfo>")
        lines.append(u"  </Categories>")

    lines.append(_build_nozzles_xml(info, part_type, indent=u"  "))
    lines.append(u"</EquipmentType>")
    return u"\n".join(lines) + u"\n"


def build_rels(info, preview_relative):
    """_rels/.rels：EquipmentType 关系 + 主显示图关系（Id 用脚本名，与自带模板一致）。"""
    lines = [
        u'<?xml version="1.0" encoding="utf-8"?>',
        u'<Relationships xmlns="%s">' % REL_NS,
        u'\t<Relationship Type="Plant/Equipment/EquipmentType" '
        u'Target="/content/EquipmentType.xml" Id="PlantEquipmentType" />',
    ]
    if preview_relative:
        lines.append(u'\t<Relationship Type="Plant/Equipment/Preview" Target="/%s" Id="%s" />'
                     % (preview_relative, _xml_attr(info["name"])))
    lines.append(u"</Relationships>")
    return u"\n".join(lines) + u"\n"


def build_peqx(script_path, out_path, preview_png=None, display_name=None,
               part_type=None, part_sub_type=None):
    """把脚本打包成 .peqx。preview_png 传 200×200 的 PNG 路径（可空）。"""
    info = parse_script(script_path)
    resolved = resolve_equipment_type(info, part_type, part_sub_type)
    xml = build_equipment_xml(info, display_name, resolved[0], resolved[1])

    preview_relative = u""
    if preview_png and os.path.isfile(preview_png):
        preview_relative = u"preview/%s.png" % info["name"].lower()

    folder = os.path.dirname(os.path.abspath(out_path))
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    # 用 UTF-8 写 XML；zip 里统一正斜杠路径
    content_types_bytes = CONTENT_TYPES.encode("utf-8") if isinstance(CONTENT_TYPES, str) else CONTENT_TYPES
    xml_bytes = xml.encode("utf-8") if isinstance(xml, str) else xml
    rels_bytes = build_rels(info, preview_relative)
    rels_bytes = rels_bytes.encode("utf-8") if isinstance(rels_bytes, str) else rels_bytes

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_bytes)
        archive.writestr("content/EquipmentType.xml", xml_bytes)
        archive.writestr("_rels/.rels", rels_bytes)
        if preview_relative:
            archive.write(preview_png, preview_relative)

    return {"path": out_path, "name": info["name"], "info": info,
            "part_type": resolved[0], "part_sub_type": resolved[1],
            "preview": preview_relative}


def resolve_equipment_type(info, part_type=None, part_sub_type=None):
    """确定这台设备最终写进 peqx 的 (PartType, PartSubType)。

    优先用调用方显式指定的类型；没指定时按脚本名 / Group 关键词精准推断。
    推断结果严格对应官方自带模板的合法枚举，确保在 Plant 3D 创建设备菜单中精准出现。
    """
    if part_type and part_sub_type:
        return (part_type, part_sub_type)

    grp_str = (info.get("group") or u"").split(",")[0].strip()
    nm_up = (info.get("name") or u"").upper()
    all_str = (nm_up + " " + grp_str).lower()

    if "pump" in all_str or nm_up.startswith("CAP"):
        return ("Pump", "HorizontalCentrifugalPump")
    if "drum" in all_str or "tank" in all_str:
        return ("Tank", "GeneralVessel")
    if "heat" in all_str or "exch" in all_str or "reboiler" in all_str:
        return ("HeatExchanger", "ShellTubeHeatExchanger")
    if "reactor" in all_str or "vessel" in all_str:
        return ("Vessel", "GeneralVessel")
    if "heater" in all_str:
        return ("Heater", "FiredHeater")
    if "strainer" in all_str:
        return ("StrainerEquipment", "General")
    return ("Vessel", "GeneralVessel")


def equipment_folder(plant_root):
    return os.path.join(plant_root, "CPak Common", "equipment")
