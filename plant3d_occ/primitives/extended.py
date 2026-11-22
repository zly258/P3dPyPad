# -*- coding: utf-8 -*-
"""Plant 3D Extended Primitives (`varmain.primitiv` curved, head, transition & elbow primitives).

100% compatible with both native C++ `pythonocc-core` (true analytical & lofted B-Rep solids,
zero triangle mesh mixing) and `occ_fallback` (when running in headless environments).
"""

import math
import numpy as np
from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeTorus
from ..core.body import OccBody
from .native import HALFSPHERE, CONE


def _make_b_rep_sphere_segment(center: gp_Pnt, r: float, theta_min: float, theta_max: float, phi_sweep: float = 2.0 * math.pi):
    """Builds a true analytical B-Rep sphere segment on native C++ pythonocc-core
    (`BRepPrimAPI_MakeSphere`), or falls back to `_make_sphere_shape` in headless fallback mode.
    """
    try:
        from OCC.Core.TopoDS import TopoDS_Shape as _NativeShape  # noqa: F401
        ax = gp_Ax2(center, gp_Dir(0.0, 0.0, 1.0))
        if phi_sweep >= 2.0 * math.pi - 1e-4:
            return BRepPrimAPI_MakeSphere(ax, float(r), float(theta_min), float(theta_max)).Shape()
        return BRepPrimAPI_MakeSphere(ax, float(r), float(theta_min), float(theta_max), float(phi_sweep)).Shape()
    except ImportError:
        from ..core.occ_fallback import _make_sphere_shape
        return _make_sphere_shape(center, r, theta_min, theta_max, phi_sweep=phi_sweep)


def _make_b_rep_elbow(ax2: gp_Ax2, r_major: float, r_start: float, r_end: float, angle_sweep_rad: float, n_seg: int = 0):
    """Builds a true smooth B-Rep elbow/torus segment on native C++ pythonocc-core:
    - Equal-radius smooth elbow (`r_start == r_end`, `n_seg == 0`): single analytical `BRepPrimAPI_MakeTorus(ax2, r_major, r_start, angle_sweep_rad)`!
    - Reducing smooth elbow (`r_start != r_end`): smooth `BRepOffsetAPI_ThruSections(True, False)` across circular wires!
    - Segmented miter elbow (`n_seg > 0`): ruled `BRepOffsetAPI_ThruSections(True, True)` across `n_seg` segments!
    """
    try:
        from OCC.Core.gp import gp_Circ, gp_Vec
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
        from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections

        steps = max(2, n_seg) if n_seg > 0 else 16
        ruled = bool(n_seg > 0)
        loft = BRepOffsetAPI_ThruSections(True, ruled)
        loc = ax2.Location()
        vz = ax2.Direction()
        vx = ax2.XDirection()
        vy_vec = gp_Vec(vz.Y() * vx.Z() - vz.Z() * vx.Y(), vz.Z() * vx.X() - vz.X() * vx.Z(), vz.X() * vx.Y() - vz.Y() * vx.X())
        vy = gp_Dir(vy_vec.X(), vy_vec.Y(), vy_vec.Z())

        for i in range(steps + 1):
            t = i / float(steps)
            u = t * angle_sweep_rad
            ru = r_start + t * (r_end - r_start)
            cu, su = math.cos(u), math.sin(u)
            radial_x = cu * vx.X() + su * vy.X()
            radial_y = cu * vx.Y() + su * vy.Y()
            radial_z = cu * vx.Z() + su * vy.Z()
            tang_x = -su * vx.X() + cu * vy.X()
            tang_y = -su * vx.Y() + cu * vy.Y()
            tang_z = -su * vx.Z() + cu * vy.Z()

            c_pt = gp_Pnt(
                loc.X() + r_major * radial_x,
                loc.Y() + r_major * radial_y,
                loc.Z() + r_major * radial_z,
            )
            c_ax = gp_Ax2(c_pt, gp_Dir(tang_x, tang_y, tang_z), gp_Dir(radial_x, radial_y, radial_z))
            wire = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(gp_Circ(c_ax, max(0.1, ru))).Edge()).Wire()
            loft.AddWire(wire)
        loft.Build()
        if loft.IsDone():
            return loft.Shape()
    except ImportError:
        pass

    from ..core.occ_fallback import _make_torus_shape
    n_u = max(3, n_seg * 2 + 1) if n_seg > 0 else 28
    return _make_torus_shape(ax2, r_major, r_start, angle_sweep_rad=angle_sweep_rad, r2_end=r_end, n_u=n_u)


