# -*- coding: utf-8 -*-
"""Plant 3D Core Primitives (`varmain.primitiv` native primitives).

100% compatible with both native C++ `pythonocc-core` (true analytical B-Rep solids)
and `occ_fallback` (when running in headless environments without pythonocc-core).
"""

import math
from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCC.Core.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeCone,
    BRepPrimAPI_MakeTorus,
    BRepPrimAPI_MakeSphere,
)
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from ..core.body import OccBody


def _make_native_eccentric_cone(r1: float, r2: float, h: float, ecc_x: float):
    """Builds an analytical B-Rep eccentric cone/frustum in native C++ OpenCASCADE
    using `BRepOffsetAPI_ThruSections(True, True)` between two circular wires,
    or falls back to `_make_cone_shape` when running in pure-Python fallback mode.
    """
    try:
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
        from OCC.Core.gp import gp_Circ
        from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections

        rb = max(0.05, float(r1))
        rt = max(0.05, float(r2))
        ax_b = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
        ax_t = gp_Ax2(gp_Pnt(float(ecc_x), 0.0, float(h)), gp_Dir(0.0, 0.0, 1.0))
        wb = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(gp_Circ(ax_b, rb)).Edge()).Wire()
        wt = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(gp_Circ(ax_t, rt)).Edge()).Wire()
        loft = BRepOffsetAPI_ThruSections(True, True)
        loft.AddWire(wb)
        loft.AddWire(wt)
        loft.Build()
        if loft.IsDone():
            return loft.Shape()
    except ImportError:
        pass
    from ..core.occ_fallback import _make_cone_shape
    ax = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    return _make_cone_shape(ax, r1, r2, h, ecc_x=ecc_x)


def BOX(s, L=100.0, W=100.0, H=100.0, **kw):
    """Plant 3D BOX(s, L, W, H):
    Centered at origin (0, 0, 0):
      - X extent is H: [-H/2, +H/2]
      - Y extent is L: [-L/2, +L/2]
      - Z extent is W: [-W/2, +W/2]
    """
    L = max(1e-3, float(L or 0.0))
    W = max(1e-3, float(W or 0.0))
    H = max(1e-3, float(H or 0.0))
    p1 = gp_Pnt(-H / 2.0, -L / 2.0, -W / 2.0)
    p2 = gp_Pnt(H / 2.0, L / 2.0, W / 2.0)
    shape = BRepPrimAPI_MakeBox(p1, p2).Shape()
    return OccBody(s, shape, params={"L": L, "W": W, "H": H})


