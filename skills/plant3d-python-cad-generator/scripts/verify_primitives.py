# -*- coding: utf-8 -*-
"""Plant 3D 原语契约校验。

基准来自 skills/plant3d-python-cad-generator/references/api/01_primitives_and_transforms.md
（即 PD1746 / PD4214-L 与 variants.zip 反编译结论），逐项比对 plant3d_occ 的实现。

校验项：
  * 基准点与各轴向包络（包围盒）
  * 关键字参数语义（如 CYLINDER 的 O 是内孔半径、ARC3D 的 D 是半径）
  * 变换正确性（translate / rotateX-Y-Z）
  * CSG 正确性（uniteWith / subtractFrom / intersectWith 的体积关系）

用法：python tools/verify_primitives.py
"""
from __future__ import print_function

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from OCC.Core.Bnd import Bnd_Box                      # noqa: E402
from OCC.Core.BRepBndLib import brepbndlib           # noqa: E402
from OCC.Core.BRepGProp import brepgprop             # noqa: E402
from OCC.Core.GProp import GProp_GProps              # noqa: E402

from plant3d_occ.core.session import OccSession       # noqa: E402
from plant3d_occ import primitives as P               # noqa: E402

TOL = 0.35  # 包围盒容差（mm），B-Rep 离散化与浮点误差

results = []


def bbox(shape):
    box = Bnd_Box()
    # 必须用 AddOptimal：brepbndlib.Add 对回转体（圆环/球面）会把包围盒按
    # 曲面容差放大——MakeTorus(50,10) 会被算成 ±64.94，而精确值就是 ±60。
    brepbndlib.AddOptimal(shape, box, False, False)
    if box.IsVoid():
        return None
    return box.Get()


def volume(shape):
    props = GProp_GProps()
    brepgprop.VolumeProperties(shape, props)
    return props.Mass()


def check(name, shape, expect):
    """expect: {'x':(lo,hi), 'y':(lo,hi), 'z':(lo,hi)}，None 表示该轴不校验。"""
    b = bbox(shape)
    if b is None:
        results.append((name, False, "包围盒为空"))
        return
    xmin, ymin, zmin, xmax, ymax, zmax = b
    got = {"x": (xmin, xmax), "y": (ymin, ymax), "z": (zmin, zmax)}

    bad = []
    for axis, want in expect.items():
        if want is None:
            continue
        lo, hi = got[axis]
        if abs(lo - want[0]) > TOL or abs(hi - want[1]) > TOL:
            bad.append("%s 期望[%.2f,%.2f] 实际[%.2f,%.2f]" % (axis.upper(), want[0], want[1], lo, hi))

    detail = "%s 体积=%.1f" % (
        " ".join("%s[%.1f,%.1f]" % (a.upper(), got[a][0], got[a][1]) for a in ("x", "y", "z")),
        volume(shape))
    results.append((name, not bad, ("；".join(bad) + "  " if bad else "") + detail))


def new_s():
    return OccSession()


