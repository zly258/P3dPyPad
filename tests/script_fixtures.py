# -*- coding: utf-8 -*-
"""测试用的脚本 fixture。

脚本库（pyscripts/ 下的 ZD_* / HG_* 批量构件）可能被整体移除，只剩样板脚本。
这里统一提供「能拿到就用、拿不到就跳过」的入口，避免每个测试各写一份兜底逻辑。
"""

import glob
import os

PKG_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_ROOT = os.path.join(PKG_ROOT, "pyscripts")

# 样板脚本：曾是全体素与 CSG 基准测试脚本，目录整理后已移除；兜底退化为 template_scripts()。
BENCH_SCRIPT = None


def _glob(pattern):
    return sorted(glob.glob(os.path.join(SCRIPTS_ROOT, pattern), recursive=True))


def zd_scripts():
    """CD/ZD 2010 电力标准批量构件（supports/ 库，也兼容旧 custom_scripts 位置）。"""
    found = _glob(os.path.join("supports", "cd_zd2010", "**", "ZD_*.py"))
    found.extend(_glob(os.path.join("custom_scripts", "cd_zd2010", "**", "ZD_*.py")))
    found.extend(_glob(os.path.join("custom", "**", "ZD_*.py")))
    return sorted(set(found))


def hg_scripts():
    """化工 HG/T 21629 批量构件（supports/ 库，也兼容旧 custom_scripts 位置）。"""
    found = _glob(os.path.join("supports", "hgt_21629", "**", "HG_*.py"))
    found.extend(_glob(os.path.join("custom_scripts", "hgt_21629", "**", "HG_*.py")))
    found.extend(_glob(os.path.join("hgt_21629", "**", "HG_*.py")))
    return sorted(set(found))


def template_scripts():
    """custom_scripts 下按构件类别分组的工业模板构件。

    目录名与 pyscripts 的分层约定一致（01 管件起，06 设备止），新增类别时只改这里。
    """
    groups = ("01_pipe_fittings", "02_flanges_gaskets", "03_valves",
              "04_instruments", "05_supports", "06_equipment")
    found = []
    for group in groups:
        found.extend(_glob(os.path.join("custom_scripts", group, "*.py")))
        found.extend(_glob(os.path.join(group, "*.py")))
    return sorted(found)


def all_scripts():
    return _glob("**/*.py")


def first_renderable_script():
    """任意一个能建模的脚本：优先批量构件，退化到模板脚本。"""
    for candidate in hg_scripts() + zd_scripts() + template_scripts():
        return candidate
    return None


def first_publishable_script(group=None):
    """第一个 inspect_script 认为可发布的脚本；没有就返回 None。

    传 group 时只接受该构件大类（如 "Support"）。发布链路是按 SUPPORTS 库
    走的，pyscripts 里又同时有弯头/阀门等类别，所以调用方需要显式指定类别。
    """
    from plant3d_occ.catalog.model import inspect_script

    fallback = None
    for candidate in hg_scripts() + zd_scripts() + template_scripts():
        job = inspect_script(candidate)
        if job["skip_reason"]:
            continue
        if group is None or job.get("group") == group:
            return candidate
        if fallback is None:
            fallback = candidate
    return fallback


def library_present():
    """批量脚本库是否还在（用于决定整组测试跳过还是执行）。"""
    return bool(hg_scripts() or zd_scripts() or template_scripts())
