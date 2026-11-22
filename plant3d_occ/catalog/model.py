# -*- coding: utf-8 -*-
"""从脚本和同名 CSV 整理出一条可写入元件库的族。

同时支持：
- 从同名 `.csv` 读取多规格尺寸表
- 当指定 `auto_generate_sizes=True`（或调用 `ensure_script_csv`）时，自动根据脚本
  `def` 函数签名默认值与标准管径系列生成预设规格行与 `.csv` 文件。
"""
import io
import os
import re
import uuid

_NS = uuid.UUID("8f3e2a1c-6b4d-4e7f-9a0b-1c2d3e4f5061")

_OD_TO_DN = (
    (10.2, 6), (13.5, 8), (17.2, 10), (21.3, 15), (26.9, 20), (33.7, 25),
    (42.4, 32), (48.3, 40), (60.3, 50), (76.1, 65), (76.2, 65), (88.9, 80),
    (108.0, 100), (114.3, 100), (133.0, 125), (139.7, 125), (159.0, 150), (168.3, 150),
    (219.1, 200), (273.0, 250), (323.9, 300), (355.6, 350), (406.4, 400),
    (457.0, 450), (508.0, 500), (610.0, 600), (711.0, 700),
    (813.0, 800), (914.0, 900), (1016.0, 1000),
)

_META_COLUMNS = {
    "预设名", "名称", "规格名", "PartNumber", "DN", "NominalDiameter", "公称直径",
    "DN2", "DN3", "DN4",
    "EndType", "EndType2", "EndType3", "EndType4",
    "LongDesc", "ShortDesc", "ItemCode", "Material", "MATL", "Standard",
    "SKEY", "IsoSymbol", "PartSubType", "PressureClass", "Facing",
    "Schedule", "Weight",
}

_GROUPS = {
    "Support": {
        "domain": "support",
        "pnp_class": "Support",
        "image": "Support",
        "chain": ["PipeRunComponent", "Support"],
        "end": "Undefined_ET",
        "iso": "TYPE=SUPPORT,SKEY=SKID",
        "category": "Default",
    },
    "Elbow": {
        "domain": "piping",
        "pnp_class": "Elbow",
        "image": "Elbow",
        "chain": ["PipeRunComponent", "Elbow"],
        "end": "BV",
        "iso": "TYPE=BEND,SKEY=BEBW",
        "category": "Fittings",
    },
    "Tee": {
        "domain": "piping",
        "pnp_class": "Tee",
        "image": "Tee",
        "chain": ["PipeRunComponent", "SingleBranchFitting", "Tee"],
        "end": "BV",
        "iso": "TYPE=TEE,SKEY=TEBW",
        "category": "Fittings",
    },
    "Reducer": {
        "domain": "piping",
        "pnp_class": "Reducer",
        "image": "Reducer",
        "chain": ["PipeRunComponent", "Reducer"],
        "end": "BV",
        "iso": "TYPE=REDUCER-CONCENTRIC,SKEY=REBW",
        "category": "Fittings",
    },
    "Cross": {
        "domain": "piping",
        "pnp_class": "Cross",
        "image": "Cross",
        "chain": ["PipeRunComponent", "Cross"],
        "end": "BV",
        "iso": "TYPE=CROSS,SKEY=CRBW",
        "category": "Fittings",
    },
    "Cap": {
        "domain": "piping",
        "pnp_class": "Cap",
        "image": "Cap",
        "chain": ["PipeRunComponent", "Cap"],
        "end": "BV",
        "iso": "TYPE=CAP,SKEY=CPBW",
        "category": "Fittings",
    },
    "Blind": {
        "domain": "piping",
        "pnp_class": "BlindFlange",
        "image": "BlindFlange",
        "chain": ["PipeRunComponent", "BlindFlange"],
        "end": "FL",
        "iso": "TYPE=FLANGE-BLIND,SKEY=FLBL",
        "category": "Fittings",
    },
    "Flange": {
        "domain": "piping",
        "pnp_class": "Flange",
        "image": "Flange",
        "chain": ["PipeRunComponent", "Flange"],
        "end": "FL",
        "iso": "TYPE=FLANGE,SKEY=FLWN",
        "category": "Fittings",
    },
    "Pipe": {
        "domain": "piping",
        "pnp_class": "Pipe",
        "image": "Pipe",
        "chain": ["PipeRunComponent", "Pipe"],
        "end": "BV",
        "iso": "TYPE=PIPE,SKEY=PIPL",
        "category": "Pipe",
    },
    "Instrument": {
        "domain": "instrumentation",
        "pnp_class": "Instrument",
        "image": "Instrument",
        "chain": ["PipeRunComponent", "Instrument"],
        "end": "Undefined_ET",
        "iso": "TYPE=INSTRUMENT,SKEY=INST",
        "category": "Instrumentation",
    },
    "Valve": {
        "domain": "piping",
        "pnp_class": "Valve",
        "image": "Valve",
        "chain": ["PipeRunComponent", "Valve"],
        "end": "FL",
        "iso": "TYPE=VALVE,SKEY=VVFL",
        "category": "Valves",
    },
}

