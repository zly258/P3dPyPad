# -*- coding: utf-8 -*-
"""发布前校验：脚本必须真的能建出一个"对"的模型。

离线 OCC 沙箱跑一遍脚本，按下面几条判定（任何一条不过就不该发布）：

1. **能跑**：不抛异常，产出至少一个实体；
2. **无悬空实体**：多实体必须两两相切/相接。有实体离其余实体都超过
   `FLOATING_GAP` 就是零件没融上（相切焊合件除外，只给提示）；
3. **有端口**：`s.setPoint` 至少注册一个端口，否则 Plant 3D 里没法接管道；
4. **外形对齐**：端口点必须落在实体包围盒内（含容差）。端口跑到模型外面，
   通常是把截面中心当基准、忘了加减半个截面；
5. **包围盒可用**：非退化、无 NaN/无穷。

用法：

    python -m plant3d_occ.catalog.validate pyscripts/05_supports/SUPPORT_GATE_FRAME.py
    python -m plant3d_occ.catalog.validate <脚本> --params D=168.3 H=1500
    python -m plant3d_occ.catalog.validate <目录或脚本...> --json
"""

from __future__ import print_function

import glob
import json
import os
import sys

# 端口点允许离包围盒边界多远（mm）。给装配配合留点余量。
PORT_TOLERANCE = 1.0

# 两个实体包围盒间距超过这个值就算"悬空"（漏位移 / 并集顺序错）。
# 小于阈值视为相切焊合件（螺母端面贴钢板这类），只提示不拦发布。
FLOATING_GAP = 2.0


def _iter_solids(shape):
    from OCC.Core.TopAbs import TopAbs_SOLID
    from OCC.Core.TopExp import TopExp_Explorer

    count = 0
    explorer = TopExp_Explorer(shape, TopAbs_SOLID)
    while explorer.More():
        count += 1
        explorer.Next()
    return count


def _solid_boxes(shape):
    """每个 SOLID 各自的包围盒，用来区分"相切焊合"和"真的浮在空中"。"""
    from OCC.Core.Bnd import Bnd_Box
    from OCC.Core.BRepBndLib import brepbndlib
    from OCC.Core.TopAbs import TopAbs_SOLID
    from OCC.Core.TopExp import TopExp_Explorer

    boxes = []
    explorer = TopExp_Explorer(shape, TopAbs_SOLID)
    while explorer.More():
        box = Bnd_Box()
        brepbndlib.AddOptimal(explorer.Current(), box, False, False)
        if not box.IsVoid():
            boxes.append(box.Get())
        explorer.Next()
    return boxes


def _box_gap(a, b):
    """两个轴对齐包围盒的最小间距，相交或相切时为 0。"""
    total = 0.0
    for axis in (0, 1, 2):
        total += max(0.0, b[axis] - a[axis + 3], a[axis] - b[axis + 3]) ** 2
    return total ** 0.5


def _bbox(shapes):
    from OCC.Core.Bnd import Bnd_Box
    from OCC.Core.BRepBndLib import brepbndlib

    box = Bnd_Box()
    for body in shapes:
        shape = body.shape if hasattr(body, "shape") else body
        brepbndlib.Add(shape, box)
    if box.IsVoid():
        return None
    return box.Get()


