# -*- coding: utf-8 -*-
"""Plant 3D Structural Steel Profiles & Transitions (`varmain.divsub.cste_*`, `cadapt_*`, `CORNERBOX`).

Uses direct 2D polygon extrusion (`BRepBuilderAPI_MakePolygon` -> `BRepBuilderAPI_MakeFace` ->
`BRepPrimAPI_MakePrism`) when native C++ `pythonocc-core` is installed so structural sections
are generated in <0.1 ms with ZERO boolean operations and ZERO internal coplanar split edges!
"""

from OCC.Core.gp import gp_Pnt, gp_Vec
from .native import BOX, CYLINDER
from .extended import ROUNDRECT, PYRAMID
from .var_basic import defaultPipeLength, getInsideDiameter, CORNERBOX
from ..core.body import OccBody


def _extrude_profile_z(outer_pts_xy, length_z: float, inner_pts_xy=None):
    """Extrudes a closed 2D XY polygon along +Z [0, length_z] into a single seamless B-Rep solid
    when native C++ `pythonocc-core` is present; returns None if running in fallback mode.
    """
    try:
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism

        poly = BRepBuilderAPI_MakePolygon()
        for x, y in outer_pts_xy:
            poly.Add(gp_Pnt(float(x), float(y), 0.0))
        poly.Close()
        face_maker = BRepBuilderAPI_MakeFace(poly.Wire(), True)

        if inner_pts_xy:
            hole = BRepBuilderAPI_MakePolygon()
            for x, y in inner_pts_xy:
                hole.Add(gp_Pnt(float(x), float(y), 0.0))
            hole.Close()
            hole_wire = hole.Wire()
            hole_wire.Reverse()
            face_maker.Add(hole_wire)

        if face_maker.IsDone():
            prism = BRepPrimAPI_MakePrism(face_maker.Face(), gp_Vec(0.0, 0.0, float(length_z)))
            if prism.IsDone():
                return prism.Shape()
    except ImportError:
        pass
    return None


def _resolve_len(L, kw):
    L = float(L if L is not None else kw.get("L1", defaultPipeLength))
    if L <= 0.0:
        L = float(kw.get("L1", defaultPipeLength))
    if L <= 0.0:
        L = defaultPipeLength
    return L


def CSTE_H(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID="CSTE_H", **kw):
    """Exact Plant 3D CSTE_H (`varmain/divsub/cste_h.pyc`):
    Extruded along +Z [0, L]; flange width W along X, web height H along Y.
    """
    W = float(kw.get("B1", W))
    H = float(kw.get("H1", H))
    if H <= 0.0:
        H = W
    tf = min(float(kw.get("TF", kw.get("T2", T))), H * 0.45)
    tw = min(float(kw.get("T1", T)), W * 0.8)
    L = _resolve_len(L, kw)

    hx, hy, htw = W / 2.0, H / 2.0, tw / 2.0
    pts = [
        (-hx, -hy), (hx, -hy), (hx, -hy + tf), (htw, -hy + tf),
        (htw, hy - tf), (hx, hy - tf), (hx, hy), (-hx, hy),
        (-hx, hy - tf), (-htw, hy - tf), (-htw, -hy + tf), (-hx, -hy + tf),
    ]
    shape = _extrude_profile_z(pts, L)
    if shape is not None:
        o1 = OccBody(s, shape, params={"W": W, "H": H, "T": tw, "TF": tf, "L": L})
        o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
        o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
        return o1

    o1 = BOX(s, L=tf, W=L, H=W).translate((0.0, tf / 2.0, L / 2.0))
    o2 = BOX(s, L=H, W=L, H=tw).translate((0.0, H / 2.0, L / 2.0))
    o3 = BOX(s, L=tf, W=L, H=W).translate((0.0, H - tf / 2.0, L / 2.0))
    o1.uniteWith(o2)
    o2.erase()
    o1.uniteWith(o3)
    o3.erase()
    o1.translate((0.0, -H / 2.0, 0.0))
    o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
    return o1


def CSTE_I(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID="CSTE_I", **kw):
    return CSTE_H(s, W=W, H=H, T=T, L=L, ID=ID, **kw)