def CYLINDER(s, *args, R=0.0, R1=0.0, R2=0.0, H=0.0, O=0.0, **kw):
    """Plant 3D CYLINDER(s, R, H, O=0.0) or CYLINDER(s, R1, R2, H, O=0.0).
    Base center at (0, 0, 0), height H along +Z [0, H], inner bore radius O.
    """
    if len(args) == 2:
        R, H = float(args[0]), float(args[1])
    elif len(args) == 3:
        R, H, O = float(args[0]), float(args[1]), float(args[2])
    elif len(args) >= 4:
        R1, R2, H, O = float(args[0]), float(args[1]), float(args[2]), float(args[3])

    R = float(R or 0.0)
    R1 = float(R1 or 0.0)
    R2 = float(R2 or 0.0)
    H = max(1e-3, float(H or 0.0))
    O = float(O or 0.0)

    is_elliptical = (R1 > 0.0 and R2 > 0.0 and abs(R1 - R2) > 1e-5)
    if R1 > 0.0 and R <= 0.0:
        R = R1
    R = max(1e-3, R)

    if is_elliptical:
        try:
            from OCC.Core.gp import gp_Elips, gp_Vec, gp_Ax1, gp_Trsf
            from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform
            from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
            ax_e = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0), gp_Dir(1.0, 0.0, 0.0))
            major_r = max(R1, R2)
            minor_r = min(R1, R2)
            el = gp_Elips(ax_e, major_r, minor_r)
            w = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(el).Edge()).Wire()
            f = BRepBuilderAPI_MakeFace(w, True).Face()
            outer = BRepPrimAPI_MakePrism(f, gp_Vec(0.0, 0.0, H)).Shape()
            if R1 < R2:
                trsf = gp_Trsf()
                trsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 0.5 * math.pi)
                outer = BRepBuilderAPI_Transform(outer, trsf, True).Shape()
        except Exception:
            ax = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
            outer = BRepPrimAPI_MakeCylinder(ax, R, H).Shape()
    else:
        ax = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
        outer = BRepPrimAPI_MakeCylinder(ax, R, H).Shape()

    min_outer_r = min(R, R1 or R, R2 or R)
    if 1e-4 < O < min_outer_r - 1e-4:
        ax_cut = gp_Ax2(gp_Pnt(0.0, 0.0, -0.5), gp_Dir(0.0, 0.0, 1.0))
        inner = BRepPrimAPI_MakeCylinder(ax_cut, O, H + 1.0).Shape()
        cut = BRepAlgoAPI_Cut(outer, inner)
        if hasattr(cut, "SetFuzzyValue"):
            cut.SetFuzzyValue(1e-4)
        if hasattr(cut, "Build"):
            cut.Build()
        if not hasattr(cut, "IsDone") or cut.IsDone():
            outer = cut.Shape()

    body = OccBody(s, outer, params={"R": R, "R1": R1 or R, "R2": R2 or R, "H": H, "O": O})
    body.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    body.addPoint((0.0, 0.0, H), (0.0, 0.0, 1.0))
    return body


def CONE(s, R1=50.0, R2=25.0, H=100.0, E=0.0, **kw):
    """Plant 3D CONE(s, R1, R2, H, E=0.0):
    Base at (0, 0, 0) with radius R1 (Z=0), top at (E, 0, H) with radius R2 (Z=H).
    """
    R1 = max(0.0, float(R1 or 0.0))
    R2 = max(0.0, float(R2 or 0.0))
    H = max(1e-3, float(H or 0.0))
    E = float(E or 0.0)
    if R1 < 1e-4 and R2 < 1e-4:
        R1 = 1e-3

    ax = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    if abs(E) > 1e-4:
        shape = _make_native_eccentric_cone(R1, R2, H, E)
    elif abs(R1 - R2) < 1e-4:
        shape = BRepPrimAPI_MakeCylinder(ax, max(R1, 1e-3), H).Shape()
    else:
        shape = BRepPrimAPI_MakeCone(ax, R1, R2, H).Shape()

    body = OccBody(s, shape, params={"R1": R1, "R2": R2, "H": H, "E": E})
    body.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    body.addPoint((E, 0.0, H), (0.0, 0.0, 1.0))
    return body


def TORUS(s, R1=100.0, R2=15.0, **kw):
    """Plant 3D TORUS(s, R1, R2):
    Centered at (0, 0, 0) in XY plane, revolution axis along Z.
    """
    R1 = max(1e-3, float(R1 or 0.0))
    R2 = max(1e-3, float(R2 or 0.0))
    if R1 <= R2:
        R1 = R2 + 1e-3
    ax = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    shape = BRepPrimAPI_MakeTorus(ax, R1, R2).Shape()
    return OccBody(s, shape, params={"R1": R1, "R2": R2})


def HALFSPHERE(s, R=50.0, **kw):
    """Plant 3D HALFSPHERE(s, R):
    Base center at (0, 0, 0), dome extending [0, R] along +Z.
    """
    R = max(1e-3, float(R or 0.0))
    shape = BRepPrimAPI_MakeSphere(gp_Pnt(0.0, 0.0, 0.0), R, 0.0, math.pi / 2.0).Shape()
    return OccBody(s, shape, params={"R": R, "H": R})