def main():
    s = new_s()

    # ---- BOX: 质心在原点；H→X, L→Y, W→Z（非直觉映射）----
    check("BOX(L=10,W=20,H=30)",
          P.BOX(s, L=10.0, W=20.0, H=30.0).shape,
          {"x": (-15, 15), "y": (-5, 5), "z": (-10, 10)})

    # ---- CYLINDER: 底面圆心原点，H 沿 +Z ----
    check("CYLINDER(R=10,H=30)",
          P.CYLINDER(s, R=10.0, H=30.0).shape,
          {"x": (-10, 10), "y": (-10, 10), "z": (0, 30)})

    solid_v = volume(P.CYLINDER(s, R=10.0, H=30.0).shape)
    bore_v = volume(P.CYLINDER(s, R=10.0, H=30.0, O=6.0).shape)
    expect_bore = math.pi * (100 - 36) * 30
    ok = abs(bore_v - expect_bore) / expect_bore < 0.06
    results.append(("CYLINDER O=6 为内孔半径（应挖掉 6 通道）", ok,
                    "实心=%.0f 空心=%.0f 期望空心≈%.0f" % (solid_v, bore_v, expect_bore)))

    check("CYLINDER(R1=10,R2=20,H=30) 椭圆柱",
          P.CYLINDER(s, R1=10.0, R2=20.0, H=30.0).shape,
          {"x": (-10, 10), "y": (-20, 20), "z": (0, 30)})

    # ---- CONE: 底面半径 R1 在 Z=0，顶面 R2 在 Z=H ----
    check("CONE(R1=10,R2=5,H=30)",
          P.CONE(s, R1=10.0, R2=5.0, H=30.0).shape,
          {"x": (-10, 10), "y": (-10, 10), "z": (0, 30)})

    check("CONE(E=8) 顶面沿 +X 偏心",
          P.CONE(s, R1=10.0, R2=5.0, H=30.0, E=8.0).shape,
          {"x": (-10, 13), "z": (0, 30)})

    # ---- TORUS: 环心原点，中心线在 XY 平面 ----
    check("TORUS(R1=50,R2=10)",
          P.TORUS(s, R1=50.0, R2=10.0).shape,
          {"x": (-60, 60), "y": (-60, 60), "z": (-10, 10)})

    # ---- HALFSPHERE: 极点朝 +Z，赤道在 Z=0 ----
    check("HALFSPHERE(R=10)",
          P.HALFSPHERE(s, R=10.0).shape,
          {"x": (-10, 10), "y": (-10, 10), "z": (0, 10)})

    # ---- ELLIPSOIDHEAD: 底面圆心原点，沿 +Z ----
    b = bbox(P.ELLIPSOIDHEAD(s, R=10.0).shape)
    ok = b is not None and abs(b[2]) < TOL and b[5] > 1.0
    results.append(("ELLIPSOIDHEAD(R=10) 底面在 Z=0、沿 +Z 生长", ok,
                    "Z[%.2f,%.2f]" % (b[2], b[5]) if b else "包围盒为空"))

    # ---- ELLIPSOIDSEGMENT: 质心原点，RX 沿 X / RY 沿 Y、Z ----
    check("ELLIPSOIDSEGMENT(RX=10,RY=5)",
          P.ELLIPSOIDSEGMENT(s, RX=10.0, RY=5.0).shape,
          {"x": (-10, 10), "y": (-5, 5), "z": (-5, 5)})

    # ---- PYRAMID / ROUNDRECT / SPHERESEGMENT: 底面在 Z=0 沿 +Z ----
    for label, fn, kw, hi in [
        ("PYRAMID(L=20,W=10,H=15)", P.PYRAMID, dict(L=20.0, W=10.0, H=15.0), 15.0),
        ("ROUNDRECT(L=20,W=10,H=15,R2=4)", P.ROUNDRECT, dict(L=20.0, W=10.0, H=15.0, R2=4.0), 15.0),
        # SPHERESEGMENT 的 P 是球台高度，必须 <= R - Q，否则几何上不存在；
        # 用 R=10,P=5,Q=0（下半球面上方 5mm 的球台）来验证生长区间。
        ("SPHERESEGMENT(R=10,P=5,Q=0)", P.SPHERESEGMENT, dict(R=10.0, P=5.0, Q=0.0), 5.0),
    ]:
        try:
            b = bbox(fn(s, **kw).shape)
        except Exception as exc:  # noqa: BLE001
            results.append((label, False, "抛异常 %s: %s" % (type(exc).__name__, exc)))
            continue
        ok = b is not None and abs(b[2]) < TOL and abs(b[5] - hi) < TOL
        results.append((label, ok, "Z[%.2f,%.2f] 期望起于0、止于%.1f" % (b[2], b[5], hi) if b else "包围盒为空"))

    # ---- ARC3D: D 是半径（非直径）----
    try:
        thin = bbox(P.ARC3D(s, D=10.0, R=50.0, A=90.0).shape)
        fat = bbox(P.ARC3D(s, D=20.0, R=50.0, A=90.0).shape)
        if thin and fat:
            # D 是管半径：包络 = R + D，故 D 增大 10 时包络也增大 10。
            # 若把 D 误当直径，包络只增大 5，弯头会小一半。
            ok = abs((fat[3] - fat[0]) - (thin[3] - thin[0]) - 10.0) < 1.5
            results.append(("ARC3D 的 D 为半径（D+10 则包络+10）", ok,
                            "D=10 包络X宽=%.2f  D=20 包络X宽=%.2f" % (thin[3] - thin[0], fat[3] - fat[0])))
        else:
            results.append(("ARC3D 的 D 为半径", False, "包围盒为空"))
    except Exception as exc:  # noqa: BLE001
        results.append(("ARC3D 的 D 为半径", False, "抛异常 %s: %s" % (type(exc).__name__, exc)))

    # ---- 变换 ----
    moved = P.BOX(s, L=10.0, W=20.0, H=30.0).translate((100.0, 200.0, 300.0))
    b = bbox(moved.shape)
    ok = b is not None and abs((b[0] + b[3]) / 2 - 100.0) < TOL and abs((b[2] + b[5]) / 2 - 300.0) < TOL
    results.append(("translate 位移生效", ok,
                    "中心=(%.1f,%.1f,%.1f) 期望(100,200,300)" % ((b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2)))

    # rotateX(90): 原 +Y 应转到 +Z
    rot = P.BOX(s, L=10.0, W=20.0, H=30.0).rotateX(90.0)
    b = bbox(rot.shape)
    # 旋转前 Y 跨度=10、Z 跨度=20；绕 X 转 90° 后 Y 跨度=20、Z 跨度=10
    ok = b is not None and abs((b[4] - b[1]) - 20.0) < TOL and abs((b[5] - b[2]) - 10.0) < TOL
    results.append(("rotateX(90) 轴向正确（Y span↔Z span）", ok,
                    "Y span=%.1f(期望20) Z span=%.1f(期望10)" % (b[4] - b[1], b[5] - b[2]) if b else "包围盒为空"))

    # rotateY(90): 原 +Z 应转到 +X
    roty = P.CYLINDER(s, R=5.0, H=40.0).rotateY(90.0)
    b = bbox(roty.shape)
    ok = b is not None and abs((b[3] - b[0]) - 40.0) < TOL and abs((b[5] - b[2]) - 10.0) < TOL
    results.append(("rotateY(90) 把 +Z 转到 +X（管轴沿 X）", ok,
                    "X span=%.1f(期望40) Z span=%.1f(期望10)" % (b[3] - b[0], b[5] - b[2]) if b else "包围盒为空"))

    # ---- CSG ----
    a = P.CYLINDER(s, R=10.0, H=30.0)
    bpart = P.CYLINDER(s, R=5.0, H=30.0).translate((0.0, 0.0, 0.0))
    va = volume(a.shape)
    a.subtractFrom(bpart)
    v_cut = volume(a.shape)
    expect_cut = math.pi * (100 - 25) * 30
    ok = abs(v_cut - expect_cut) / expect_cut < 0.06
    results.append(("subtractFrom（挖内孔）体积正确", ok,
                    "挖后=%.0f 期望≈%.0f" % (v_cut, expect_cut)))

    c1 = P.CYLINDER(s, R=10.0, H=30.0)
    c2 = P.CYLINDER(s, R=10.0, H=30.0).translate((10.0, 0.0, 0.0))
    c1.uniteWith(c2)
    v_union = volume(c1.shape)
    ok = v_union > va * 1.4
    results.append(("uniteWith 合并体积增大", ok, "合并后=%.0f 单体=%.0f" % (v_union, va)))

    # ---- 输出 ----
    print("Plant 3D 原语契约校验")
    print("=" * 78)
    failed = 0
    for name, ok, detail in results:
        print("%s %-42s %s" % ("PASS" if ok else "FAIL", name, detail))
        if not ok:
            failed += 1
    print("=" * 78)
    print("共 %d 项，通过 %d，失败 %d" % (len(results), len(results) - failed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())