# -*- coding: utf-8 -*-
"""全量外形验收：把 pyscripts 下每个脚本跑一遍，校验能否生成有效实体。

检查项：
  1. 能否解析出 def 入口
  2. 能否在 OCC 沙箱里执行成功
  3. 是否生成了至少一个有效实体
  4. 实体包围盒是否有意义（非零体积、无 NaN/Inf）
  5. 记录失败脚本的真实异常

用法：python tools/verify_shapes.py [--json 输出文件]
"""
from __future__ import print_function

import io
import json
import math
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from plant3d_occ.runner.sandbox import run_script_in_sandbox  # noqa: E402


def iter_scripts(root):
    """枚举需要验收的脚本：跳过基底脚本与热更新临时文件。"""
    for dirpath, dirnames, filenames in os.walk(root):
        # 跳过缓存目录与"依赖备查"目录：后者是组件 star-import 的兄弟模块，
        # 没有可用入口，本来就不是构件，跑它只会制造噪声。
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", "_dependencies")]
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            if fn.startswith("_") or fn.startswith("dev_"):
                continue
            yield os.path.join(dirpath, fn)


def shape_bounds(shapes):
    """所有形状的联合包围盒；同时暴露 NaN/Inf。"""
    from OCC.Core.Bnd import Bnd_Box
    from OCC.Core.BRepBndLib import brepbndlib

    box = Bnd_Box()
    for sh in shapes:
        # AddOptimal 才是精确解算；brepbndlib.Add 对回转体会按容差放大
        brepbndlib.AddOptimal(sh, box, False, False)
    if box.IsVoid():
        return None
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    return (xmin, ymin, zmin, xmax, ymax, zmax)


def invalid_shapes(shapes):
    """返回不通过的 B-Rep 有效性的实体数量。

    只看包围盒非空是不够的：损坏的壳同样有包围盒，
    但渲染出来是破面、布尔与标注都会出错。几何质量必须过 BRepCheck。
    """
    from OCC.Core.BRepCheck import BRepCheck_Analyzer

    bad = 0
    for sh in shapes:
        try:
            if not BRepCheck_Analyzer(sh).IsValid():
                bad += 1
        except Exception:
            bad += 1
    return bad


def check_one(path):
    """跑单个脚本，返回结果字典。"""
    name = os.path.basename(path)
    res = {"script": name, "path": path, "ok": False, "reason": "", "detail": ""}
    try:
        session, entry, shapes = run_script_in_sandbox(path)
    except Exception as exc:  # noqa: BLE001
        res["reason"] = "执行异常"
        res["detail"] = "%s: %s" % (type(exc).__name__, exc)
        lines = traceback.format_exc().strip().splitlines()
        # 取指向脚本自身的那一帧，便于定位
        for ln in reversed(lines):
            if ".py\"" in ln and "plant3d_occ" not in ln:
                res["detail"] += " | " + ln.strip()
                break
        return res

    if not entry:
        res["reason"] = "未找到 def 入口"
        return res

    if not shapes:
        res["reason"] = "未生成实体"
        return res

    try:
        bounds = shape_bounds(shapes)
    except Exception as exc:  # noqa: BLE001
        res["reason"] = "包围盒计算失败"
        res["detail"] = "%s: %s" % (type(exc).__name__, exc)
        return res

    if bounds is None:
        res["reason"] = "包围盒为空（实体无效）"
        return res

    vals = list(bounds)
    if any(math.isnan(v) or math.isinf(v) for v in vals):
        res["reason"] = "包围盒含 NaN/Inf"
        res["detail"] = str(vals)
        return res

    xmin, ymin, zmin, xmax, ymax, zmax = vals
    lx, ly, lz = xmax - xmin, ymax - ymin, zmax - zmin
    res["dims"] = [round(lx, 2), round(ly, 2), round(lz, 2)]
    res["shapeCount"] = len(shapes)

    if max(lx, ly, lz) <= 1e-6:
        res["reason"] = "实体尺寸为零"
        return res

    bad_brep = invalid_shapes(shapes)
    res["invalidShapeCount"] = bad_brep
    if bad_brep > 0:
        res["reason"] = "B-Rep 无效（壳已损坏，渲染/布尔会出错）"
        return res

    # 端口是可选信息，缺失不算失败，但记录以便人工核查
    res["portCount"] = len(getattr(session, "ports", []) or [])
    res["gripCount"] = len(getattr(session, "grips", []) or [])

    res["ok"] = True
    return res


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    root = os.path.join(repo_root, "pyscripts", "custom_scripts")
    if not os.path.isdir(root):
        root = os.path.join(repo_root, "pyscripts")
    out_json = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--json" and i + 1 < len(args):
            out_json = args[i + 1]
            i += 2
        elif args[i] == "--root" and i + 1 < len(args):
            root = os.path.abspath(args[i + 1])
            i += 2
        else:
            i += 1

    scripts = list(iter_scripts(root))
    results = []
    for i, path in enumerate(scripts, 1):
        rel = os.path.relpath(path, root)
        r = check_one(path)
        r["rel"] = rel
        results.append(r)
        status = "OK  " if r["ok"] else "FAIL"
        extra = ""
        if r["ok"]:
            extra = "dims=%s solids=%d ports=%d" % (r.get("dims"), r.get("shapeCount", 0), r.get("portCount", 0))
        else:
            extra = "%s %s" % (r["reason"], r["detail"])
        print("[%3d/%d] %s %-46s %s" % (i, len(scripts), status, rel, extra))

    ok = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]
    no_ports = [r for r in ok if r.get("portCount", 0) == 0]
    no_grips = [r for r in ok if r.get("gripCount", 0) == 0]

    print("\n" + "=" * 78)
    print(u"外形验收：共 %d 个脚本，成功 %d，失败 %d" % (len(results), len(ok), len(bad)))
    print(u"其中：无端口 %d 个，无尺寸标注 %d 个（这两项不阻断，供人工核查）"
          % (len(no_ports), len(no_grips)))

    if bad:
        print(u"\n失败清单：")
        for r in bad:
            print(u"  %-46s %s %s" % (r["rel"], r["reason"], r["detail"]))

    if out_json:
        with io.open(out_json, "w", encoding="utf-8") as fp:
            fp.write(json.dumps({
                "total": len(results),
                "ok": len(ok),
                "failed": len(bad),
                "withoutPorts": [r["rel"] for r in no_ports],
                "withoutGrips": [r["rel"] for r in no_grips],
                "results": results,
            }, ensure_ascii=False, indent=2))

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