_EQUIPMENT_GROUPS = {"Equipment", "Vessel", "Tank", "Pump", "HeatExchanger"}

_ANNOTATION_DOMAINS = {"support", "equipment"}


def needs_dimension_annotation(job):
    """只有支吊架和设备需要生成轴测尺寸标注图，其余构件仅生成着色轴测图。"""
    domain = str((job or {}).get("domain") or "").strip().lower()
    if domain in _ANNOTATION_DOMAINS:
        return True
    group = str((job or {}).get("group") or "").strip()
    return group == "Support" or group in _EQUIPMENT_GROUPS


_SKIP_GROUPS = {
    "Structure": "结构钢不进管道/支吊架元件库",
    "Structural": "结构钢不进管道/支吊架元件库",
}

_NUMERIC = {"LENGTH", "LENGTH0", "ANGLE"}
_REQUIRED = {"LENGTH", "LENGTH0", "ANGLE", "INT", "BOOL", "ENUM"}


def stable_uuid(name):
    return uuid.uuid5(_NS, name)


def guid_blob(value):
    return value.bytes_le


def guid_text(value):
    return str(value)


def braced_guid(value):
    return "{" + str(value).upper() + "}"


def iter_scripts(root):
    if not root or not os.path.isdir(root):
        return
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]
        for name in sorted(files):
            if name.endswith(".py") and not name.startswith("_"):
                yield os.path.join(dirpath, name)