def SPHERE(s, R=50.0, **kw):
    """Full sphere centered at (0, 0, 0) with radius R."""
    R = max(1e-3, float(R or 0.0))
    shape = BRepPrimAPI_MakeSphere(gp_Pnt(0.0, 0.0, 0.0), R).Shape()
    return OccBody(s, shape, params={"R": R, "H": 2.0 * R})


def SPHERESEGMENT(s, R=50.0, P=25.0, Q=0.0, **kw):
    """Plant 3D SPHERESEGMENT(s, R, P, Q):
    Base point (0, 0, 0) is the center of the lower plane of the segment (Z in [0, P]).
    """
    R = max(1e-3, float(R or 0.0))
    Q = float(Q or 0.0)
    P = max(1e-3, float(P or 0.0))
    z0 = max(-R + 1e-4, min(R - 1e-4, Q))
    z1 = max(z0 + 1e-4, min(R, Q + P))
    theta_min = math.asin(max(-1.0, min(1.0, z0 / R)))
    theta_max = math.asin(max(-1.0, min(1.0, z1 / R)))
    shape = _make_b_rep_sphere_segment(gp_Pnt(0.0, 0.0, -z0), R, theta_min, theta_max)
    return OccBody(s, shape, params={"R": R, "P": P, "Q": Q, "H": z1 - z0})


def _make_analytical_ellipsoid_head(r: float, h: float):
    try:
        from OCC.Core.gp import gp_Ax2, gp_Ax1, gp_Dir, gp_Elips, gp_Pnt
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
        from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeRevol

        ax_el = gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, -1.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
        elips = gp_Elips(ax_el, float(r), float(h))
        e_arc = BRepBuilderAPI_MakeEdge(elips, 0.0, 0.5 * math.pi).Edge()
        e_base = BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(float(r), 0.0, 0.0)).Edge()
        e_axis = BRepBuilderAPI_MakeEdge(gp_Pnt(0.0, 0.0, float(h)), gp_Pnt(0.0, 0.0, 0.0)).Edge()

        wire = BRepBuilderAPI_MakeWire(e_base, e_arc, e_axis).Wire()
        face = BRepBuilderAPI_MakeFace(wire, True).Face()
        revol = BRepPrimAPI_MakeRevol(face, gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)))
        if revol.IsDone():
            return revol.Shape()
    except Exception:
        pass
    return None


def ELLIPSOIDHEAD(s, R=50.0, H=None, **kw):
    """Plant 3D ELLIPSOIDHEAD(s, R):
    Normalized ellipsoid head with base center at (0, 0, 0), height H along +Z.
    """
    R = max(1e-3, float(R or 0.0))
    h_real = float(H) if (H is not None and float(H) > 0.0) else R * 0.5
    shape = _make_analytical_ellipsoid_head(R, h_real)
    if shape is not None:
        body = OccBody(s, shape, params={"R": R, "H": h_real})
    else:
        body = HALFSPHERE(s, R=R)
        scale_z = h_real / R
        if abs(scale_z - 1.0) > 1e-6:
            body.scaleXYZ(1.0, 1.0, scale_z)
        body.setParameters({"R": R, "H": h_real})
    return body


def ELLIPSOIDHEAD2(s, R=50.0, **kw):
    return ELLIPSOIDHEAD(s, R=R, H=float(R or 0.0) * 0.5, **kw)


def ELLIPSOIDSEGMENT(s, RX=50.0, RY=30.0, A1=360.0, A2=0.0, A3=0.0, A4=180.0, **kw):
    RX = max(1e-3, float(RX or 0.0))
    RY = max(1e-3, float(RY or 0.0))
    A1 = float(A1 if A1 is not None else 360.0)
    A2 = float(A2 or 0.0)
    A3 = float(A3 or 0.0)
    A4 = float(A4 if A4 is not None else 180.0)
    t_min = math.radians(90.0 - max(A3, A4))
    t_max = math.radians(90.0 - min(A3, A4))
    phi = math.radians(max(1.0, min(360.0, A1)))
    shape = _make_b_rep_sphere_segment(gp_Pnt(0.0, 0.0, 0.0), 1.0, t_min, t_max, phi_sweep=phi)
    body = OccBody(s, shape, params={"RX": RX, "RY": RY, "H": 2.0 * RY})
    if abs(A2) > 1e-5:
        body.rotateZ(A2)
    body.rotateY(90.0)
    body.scaleXYZ(RX, RY, RY)
    return body