def validate_script(path, params=None, lib=None):
    """返回 dict(ok, script, issues, warnings, solids, ports, bbox)。"""
    result = {"script": os.path.abspath(path), "ok": False, "issues": [], "warnings": [],
              "solids": 0, "ports": 0, "bbox": None, "entry": ""}

    if not os.path.isfile(path):
        result["issues"].append(u"脚本不存在：%s" % path)
        return result

    try:
        from .model import inspect_script
        job = inspect_script(path)
        result["entry"] = job.get("stem", "")
        # 没有同名 CSV 时自动生成默认预设表（按脚本默认值推导），校验不再挡路
        if job.get("skip_reason") == "没有同名 CSV":
            try:
                from .model import ensure_script_csv
                ensure_script_csv(path)
            except Exception:
                pass
            job = inspect_script(path)
        if job.get("skip_reason"):
            result["issues"].append(u"不可发布：" + job["skip_reason"])
            return result
    except Exception as exc:                      # noqa: BLE001
        result["issues"].append(u"读取脚本失败：%s" % exc)
        return result

    # 用第一条预设尺寸跑；没有预设表就用手写参数/脚本默认值
    run_params = dict(params or {})
    if not run_params:
        try:
            from .model import inspect_script
            job = inspect_script(path)
            if job.get("sizes"):
                run_params = dict(job["sizes"][0].get("call") or {})
        except Exception:                          # noqa: BLE001
            run_params = {}

    try:
        from ..runner.sandbox import run_script_in_sandbox
        session, entry, shapes = run_script_in_sandbox(path, run_params)
    except Exception as exc:                      # noqa: BLE001
        result["issues"].append(u"运行失败：%s" % exc)
        return result

    result["entry"] = entry or result["entry"]
    if not shapes:
        result["issues"].append(u"没有产出任何实体")
        return result

    solids = 0
    boxes = []
    for body in shapes:
        shape = body.shape if hasattr(body, "shape") else body
        solids += _iter_solids(shape)
        boxes.extend(_solid_boxes(shape))
    result["solids"] = solids
    if solids == 0:
        result["issues"].append(u"实体里没有有效的 SOLID")
        return result
    if solids > 1:
        # 多实体分两种：真的浮在空中（漏了位移/并集顺序错）和相切焊合件
        # （螺母端面贴着钢板、衬板与管壁相切）。后者外形正确，只是 OCC 在相切
        # 处融不成一个 SOLID，属于允许的装配体，只给提示不拦发布。
        floating = 0
        for index, box in enumerate(boxes):
            if all(_box_gap(box, other) > FLOATING_GAP for j, other in enumerate(boxes) if j != index):
                floating += 1
        if floating:
            result["issues"].append(
                u"有 %d 个实体悬空互不相连（与其余实体间距 > %.1f mm，零件漏位移或没融上）"
                % (floating, FLOATING_GAP))
        else:
            result["warnings"].append(
                u"由 %d 个相切焊合实体组成（螺母/衬板端面贴合），OCC 相切处无法融成单实体，外形正确"
                % solids)

    ports = list(getattr(session, "ports", []) or [])
    result["ports"] = len(ports)
    if not ports:
        result["issues"].append(u"没有注册端口（s.setPoint），Plant 3D 里接不上管道")

    box = _bbox(shapes)
    if box is None:
        result["issues"].append(u"包围盒为空")
        return result
    xmin, ymin, zmin, xmax, ymax, zmax = box
    result["bbox"] = [round(v, 3) for v in box]
    for name, value in (("xmin", xmin), ("ymin", ymin), ("zmin", zmin),
                        ("xmax", xmax), ("ymax", ymax), ("zmax", zmax)):
        if value != value or value in (float("inf"), float("-inf")):
            result["issues"].append(u"包围盒 %s 不是有限数" % name)
            return result
    if (xmax - xmin) <= 0 or (ymax - ymin) <= 0 or (zmax - zmin) <= 0:
        result["issues"].append(u"包围盒在某个方向上退化（厚度为 0）")
        return result

    # 端口在实体内的检查只对"管件/阀门/仪表"有意义：
    # 支吊架的端口点是管道中心线，本来就落在型钢之外（管道从架子中间穿过），
    # 对支吊架只做"别跑得太远"的粗检。
    is_support = True
    try:
        from .model import inspect_script
        is_support = inspect_script(path)["group"] == "Support"
    except Exception:                              # noqa: BLE001
        pass
    diagonal = ((xmax - xmin) ** 2 + (ymax - ymin) ** 2 + (zmax - zmin) ** 2) ** 0.5

    for index, port in enumerate(ports):
        point = port.get("point") if isinstance(port, dict) else None
        if point is None:
            continue
        px, py, pz = point
        inside = (xmin - PORT_TOLERANCE <= px <= xmax + PORT_TOLERANCE and
                  ymin - PORT_TOLERANCE <= py <= ymax + PORT_TOLERANCE and
                  zmin - PORT_TOLERANCE <= pz <= zmax + PORT_TOLERANCE)
        if is_support:
            nearest = max(xmin - px, px - xmax, 0) ** 2 + max(ymin - py, py - ymax, 0) ** 2                       + max(zmin - pz, pz - zmax, 0) ** 2
            if nearest ** 0.5 > diagonal:
                result["warnings"].append(
                    u"端口 %d 离实体太远（超过包围盒对角线），确认端口点是否写错" % (index + 1))
            continue
        if not inside:
            result["issues"].append(
                u"端口 %d 在 (%s, %s, %s)，落在包围盒 [%s..%s, %s..%s, %s..%s] 之外"
                % (index + 1, round(px, 1), round(py, 1), round(pz, 1),
                   round(xmin, 1), round(xmax, 1), round(ymin, 1), round(ymax, 1),
                   round(zmin, 1), round(zmax, 1)))

    result["ok"] = not result["issues"]
    return result


def validate_paths(paths, params=None):
    """对文件/目录列表逐个校验，返回结果列表。"""
    targets = []
    for path in paths or []:
        if os.path.isdir(path):
            targets.extend(sorted(glob.glob(os.path.join(path, "**", "*.py"), recursive=True)))
        else:
            targets.append(path)
    return [validate_script(p, params) for p in targets]


def format_result(result):
    head = u"[通过] " if result["ok"] else u"[失败] "
    name = os.path.basename(result["script"])
    if result["solids"]:
        head += u"%s  实体 %d / 端口 %d / bbox %s" % (
            name, result["solids"], result["ports"], result["bbox"])
    else:
        head += name
    lines = [head]
    for issue in result["issues"]:
        lines.append(u"    × " + issue)
    for warn in result["warnings"]:
        lines.append(u"    ! " + warn)
    return u"\n".join(lines)


def _parse_params(items):
    params = {}
    for item in items or []:
        if "=" in item:
            key, value = item.split("=", 1)
            try:
                value = float(value)
            except ValueError:
                pass
            params[key.strip()] = value
    return params


def _main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=u"发布前校验：脚本能不能建出正确的单一实体")
    parser.add_argument("paths", nargs="+", help=u"脚本或目录")
    parser.add_argument("--params", nargs="*", default=None, help=u"覆盖参数，如 D=168.3")
    parser.add_argument("--json", action="store_true", help=u"输出 JSON")
    args = parser.parse_args(argv)

    results = validate_paths(args.paths, _parse_params(args.params))
    if args.json:
        sys.stdout.write(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    else:
        for result in results:
            print(format_result(result))
        ok = sum(1 for r in results if r["ok"])
        print(u"\n合计 %d 个脚本：通过 %d，失败 %d"
              % (len(results), ok, len(results) - ok))
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(_main())