def inspect_script(path, auto_generate_sizes=False):
    """读一个 .py 和同名 .csv。skip_reason 非空表示这次不能发布。"""
    path = os.path.abspath(path)
    job = {
        "path": path,
        "stem": os.path.splitext(os.path.basename(path))[0],
        "skip_reason": None,
        "warnings": [],
        "sizes": [],
        "group": "",
        "domain": "",
        "pnp_class": "",
        "image": "",
        "chain": [],
        "ports": 1,
        "length_unit": "mm",
        "first_port_endtypes": "",
        "category": "Default",
        "equipment": False,
        "tooltip": "",
        "tooltip_short": "",
        "tooltip_long": "",
        "params": [],
        "params_meta": [],
        "defaults": {},
    }
    if job["stem"].startswith("P3D_"):
        job["skip_reason"] = "基准脚本，不进元件库"
        return job
    try:
        text = _read_text(path)
    except OSError as exc:
        job["skip_reason"] = "无法读取脚本: " + str(exc)
        return job

    header = _parse_activate(text)
    if header is None:
        job["skip_reason"] = "没有 @activate"
        return job
    group = header["group"]
    job["group"] = group
    job["ports"] = header["ports"]
    job["length_unit"] = header["length_unit"]
    job["first_port_endtypes"] = header["first_port_endtypes"]
    job["tooltip_short"] = header["tooltip"] or job["stem"]
    job["tooltip_long"] = header["tooltip_long"] or job["tooltip_short"]
    job["tooltip"] = job["tooltip_short"]

    defaults = _parse_def_defaults(text, job["stem"])
    job["defaults"] = defaults
    job["params"] = _parse_params(text)
    job["params_meta"] = _parse_params_detailed(text, defaults)

    if group in _SKIP_GROUPS:
        job["skip_reason"] = _SKIP_GROUPS[group]
        return job
    if group in _EQUIPMENT_GROUPS:
        job["domain"] = "equipment"
        job["pnp_class"] = "Equipment"
        job["image"] = "Equipment"
        job["chain"] = []
        job["category"] = "Equipment"
        job["sizes"] = []
        csv_path = os.path.splitext(path)[0] + ".csv"
        job["csv_path"] = csv_path if os.path.isfile(csv_path) else ""
        return job

    spec = _GROUPS.get(group)
    if spec is None:
        job["skip_reason"] = "不支持的 Group: " + (group or "(空)")
        return job
    job["domain"] = spec["domain"]
    job["pnp_class"] = spec["pnp_class"]
    job["image"] = spec["image"]
    job["chain"] = list(spec["chain"])
    job["category"] = spec["category"]

    csv_path = os.path.splitext(path)[0] + ".csv"
    job["csv_path"] = csv_path
    if not os.path.isfile(csv_path):
        if auto_generate_sizes and job["params"] and defaults:
            csv_header, rows = _synthesize_default_rows(job["stem"], job["params"], defaults)
        else:
            job["skip_reason"] = "没有同名 CSV"
            return job
    else:
        try:
            csv_header, rows = _read_csv(csv_path)
        except OSError as exc:
            job["skip_reason"] = "无法读取 CSV: " + str(exc)
            return job
    if not rows:
        job["skip_reason"] = "CSV 没有数据行"
        return job

    missing = [name for name, typ in job["params"] if typ in _REQUIRED and name not in csv_header]
    if missing:
        job["skip_reason"] = "CSV 缺少参数: " + ", ".join(missing)
        return job

    seen = {}
    for index, row in enumerate(rows):
        preset = _preset_name(row, csv_header, index)
        if preset in seen:
            seen[preset] += 1
            preset = preset + "-" + str(seen[preset])
        else:
            seen[preset] = 1
        try:
            size = _build_size(job, spec, row, preset)
        except ValueError as exc:
            job["warnings"].append(preset + " 跳过: " + str(exc))
            continue
        job["sizes"].append(size)
    if not job["sizes"]:
        job["skip_reason"] = "没有可写入的尺寸行"
    else:
        unique = []
        for note in job["warnings"]:
            if note not in unique:
                unique.append(note)
        job["warnings"] = unique
    return job


def _synthesize_default_rows(stem, params, defaults):
    """Synthesizes multi-size preset rows from function signature defaults."""
    header = ["预设名", "DN"] + [name for name, _ in params]
    rows = []
    has_d = any(name == "D" for name, _ in params)
    if has_d:
        base_d = float(defaults.get("D", 114.3))
        dn_series = [
            (50, 60.3),
            (80, 88.9),
            (100, 114.3),
            (150, 168.3),
            (200, 219.1),
        ]
        for dn, od in dn_series:
            row = {"预设名": "%s-DN%d" % (stem.upper(), dn), "DN": str(dn)}
            ratio = od / base_d if base_d > 1.0 else 1.0
            for name, _typ in params:
                if name == "D":
                    row[name] = str(od)
                elif name == "ID":
                    row[name] = "%s-DN%d" % (stem.upper(), dn)
                elif name == "SW" and base_d > 1.0 and float(defaults.get("SW", 0.0) or 0.0) > 0.0:
                    sw_def = float(defaults.get("SW", 0.0))
                    row[name] = str(round(min(sw_def, od * 0.72) if od < base_d else sw_def * ratio, 1))
                else:
                    row[name] = str(defaults.get(name, 0.0))
            rows.append(row)
    else:
        row = {"预设名": "%s-STD" % stem.upper(), "DN": "100"}
        for name, _typ in params:
            row[name] = str(defaults.get(name, 0.0))
        rows.append(row)
    return header, rows


