# -*- coding: utf-8 -*-
"""元件库、等级库哪些名字是 Plant 写死的，哪些可以自建。

位置只有两处，不随年份变化：

- 元件库放在内容根的 CPak Common（或界面上选中的那个目录）。
- 等级库放在当前项目的等级库工作表 / Spec Sheets。

下面这些名字有特殊行为，不是合法名称白名单。新建时禁止覆盖同名原厂文件。
"""

import os
import re

# 功能区「添加支吊架」默认打开的等级。规格查看器不限制名字，例如 PipeSupports 也能用。
LOCKED_SUPPORT_SPEC_FILE = "PipeSupportsSpec.pspc"
PREFERRED_SUPPORT_SPEC_FILE = "PipeSupports.pspc"
# 原厂支吊架零件的 CatalogId。新零件也可以指向别的元件库，但这一份的内部名不能改。
LOCKED_SUPPORT_CATALOG_FILE = "SUPPORTS Catalog metric.acat"
LOCKED_SUPPORT_CATALOG_NAME = "SUPPORTS Catalog metric"

# 小写文件名 -> 为什么不能覆盖。依据是 Plant 2019/2026 安装目录里的明文字符串。
LOCKED_CATALOG_FILES = {
    "supports catalog metric.acat": "原厂支吊架零件的 CatalogId 就是 SUPPORTS Catalog metric，改名后旧零件会丢。",
    "supports catalog.acat": "英制支吊架原厂库，内部名 SUPPORTS Catalog 不能改。",
    "actuator catalog.acat": "执行机构命令按 Actuator Catalog 这个名字取库。",
    "nozzle catalog.acat": "设备管嘴按 NOZZLE Catalog 这个名字取库。",
    "placeholder metric catalog.pcat": "占位零件用的公制元件库，跟等级 PlaceHolder Metric 配对。",
    "placeholder imperial catalog.pcat": "占位零件用的英制元件库，跟等级 PlaceHolder Imperial 配对。",
    "customparts metric catalog.pcat": "PLANTCUSTOMPARTS 的公制自定义零件库。",
    "customparts imperial catalog.pcat": "PLANTCUSTOMPARTS 的英制自定义零件库。",
    "instrumentation metric.pcat": "原厂公制仪表库。仪表可以不进它，但不要新建同名空库盖掉。",
    "instrumentation imperial.pcat": "原厂英制仪表库。仪表可以不进它，但不要新建同名空库盖掉。",
}

LOCKED_SPEC_FILES = {
    "pipesupportsspec.pspc": "功能区「添加支吊架」默认打开 PipeSupportsSpec。规格查看器里的其他等级（如 PipeSupports）仍可插入。",
    "placeholder metric.pspc": "占位零件命令按单位打开 PlaceHolder Metric。",
    "placeholder imperial.pspc": "占位零件命令按单位打开 PlaceHolder Imperial。",
    "customparts metric.pspc": "自定义零件命令按单位打开 CustomParts Metric。",
    "customparts imperial.pspc": "自定义零件命令按单位打开 CustomParts Imperial。",
    "instrumentation metric.pspc": "不会出现在「设为当前等级」里。仪表零件不必放进这一份。",
    "instrumentation imperial.pspc": "不会出现在「设为当前等级」里。仪表零件不必放进这一份。",
}

_BAD_NAME = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def locked_catalog_reason(filename):
    return LOCKED_CATALOG_FILES.get(os.path.basename(filename or "").lower(), "")


def locked_spec_reason(filename):
    return LOCKED_SPEC_FILES.get(os.path.basename(filename or "").lower(), "")


def is_support_catalog(filename):
    base = os.path.basename(filename or "").lower()
    return "support" in base and base.endswith(".acat")


def clean_library_stem(name):
    """去掉用户输入里的扩展名和空白。空、路径分隔符、Windows 非法字符都拒绝。"""
    text = (name or "").strip().strip(".")
    lower = text.lower()
    for ext in (".pcat", ".acat", ".pspc", ".pspx"):
        if lower.endswith(ext):
            text = text[: -len(ext)].strip()
            lower = text.lower()
    if not text:
        raise ValueError("名称不能为空。")
    if _BAD_NAME.search(text) or text in (".", ".."):
        raise ValueError("名称不能包含 \\ / : * ? \" < > | 。")
    return text


def catalog_filename(name, kind="piping"):
    """配管用 .pcat，支吊架类用 .acat。kind 为 support / actuator / nozzle 时用 .acat。"""
    stem = clean_library_stem(name)
    ext = ".acat" if kind in ("support", "actuator", "nozzle") else ".pcat"
    filename = stem + ext
    reason = locked_catalog_reason(filename)
    if not reason:
        for locked_name, why in LOCKED_CATALOG_FILES.items():
            if os.path.splitext(locked_name)[0] == stem.lower():
                reason = why
                break
    if reason:
        raise ValueError("不能覆盖固定元件库 %s。%s" % (stem, reason))
    return filename, stem


def spec_filename(name):
    stem = clean_library_stem(name)
    filename = stem + ".pspc"
    reason = locked_spec_reason(filename)
    if reason:
        raise ValueError("不能新建覆盖固定等级 %s。%s请在列表里直接选它。" % (filename, reason))
    return filename, stem