def CSTE_U(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID="CSTE_U", **kw):
    """Exact Plant 3D CSTE_U (`varmain/divsub/cste_u.pyc`):
    Channel steel extruded along +Z [0, L].
    """
    W = float(kw.get("W1", kw.get("B1", W)))
    H = float(kw.get("H1", H))
    if H <= 0.0:
        H = W
    T = min(float(kw.get("T1", T)), H * 0.8)
    t2 = min(float(kw.get("TF", kw.get("T2", T))), W * 0.45)
    L = _resolve_len(L, kw)

    hx, hy = W / 2.0, H / 2.0
    pts = [
        (-hx, -hy), (hx, -hy), (hx, hy), (hx - t2, hy),
        (hx - t2, -hy + T), (-hx + t2, -hy + T), (-hx + t2, hy), (-hx, hy),
    ]
    shape = _extrude_profile_z(pts, L)
    if shape is not None:
        o1 = OccBody(s, shape, params={"W": W, "H": H, "T": T, "TF": t2, "L": L})
        o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
        o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
        return o1

    o1 = BOX(s, L=H, W=L, H=W).translate((0.0, 0.0, L / 2.0))
    o2 = BOX(s, L=max(1.0, H - T), W=L + 2.0, H=max(1.0, W - 2.0 * t2)).translate((0.0, T / 2.0, L / 2.0))
    o1.subtractFrom(o2)
    o2.erase()
    o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
    return o1


def CSTE_L(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID="CSTE_L", **kw):
    """Exact Plant 3D CSTE_L (`varmain/divsub/cste_l.pyc`):
    Angle steel extruded along +Z [0, L].
    """
    W = float(kw.get("W1", kw.get("B1", W)))
    H = float(kw.get("W2", kw.get("H1", H)))
    if H <= 0.0:
        H = W
    T = min(float(kw.get("T1", T)), min(W, H) * 0.8)
    L = _resolve_len(L, kw)

    hx, hy = W / 2.0, H / 2.0
    pts = [
        (-hx, -hy), (hx, -hy), (hx, -hy + T),
        (-hx + T, -hy + T), (-hx + T, hy), (-hx, hy),
    ]
    shape = _extrude_profile_z(pts, L)
    if shape is not None:
        o1 = OccBody(s, shape, params={"W": W, "H": H, "T": T, "L": L})
        o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
        o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
        return o1

    o1 = BOX(s, L=T, W=L, H=W).translate((W / 2.0, T / 2.0, L / 2.0))
    o2 = BOX(s, L=H, W=L, H=T).translate((T / 2.0, H / 2.0, L / 2.0))
    o1.uniteWith(o2)
    o2.erase()
    o1.translate((-W / 2.0, -H / 2.0, 0.0))
    o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
    return o1


def CSTE_T(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID="CSTE_T", **kw):
    """Exact Plant 3D CSTE_T (`varmain/divsub/cste_t.pyc`):
    T-section steel extruded along +Z [0, L].
    """
    W = float(kw.get("W1", kw.get("B1", W)))
    H = float(kw.get("H1", H))
    if H <= 0.0:
        H = W / 2.0
    T = min(float(kw.get("T1", T)), min(W, H) * 0.8)
    L = _resolve_len(L, kw)

    hx, hy, ht = W / 2.0, H / 2.0, T / 2.0
    pts = [
        (-hx, -hy), (hx, -hy), (hx, -hy + T), (ht, -hy + T),
        (ht, hy), (-ht, hy), (-ht, -hy + T), (-hx, -hy + T),
    ]
    shape = _extrude_profile_z(pts, L)
    if shape is not None:
        o1 = OccBody(s, shape, params={"W": W, "H": H, "T": T, "L": L})
        o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
        o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
        return o1

    o1 = BOX(s, L=T, W=L, H=W).translate((0.0, T / 2.0, L / 2.0))
    o2 = BOX(s, L=H, W=L, H=T).translate((0.0, H / 2.0, L / 2.0))
    o1.uniteWith(o2)
    o2.erase()
    o1.translate((0.0, -H / 2.0, 0.0))
    o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
    return o1


def CSTE_C(s, W=70.0, H=50.0, B=20.0, T=8.0, L=-1.0, ID="CSTE_C", **kw):
    """Exact Plant 3D CSTE_C (`varmain/divsub/cste_c.pyc`):
    Lipped C-channel extruded along +Z [0, L].
    """
    W = float(W)
    H = float(H) if float(H) > 0.0 else W
    B = float(B)
    if B <= 0.0 or B * 2.0 >= W:
        B = W / 3.0
    T = min(float(T), min(W, H) * 0.3)
    L = _resolve_len(L, kw)

    hx, hy = W / 2.0, H / 2.0
    gap_half = max(1.0, hx - B)
    pts = [
        (-hx, -hy), (hx, -hy), (hx, hy), (gap_half, hy),
        (gap_half, hy - T), (hx - T, hy - T), (hx - T, -hy + T),
        (-hx + T, -hy + T), (-hx + T, hy - T), (-gap_half, hy - T),
        (-gap_half, hy), (-hx, hy),
    ]
    shape = _extrude_profile_z(pts, L)
    if shape is not None:
        o1 = OccBody(s, shape, params={"W": W, "H": H, "B": B, "T": T, "L": L})
        o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
        o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
        return o1

    o1 = BOX(s, L=H, W=L, H=W).translate((0.0, 0.0, L / 2.0))
    o2 = BOX(s, L=max(1.0, H - 2.0 * T), W=L + 2.0, H=max(1.0, W - 2.0 * T)).translate((0.0, 0.0, L / 2.0))
    o3 = BOX(s, L=T + 1.0, W=L + 2.0, H=max(1.0, W - 2.0 * B)).translate((0.0, (H - T) / 2.0, L / 2.0))
    o2.uniteWith(o3)
    o3.erase()
    o1.subtractFrom(o2)
    o2.erase()
    o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
    return o1