def ensure_script_csv(script_path: str, overwrite: bool = False) -> str:
    """Ensures a companion `.csv` preset table exists for `script_path`."""
    csv_path = os.path.splitext(script_path)[0] + ".csv"
    if os.path.isfile(csv_path) and not overwrite:
        return csv_path
    text = _read_text(script_path)
    stem = os.path.splitext(os.path.basename(script_path))[0]
    params = _parse_params(text)
    defaults = _parse_def_defaults(text, stem)
    header, rows = _synthesize_default_rows(stem, params, defaults)
    lines = [",".join(header)]
    for r in rows:
        lines.append(",".join(str(r.get(col, "")) for col in header))
    with io.open(csv_path, "w", encoding="utf-8-sig") as fp:
        fp.write("\n".join(lines) + "\n")
    return csv_path


def activate_body(text):
    """取 @activate(...) 括号内的文本，能正确跳过字符串里的括号。

    Tooltip 里常有 "(GB/T 151 BEM)"、"(API 608)" 这类括号，用 `[^)]*` 正则会
    在第一个 `)` 处截断，TooltipShort / TooltipLong 就整个取不到，发布出去的
    名称和描述会退化成脚本名。
    """
    idx = text.find("@activate")
    if idx < 0:
        return ""
    start = text.find("(", idx)
    if start < 0:
        return ""
    depth = 0
    quote = ""
    i = start
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = ""
        elif ch in "\"'":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[start + 1:i]
        i += 1
    return ""


def _parse_activate(text):
    body = activate_body(text)
    if not body:
        return None
    group = re.search(r'Group\s*=\s*[uU]?["\']([^"\']*)["\']', body)
    ports = re.search(r'Ports\s*=\s*["\']?(\d+)["\']?', body)
    tip = re.search(r'TooltipShort\s*=\s*[uU]?["\']([^"\']*)["\']', body)
    tip_long = re.search(r'TooltipLong\s*=\s*[uU]?["\']([^"\']*)["\']', body)
    unit = re.search(r'LengthUnit\s*=\s*[uU]?["\']([^"\']*)["\']', body)
    fpe = re.search(r'FirstPortEndtypes\s*=\s*[uU]?["\']([^"\']*)["\']', body)
    count = int(ports.group(1)) if ports else 1
    if count < 1:
        count = 1
    if count > 4:
        count = 4
    return {
        "group": group.group(1) if group else "",
        "ports": count,
        "tooltip": tip.group(1) if tip else "",
        "tooltip_long": tip_long.group(1) if tip_long else "",
        "length_unit": unit.group(1) if unit else "mm",
        "first_port_endtypes": fpe.group(1) if fpe else "",
    }


def _parse_params(text):
    found = []
    for match in re.finditer(
        r"@param\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z0-9_]+)",
        text,
    ):
        found.append((match.group(1), match.group(2)))
    return found