def TORISPHERICHEAD(s, R=50.0, **kw):
    R = max(1e-3, float(R or 0.0))
    h_real = R * 0.3872
    body = HALFSPHERE(s, R=R)
    body.scaleXYZ(1.0, 1.0, h_real / R)
    body.setParameters({"R": R, "H": h_real})
    return body


def TORISPHERICHEAD2(s, R=50.0, **kw):
    R = max(1e-3, float(R or 0.0))
    r2 = min(25.0, 0.45 * R)
    r1 = 2.0 * R
    term = max(0.0, (r1 - r2) ** 2 - (R - r2) ** 2)
    h_real = max(0.2 * R, r1 - math.sqrt(term))
    body = HALFSPHERE(s, R=R)
    body.scaleXYZ(1.0, 1.0, h_real / R)
    body.setParameters({"R": R, "H": h_real})
    return body


def TORISPHERICHEADH(s, R=50.0, H=20.0, **kw):
    R = max(1e-3, float(R or 0.0))
    h_real = float(H) if float(H or 0.0) > 0.0 else R * 0.3872
    body = HALFSPHERE(s, R=R)
    body.scaleXYZ(1.0, 1.0, h_real / R)
    body.setParameters({"R": R, "H": h_real})
    return body


TORISPERICHEAD = TORISPHERICHEAD
TORISPERICHEAD2 = TORISPHERICHEAD2
TORISPERICHEADH = TORISPHERICHEADH


def ARC3D2(s, D=25.0, D2=0.0, R=100.0, A=90.0, **kw):
    """Plant 3D ARC3D2(s, D, D2, R, A):
    D: first 1/2 diameter (pipe radius at port 0)
    D2: second 1/2 diameter (pipe radius at port 1; if <= 0, D is used)
    R: bend radius
    A: bend angle in degrees (0 < A <= 180)
    """
    r1 = max(1e-3, float(D or 0.0))
    r2 = float(D2) if (D2 is not None and float(D2) > 1e-4) else r1
    R = max(max(r1, r2) + 1e-3, float(R or 0.0))
    A = max(1.0, min(180.0, float(A if A is not None else 90.0)))
    rad = math.radians(A)

    if abs(A - 180.0) < 1e-4:
        mX = R
        cx, cy = R, R
        p0 = (R, 0.0, 0.0)
        d0 = (1.0, 0.0, 0.0)
        p1 = (R, 2.0 * R, 0.0)
        d1 = (1.0, 0.0, 0.0)
    else:
        mX = R * math.tan(rad / 2.0)
        cx, cy = mX, R
        p0 = (mX, 0.0, 0.0)
        d0 = (1.0, 0.0, 0.0)
        p1 = (-mX * math.cos(rad), mX * math.sin(rad), 0.0)
        d1 = (-math.cos(rad), math.sin(rad), 0.0)

    start_ang = math.radians(-90.0 - A)
    vx = gp_Dir(math.cos(start_ang), math.sin(start_ang), 0.0)
    ax = gp_Ax2(gp_Pnt(cx, cy, 0.0), gp_Dir(0.0, 0.0, 1.0), vx)

    shape = _make_b_rep_elbow(ax, R, r2, r1, rad, n_seg=0)
    body = OccBody(s, shape, params={"D": r1, "D2": r2, "R": R, "A": A})
    body.addPoint(p0, d0)
    body.addPoint(p1, d1)
    return body


def ARC3D(s, D=25.0, R=100.0, A=90.0, **kw):
    return ARC3D2(s, D=D, D2=D, R=R, A=A, **kw)


def ARC3DS(s, D=25.0, D2=0.0, R=100.0, A=90.0, S=3, **kw):
    """Plant 3D ARC3DS(s, D, D2, R, A, S) segmented miter elbow."""
    r1 = max(1e-3, float(D or 0.0))
    r2 = float(D2) if (D2 is not None and float(D2) > 1e-4) else r1
    R = max(max(r1, r2) + 1e-3, float(R or 0.0))
    A = max(1.0, min(180.0, float(A if A is not None else 90.0)))
    n_seg = max(1, int(S or 3))
    rad = math.radians(A)
    mX = R if abs(A - 180.0) < 1e-4 else R * math.tan(rad / 2.0)
    cx, cy = mX, R
    start_ang = math.radians(-90.0 - A)
    ax = gp_Ax2(gp_Pnt(cx, cy, 0.0), gp_Dir(0.0, 0.0, 1.0), gp_Dir(math.cos(start_ang), math.sin(start_ang), 0.0))
    shape = _make_b_rep_elbow(ax, R, r2, r1, rad, n_seg=n_seg)
    body = OccBody(s, shape, params={"D": r1, "D2": r2, "R": R, "A": A, "S": n_seg})
    body.addPoint((mX, 0.0, 0.0), (1.0, 0.0, 0.0))
    if abs(A - 180.0) < 1e-4:
        body.addPoint((R, 2.0 * R, 0.0), (1.0, 0.0, 0.0))
    else:
        body.addPoint((-mX * math.cos(rad), mX * math.sin(rad), 0.0), (-math.cos(rad), math.sin(rad), 0.0))
    return body