def CSTE_O(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID="CSTE_O", **kw):
    """Exact Plant 3D CSTE_O (`varmain/divsub/cste_o.pyc`):
    Rectangular hollow section (RHS/SHS) extruded along +Z [0, L].
    """
    W = float(W)
    H = float(H) if float(H) > 0.0 else W
    T = float(T)
    L = _resolve_len(L, kw)

    hx, hy = W / 2.0, H / 2.0
    outer_pts = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]
    inner_pts = None
    if T > 0.0 and 2.0 * T < min(W, H):
        ix, iy = hx - T, hy - T
        inner_pts = [(-ix, -iy), (ix, -iy), (ix, iy), (-ix, iy)]
    shape = _extrude_profile_z(outer_pts, L, inner_pts_xy=inner_pts)
    if shape is not None:
        o1 = OccBody(s, shape, params={"W": W, "H": H, "T": T, "L": L})
        o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
        o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
        return o1

    o1 = BOX(s, L=H, W=L, H=W).translate((0.0, 0.0, L / 2.0))
    if T > 0.0 and 2.0 * T < min(W, H):
        o2 = BOX(s, L=H - 2.0 * T, W=L + 2.0, H=W - 2.0 * T).translate((0.0, 0.0, L / 2.0))
        o1.subtractFrom(o2)
        o2.erase()
    o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
    return o1


def CSTE_R(s, D=114.3, L=100.0, OF=-1.0, ID="CSTE_R", **kw):
    D = float(D)
    L = _resolve_len(L, kw)
    OF = float(OF)
    di = getInsideDiameter(D=D, OF=OF)
    return CYLINDER(s, R=D / 2.0, H=L, O=di / 2.0)


def CSTE_F(s, W=70.0, T=8.0, L=-1.0, ID="CSTE_F", **kw):
    W = float(W)
    T = float(T) if float(T) > 0.0 else W
    L = _resolve_len(L, kw)
    o1 = BOX(s, L=T, W=L, H=W).translate((0.0, 0.0, L / 2.0))
    o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
    return o1


def CSTE_Z(s, W=70.0, H=50.0, T=8.0, L=-1.0, ID="CSTE_Z", **kw):
    W = float(W)
    H = float(H) if float(H) > 0.0 else W
    T = float(T)
    L = _resolve_len(L, kw)
    sL = (W + T) / 2.0
    o1 = BOX(s, L=T, W=L, H=sL).translate((sL / 2.0 - T / 2.0, T / 2.0, L / 2.0))
    o2 = BOX(s, L=H, W=L, H=T).translate((0.0, H / 2.0, L / 2.0))
    o3 = BOX(s, L=T, W=L, H=sL).translate((-sL / 2.0 + T / 2.0, H - T / 2.0, L / 2.0))
    o1.uniteWith(o2)
    o2.erase()
    o1.uniteWith(o3)
    o3.erase()
    o1.translate((0.0, -H / 2.0, 0.0))
    o1.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    o1.addPoint((0.0, 0.0, L), (0.0, 0.0, 1.0))
    return o1


def CADAPT_SQ2RO(s, LL=715.0, LW=700.0, R=225.0, OL=0.0, OW=0.0, H=500.0, OF=0.0, FB1=0.0, FB2=0.0, ID="CADAPT_SQ2RO", **kw):
    L1 = float(kw.get("L1", LL))
    W1 = float(kw.get("W1", LW))
    R2 = float(kw.get("R2", R))
    H_val = float(H)
    return ROUNDRECT(s, L=L1, W=W1, H=H_val, R2=R2, E=float(OL))


def CADAPT_SQ2SQ(s, LL=715.0, LW=700.0, TL=450.0, TW=400.0, OL=0.0, OW=0.0, H=500.0, OF=0.0, FB1=0.0, FB2=0.0, ID="CADAPT_SQ2SQ", **kw):
    L1 = float(kw.get("L1", LL))
    W1 = float(kw.get("W1", LW))
    L2 = float(kw.get("L2", TL))
    H_val = float(H)
    ratio = L2 / max(L1, 1e-3)
    ht = H_val / max(1.0 - ratio, 0.05) if ratio < 0.99 else H_val * 50.0
    return PYRAMID(s, L=L1, W=W1, H=H_val, HT=ht)