def _parse_params_detailed(text, defaults):
    result = []
    cur_group = "MainDimensions"
    for line in text.splitlines():
        gm = re.search(r'@group\s*\(\s*[uU]?["\']([^"\']+)["\']', line)
        if gm:
            cur_group = gm.group(1)
            continue
        pm = re.search(r"@param\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z0-9_]+)(.*)\)", line)
        if pm:
            pname = pm.group(1)
            ptype = pm.group(2)
            rest = pm.group(3)
            ts = re.search(r'TooltipShort\s*=\s*[uU]?["\']([^"\']*)["\']', rest)
            tl = re.search(r'TooltipLong\s*=\s*[uU]?["\']([^"\']*)["\']', rest)
            ask = re.search(r"Ask4Dist\s*=\s*(True|1)", rest)
            result.append({
                "name": pname,
                "type": ptype,
                "group": cur_group,
                "tooltip_short": ts.group(1) if ts else pname,
                "tooltip_long": tl.group(1) if tl else (ts.group(1) if ts else pname),
                "ask4dist": bool(ask),
                "default": defaults.get(pname, 0.0),
            })
    return result


def _parse_def_defaults(text, stem_hint=None):
    defaults = {}
    pattern = r"def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*s\s*,([^)]*)\)"
    for m in re.finditer(pattern, text, re.S):
        fn_name = m.group(1)
        sig = m.group(2)
        for part in sig.split(","):
            part = part.strip()
            if "=" not in part or part.startswith("*"):
                continue
            k, v = part.split("=", 1)
            k = k.strip()
            v = v.strip()
            if v.startswith(("u'", 'u"', "'", '"')):
                v = v.lstrip("u").strip("'\"")
                defaults[k] = v
            else:
                try:
                    defaults[k] = float(v) if ("." in v or "e" in v.lower()) else int(v)
                except ValueError:
                    defaults[k] = v
        if stem_hint and fn_name == stem_hint:
            break
    return defaults


def _read_text(path):
    with open(path, "rb") as handle:
        raw = handle.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8", errors="ignore")


def _read_csv(path):
    text = _read_text(path)
    lines = [line.strip("\r\n") for line in text.split("\n") if line.strip() != "" and not line.lstrip().startswith("#")]
    if not lines:
        return [], []
    header = [cell.strip() for cell in lines[0].split(",")]
    rows = []
    for line in lines[1:]:
        cells = [cell.strip() for cell in line.split(",")]
        if len(cells) < len(header):
            cells = cells + [""] * (len(header) - len(cells))
        elif len(cells) > len(header):
            cells = cells[:len(header)]
        rows.append(dict(zip(header, cells)))
    return header, rows


def _preset_name(row, header, index):
    for key in ("预设名", "名称", "规格名", "PartNumber"):
        if key in row and str(row[key]).strip():
            return str(row[key]).strip()
    if header and str(row.get(header[0], "")).strip():
        return str(row[header[0]]).strip()
    return "S" + str(index + 1)


def _build_size(job, spec, row, preset):
    call = {}
    parts = []
    for name, typ in job["params"]:
        raw = row.get(name, "")
        if raw is None or str(raw).strip() == "":
            if typ in _REQUIRED:
                raise ValueError("参数 " + name + " 为空")
            continue
        value = _coerce(typ, raw)
        call[name] = value
        parts.append(name + "=" + _format_param(typ, value))

    primary_od = _first_float(call, ("D", "D1", "D_CASE", "D_CONN"))
    nominals = []
    ods = []
    ends = []
    for index in range(1, job["ports"] + 1):
        explicit = _explicit_dn(row, index)
        od = _port_od(call, index, primary_od)
        if explicit is not None:
            nominal = explicit
            note = "csv"
        elif od is not None:
            mapped = _dn_for_od(od)
            if mapped is not None:
                nominal = mapped
                note = "od"
            else:
                nominal = od
                note = "fallback"
        else:
            nominal = 0.0
            note = "missing"
        if index == 1 and note == "fallback":
            job["warnings"].append(preset + " 没有 DN，公称直径暂用外径 " + _num(nominal))
        elif index == 1 and note == "missing":
            job["warnings"].append(preset + " 没有 DN 也没有外径 D")
        nominals.append(nominal)
        ods.append(od if od is not None else nominal)
        ends.append(_end_type(spec, row, index))

    short = _cell(row, "ShortDesc") or job["tooltip"]
    long_desc = _cell(row, "LongDesc") or (short + ", " + preset)
    iso = _cell(row, "IsoSymbol") or spec["iso"]
    skey = _cell(row, "SKEY")
    if skey and not _cell(row, "IsoSymbol"):
        if "SKEY=" in iso:
            iso = re.sub(r"SKEY=[^,]*", "SKEY=" + skey, iso)
        else:
            iso = iso + ",SKEY=" + skey
    weight = _optional_float(row.get("Weight"))
    return {
        "preset": preset,
        "call": call,
        "param_def": ",".join(parts),
        "nominals": nominals,
        "ods": ods,
        "ends": ends,
        "short": short[:255],
        "long": long_desc[:255],
        "item_code": (_cell(row, "ItemCode") or preset)[:255],
        "material": (_cell(row, "Material") or _cell(row, "MATL") or "")[:255],
        "standard": (_cell(row, "Standard") or "")[:255],
        "iso": iso[:255],
        "subtype": (_cell(row, "PartSubType") or "")[:255],
        "pressure": (_cell(row, "PressureClass") or "")[:255],
        "facing": (_cell(row, "Facing") or "")[:255],
        "schedule": (_cell(row, "Schedule") or "")[:255],
        "weight": weight,
    }