def PYRAMID(s, L=100.0, W=100.0, H=100.0, HT=0.0, **kw):
    """Plant 3D PYRAMID(s, L, W, H, HT=0.0):
    Exact 6-face B-Rep frustum/pyramid on native C++ pythonocc-core (`BRepOffsetAPI_ThruSections`).
    """
    L = max(1e-3, float(L or 0.0))
    W = max(1e-3, float(W or 0.0))
    H = max(1e-3, float(H or 0.0))
    HT = float(HT or 0.0)
    ratio = (HT - H) / HT if HT > H else 0.02

    hx0, hy0 = 0.5 * L, 0.5 * W
    hx1, hy1 = max(0.05, hx0 * ratio), max(0.05, hy0 * ratio)

    try:
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
        from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections

        poly0 = BRepBuilderAPI_MakePolygon()
        for x, y in ((-hx0, -hy0), (hx0, -hy0), (hx0, hy0), (-hx0, hy0)):
            poly0.Add(gp_Pnt(x, y, 0.0))
        poly0.Close()

        poly1 = BRepBuilderAPI_MakePolygon()
        for x, y in ((-hx1, -hy1), (hx1, -hy1), (hx1, hy1), (-hx1, hy1)):
            poly1.Add(gp_Pnt(x, y, H))
        poly1.Close()

        loft = BRepOffsetAPI_ThruSections(True, True)
        loft.AddWire(poly0.Wire())
        loft.AddWire(poly1.Wire())
        loft.Build()
        if loft.IsDone():
            return OccBody(s, loft.Shape(), params={"L": L, "W": W, "H": H, "HT": HT if HT > 0 else H})
    except ImportError:
        pass

    from ..core.occ_fallback import TopoDS_Shape
    verts = np.array([
        [-hx0, -hy0, 0.0], [hx0, -hy0, 0.0], [hx0, hy0, 0.0], [-hx0, hy0, 0.0],
        [-hx1, -hy1, H],   [hx1, -hy1, H],   [hx1, hy1, H],   [-hx1, hy1, H],
    ], dtype=np.float64)
    tris = np.array([
        [0, 2, 1], [0, 3, 2],
        [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4],
        [1, 2, 6], [1, 6, 5],
        [2, 3, 7], [2, 7, 6],
        [3, 0, 4], [3, 4, 7],
    ], dtype=np.int32)
    edge_idx = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]
    edges = np.array([[verts[a], verts[b]] for a, b in edge_idx], dtype=np.float64)

    def pyr_sdf(pts: np.ndarray) -> np.ndarray:
        t = np.clip(pts[:, 2] / H, 0.0, 1.0)
        hxt = hx0 + t * (hx1 - hx0)
        hyt = hy0 + t * (hy1 - hy0)
        dx = np.abs(pts[:, 0]) - hxt
        dy = np.abs(pts[:, 1]) - hyt
        dz = np.abs(pts[:, 2] - 0.5 * H) - 0.5 * H
        q = np.column_stack([dx, dy, dz])
        return np.linalg.norm(np.maximum(q, 0.0), axis=1) + np.minimum(np.max(q, axis=1), 0.0)

    shape = TopoDS_Shape(verts, tris, edges, pyr_sdf)
    return OccBody(s, shape, params={"L": L, "W": W, "H": H, "HT": HT if HT > 0 else H})


