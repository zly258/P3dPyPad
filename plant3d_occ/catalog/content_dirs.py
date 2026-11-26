# -*- coding: utf-8 -*-
"""从 Plant 的 PLANTCONTENTFOLDER 找出各版本的 CPak Common。

Plant 把内容根目录存在注册表系统变量里，不是写死盘符：

    HKLM\\Software\\Autodesk\\AutoCAD\\<Rxx.x>\\<ACAD-xxxx>\\Variables\\PLANTCONTENTFOLDER
    HKCU 同路径若存在则优先于 HKLM。

另外认进程环境变量 PLANTCONTENTFOLDER 和 PLANT3D_CONTENT_DIR。
"""

import os
import re

_YEAR_RE = re.compile(r"Plant 3D (\d{4})")


def to_cpak_common(path):
    """内容根目录补上 CPak Common；已经指到该目录则原样返回。不存在则返回空串。"""
    text = (path or "").strip().strip('"').rstrip("\\/")
    if not text:
        return ""
    base = os.path.basename(text).lower()
    if base == "cpak common" and os.path.isdir(text):
        return os.path.normpath(text)
    nested = os.path.join(text, "CPak Common")
    if os.path.isdir(nested):
        return os.path.normpath(nested)
    if os.path.isdir(text):
        return os.path.normpath(text)
    return ""


def _year_of(path):
    match = _YEAR_RE.search(path or "")
    return int(match.group(1)) if match else 0


def _registry_content_roots():
    """[(path, hive_name)]。只收集键的默认值，不猜盘符。"""
    if os.name != "nt":
        return []
    try:
        import winreg
    except ImportError:
        return []
    found = []
    roots = (
        (winreg.HKEY_CURRENT_USER, "HKCU", r"Software\Autodesk\AutoCAD"),
        (winreg.HKEY_LOCAL_MACHINE, "HKLM", r"Software\Autodesk\AutoCAD"),
        (winreg.HKEY_LOCAL_MACHINE, "HKLM", r"Software\WOW6432Node\Autodesk\AutoCAD"),
    )
    for hive, hive_name, autocad in roots:
        for release in _subkeys(hive, autocad):
            release_path = autocad + "\\" + release
            for product in _subkeys(hive, release_path):
                key_path = release_path + "\\" + product + r"\Variables\PLANTCONTENTFOLDER"
                value = _default_value(hive, key_path)
                if value:
                    found.append((value, "%s %s" % (hive_name, release)))
    return found


def _subkeys(hive, path):
    import winreg
    names = []
    try:
        with winreg.OpenKey(hive, path) as key:
            index = 0
            while True:
                try:
                    names.append(winreg.EnumKey(key, index))
                    index += 1
                except OSError:
                    break
    except OSError:
        return []
    return names


def _default_value(hive, path):
    import winreg
    try:
        with winreg.OpenKey(hive, path) as key:
            value, _typ = winreg.QueryValueEx(key, "")
    except OSError:
        return ""
    if isinstance(value, str):
        return value.strip()
    return ""


def _disk_content_dirs():
    """注册表没有时，再在常见盘符上找 AutoCAD Plant 3D * Content\\CPak Common。"""
    try:
        import glob
    except ImportError:
        return []
    found = []
    for drive in ("C:", "D:", "E:"):
        pattern = os.path.join(drive + "\\", "AutoCAD Plant 3D * Content", "CPak Common")
        found.extend(glob.glob(pattern))
    return found


def list_cpak_common_dirs():
    """已安装的 CPak Common，新年份在前。

    每项是 {"path", "year", "source"}。同一路径只保留一条，HKCU 优先于 HKLM。
    """
    ranked = []
    for env_name in ("PLANTCONTENTFOLDER", "PLANT3D_CONTENT_DIR"):
        env_path = to_cpak_common(os.environ.get(env_name, ""))
        if env_path:
            ranked.append((env_path, _year_of(env_path), "环境变量 " + env_name, 0))
    for raw, source in _registry_content_roots():
        path = to_cpak_common(raw)
        if not path:
            continue
        priority = 1 if source.startswith("HKCU") else 2
        ranked.append((path, _year_of(path), "注册表 " + source, priority))
    for raw in _disk_content_dirs():
        path = to_cpak_common(raw)
        if path:
            ranked.append((path, _year_of(path), "磁盘", 3))

    ranked.sort(key=lambda item: (-item[1], item[3], item[0].lower()))
    seen = set()
    result = []
    for path, year, source, _priority in ranked:
        key = os.path.normcase(path)
        if key in seen:
            continue
        seen.add(key)
        result.append({"path": path, "year": year, "source": source})
    return result