def _cell(row, key):
    value = row.get(key)
    if value is None:
        return ""
    return str(value).strip()


def _explicit_dn(row, index):
    keys = ("DN", "NominalDiameter", "公称直径") if index == 1 else ("DN" + str(index),)
    for key in keys:
        if key in row and str(row[key]).strip():
            return float(_clean_num(row[key]))
    return None


def _port_od(call, index, primary):
    if index == 1:
        return primary
    if index == 2:
        for key in ("D2", "DB"):
            if key in call:
                try:
                    return float(call[key])
                except (TypeError, ValueError):
                    pass
    if index >= 3 and "DB" in call:
        try:
            return float(call["DB"])
        except (TypeError, ValueError):
            pass
    key = "D" + str(index)
    if key in call:
        try:
            return float(call[key])
        except (TypeError, ValueError):
            pass
    return primary


def _first_float(call, keys):
    for key in keys:
        if key not in call:
            continue
        try:
            return float(call[key])
        except (TypeError, ValueError):
            continue
    return None


def _dn_for_od(od):
    for known, dn in _OD_TO_DN:
        if abs(float(od) - known) <= 0.6:
            return float(dn)
    return None


def _end_type(spec, row, index):
    key = "EndType" if index == 1 else "EndType" + str(index)
    text = _cell(row, key)
    if text:
        return text
    return spec["end"]


def _coerce(typ, raw):
    if typ in _NUMERIC:
        return float(_clean_num(raw))
    if typ == "INT":
        return int(float(_clean_num(raw)))
    if typ == "ENUM":
        return int(float(_clean_num(raw)))
    if typ == "BOOL":
        return str(raw).strip().lower() in ("1", "true", "yes", "y")
    text = str(raw).strip().replace(",", " ").replace("=", " ")
    return text


def _format_param(typ, value):
    if typ == "BOOL":
        return "1" if value else "0"
    if typ in _NUMERIC:
        return _num(value)
    if typ in ("INT", "ENUM"):
        return str(int(value))
    return str(value)


def _clean_num(raw):
    text = str(raw).strip().replace(" ", "")
    text = re.sub(r"^[Mm](?=\d)", "", text)
    match = re.match(r"^[+-]?\d+(?:\.\d+)?", text)
    if not match:
        raise ValueError("不是数字: " + str(raw))
    return match.group(0)


def _optional_float(raw):
    if raw is None or str(raw).strip() == "":
        return None
    return float(_clean_num(raw))


def _num(value):
    number = float(value)
    text = ("%.6f" % number).rstrip("0").rstrip(".")
    return text if text not in ("", "-0") else "0"