def ROUNDRECT(s, L=100.0, W=100.0, H=100.0, R2=30.0, E=0.0, **kw):
    """Plant 3D ROUNDRECT(s, L, W, H, R2, E=0.0):
    Smooth B-Rep transition from LxW rectangle at Z=0 to circle R2 at (E, 0, H)
    using `BRepOffsetAPI_ThruSections` on native C++ pythonocc-core.
    """
    L = max(1e-3, float(L or 0.0))
    W = max(1e-3, float(W or 0.0))
    H = max(1e-3, float(H or 0.0))
    R2 = max(1e-3, float(R2 or 0.0))
    E = float(E or 0.0)
    hx, hy = 0.5 * L, 0.5 * W

    try:
        from OCC.Core.gp import gp_Circ
        from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
        from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections

        poly0 = BRepBuilderAPI_MakePolygon()
        for x, y in ((hx, hy), (-hx, hy), (-hx, -hy), (hx, -hy)):
            poly0.Add(gp_Pnt(x, y, 0.0))
        poly0.Close()

        ax_top = gp_Ax2(gp_Pnt(E, 0.0, H), gp_Dir(0.0, 0.0, 1.0))
        w_top = BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(gp_Circ(ax_top, R2)).Edge()).Wire()

        loft = BRepOffsetAPI_ThruSections(True, True)
        loft.AddWire(poly0.Wire())
        loft.AddWire(w_top)
        loft.Build()
        if loft.IsDone():
            body = OccBody(s, loft.Shape(), params={"L": L, "W": W, "H": H, "R2": R2, "E": E})
            body.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
            body.addPoint((E, 0.0, H), (0.0, 0.0, 1.0))
            return body
    except ImportError:
        pass

    from ..core.occ_fallback import TopoDS_Shape
    corners = np.array([[hx, hy, 0.0], [-hx, hy, 0.0], [-hx, -hy, 0.0], [hx, -hy, 0.0]], dtype=np.float64)
    n_per_quad = 9
    angles = np.linspace(0.0, 2.0 * math.pi, 4 * n_per_quad, endpoint=False)
    n_top = len(angles)
    top_ring = np.column_stack([E + R2 * np.cos(angles), R2 * np.sin(angles), np.full(n_top, H)])
    bot_center = np.array([[0.0, 0.0, 0.0]])
    top_center = np.array([[E, 0.0, H]])
    verts = np.vstack([corners, top_ring, bot_center, top_center])
    ic_top = 4 + n_top

    tris = [[0, 2, 1], [0, 3, 2]]
    edges = [
        [corners[0], corners[1]],
        [corners[1], corners[2]],
        [corners[2], corners[3]],
        [corners[3], corners[0]],
    ]
    for q in range(4):
        q_next = (q + 1) % 4
        i_start = q * n_per_quad
        i_end = ((q + 1) * n_per_quad) % n_top
        for k in range(n_per_quad):
            t_cur = 4 + (i_start + k) % n_top
            t_nxt = 4 + (i_start + k + 1) % n_top
            tris.append([q, t_cur, t_nxt])
            edges.append([top_ring[(i_start + k) % n_top], top_ring[(i_start + k + 1) % n_top]])
        tris.append([q, 4 + i_end, q_next])
        edges.append([corners[q], top_ring[i_start]])
        edges.append([corners[q], top_ring[i_end]])
    for i in range(n_top):
        j = (i + 1) % n_top
        tris.append([ic_top, 4 + i, 4 + j])

    def rr_sdf(pts: np.ndarray) -> np.ndarray:
        t = np.clip(pts[:, 2] / H, 0.0, 1.0)
        cx = t * E
        px = pts[:, 0] - cx
        py = pts[:, 1]
        d_rect = np.maximum(np.abs(px) - hx * (1.0 - t), np.abs(py) - hy * (1.0 - t))
        d_circ = np.hypot(px, py) - R2 * t
        d_xy = (1.0 - t) * d_rect + t * d_circ
        d_z = np.abs(pts[:, 2] - 0.5 * H) - 0.5 * H
        q = np.column_stack([d_xy, d_z])
        return np.linalg.norm(np.maximum(q, 0.0), axis=1) + np.minimum(np.max(q, axis=1), 0.0)

    shape = TopoDS_Shape(
        np.array(verts, dtype=np.float64),
        np.array(tris, dtype=np.int32),
        np.array(edges, dtype=np.float64),
        rr_sdf,
    )
    body = OccBody(s, shape, params={"L": L, "W": W, "H": H, "R2": R2, "E": E})
    body.addPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    body.addPoint((E, 0.0, H), (0.0, 0.0, 1.0))
    return body


def ELLIPSE(s, R1=50.0, R2=30.0, H=1.0, **kw):
    from .native import CYLINDER
    return CYLINDER(s, R1=R1, R2=R2, H=max(1.0, float(H or 1.0)), O=0.0)


def LOFT(s, profiles=None, **kw):
    return PYRAMID(s, L=float(kw.get("L", 100.0)), W=float(kw.get("W", 100.0)), H=float(kw.get("H", 100.0)))
