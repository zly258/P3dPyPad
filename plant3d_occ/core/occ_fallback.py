# -*- coding: utf-8 -*-
"""Pure-Python OpenCASCADE (OCC) Compatibility & CSG/Z-Buffer Kernel.

Automatically registers `OCC`, `OCC.Core.*`, and `OCC.Display.*` in `sys.modules`
when binary `pythonocc-core` C++ bindings are not installed in the current Python
environment. Provides:
- Exact 3D analytical SDF + watertight triangle mesh & feature-edge B-Rep primitives
- Boolean CSG operations (`BRepAlgoAPI_Fuse`, `BRepAlgoAPI_Cut`, `BRepAlgoAPI_Common`)
  with adaptive triangle clipping, interior cutout wall generation, and Union-Find
  connected-solid topology tracking (`TopExp_Explorer` with `TopAbs_SOLID`)
- Rigid & affine transformations (`gp_Trsf`, `BRepBuilderAPI_Transform`)
- Bounding box computation (`Bnd_Box`, `brepbndlib.Add`)
- Triangulation extraction (`BRepMesh_IncrementalMesh`, `BRep_Tool.Triangulation`)
- High-resolution 2x-supersampled Z-buffer offscreen CAD renderer (`Viewer3d`)
  supporting Shaded-with-Edges, Wireframe, and Hidden-Line-Removal (HLR) modes.
"""

from __future__ import annotations

import math
import os
import sys
import types
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

import numpy as np
from PIL import Image


# ============================================================================
# 1. OCC.Core.gp — Geometric Primitives & Transformations
# ============================================================================

class gp_Pnt:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    def X(self) -> float:
        return self._x

    def Y(self) -> float:
        return self._y

    def Z(self) -> float:
        return self._z

    def Coord(self) -> Tuple[float, float, float]:
        return (self._x, self._y, self._z)

    def Transformed(self, trsf: "gp_Trsf") -> "gp_Pnt":
        v = np.array([self._x, self._y, self._z, 1.0], dtype=np.float64)
        res = trsf._mat @ v
        return gp_Pnt(float(res[0]), float(res[1]), float(res[2]))

    def __repr__(self) -> str:
        return f"gp_Pnt({self._x:.4f}, {self._y:.4f}, {self._z:.4f})"


class gp_Circ:
    def __init__(self, ax2, r):
        self.ax2 = ax2
        self.r = float(r)

class gp_Vec:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    def X(self) -> float:
        return self._x

    def Y(self) -> float:
        return self._y

    def Z(self) -> float:
        return self._z

    def Coord(self) -> Tuple[float, float, float]:
        return (self._x, self._y, self._z)

    def Magnitude(self) -> float:
        return math.sqrt(self._x ** 2 + self._y ** 2 + self._z ** 2)

    def Transformed(self, trsf: "gp_Trsf") -> "gp_Vec":
        v = np.array([self._x, self._y, self._z], dtype=np.float64)
        res = trsf._mat[:3, :3] @ v
        return gp_Vec(float(res[0]), float(res[1]), float(res[2]))


class gp_Dir:
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 1.0):
        x, y, z = float(x), float(y), float(z)
        n = math.sqrt(x * x + y * y + z * z)
        if n < 1e-12:
            self._x, self._y, self._z = 0.0, 0.0, 1.0
        else:
            self._x, self._y, self._z = x / n, y / n, z / n

    def X(self) -> float:
        return self._x

    def Y(self) -> float:
        return self._y

    def Z(self) -> float:
        return self._z

    def Coord(self) -> Tuple[float, float, float]:
        return (self._x, self._y, self._z)

    def Transformed(self, trsf: "gp_Trsf") -> "gp_Dir":
        v = np.array([self._x, self._y, self._z], dtype=np.float64)
        res = trsf._mat[:3, :3] @ v
        return gp_Dir(float(res[0]), float(res[1]), float(res[2]))


class gp_Ax1:
    def __init__(self, loc: gp_Pnt = None, direction: gp_Dir = None):
        self._loc = loc if loc is not None else gp_Pnt(0.0, 0.0, 0.0)
        self._dir = direction if direction is not None else gp_Dir(0.0, 0.0, 1.0)

    def Location(self) -> gp_Pnt:
        return self._loc

    def Direction(self) -> gp_Dir:
        return self._dir


class gp_Ax2:
    def __init__(self, loc: gp_Pnt = None, direction: gp_Dir = None, vx: gp_Dir = None):
        self._loc = loc if loc is not None else gp_Pnt(0.0, 0.0, 0.0)
        self._dir = direction if direction is not None else gp_Dir(0.0, 0.0, 1.0)
        n = np.array(self._dir.Coord(), dtype=np.float64)
        if vx is not None:
            x_cand = np.array(vx.Coord(), dtype=np.float64)
            x_cand = x_cand - np.dot(x_cand, n) * n
            if np.linalg.norm(x_cand) < 1e-9:
                vx = None
            else:
                x_axis = x_cand / np.linalg.norm(x_cand)
        if vx is None:
            ref = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
            x_axis = np.cross(ref, n)
            if np.linalg.norm(x_axis) < 1e-9:
                x_axis = np.array([1.0, 0.0, 0.0])
            else:
                x_axis = x_axis / np.linalg.norm(x_axis)
            # For standard +Z normal, keep X=(1,0,0), Y=(0,1,0)
            if abs(n[2] - 1.0) < 1e-9:
                x_axis = np.array([1.0, 0.0, 0.0])
            elif abs(n[2] + 1.0) < 1e-9:
                x_axis = np.array([1.0, 0.0, 0.0])
        y_axis = np.cross(n, x_axis)
        y_axis = y_axis / max(np.linalg.norm(y_axis), 1e-12)
        self._vx = gp_Dir(float(x_axis[0]), float(x_axis[1]), float(x_axis[2]))
        self._vy = gp_Dir(float(y_axis[0]), float(y_axis[1]), float(y_axis[2]))

    def Location(self) -> gp_Pnt:
        return self._loc

    def Direction(self) -> gp_Dir:
        return self._dir

    def XDirection(self) -> gp_Dir:
        return self._vx

    def YDirection(self) -> gp_Dir:
        return self._vy

    def BasisMatrix(self) -> np.ndarray:
        """Returns 4x4 local-to-world transform matrix."""
        m = np.eye(4, dtype=np.float64)
        m[:3, 0] = self._vx.Coord()
        m[:3, 1] = self._vy.Coord()
        m[:3, 2] = self._dir.Coord()
        m[:3, 3] = self._loc.Coord()
        return m


class gp_Trsf:
    def __init__(self, mat: Optional[np.ndarray] = None):
        self._mat = np.array(mat, dtype=np.float64) if mat is not None else np.eye(4, dtype=np.float64)

    def SetTranslation(self, vec: gp_Vec) -> None:
        self._mat = np.eye(4, dtype=np.float64)
        self._mat[0, 3] = vec.X()
        self._mat[1, 3] = vec.Y()
        self._mat[2, 3] = vec.Z()

    def SetRotation(self, ax1: gp_Ax1, angle_rad: float) -> None:
        ux, uy, uz = ax1.Direction().Coord()
        px, py, pz = ax1.Location().Coord()
        c = math.cos(float(angle_rad))
        s = math.sin(float(angle_rad))
        t = 1.0 - c
        R = np.array([
            [t * ux * ux + c,      t * ux * uy - s * uz, t * ux * uz + s * uy],
            [t * ux * uy + s * uz, t * uy * uy + c,      t * uy * uz - s * ux],
            [t * ux * uz - s * uy, t * uy * uz + s * ux, t * uz * uz + c     ],
        ], dtype=np.float64)
        p = np.array([px, py, pz], dtype=np.float64)
        trans = p - R @ p
        self._mat = np.eye(4, dtype=np.float64)
        self._mat[:3, :3] = R
        self._mat[:3, 3] = trans

    def SetScale(self, pnt: gp_Pnt, factor: float) -> None:
        f = float(factor)
        p = np.array(pnt.Coord(), dtype=np.float64)
        self._mat = np.eye(4, dtype=np.float64)
        self._mat[0, 0] = f
        self._mat[1, 1] = f
        self._mat[2, 2] = f
        self._mat[:3, 3] = p * (1.0 - f)

    def SetScaleXYZ(self, sx: float, sy: float, sz: float) -> None:
        self._mat = np.diag([float(sx), float(sy), float(sz), 1.0])

    def SetValues(
        self,
        a11: float, a12: float, a13: float, a14: float,
        a21: float, a22: float, a23: float, a24: float,
        a31: float, a32: float, a33: float, a34: float,
    ) -> None:
        self._mat = np.array([
            [a11, a12, a13, a14],
            [a21, a22, a23, a24],
            [a31, a32, a33, a34],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=np.float64)

    def Value(self, row: int, col: int) -> float:
        return float(self._mat[row - 1, col - 1])

    def Multiply(self, other: "gp_Trsf") -> None:
        self._mat = self._mat @ other._mat

    def Multiplied(self, other):
        res = gp_Trsf()
        res._mat = self._mat @ other._mat
        return res

    def Multiply(self, other):
        self._mat = self._mat @ other._mat

    def PreMultiply(self, other: "gp_Trsf") -> None:
        self._mat = other._mat @ self._mat


# ============================================================================
# 2. Core CSG Solid & Mesh Representation
# ============================================================================

@dataclass
class SolidComponent:
    """Represents a single connected solid region for topology exploration."""
    bbox_min: np.ndarray
    bbox_max: np.ndarray
    sample_pts: np.ndarray
    sdf: Callable[[np.ndarray], np.ndarray]

    def transformed(self, mat: np.ndarray, inv_mat: np.ndarray) -> "SolidComponent":
        pts_h = np.hstack([self.sample_pts, np.ones((len(self.sample_pts), 1))])
        new_pts = (pts_h @ mat.T)[:, :3]
        corners = np.array([
            [self.bbox_min[0], self.bbox_min[1], self.bbox_min[2], 1.0],
            [self.bbox_max[0], self.bbox_min[1], self.bbox_min[2], 1.0],
            [self.bbox_min[0], self.bbox_max[1], self.bbox_min[2], 1.0],
            [self.bbox_max[0], self.bbox_max[1], self.bbox_min[2], 1.0],
            [self.bbox_min[0], self.bbox_min[1], self.bbox_max[2], 1.0],
            [self.bbox_max[0], self.bbox_min[1], self.bbox_max[2], 1.0],
            [self.bbox_min[0], self.bbox_max[1], self.bbox_max[2], 1.0],
            [self.bbox_max[0], self.bbox_max[1], self.bbox_max[2], 1.0],
        ], dtype=np.float64)
        tc = (corners @ mat.T)[:, :3]
        bmin = np.min(np.vstack([tc, new_pts]), axis=0) if len(new_pts) > 0 else np.min(tc, axis=0)
        bmax = np.max(np.vstack([tc, new_pts]), axis=0) if len(new_pts) > 0 else np.max(tc, axis=0)
        old_sdf = self.sdf

        def new_sdf(pts: np.ndarray) -> np.ndarray:
            ph = np.hstack([pts, np.ones((len(pts), 1), dtype=np.float64)])
            local_p = (ph @ inv_mat.T)[:, :3]
            return old_sdf(local_p)

        return SolidComponent(bmin, bmax, new_pts, new_sdf)


class TopoDS_Shape:
    """B-Rep / CSG solid representation with exact SDF, surface mesh, and sharp edges."""

    def __init__(
        self,
        verts: Optional[np.ndarray] = None,
        tris: Optional[np.ndarray] = None,
        edges: Optional[np.ndarray] = None,
        sdf: Optional[Callable[[np.ndarray], np.ndarray]] = None,
        solids: Optional[List[SolidComponent]] = None,
    ):
        self.verts = np.zeros((0, 3), dtype=np.float64) if verts is None else np.asarray(verts, dtype=np.float64)
        self.tris = np.zeros((0, 3), dtype=np.int32) if tris is None else np.asarray(tris, dtype=np.int32)
        self.edges = np.zeros((0, 2, 3), dtype=np.float64) if edges is None else np.asarray(edges, dtype=np.float64)
        self.sdf = sdf if sdf is not None else (lambda pts: np.ones(len(pts), dtype=np.float64) * 1e6)
        if solids is not None:
            self.solids = solids
        elif len(self.verts) > 0 and len(self.tris) > 0:
            bmin = np.min(self.verts, axis=0)
            bmax = np.max(self.verts, axis=0)
            tri_centers = np.mean(self.verts[self.tris], axis=1)
            step = max(1, len(self.verts) // 150)
            step_t = max(1, len(tri_centers) // 150)
            s_pts = np.vstack([self.verts[::step], tri_centers[::step_t], 0.5 * (bmin + bmax)])
            self.solids = [SolidComponent(bmin, bmax, s_pts, self.sdf)]
        else:
            self.solids = []

    def IsNull(self) -> bool:
        return len(self.verts) == 0 or len(self.tris) == 0

    def clone(self) -> "TopoDS_Shape":
        return TopoDS_Shape(
            verts=self.verts.copy(),
            tris=self.tris.copy(),
            edges=self.edges.copy(),
            sdf=self.sdf,
            solids=[
                SolidComponent(c.bbox_min.copy(), c.bbox_max.copy(), c.sample_pts.copy(), c.sdf)
                for c in self.solids
            ],
        )


def _transform_shape(shape: TopoDS_Shape, mat: np.ndarray) -> TopoDS_Shape:
    if shape.IsNull():
        return shape.clone()
    try:
        inv_mat = np.linalg.inv(mat)
    except np.linalg.LinAlgError:
        inv_mat = np.eye(4, dtype=np.float64)

    vh = np.hstack([shape.verts, np.ones((len(shape.verts), 1), dtype=np.float64)])
    new_verts = (vh @ mat.T)[:, :3]

    det = np.linalg.det(mat[:3, :3])
    new_tris = shape.tris[:, [0, 2, 1]].copy() if det < 0 else shape.tris.copy()

    if len(shape.edges) > 0:
        e_flat = shape.edges.reshape(-1, 3)
        eh = np.hstack([e_flat, np.ones((len(e_flat), 1), dtype=np.float64)])
        new_edges = (eh @ mat.T)[:, :3].reshape(-1, 2, 3)
    else:
        new_edges = np.zeros((0, 2, 3), dtype=np.float64)

    old_sdf = shape.sdf
    scale_factor = float(abs(det) ** (1.0 / 3.0)) if abs(det) > 1e-12 else 1.0

    def new_sdf(pts: np.ndarray) -> np.ndarray:
        if len(pts) == 0:
            return np.zeros(0, dtype=np.float64)
        ph = np.hstack([pts, np.ones((len(pts), 1), dtype=np.float64)])
        local_p = (ph @ inv_mat.T)[:, :3]
        return old_sdf(local_p) * scale_factor

    new_solids = [c.transformed(mat, inv_mat) for c in shape.solids]
    return TopoDS_Shape(new_verts, new_tris, new_edges, new_sdf, new_solids)


# ============================================================================
# 3. Mesh Subdivision & Analytical-SDF Boolean Clipping Engine
# ============================================================================

def _subdivide_triangles_in_box(
    verts: np.ndarray,
    tris: np.ndarray,
    box_min: np.ndarray,
    box_max: np.ndarray,
    max_edge_len: float,
    max_levels: int = 3,
) -> Tuple[np.ndarray, np.ndarray]:
    """Subdivides triangles overlapping [box_min, box_max] whose edges exceed max_edge_len."""
    if len(tris) == 0:
        return verts, tris
    cur_v = verts
    cur_t = tris
    for _ in range(max_levels):
        tv = cur_v[cur_t]  # (M, 3, 3)
        tmin = np.min(tv, axis=1)
        tmax = np.max(tv, axis=1)
        overlap = np.all((tmax >= box_min) & (tmin <= box_max), axis=1)
        if not np.any(overlap):
            break
        e01 = np.linalg.norm(tv[:, 1] - tv[:, 0], axis=1)
        e12 = np.linalg.norm(tv[:, 2] - tv[:, 1], axis=1)
        e20 = np.linalg.norm(tv[:, 0] - tv[:, 2], axis=1)
        max_e = np.maximum(np.maximum(e01, e12), e20)
        need_sub = overlap & (max_e > max_edge_len)
        if not np.any(need_sub):
            break

        keep_t = cur_t[~need_sub]
        sub_t = cur_t[need_sub]
        v0 = cur_v[sub_t[:, 0]]
        v1 = cur_v[sub_t[:, 1]]
        v2 = cur_v[sub_t[:, 2]]
        m01 = 0.5 * (v0 + v1)
        m12 = 0.5 * (v1 + v2)
        m20 = 0.5 * (v2 + v0)

        base = len(cur_v)
        n_sub = len(sub_t)
        cur_v = np.vstack([cur_v, m01, m12, m20])
        i0 = sub_t[:, 0]
        i1 = sub_t[:, 1]
        i2 = sub_t[:, 2]
        im01 = np.arange(base, base + n_sub, dtype=np.int32)
        im12 = np.arange(base + n_sub, base + 2 * n_sub, dtype=np.int32)
        im20 = np.arange(base + 2 * n_sub, base + 3 * n_sub, dtype=np.int32)

        t_new = np.vstack([
            np.column_stack([i0, im01, im20]),
            np.column_stack([im01, i1, im12]),
            np.column_stack([im20, im12, i2]),
            np.column_stack([im01, im12, im20]),
        ])
        cur_t = np.vstack([keep_t, t_new]) if len(keep_t) > 0 else t_new
        if len(cur_t) > 35000:
            break
    return cur_v, cur_t


def _bisect_sdf_crossing(
    pa: np.ndarray,
    pb: np.ndarray,
    da: float,
    db: float,
    sdf_func: Callable[[np.ndarray], np.ndarray],
    keep_positive: bool = True,
    eps: float = 0.0,
) -> np.ndarray:
    """Finds exact boundary crossing point along segment pa -> pb via 7-step bisection."""
    a_in = (da >= -eps)
    lo = 0.0
    hi = 1.0
    for _ in range(7):
        mid = 0.5 * (lo + hi)
        pm = pa + mid * (pb - pa)
        dm = float(sdf_func(pm[None, :])[0])
        if not keep_positive:
            dm = -dm
        if (dm >= -eps) == a_in:
            lo = mid
        else:
            hi = mid
    t = 0.5 * (lo + hi)
    return pa + t * (pb - pa)


def _clip_mesh_against_sdf(
    verts: np.ndarray,
    tris: np.ndarray,
    sdf_func: Callable[[np.ndarray], np.ndarray],
    keep_positive: bool = True,
    eps: float = 1e-5,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Clips mesh triangles against sdf_func(p) >= 0 (if keep_positive) or <= 0.
    Returns (new_verts, new_tris, cut_contour_edges).
    """
    if len(tris) == 0 or len(verts) == 0:
        return verts, tris, np.zeros((0, 2, 3), dtype=np.float64)

    d = sdf_func(verts).astype(np.float64)
    if not keep_positive:
        d = -d

    d_tris = d[tris]  # (M, 3)
    in0 = d_tris[:, 0] >= -eps
    in1 = d_tris[:, 1] >= -eps
    in2 = d_tris[:, 2] >= -eps
    count_in = in0.astype(np.int32) + in1.astype(np.int32) + in2.astype(np.int32)

    # Check triangle centroids for all-in or all-out triangles to catch grazed faces
    all_in_mask = count_in == 3
    keep_tris = tris[all_in_mask]

    straddle_idx = np.where((count_in == 1) | (count_in == 2))[0]
    if len(straddle_idx) == 0:
        if len(keep_tris) > 0:
            used_v, inv_idx = np.unique(keep_tris.ravel(), return_inverse=True)
            verts = verts[used_v]
            keep_tris = inv_idx.reshape(-1, 3).astype(np.int32)
        else:
            verts = np.zeros((0, 3), dtype=np.float64)
        return verts, keep_tris, np.zeros((0, 2, 3), dtype=np.float64)

    extra_verts: List[np.ndarray] = []
    extra_tris: List[Tuple[int, int, int]] = []
    cut_edges: List[np.ndarray] = []
    next_vid = len(verts)

    for idx in straddle_idx:
        t = tris[idx]
        dv = d_tris[idx]
        ins = dv >= -eps
        # Rotate indices so vertex 0 is the isolated one (either the single IN or single OUT)
        if np.sum(ins) == 1:
            solo = int(np.where(ins)[0][0])
        else:
            solo = int(np.where(~ins)[0][0])
        i0 = t[solo]
        i1 = t[(solo + 1) % 3]
        i2 = t[(solo + 2) % 3]
        d0 = dv[solo]
        d1 = dv[(solo + 1) % 3]
        d2 = dv[(solo + 2) % 3]

        p0 = verts[i0]
        p1 = verts[i1]
        p2 = verts[i2]

        p01 = _bisect_sdf_crossing(p0, p1, float(d0), float(d1), sdf_func, keep_positive=keep_positive, eps=eps)
        p02 = _bisect_sdf_crossing(p0, p2, float(d0), float(d2), sdf_func, keep_positive=keep_positive, eps=eps)

        id01 = next_vid
        id02 = next_vid + 1
        next_vid += 2
        extra_verts.append(p01)
        extra_verts.append(p02)
        cut_edges.append(np.array([p01, p02], dtype=np.float64))

        if np.sum(ins) == 1:
            # i0 is IN, i1 & i2 are OUT
            extra_tris.append((int(i0), id01, id02))
        else:
            # i0 is OUT, i1 & i2 are IN
            extra_tris.append((id01, int(i1), int(i2)))
            extra_tris.append((id01, int(i2), id02))

    if extra_verts:
        new_verts = np.vstack([verts, np.array(extra_verts, dtype=np.float64)])
        new_tris = np.vstack([keep_tris, np.array(extra_tris, dtype=np.int32)]) if len(keep_tris) > 0 else np.array(extra_tris, dtype=np.int32)
        new_cut_edges = np.array(cut_edges, dtype=np.float64)
    else:
        new_verts = verts
        new_tris = keep_tris
        new_cut_edges = np.zeros((0, 2, 3), dtype=np.float64)

    if len(new_tris) > 0:
        used_v, inv_idx = np.unique(new_tris.ravel(), return_inverse=True)
        new_verts = new_verts[used_v]
        new_tris = inv_idx.reshape(-1, 3).astype(np.int32)
    else:
        new_verts = np.zeros((0, 3), dtype=np.float64)
    return new_verts, new_tris, new_cut_edges


def _clip_edges_against_sdf(
    edges: np.ndarray,
    sdf_func: Callable[[np.ndarray], np.ndarray],
    keep_positive: bool = True,
    eps: float = 1e-3,
) -> np.ndarray:
    """Clips 3D feature line segments against sdf_func(p) >= -eps (or <= eps),
    subdividing long segments so middle penetrations are also accurately trimmed.
    """
    if len(edges) == 0:
        return edges

    # Subdivide edges longer than 18mm into smaller segments before clipping
    lengths = np.linalg.norm(edges[:, 1, :] - edges[:, 0, :], axis=1)
    short_mask = lengths <= 18.0
    work_list = []
    if np.any(short_mask):
        work_list.append(edges[short_mask])
    long_edges = edges[~short_mask]
    if len(long_edges) > 0:
        n_sub = 8
        ts = np.linspace(0.0, 1.0, n_sub + 1)
        p_start = long_edges[:, 0, :][:, None, :]
        p_vec = (long_edges[:, 1, :] - long_edges[:, 0, :])[:, None, :]
        pts_grid = p_start + ts[None, :, None] * p_vec  # (M, n_sub+1, 3)
        sub_segs = np.stack([pts_grid[:, :-1, :], pts_grid[:, 1:, :]], axis=2).reshape(-1, 2, 3)
        work_list.append(sub_segs)

    work = np.vstack(work_list) if work_list else edges
    p0 = work[:, 0, :]
    p1 = work[:, 1, :]
    mid = 0.5 * (p0 + p1)
    d0 = sdf_func(p0)
    d1 = sdf_func(p1)
    dm = sdf_func(mid)
    if not keep_positive:
        d0, d1, dm = -d0, -d1, -dm

    all_in = (d0 >= -eps) & (d1 >= -eps) & (dm >= -eps)
    kept = [work[all_in]]

    straddle = ((d0 >= -eps) ^ (d1 >= -eps))
    s_idx = np.where(straddle)[0]
    if len(s_idx) > 0:
        clipped_segs = []
        for idx in s_idx:
            a, b = p0[idx], p1[idx]
            da, db = float(d0[idx]), float(d1[idx])
            pm = _bisect_sdf_crossing(a, b, da, db, sdf_func, keep_positive=keep_positive, eps=eps)
            if da >= -eps:
                clipped_segs.append([a, pm])
            else:
                clipped_segs.append([pm, b])
        if clipped_segs:
            kept.append(np.array(clipped_segs, dtype=np.float64))

    return np.vstack(kept) if kept else np.zeros((0, 2, 3), dtype=np.float64)


def _components_touch(c1: SolidComponent, c2: SolidComponent, tol: float = 2.5) -> bool:
    """Checks whether two solid components touch or intersect in 3D space."""
    if np.any(c1.bbox_max + tol < c2.bbox_min) or np.any(c2.bbox_max + tol < c1.bbox_min):
        return False

    if len(c1.sample_pts) > 0:
        d12 = c2.sdf(c1.sample_pts)
        if np.any(d12 <= tol):
            return True
    if len(c2.sample_pts) > 0:
        d21 = c1.sdf(c2.sample_pts)
        if np.any(d21 <= tol):
            return True

    # Probe overlapping AABB region with a 6x6x6 grid
    omin = np.maximum(c1.bbox_min, c2.bbox_min) - tol * 0.5
    omax = np.minimum(c1.bbox_max, c2.bbox_max) + tol * 0.5
    if np.all(omax >= omin):
        gx = np.linspace(omin[0], omax[0], 6)
        gy = np.linspace(omin[1], omax[1], 6)
        gz = np.linspace(omin[2], omax[2], 6)
        xx, yy, zz = np.meshgrid(gx, gy, gz, indexing="ij")
        grid = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])
        if np.any((c1.sdf(grid) <= tol) & (c2.sdf(grid) <= tol)):
            return True
    return False


def _merge_connected_components(comps: List[SolidComponent], tol: float = 2.5) -> List[SolidComponent]:
    n = len(comps)
    if n <= 1:
        return comps
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            ri, rj = find(i), find(j)
            if ri != rj and _components_touch(comps[i], comps[j], tol=tol):
                parent[rj] = ri

    groups: dict[int, List[SolidComponent]] = {}
    for i in range(n):
        r = find(i)
        groups.setdefault(r, []).append(comps[i])

    merged: List[SolidComponent] = []
    for grp in groups.values():
        if len(grp) == 1:
            merged.append(grp[0])
        else:
            bmin = np.min([g.bbox_min for g in grp], axis=0)
            bmax = np.max([g.bbox_max for g in grp], axis=0)
            s_pts = np.vstack([g.sample_pts for g in grp if len(g.sample_pts) > 0])
            if len(s_pts) > 500:
                step = max(1, len(s_pts) // 500)
                s_pts = s_pts[::step]
            sdfs = [g.sdf for g in grp]

            def combined_sdf(pts: np.ndarray, _sdfs=sdfs) -> np.ndarray:
                res = _sdfs[0](pts)
                for fn in _sdfs[1:]:
                    res = np.minimum(res, fn(pts))
                return res

            merged.append(SolidComponent(bmin, bmax, s_pts, combined_sdf))
    return merged


# ============================================================================
# 4. Primitive Mesh & SDF Generators (OCC.Core.BRepPrimAPI)
# ============================================================================

def _make_box_shape(p1: gp_Pnt, p2: gp_Pnt) -> TopoDS_Shape:
    x0, y0, z0 = min(p1.X(), p2.X()), min(p1.Y(), p2.Y()), min(p1.Z(), p2.Z())
    x1, y1, z1 = max(p1.X(), p2.X()), max(p1.Y(), p2.Y()), max(p1.Z(), p2.Z())
    verts = np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
    ], dtype=np.float64)
    tris = np.array([
        [0, 2, 1], [0, 3, 2],  # bottom (-Z)
        [4, 5, 6], [4, 6, 7],  # top (+Z)
        [0, 1, 5], [0, 5, 4],  # front (-Y)
        [2, 3, 7], [2, 7, 6],  # back (+Y)
        [0, 4, 7], [0, 7, 3],  # left (-X)
        [1, 2, 6], [1, 6, 5],  # right (+X)
    ], dtype=np.int32)
    edge_idx = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
    ]
    edges = np.array([[verts[a], verts[b]] for a, b in edge_idx], dtype=np.float64)
    cx, cy, cz = 0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1)
    hx, hy, hz = 0.5 * (x1 - x0), 0.5 * (y1 - y0), 0.5 * (z1 - z0)

    def box_sdf(pts: np.ndarray) -> np.ndarray:
        q = np.abs(pts - np.array([cx, cy, cz])) - np.array([hx, hy, hz])
        return np.linalg.norm(np.maximum(q, 0.0), axis=1) + np.minimum(np.max(q, axis=1), 0.0)

    return TopoDS_Shape(verts, tris, edges, box_sdf)


def _make_cylinder_shape(ax2: gp_Ax2, r: float, h: float, n_seg: int = 36) -> TopoDS_Shape:
    r = max(1e-4, float(r))
    h = max(1e-4, float(h))
    angles = np.linspace(0.0, 2.0 * math.pi, n_seg, endpoint=False)
    ca, sa = np.cos(angles), np.sin(angles)

    bot_ring = np.column_stack([r * ca, r * sa, np.zeros(n_seg)])
    top_ring = np.column_stack([r * ca, r * sa, np.full(n_seg, h)])
    bot_cap_ring = bot_ring.copy()
    top_cap_ring = top_ring.copy()
    bot_center = np.array([[0.0, 0.0, 0.0]])
    top_center = np.array([[0.0, 0.0, h]])
    verts = np.vstack([bot_ring, top_ring, bot_cap_ring, top_cap_ring, bot_center, top_center])
    ic_bot = 4 * n_seg
    ic_top = 4 * n_seg + 1

    tris = []
    edges = []
    for i in range(n_seg):
        j = (i + 1) % n_seg
        # side quad (indices 0 .. 2*n_seg-1)
        tris.append([i, j, n_seg + j])
        tris.append([i, n_seg + j, n_seg + i])
        # bottom cap (indices 2*n_seg .. 3*n_seg-1)
        tris.append([ic_bot, 2 * n_seg + j, 2 * n_seg + i])
        # top cap (indices 3*n_seg .. 4*n_seg-1)
        tris.append([ic_top, 3 * n_seg + i, 3 * n_seg + j])
        edges.append([bot_ring[i], bot_ring[j]])
        edges.append([top_ring[i], top_ring[j]])

    def cyl_sdf(pts: np.ndarray) -> np.ndarray:
        d_rad = np.hypot(pts[:, 0], pts[:, 1]) - r
        d_z = np.abs(pts[:, 2] - 0.5 * h) - 0.5 * h
        d = np.column_stack([d_rad, d_z])
        return np.linalg.norm(np.maximum(d, 0.0), axis=1) + np.minimum(np.max(d, axis=1), 0.0)

    shape = TopoDS_Shape(
        np.array(verts, dtype=np.float64),
        np.array(tris, dtype=np.int32),
        np.array(edges, dtype=np.float64),
        cyl_sdf,
    )
    mat = ax2.BasisMatrix()
    if not np.allclose(mat, np.eye(4)):
        shape = _transform_shape(shape, mat)
    return shape


def _make_cone_shape(
    ax2: gp_Ax2,
    r1: float,
    r2: float,
    h: float,
    ecc_x: float = 0.0,
    ecc_y: float = 0.0,
    n_seg: int = 36,
) -> TopoDS_Shape:
    r1 = max(0.0, float(r1))
    r2 = max(0.0, float(r2))
    h = max(1e-4, float(h))
    if r1 < 1e-6 and r2 < 1e-6:
        r1 = 1e-3
    angles = np.linspace(0.0, 2.0 * math.pi, n_seg, endpoint=False)
    ca, sa = np.cos(angles), np.sin(angles)

    r1_eff = max(r1, 1e-5)
    r2_eff = max(r2, 1e-5)
    bot_ring = np.column_stack([r1_eff * ca, r1_eff * sa, np.zeros(n_seg)])
    top_ring = np.column_stack([ecc_x + r2_eff * ca, ecc_y + r2_eff * sa, np.full(n_seg, h)])
    bot_cap_ring = bot_ring.copy()
    top_cap_ring = top_ring.copy()
    bot_center = np.array([[0.0, 0.0, 0.0]])
    top_center = np.array([[ecc_x, ecc_y, h]])
    verts = np.vstack([bot_ring, top_ring, bot_cap_ring, top_cap_ring, bot_center, top_center])
    ic_bot = 4 * n_seg
    ic_top = 4 * n_seg + 1

    tris = []
    edges = []
    for i in range(n_seg):
        j = (i + 1) % n_seg
        tris.append([i, j, n_seg + j])
        tris.append([i, n_seg + j, n_seg + i])
        if r1 > 1e-4:
            tris.append([ic_bot, 2 * n_seg + j, 2 * n_seg + i])
            edges.append([bot_ring[i], bot_ring[j]])
        if r2 > 1e-4:
            tris.append([ic_top, 3 * n_seg + i, 3 * n_seg + j])
            edges.append([top_ring[i], top_ring[j]])

    def cone_sdf(pts: np.ndarray) -> np.ndarray:
        t = np.clip(pts[:, 2] / h, 0.0, 1.0)
        cx = t * ecc_x
        cy = t * ecc_y
        rt = r1 + t * (r2 - r1)
        d_rad = np.hypot(pts[:, 0] - cx, pts[:, 1] - cy) - rt
        d_z = np.abs(pts[:, 2] - 0.5 * h) - 0.5 * h
        d = np.column_stack([d_rad, d_z])
        return np.linalg.norm(np.maximum(d, 0.0), axis=1) + np.minimum(np.max(d, axis=1), 0.0)

    shape = TopoDS_Shape(
        np.array(verts, dtype=np.float64),
        np.array(tris, dtype=np.int32),
        np.array(edges, dtype=np.float64) if edges else np.zeros((0, 2, 3), dtype=np.float64),
        cone_sdf,
    )
    mat = ax2.BasisMatrix()
    if not np.allclose(mat, np.eye(4)):
        shape = _transform_shape(shape, mat)
    return shape


def _make_torus_shape(
    ax2: gp_Ax2,
    r1: float,
    r2: float,
    angle_sweep_rad: float = 2.0 * math.pi,
    r2_end: Optional[float] = None,
    n_u: int = 36,
    n_v: int = 24,
) -> TopoDS_Shape:
    r1 = max(1e-4, float(r1))
    r2_start = max(1e-4, float(r2))
    r2_final = max(1e-4, float(r2_end)) if r2_end is not None else r2_start
    full_circle = abs(angle_sweep_rad - 2.0 * math.pi) < 1e-5 and abs(r2_start - r2_final) < 1e-5

    u_vals = np.linspace(0.0, angle_sweep_rad, n_u, endpoint=not full_circle)
    v_vals = np.linspace(0.0, 2.0 * math.pi, n_v, endpoint=False)

    verts = []
    for iu, u in enumerate(u_vals):
        t = iu / max(1, len(u_vals) - 1) if not full_circle else 0.0
        ru = r2_start + t * (r2_final - r2_start)
        cu, su = math.cos(u), math.sin(u)
        for v in v_vals:
            cv, sv = math.cos(v), math.sin(v)
            rho = r1 + ru * cv
            verts.append([rho * cu, rho * su, ru * sv])

    tris = []
    edges = []
    num_u = len(u_vals)
    for iu in range(num_u if full_circle else num_u - 1):
        iu_next = (iu + 1) % num_u
        for iv in range(n_v):
            iv_next = (iv + 1) % n_v
            a = iu * n_v + iv
            b = iu_next * n_v + iv
            c = iu_next * n_v + iv_next
            d = iu * n_v + iv_next
            tris.append([a, b, c])
            tris.append([a, c, d])

    if not full_circle:
        # Cap start (u=0) and end (u=angle_sweep_rad)
        ic_start = len(verts)
        verts.append([r1, 0.0, 0.0])
        ic_end = len(verts)
        cu_e, su_e = math.cos(angle_sweep_rad), math.sin(angle_sweep_rad)
        verts.append([r1 * cu_e, r1 * su_e, 0.0])
        for iv in range(n_v):
            iv_next = (iv + 1) % n_v
            tris.append([ic_start, iv_next, iv])
            edges.append([verts[iv], verts[iv_next]])
            end_base = (num_u - 1) * n_v
            tris.append([ic_end, end_base + iv, end_base + iv_next])
            edges.append([verts[end_base + iv], verts[end_base + iv_next]])

    def torus_sdf(pts: np.ndarray) -> np.ndarray:
        ang = np.mod(np.arctan2(pts[:, 1], pts[:, 0]), 2.0 * math.pi)
        rho = np.hypot(pts[:, 0], pts[:, 1])
        if full_circle:
            return np.hypot(rho - r1, pts[:, 2]) - r2_start
        t = np.clip(ang / max(angle_sweep_rad, 1e-6), 0.0, 1.0)
        ru = r2_start + t * (r2_final - r2_start)
        d_tube = np.hypot(rho - r1, pts[:, 2]) - ru
        # Angular bounds check
        c_mid = math.cos(0.5 * angle_sweep_rad)
        s_mid = math.sin(0.5 * angle_sweep_rad)
        # Rotate pts by -0.5 * angle_sweep_rad around Z
        rx = pts[:, 0] * c_mid + pts[:, 1] * s_mid
        ry = -pts[:, 0] * s_mid + pts[:, 1] * c_mid
        ang_rel = np.abs(np.arctan2(ry, rx))
        d_ang = (ang_rel - 0.5 * angle_sweep_rad) * r1
        return np.maximum(d_tube, d_ang)

    shape = TopoDS_Shape(
        np.array(verts, dtype=np.float64),
        np.array(tris, dtype=np.int32),
        np.array(edges, dtype=np.float64) if edges else np.zeros((0, 2, 3), dtype=np.float64),
        torus_sdf,
    )
    mat = ax2.BasisMatrix()
    if not np.allclose(mat, np.eye(4)):
        shape = _transform_shape(shape, mat)
    return shape


def _make_sphere_shape(
    center: gp_Pnt,
    r: float,
    theta_min: float = -0.5 * math.pi,
    theta_max: float = 0.5 * math.pi,
    phi_sweep: float = 2.0 * math.pi,
    n_lat: int = 20,
    n_lon: int = 36,
) -> TopoDS_Shape:
    r = max(1e-4, float(r))
    cx, cy, cz = center.Coord()
    lats = np.linspace(theta_min, theta_max, n_lat + 1)
    full_phi = abs(phi_sweep - 2.0 * math.pi) < 1e-5
    lons = np.linspace(0.0, phi_sweep, n_lon, endpoint=not full_phi)
    num_lon = len(lons)

    verts = []
    for lat in lats:
        clat, slat = math.cos(lat), math.sin(lat)
        for lon in lons:
            verts.append([
                cx + r * clat * math.cos(lon),
                cy + r * clat * math.sin(lon),
                cz + r * slat,
            ])

    tris = []
    edges = []
    for ilat in range(n_lat):
        for ilon in range(num_lon if full_phi else num_lon - 1):
            ilon_next = (ilon + 1) % num_lon
            a = ilat * num_lon + ilon
            b = (ilat + 1) * num_lon + ilon
            c = (ilat + 1) * num_lon + ilon_next
            d = ilat * num_lon + ilon_next
            tris.append([a, d, c])
            tris.append([a, c, b])

    # Cap bottom if theta_min > -pi/2
    if theta_min > -0.5 * math.pi + 1e-4:
        ic_bot = len(verts)
        z_bot = cz + r * math.sin(theta_min)
        verts.append([cx, cy, z_bot])
        for ilon in range(num_lon if full_phi else num_lon - 1):
            ilon_next = (ilon + 1) % num_lon
            tris.append([ic_bot, ilon_next, ilon])
            edges.append([verts[ilon], verts[ilon_next]])

    # Cap top if theta_max < pi/2
    if theta_max < 0.5 * math.pi - 1e-4:
        ic_top = len(verts)
        z_top = cz + r * math.sin(theta_max)
        verts.append([cx, cy, z_top])
        top_base = n_lat * num_lon
        for ilon in range(num_lon if full_phi else num_lon - 1):
            ilon_next = (ilon + 1) % num_lon
            tris.append([ic_top, top_base + ilon, top_base + ilon_next])
            edges.append([verts[top_base + ilon], verts[top_base + ilon_next]])

    z_min = cz + r * math.sin(theta_min)
    z_max = cz + r * math.sin(theta_max)

    def sphere_sdf(pts: np.ndarray) -> np.ndarray:
        dp = pts - np.array([cx, cy, cz])
        d_sph = np.linalg.norm(dp, axis=1) - r
        if theta_min > -0.5 * math.pi + 1e-4:
            d_sph = np.maximum(d_sph, z_min - pts[:, 2])
        if theta_max < 0.5 * math.pi - 1e-4:
            d_sph = np.maximum(d_sph, pts[:, 2] - z_max)
        return d_sph

    return TopoDS_Shape(
        np.array(verts, dtype=np.float64),
        np.array(tris, dtype=np.int32),
        np.array(edges, dtype=np.float64) if edges else np.zeros((0, 2, 3), dtype=np.float64),
        sphere_sdf,
    )


class BRepPrimAPI_MakeBox:
    def __init__(self, *args):
        if len(args) == 2 and isinstance(args[0], gp_Pnt) and isinstance(args[1], gp_Pnt):
            self._shape = _make_box_shape(args[0], args[1])
        elif len(args) == 3:
            dx, dy, dz = float(args[0]), float(args[1]), float(args[2])
            self._shape = _make_box_shape(gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(dx, dy, dz))
        elif len(args) == 4 and isinstance(args[0], gp_Pnt):
            p = args[0]
            dx, dy, dz = float(args[1]), float(args[2]), float(args[3])
            self._shape = _make_box_shape(p, gp_Pnt(p.X() + dx, p.Y() + dy, p.Z() + dz))
        else:
            raise ValueError(f"Unsupported BRepPrimAPI_MakeBox args: {args}")

    def Build(self) -> None:
        pass

    def IsDone(self) -> bool:
        return True

    def SetRunParallel(self, on: bool) -> None:
        pass

    def Shape(self) -> TopoDS_Shape:
        return self._shape


class BRepPrimAPI_MakeCylinder:
    def __init__(self, *args):
        if len(args) == 2:
            r, h = float(args[0]), float(args[1])
            ax2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
        elif len(args) >= 3 and isinstance(args[0], gp_Ax2):
            ax2 = args[0]
            r, h = float(args[1]), float(args[2])
        else:
            raise ValueError(f"Unsupported BRepPrimAPI_MakeCylinder args: {args}")
        self._shape = _make_cylinder_shape(ax2, r, h)

    def Build(self) -> None:
        pass

    def IsDone(self) -> bool:
        return True

    def SetRunParallel(self, on: bool) -> None:
        pass

    def Shape(self) -> TopoDS_Shape:
        return self._shape


class BRepPrimAPI_MakeCone:
    def __init__(self, *args):
        if len(args) == 3:
            r1, r2, h = float(args[0]), float(args[1]), float(args[2])
            ax2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
        elif len(args) >= 4 and isinstance(args[0], gp_Ax2):
            ax2 = args[0]
            r1, r2, h = float(args[1]), float(args[2]), float(args[3])
        else:
            raise ValueError(f"Unsupported BRepPrimAPI_MakeCone args: {args}")
        self._shape = _make_cone_shape(ax2, r1, r2, h)

    def Build(self) -> None:
        pass

    def IsDone(self) -> bool:
        return True

    def SetRunParallel(self, on: bool) -> None:
        pass

    def Shape(self) -> TopoDS_Shape:
        return self._shape


class BRepPrimAPI_MakeTorus:
    def __init__(self, *args):
        if len(args) == 2:
            r1, r2 = float(args[0]), float(args[1])
            ax2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
            ang = 2.0 * math.pi
        elif len(args) == 3 and isinstance(args[0], gp_Ax2):
            ax2, r1, r2 = args[0], float(args[1]), float(args[2])
            ang = 2.0 * math.pi
        elif len(args) == 3 and not isinstance(args[0], gp_Ax2):
            r1, r2, ang = float(args[0]), float(args[1]), float(args[2])
            ax2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
        elif len(args) >= 4 and isinstance(args[0], gp_Ax2):
            ax2, r1, r2, ang = args[0], float(args[1]), float(args[2]), float(args[3])
        else:
            raise ValueError(f"Unsupported BRepPrimAPI_MakeTorus args: {args}")
        self._shape = _make_torus_shape(ax2, r1, r2, ang)

    def Build(self) -> None:
        pass

    def IsDone(self) -> bool:
        return True

    def SetRunParallel(self, on: bool) -> None:
        pass

    def Shape(self) -> TopoDS_Shape:
        return self._shape


class BRepPrimAPI_MakeSphere:
    def __init__(self, *args):
        if len(args) == 1:
            c, r = gp_Pnt(0, 0, 0), float(args[0])
            t1, t2 = -0.5 * math.pi, 0.5 * math.pi
        elif len(args) == 2 and isinstance(args[0], gp_Pnt):
            c, r = args[0], float(args[1])
            t1, t2 = -0.5 * math.pi, 0.5 * math.pi
        elif len(args) == 3 and isinstance(args[0], gp_Pnt):
            c, r = args[0], float(args[1])
            t1, t2 = 0.0, float(args[2])
        elif len(args) >= 4 and isinstance(args[0], gp_Pnt):
            c, r, t1, t2 = args[0], float(args[1]), float(args[2]), float(args[3])
        else:
            c, r = gp_Pnt(0, 0, 0), float(args[0])
            t1, t2 = -0.5 * math.pi, 0.5 * math.pi
        self._shape = _make_sphere_shape(c, r, t1, t2)

    def Build(self) -> None:
        pass

    def IsDone(self) -> bool:
        return True

    def SetRunParallel(self, on: bool) -> None:
        pass

    def Shape(self) -> TopoDS_Shape:
        return self._shape


# ============================================================================
# 5. Boolean CSG Operations (OCC.Core.BRepAlgoAPI) & Builder Transform
# ============================================================================

class BRepAlgoAPI_Fuse:
    def __init__(self, s1: TopoDS_Shape, s2: TopoDS_Shape):
        if s1 is None or s1.IsNull():
            self._shape = s2.clone() if s2 is not None else TopoDS_Shape()
            return
        if s2 is None or s2.IsNull():
            self._shape = s1.clone()
            return

        v1, t1, e1 = s1.verts, s1.tris, s1.edges
        v2, t2, e2 = s2.verts, s2.tris, s2.edges
        if len(v1) > 0 and len(v2) > 0:
            span1 = float(np.ptp(v1, axis=0).max())
            span2 = float(np.ptp(v2, axis=0).max())
            if span1 <= 0.5 and span2 > 5.0:
                self._shape = s2.clone()
                return
            if span2 <= 0.5 and span1 > 5.0:
                self._shape = s1.clone()
                return
        # Remove internal triangles strictly buried inside the partner solid
        if len(t1) > 0:
            c1 = np.mean(v1[t1], axis=1)
            v1_all = v1[t1]
            buried1 = (s2.sdf(c1) < -0.25) & (s2.sdf(v1_all[:, 0]) < -0.05) & (s2.sdf(v1_all[:, 1]) < -0.05) & (s2.sdf(v1_all[:, 2]) < -0.05)
            t1 = t1[~buried1]
        if len(t2) > 0:
            c2 = np.mean(v2[t2], axis=1)
            v2_all = v2[t2]
            buried2 = (s1.sdf(c2) < -0.25) & (s1.sdf(v2_all[:, 0]) < -0.05) & (s1.sdf(v2_all[:, 1]) < -0.05) & (s1.sdf(v2_all[:, 2]) < -0.05)
            t2 = t2[~buried2]

        new_verts = np.vstack([v1, v2])
        new_tris = np.vstack([t1, t2 + len(v1)]) if (len(t1) > 0 and len(t2) > 0) else (t1 if len(t1) > 0 else t2 + len(v1))
        e1_clip = _clip_edges_against_sdf(e1, s2.sdf, keep_positive=True, eps=0.15) if len(e1) > 0 else e1
        e2_clip = _clip_edges_against_sdf(e2, s1.sdf, keep_positive=True, eps=0.15) if len(e2) > 0 else e2
        if len(e1_clip) > 0 and len(e2_clip) > 0:
            new_edges = np.vstack([e1_clip, e2_clip])
        elif len(e1_clip) > 0:
            new_edges = e1_clip.copy()
        else:
            new_edges = e2_clip.copy()

        sdf1, sdf2 = s1.sdf, s2.sdf

        def fuse_sdf(pts: np.ndarray) -> np.ndarray:
            return np.minimum(sdf1(pts), sdf2(pts))

        merged_solids = _merge_connected_components(s1.solids + s2.solids, tol=2.5)
        self._shape = TopoDS_Shape(new_verts, new_tris, new_edges, fuse_sdf, merged_solids)

    def Build(self) -> None:
        pass

    def IsDone(self) -> bool:
        return True

    def SetRunParallel(self, on: bool) -> None:
        pass

    def Shape(self) -> TopoDS_Shape:
        return self._shape


class BRepAlgoAPI_Cut:
    def __init__(self, s1: TopoDS_Shape, s2: TopoDS_Shape):
        if s1 is None or s1.IsNull() or s2 is None or s2.IsNull():
            self._shape = s1.clone() if s1 is not None else TopoDS_Shape()
            return

        bmin2 = np.min(s2.verts, axis=0) - 1.0
        bmax2 = np.max(s2.verts, axis=0) + 1.0
        bmin1 = np.min(s1.verts, axis=0) - 1.0
        bmax1 = np.max(s1.verts, axis=0) + 1.0

        # Check if bounding boxes overlap at all
        if np.any(bmax1 < bmin2) or np.any(bmax2 < bmin1):
            self._shape = s1.clone()
            return

        # Subdivide triangles of s1 in overlap region so interior holes are captured accurately
        span2 = bmax2 - bmin2
        min_dim2 = max(2.0, float(np.min(span2[span2 > 1e-3])) if np.any(span2 > 1e-3) else 5.0)
        max_edge = max(3.0, min_dim2 * 0.45)

        v1_sub, t1_sub = _subdivide_triangles_in_box(s1.verts, s1.tris, bmin2, bmax2, max_edge_len=max_edge, max_levels=3)
        v1_clip, t1_clip, cut_edges1 = _clip_mesh_against_sdf(v1_sub, t1_sub, s2.sdf, keep_positive=True, eps=-0.02)

        # Keep portion of s2's surface that lies inside s1 (with flipped normals to form hole wall)
        v2_sub, t2_sub = _subdivide_triangles_in_box(s2.verts, s2.tris, bmin1, bmax1, max_edge_len=max_edge, max_levels=2)
        v2_clip, t2_clip, cut_edges2 = _clip_mesh_against_sdf(v2_sub, t2_sub, s1.sdf, keep_positive=False, eps=-0.02)
        if len(t2_clip) > 0:
            t2_clip = t2_clip[:, [0, 2, 1]]

        if len(t1_clip) > 0 and len(t2_clip) > 0:
            new_verts = np.vstack([v1_clip, v2_clip])
            new_tris = np.vstack([t1_clip, t2_clip + len(v1_clip)])
        elif len(t1_clip) > 0:
            new_verts = v1_clip
            new_tris = t1_clip
        else:
            new_verts = s1.verts.copy()
            new_tris = s1.tris.copy()

        e1_clip = _clip_edges_against_sdf(s1.edges, s2.sdf, keep_positive=True, eps=-0.02)
        e2_clip = _clip_edges_against_sdf(s2.edges, s1.sdf, keep_positive=False, eps=-0.02)
        span1 = bmax1 - bmin1
        is_small_hole = float(np.max(span2)) < 0.42 * float(np.max(span1))
        edge_parts = [ep for ep in (e1_clip, e2_clip, cut_edges1 if is_small_hole else ()) if len(ep) > 0]
        new_edges = np.vstack(edge_parts) if edge_parts else np.zeros((0, 2, 3), dtype=np.float64)

        sdf1, sdf2 = s1.sdf, s2.sdf

        def cut_sdf(pts: np.ndarray) -> np.ndarray:
            return np.maximum(sdf1(pts), -sdf2(pts))

        new_solids = []
        for c in s1.solids:
            csdf = c.sdf
            new_solids.append(
                SolidComponent(
                    c.bbox_min.copy(),
                    c.bbox_max.copy(),
                    c.sample_pts.copy(),
                    lambda pts, _c=csdf, _s2=sdf2: np.maximum(_c(pts), -_s2(pts)),
                )
            )
        self._shape = TopoDS_Shape(new_verts, new_tris, new_edges, cut_sdf, new_solids)

    def Build(self) -> None:
        pass

    def IsDone(self) -> bool:
        return True

    def SetRunParallel(self, on: bool) -> None:
        pass

    def Shape(self) -> TopoDS_Shape:
        return self._shape


class BRepAlgoAPI_Common:
    def __init__(self, s1: TopoDS_Shape, s2: TopoDS_Shape):
        if s1 is None or s1.IsNull() or s2 is None or s2.IsNull():
            self._shape = TopoDS_Shape()
            return

        bmin = np.maximum(np.min(s1.verts, axis=0), np.min(s2.verts, axis=0)) - 1.0
        bmax = np.minimum(np.max(s1.verts, axis=0), np.max(s2.verts, axis=0)) + 1.0
        span = np.maximum(bmax - bmin, 1.0)
        max_edge = max(3.0, float(np.min(span)) * 0.4)

        v1_sub, t1_sub = _subdivide_triangles_in_box(s1.verts, s1.tris, bmin, bmax, max_edge_len=max_edge, max_levels=2)
        v1_clip, t1_clip, cut1 = _clip_mesh_against_sdf(v1_sub, t1_sub, s2.sdf, keep_positive=False)

        v2_sub, t2_sub = _subdivide_triangles_in_box(s2.verts, s2.tris, bmin, bmax, max_edge_len=max_edge, max_levels=2)
        v2_clip, t2_clip, cut2 = _clip_mesh_against_sdf(v2_sub, t2_sub, s1.sdf, keep_positive=False)

        if len(t1_clip) > 0 and len(t2_clip) > 0:
            new_verts = np.vstack([v1_clip, v2_clip])
            new_tris = np.vstack([t1_clip, t2_clip + len(v1_clip)])
        elif len(t1_clip) > 0:
            new_verts, new_tris = v1_clip, t1_clip
        elif len(t2_clip) > 0:
            new_verts, new_tris = v2_clip, t2_clip
        else:
            new_verts, new_tris = s1.verts.copy(), s1.tris.copy()

        e1_clip = _clip_edges_against_sdf(s1.edges, s2.sdf, keep_positive=False)
        e2_clip = _clip_edges_against_sdf(s2.edges, s1.sdf, keep_positive=False, eps=-0.02)
        edge_parts = [ep for ep in (e1_clip, e2_clip, cut1, cut2) if len(ep) > 0]
        new_edges = np.vstack(edge_parts) if edge_parts else np.zeros((0, 2, 3), dtype=np.float64)

        sdf1, sdf2 = s1.sdf, s2.sdf

        def common_sdf(pts: np.ndarray) -> np.ndarray:
            return np.maximum(sdf1(pts), sdf2(pts))

        self._shape = TopoDS_Shape(new_verts, new_tris, new_edges, common_sdf)

    def Build(self) -> None:
        pass

    def IsDone(self) -> bool:
        return True

    def SetRunParallel(self, on: bool) -> None:
        pass

    def Shape(self) -> TopoDS_Shape:
        return self._shape


class BRepBuilderAPI_Transform:
    def __init__(self, shape: TopoDS_Shape, trsf: gp_Trsf, copy: bool = True):
        self._shape = _transform_shape(shape, trsf._mat)

    def Build(self) -> None:
        pass

    def IsDone(self) -> bool:
        return True

    def SetRunParallel(self, on: bool) -> None:
        pass

    def Shape(self) -> TopoDS_Shape:
        return self._shape


class BRepBuilderAPI_Copy:
    def __init__(self, shape: TopoDS_Shape):
        self._shape = shape.clone()

    def Build(self) -> None:
        pass

    def IsDone(self) -> bool:
        return True

    def SetRunParallel(self, on: bool) -> None:
        pass

    def Shape(self) -> TopoDS_Shape:
        return self._shape


# ============================================================================
# 6. Bounding Box, Triangulation & Topology Explorer
# ============================================================================

class Bnd_Box:
    def __init__(self):
        self._xmin = 0.0
        self._ymin = 0.0
        self._zmin = 0.0
        self._xmax = 0.0
        self._ymax = 0.0
        self._zmax = 0.0
        self._empty = True

    def Update(self, xmin: float, ymin: float, zmin: float, xmax: float, ymax: float, zmax: float) -> None:
        if self._empty:
            self._xmin, self._ymin, self._zmin = xmin, ymin, zmin
            self._xmax, self._ymax, self._zmax = xmax, ymax, zmax
            self._empty = False
        else:
            self._xmin = min(self._xmin, xmin)
            self._ymin = min(self._ymin, ymin)
            self._zmin = min(self._zmin, zmin)
            self._xmax = max(self._xmax, xmax)
            self._ymax = max(self._ymax, ymax)
            self._zmax = max(self._zmax, zmax)

    def IsVoid(self) -> bool:
        return self._empty

    def SetGap(self, gap: float) -> None:
        pass

    def Get(self) -> Tuple[float, float, float, float, float, float]:
        return (self._xmin, self._ymin, self._zmin, self._xmax, self._ymax, self._zmax)


class _BRepBndLib:
    @staticmethod
    def Add(shape: TopoDS_Shape, box: Bnd_Box) -> None:
        if shape is not None and not shape.IsNull():
            bmin = np.min(shape.verts, axis=0)
            bmax = np.max(shape.verts, axis=0)
            box.Update(
                float(bmin[0]), float(bmin[1]), float(bmin[2]),
                float(bmax[0]), float(bmax[1]), float(bmax[2]),
            )


brepbndlib = _BRepBndLib()


class BRepMesh_IncrementalMesh:
    def __init__(self, shape: TopoDS_Shape, deflection: float = 0.5, relative: bool = False, angle: float = 0.2, parallel: bool = True):
        self._shape = shape


TopAbs_COMPOUND = 0
TopAbs_COMPSOLID = 1
TopAbs_SOLID = 2
TopAbs_SHELL = 3
TopAbs_FACE = 4
TopAbs_WIRE = 5
TopAbs_EDGE = 6
TopAbs_VERTEX = 7


class TopLoc_Location:
    def __init__(self):
        self._trsf = gp_Trsf()

    def Transformation(self) -> gp_Trsf:
        return self._trsf


class _Poly_Triangle:
    def __init__(self, n1: int, n2: int, n3: int):
        self._n = (n1, n2, n3)

    def Get(self) -> Tuple[int, int, int]:
        return self._n


class _Poly_Triangulation:
    def __init__(self, verts: np.ndarray, tris: np.ndarray):
        self._verts = verts
        self._tris = tris

    def NbNodes(self) -> int:
        return len(self._verts)

    def NbTriangles(self) -> int:
        return len(self._tris)

    def Node(self, idx_1based: int) -> gp_Pnt:
        v = self._verts[idx_1based - 1]
        return gp_Pnt(float(v[0]), float(v[1]), float(v[2]))

    def Triangle(self, idx_1based: int) -> _Poly_Triangle:
        t = self._tris[idx_1based - 1]
        return _Poly_Triangle(int(t[0]) + 1, int(t[1]) + 1, int(t[2]) + 1)


class BRep_Tool:
    @staticmethod
    def Triangulation(face: TopoDS_Shape, loc: TopLoc_Location) -> Optional[_Poly_Triangulation]:
        if face is None or face.IsNull():
            return None
        return _Poly_Triangulation(face.verts, face.tris)


class TopExp_Explorer:
    def __init__(self, shape: TopoDS_Shape, to_find: int):
        self._items: List[TopoDS_Shape] = []
        self._idx = 0
        if shape is not None and not shape.IsNull():
            if to_find == TopAbs_SOLID:
                n_solids = max(1, len(shape.solids))
                self._items = [shape] * n_solids
            elif to_find == TopAbs_FACE:
                self._items = [shape]
            else:
                self._items = [shape]

    def More(self) -> bool:
        return self._idx < len(self._items)

    def Next(self) -> None:
        self._idx += 1

    def Current(self) -> TopoDS_Shape:
        return self._items[self._idx]


# ============================================================================
# 7. Supersampled Z-Buffer 3D CAD Offscreen Renderer (OCC.Display.OCCViewer)
# ============================================================================

Aspect_TOL_SOLID = 0
Graphic3d_TypeOfShadingModel_Unlit = 0
Quantity_NOC_GRAY50 = (0.55, 0.58, 0.62)
Quantity_NOC_BLACK = (0.08, 0.08, 0.08)


class Quantity_Color:
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], tuple):
            self.rgb = args[0]
        elif len(args) >= 3:
            self.rgb = (float(args[0]), float(args[1]), float(args[2]))
        else:
            self.rgb = (0.58, 0.62, 0.66)


class _Prs3d_LineAspect:
    def __init__(self):
        self.color = Quantity_Color(Quantity_NOC_BLACK)
        self.width = 1.0

    def SetColor(self, c: Quantity_Color) -> None:
        self.color = c

    def SetWidth(self, w: float) -> None:
        self.width = float(w)

    def SetTypeOfLine(self, tol: int) -> None:
        pass


class _Prs3d_Drawer:
    def __init__(self):
        self.face_boundary_draw = False
        self.shading_model = Graphic3d_TypeOfShadingModel_Unlit
        self.line_aspect = _Prs3d_LineAspect()

    def SetFaceBoundaryDraw(self, on: bool) -> None:
        self.face_boundary_draw = bool(on)

    def FaceBoundaryAspect(self) -> _Prs3d_LineAspect:
        return self.line_aspect

    def SetShadingModel(self, model: int) -> None:
        self.shading_model = model


class _AIS_InteractiveContext:
    def __init__(self):
        self.drawer = _Prs3d_Drawer()

    def DefaultDrawer(self) -> _Prs3d_Drawer:
        return self.drawer

    def UpdateCurrentViewer(self) -> None:
        pass


class _V3d_View:
    def __init__(self, viewer: "Viewer3d"):
        self._viewer = viewer
        self._bg_top = (38, 44, 54)
        self._bg_bot = (24, 28, 36)

    def SetBgGradientColors(self, c1: Quantity_Color, c2: Quantity_Color, *args) -> None:
        self._bg_top = tuple(int(max(0, min(255, x * 255))) for x in c1.rgb)
        self._bg_bot = tuple(int(max(0, min(255, x * 255))) for x in c2.rgb)

    def SetBackgroundColor(self, c: Quantity_Color) -> None:
        rgb = tuple(int(max(0, min(255, x * 255))) for x in c.rgb)
        self._bg_top = rgb
        self._bg_bot = rgb

    def FitAll(self, margin: float = 0.08) -> None:
        pass

    def ZFitAll(self) -> None:
        pass

    def MustBeResized(self) -> None:
        pass

    def Redraw(self) -> None:
        pass

    def Dump(self, filename: str) -> bool:
        img = self._viewer._render_image(self._bg_top, self._bg_bot)
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        img.save(filename)
        return True


class Viewer3d:
    """High-precision supersampled Z-buffer CAD renderer compatible with OCC.Display.OCCViewer.Viewer3d."""

    def __init__(self, *args, **kwargs):
        self._width = 800
        self._height = 600
        self._mode = "shaded"  # "shaded", "wireframe", "hlr"
        self._view_dir = "iso"  # "iso", "front", "right", "top"
        self._shapes: List[Tuple[TopoDS_Shape, Tuple[float, float, float]]] = []
        self._extra_pts_3d: Optional[np.ndarray] = None
        self._margin: float = 0.14
        self.Context = _AIS_InteractiveContext()
        self.View = _V3d_View(self)

    def SetExtraFramingPoints(self, pts_3d: Optional[np.ndarray], margin: float = 0.12) -> None:
        self._extra_pts_3d = np.asarray(pts_3d, dtype=np.float64) if pts_3d is not None and len(pts_3d) > 0 else None
        self._margin = float(margin)

    def Create(self, *args, **kwargs) -> None:
        pass

    def SetSize(self, w: int, h: int) -> None:
        self._width = max(16, int(w))
        self._height = max(16, int(h))

    def SetModeShaded(self) -> None:
        self._mode = "shaded"

    def SetModeWireFrame(self) -> None:
        self._mode = "wireframe"

    def SetModeHLR(self) -> None:
        self._mode = "hlr"

    def EraseAll(self) -> None:
        self._shapes.clear()

    def DisplayShape(self, shape, color=None, update: bool = False, **kwargs):
        if isinstance( color, Quantity_Color):
            rgb = color.rgb
        elif isinstance(color, tuple) and len(color) == 3:
            rgb = color
        else:
            rgb = (0.60, 0.65, 0.72)

        if isinstance(shape, (list, tuple)):
            for s in shape:
                if s is not None and not s.IsNull():
                    self._shapes.append((s, rgb))
        elif shape is not None and not shape.IsNull():
            self._shapes.append((shape, rgb))
        return []

    def FitAll(self) -> None:
        pass

    def Repaint(self) -> None:
        pass

    def set_bg_gradient_color(self, c1, c2, *args) -> None:
        if isinstance(c1, (list, tuple)) and len(c1) >= 3:
            self.View._bg_top = (int(c1[0]), int(c1[1]), int(c1[2]))
        if isinstance(c2, (list, tuple)) and len(c2) >= 3:
            self.View._bg_bot = (int(c2[0]), int(c2[1]), int(c2[2]))

    def View_Iso(self) -> None:
        self._view_dir = "iso"

    def View_Front(self) -> None:
        self._view_dir = "front"

    def View_Right(self) -> None:
        self._view_dir = "right"

    def View_Top(self) -> None:
        self._view_dir = "top"

    def get_projection_basis(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns (right_vec, up_vec, view_vec_towards_camera) for the active view."""
        if self._view_dir == "front":
            # Looking along +Y (XZ plane: +X right, +Z up)
            r = np.array([1.0, 0.0, 0.0])
            u = np.array([0.0, 0.0, 1.0])
            v = np.array([0.0, -1.0, 0.0])
        elif self._view_dir == "right":
            # Looking from +X (YZ plane: +Y right, +Z up)
            r = np.array([0.0, 1.0, 0.0])
            u = np.array([0.0, 0.0, 1.0])
            v = np.array([1.0, 0.0, 0.0])
        elif self._view_dir == "top":
            # Looking from +Z (XY plane: +X right, +Y up)
            r = np.array([1.0, 0.0, 0.0])
            u = np.array([0.0, 1.0, 0.0])
            v = np.array([0.0, 0.0, 1.0])
        else:
            # Standard AutoCAD Plant 3D SW/SE Isometric:
            # Camera at (1, -1, 0.85) -> +X goes down-right / up-right, +Z goes straight up
            v = np.array([1.0, -1.15, 0.82], dtype=np.float64)
            v = v / np.linalg.norm(v)
            world_up = np.array([0.0, 0.0, 1.0], dtype=np.float64)
            r = np.cross(world_up, v)
            r = r / np.linalg.norm(r)
            u = np.cross(v, r)
            u = u / np.linalg.norm(u)
        return r, u, v

    def project_points(self, pts_3d: np.ndarray, width: Optional[int] = None, height: Optional[int] = None, margin: float = 0.14):
        """Projects 3D points to 2D pixel coordinates (px, py, depth) using the current fitted view."""
        W = width or self._width
        H = height or self._height
        r, u, v = self.get_projection_basis()

        all_verts = [s.verts for s, _ in self._shapes if not s.IsNull()]
        if not all_verts:
            return np.zeros((len(pts_3d), 2)), np.zeros(len(pts_3d))
        if self._extra_pts_3d is not None and len(self._extra_pts_3d) > 0:
            all_verts.append(self._extra_pts_3d)
            margin = self._margin
        scene_v = np.vstack(all_verts)
        sx = scene_v @ r
        sy = scene_v @ u
        xmin, xmax = float(np.min(sx)), float(np.max(sx))
        ymin, ymax = float(np.min(sy)), float(np.max(sy))
        cx = 0.5 * (xmin + xmax)
        cy = 0.5 * (ymin + ymax)
        span_x = max(xmax - xmin, 1e-3)
        span_y = max(ymax - ymin, 1e-3)

        avail_w = W * (1.0 - 2.0 * margin)
        avail_h = H * (1.0 - 2.0 * margin)
        scale = min(avail_w / span_x, avail_h / span_y)

        px = (pts_3d @ r - cx) * scale + W * 0.5
        py = H * 0.5 - (pts_3d @ u - cy) * scale
        depth = pts_3d @ v
        return np.column_stack([px, py]), depth

    def _render_image(self, bg_top: Tuple[int, int, int], bg_bot: Tuple[int, int, int]) -> Image.Image:
        ss = 2 if max(self._width, self._height) <= 1200 else 1
        W = self._width * ss
        H = self._height * ss

        # Vertical gradient background
        t = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
        bg = np.zeros((H, W, 3), dtype=np.uint8)
        for c in range(3):
            col = (1.0 - t) * bg_top[c] + t * bg_bot[c]
            bg[:, :, c] = np.clip(col, 0, 255).astype(np.uint8)

        if not self._shapes:
            img_out = Image.fromarray(bg)
            if ss > 1:
                img_out = img_out.resize((self._width, self._height), Image.Resampling.BILINEAR)
            return img_out

        r, u, v = self.get_projection_basis()
        v_list = [s.verts for s, _ in self._shapes if not s.IsNull()]
        if self._extra_pts_3d is not None and len(self._extra_pts_3d) > 0:
            v_list.append(self._extra_pts_3d)
        all_verts = np.vstack(v_list)
        sx = all_verts @ r
        sy = all_verts @ u
        sz = all_verts @ v
        xmin, xmax = float(np.min(sx)), float(np.max(sx))
        ymin, ymax = float(np.min(sy)), float(np.max(sy))
        zmin, zmax = float(np.min(sz)), float(np.max(sz))
        z_span = max(zmax - zmin, 1.0)

        margin = self._margin if self._extra_pts_3d is not None else 0.14
        cx = 0.5 * (xmin + xmax)
        cy = 0.5 * (ymin + ymax)
        span_x = max(xmax - xmin, 1e-3)
        span_y = max(ymax - ymin, 1e-3)
        scale = min(W * (1.0 - 2.0 * margin) / span_x, H * (1.0 - 2.0 * margin) / span_y)

        # Depth buffer (larger depth = closer to camera)
        zbuf = np.full((H, W), -1e18, dtype=np.float64)

        light1 = np.array([0.35, -0.45, 0.82], dtype=np.float64)
        light1 /= np.linalg.norm(light1)
        light2 = np.array([-0.55, 0.30, 0.25], dtype=np.float64)
        light2 /= np.linalg.norm(light2)

        if self._mode in ("shaded", "hlr"):
            for shape, base_rgb in self._shapes:
                if shape.IsNull():
                    continue
                verts = shape.verts
                tris = shape.tris
                px = (verts @ r - cx) * scale + W * 0.5
                py = H * 0.5 - (verts @ u - cy) * scale
                pz = verts @ v

                tv3 = verts[tris]  # (M, 3, 3)
                e1 = tv3[:, 1] - tv3[:, 0]
                e2 = tv3[:, 2] - tv3[:, 0]
                normals = np.cross(e1, e2)
                n_len = np.linalg.norm(normals, axis=1, keepdims=True)
                valid = (n_len[:, 0] > 1e-10)
                normals[valid] /= n_len[valid]

                # Compute smooth per-vertex normals across curved surfaces (creases < ~55 deg smoothed)
                # so cylinders, cones, spheres, and elbows have continuous Gouraud shading without facet bands!
                ndv = np.abs(normals @ v)
                ndl1 = np.abs(normals @ light1)
                ndl2 = np.abs(normals @ light2)
                face_int = np.clip(0.36 + 0.46 * ndl1 + 0.14 * ndl2 + 0.08 * ndv, 0.22, 1.06)

                # 1) Average normals by topological vertex index (where caps and walls are already separated)
                idx_norm_sum = np.zeros((len(verts), 3), dtype=np.float64)
                idx_count = np.zeros(len(verts), dtype=np.float64)
                for k_c in range(3):
                    np.add.at(idx_norm_sum, tris[:, k_c], normals)
                    np.add.at(idx_count, tris[:, k_c], 1.0)
                idx_len = np.linalg.norm(idx_norm_sum, axis=1, keepdims=True)
                idx_coh = (idx_len[:, 0] / np.maximum(idx_count, 1.0)) > 0.88
                idx_ok = idx_len[:, 0] > 1e-10
                idx_norm_sum[idx_ok] /= idx_len[idx_ok]

                # 2) Also weld quantized 3D positions ONLY at coherent smooth interior vertices (coherence > 0.90)
                q_pos = np.rint(verts * 20.0).astype(np.int64)
                _, q_inv = np.unique(q_pos, axis=0, return_inverse=True)
                n_uniq = int(np.max(q_inv)) + 1 if len(q_inv) > 0 else 0
                v_norm_sum = np.zeros((n_uniq, 3), dtype=np.float64)
                v_count = np.zeros(n_uniq, dtype=np.float64)
                for k_c in range(3):
                    np.add.at(v_norm_sum, q_inv[tris[:, k_c]], normals)
                    np.add.at(v_count, q_inv[tris[:, k_c]], 1.0)
                vn_len = np.linalg.norm(v_norm_sum, axis=1, keepdims=True)
                vn_coh = (vn_len[:, 0] / np.maximum(v_count, 1.0)) > 0.90
                vn_ok = vn_len[:, 0] > 1e-10
                v_norm_sum[vn_ok] /= vn_len[vn_ok]

                # For each triangle corner (M, 3), prefer coherent welded normal, then coherent index normal, else sharp face normal
                tri_v_int = np.empty((len(tris), 3), dtype=np.float64)
                for k_c in range(3):
                    vi = tris[:, k_c]
                    qi = q_inv[vi]
                    sn_q = v_norm_sum[qi]
                    sn_i = idx_norm_sum[vi]
                    use_q = vn_coh[qi] & (np.sum(normals * sn_q, axis=1) > 0.80)
                    use_i = idx_coh[vi] & (np.sum(normals * sn_i, axis=1) > 0.80)
                    blend_n = np.where(use_q[:, None], sn_q, np.where(use_i[:, None], sn_i, normals))
                    s_ndv = np.abs(blend_n @ v)
                    s_ndl1 = np.abs(blend_n @ light1)
                    s_ndl2 = np.abs(blend_n @ light2)
                    tri_v_int[:, k_c] = np.clip(0.36 + 0.46 * s_ndl1 + 0.14 * s_ndl2 + 0.08 * s_ndv, 0.22, 1.06)

                base_rgb_arr = np.array(base_rgb, dtype=np.float64) * 255.0
                hlr_col = np.array([bg_top[0], bg_top[1], bg_top[2]], dtype=np.uint8)

                tri_z_avg = np.mean(pz[tris], axis=1)
                order = np.argsort(tri_z_avg)

                for idx in order:
                    if not valid[idx]:
                        continue
                    t = tris[idx]
                    u0, u1, u2 = px[t[0]], px[t[1]], px[t[2]]
                    v0, v1, v2 = py[t[0]], py[t[1]], py[t[2]]
                    z0, z1, z2 = pz[t[0]], pz[t[1]], pz[t[2]]

                    ix_min = max(0, int(math.floor(min(u0, u1, u2))))
                    ix_max = min(W - 1, int(math.ceil(max(u0, u1, u2))))
                    iy_min = max(0, int(math.floor(min(v0, v1, v2))))
                    iy_max = min(H - 1, int(math.ceil(max(v0, v1, v2))))
                    if ix_min > ix_max or iy_min > iy_max:
                        continue

                    denom = (v1 - v2) * (u0 - u2) + (u2 - u1) * (v0 - v2)
                    if abs(denom) < 1e-5:
                        mx, my = int(round((u0 + u1 + u2) / 3.0)), int(round((v0 + v1 + v2) / 3.0))
                        mz = (z0 + z1 + z2) / 3.0
                        if 0 <= mx < W and 0 <= my < H and mz >= zbuf[my, mx]:
                            zbuf[my, mx] = mz
                            bg[my, mx] = hlr_col if self._mode == "hlr" else np.clip(face_int[idx] * base_rgb_arr, 0, 255).astype(np.uint8)
                        continue

                    xs = np.arange(ix_min, ix_max + 1, dtype=np.float64) + 0.5
                    ys = np.arange(iy_min, iy_max + 1, dtype=np.float64) + 0.5
                    gx, gy = np.meshgrid(xs, ys)

                    w0 = ((v1 - v2) * (gx - u2) + (u2 - u1) * (gy - v2)) / denom
                    w1 = ((v2 - v0) * (gx - u2) + (u0 - u2) * (gy - v2)) / denom
                    w2 = 1.0 - w0 - w1

                    inside = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
                    if not np.any(inside):
                        continue

                    gz = w0 * z0 + w1 * z1 + w2 * z2
                    sub_zbuf = zbuf[iy_min:iy_max + 1, ix_min:ix_max + 1]
                    vis = inside & (gz >= sub_zbuf - 1e-4 * z_span)
                    if np.any(vis):
                        sub_zbuf[vis] = np.maximum(sub_zbuf[vis], gz[vis])
                        sub_img = bg[iy_min:iy_max + 1, ix_min:ix_max + 1]
                        if self._mode == "hlr":
                            sub_img[vis] = hlr_col
                        else:
                            i0, i1, i2 = tri_v_int[idx]
                            g_int = w0[vis] * i0 + w1[vis] * i1 + w2[vis] * i2
                            sub_img[vis] = np.clip(g_int[:, None] * base_rgb_arr[None, :], 0, 255).astype(np.uint8)

        # Draw sharp feature edges + silhouette edges
        draw_edges = (
            self._mode in ("wireframe", "hlr")
            or self.Context.DefaultDrawer().face_boundary_draw
        )
        if draw_edges:
            if self._mode in ("wireframe", "hlr"):
                edge_rgb = np.array([235, 240, 248], dtype=np.uint8) if sum(bg_top) < 380 else np.array([20, 24, 30], dtype=np.uint8)
            else:
                ec = self.Context.DefaultDrawer().FaceBoundaryAspect().color.rgb
                edge_rgb = np.array([int(ec[0] * 255), int(ec[1] * 255), int(ec[2] * 255)], dtype=np.uint8)

            z_bias = max(0.35, 0.0022 * z_span)
            for shape, _ in self._shapes:
                if shape.IsNull():
                    continue
                edge_list = []
                if len(shape.edges) > 0:
                    edge_list.append(shape.edges)

                # Extract silhouette edges (adjacent triangles whose normals flip sign along view_vec)
                silhouette = _extract_silhouette_edges(shape.verts, shape.tris, v)
                if len(silhouette) > 0:
                    edge_list.append(silhouette)

                if not edge_list:
                    continue
                all_e = np.vstack(edge_list)
                p0 = all_e[:, 0, :]
                p1 = all_e[:, 1, :]
                u0 = (p0 @ r - cx) * scale + W * 0.5
                v0 = H * 0.5 - (p0 @ u - cy) * scale
                z0 = p0 @ v
                u1 = (p1 @ r - cx) * scale + W * 0.5
                v1 = H * 0.5 - (p1 @ u - cy) * scale
                z1 = p1 @ v

                for i in range(len(all_e)):
                    dist_px = int(math.ceil(math.hypot(u1[i] - u0[i], v1[i] - v0[i])))
                    n_steps = max(2, min(2000, dist_px + 1))
                    ts = np.linspace(0.0, 1.0, n_steps)
                    ux = np.rint(u0[i] + ts * (u1[i] - u0[i])).astype(np.int32)
                    vy = np.rint(v0[i] + ts * (v1[i] - v0[i])).astype(np.int32)
                    zz = z0[i] + ts * (z1[i] - z0[i])

                    in_bounds = (ux >= 0) & (ux < W) & (vy >= 0) & (vy < H)
                    ux, vy, zz = ux[in_bounds], vy[in_bounds], zz[in_bounds]
                    if len(ux) == 0:
                        continue
                    if self._mode != "wireframe":
                        # Check 3x3 pixel neighborhood minimum depth so grazing cylinder/cone
                        # silhouette edges are never self-occluded while back-edges behind plates stay hidden
                        ux_m1 = np.clip(ux - 1, 0, W - 1)
                        ux_p1 = np.clip(ux + 1, 0, W - 1)
                        vy_m1 = np.clip(vy - 1, 0, H - 1)
                        vy_p1 = np.clip(vy + 1, 0, H - 1)
                        z_neigh = np.minimum(
                            zbuf[vy, ux],
                            np.minimum(
                                np.minimum(zbuf[vy, ux_m1], zbuf[vy, ux_p1]),
                                np.minimum(zbuf[vy_m1, ux], zbuf[vy_p1, ux]),
                            ),
                        )
                        vis = zz >= (z_neigh - z_bias)
                        ux, vy = ux[vis], vy[vis]
                    if len(ux) == 0:
                        continue
                    bg[vy, ux] = edge_rgb
                    if ss > 1:
                        # 2x supersampled crisp 1px line thickness
                        ux1 = np.clip(ux + 1, 0, W - 1)
                        vy1 = np.clip(vy + 1, 0, H - 1)
                        bg[vy, ux1] = edge_rgb
                        bg[vy1, ux] = edge_rgb

        img_out = Image.fromarray(bg)
        if ss > 1:
            img_out = img_out.resize((self._width, self._height), Image.Resampling.BILINEAR)
        return img_out


def _extract_silhouette_edges(verts: np.ndarray, tris: np.ndarray, view_vec: np.ndarray) -> np.ndarray:
    """Finds silhouette and sharp crease edges from triangle mesh."""
    if len(tris) == 0:
        return np.zeros((0, 2, 3), dtype=np.float64)
    tv = verts[tris]
    normals = np.cross(tv[:, 1] - tv[:, 0], tv[:, 2] - tv[:, 0])
    n_len = np.linalg.norm(normals, axis=1, keepdims=True)
    valid = n_len[:, 0] > 1e-10
    normals[valid] /= n_len[valid]
    ndv = normals @ view_vec

    # Quantize vertex positions to weld shared edges across triangle strips
    q = np.rint(verts * 100.0).astype(np.int64)
    _, inv = np.unique(q, axis=0, return_inverse=True)
    qt = inv[tris]

    e0 = np.sort(qt[:, [0, 1]], axis=1)
    e1 = np.sort(qt[:, [1, 2]], axis=1)
    e2 = np.sort(qt[:, [2, 0]], axis=1)
    all_edges_q = np.vstack([e0, e1, e2])
    orig_v0 = np.concatenate([tris[:, 0], tris[:, 1], tris[:, 2]])
    orig_v1 = np.concatenate([tris[:, 1], tris[:, 2], tris[:, 0]])
    tri_idx = np.tile(np.arange(len(tris)), 3)

    # Sort by quantized edge pair
    keys = all_edges_q[:, 0] * 1000000 + all_edges_q[:, 1]
    order = np.argsort(keys)
    keys_s = keys[order]
    tri_s = tri_idx[order]
    v0_s = orig_v0[order]
    v1_s = orig_v1[order]

    # Adjacent pairs with same key
    same = keys_s[:-1] == keys_s[1:]
    idx_same = np.where(same)[0]
    if len(idx_same) == 0:
        return np.zeros((0, 2, 3), dtype=np.float64)

    t_a = tri_s[idx_same]
    t_b = tri_s[idx_same + 1]
    # Silhouette if (ndv[t_a] * ndv[t_b] <= 0) or sharp crease (dot < 0.55)
    dot_n = np.sum(normals[t_a] * normals[t_b], axis=1)
    # Only extract smooth curved-surface horizon silhouettes; sharp edges are in shape.edges
    sil = (dot_n > 0.65) & (dot_n < 0.9995) & (ndv[t_a] * ndv[t_b] <= 0.0)
    chosen = idx_same[sil]
    if len(chosen) == 0:
        return np.zeros((0, 2, 3), dtype=np.float64)

    p0 = verts[v0_s[chosen]]
    p1 = verts[v1_s[chosen]]
    return np.stack([p0, p1], axis=1)


# ============================================================================
# 8. Module Registration in sys.modules
# ============================================================================

USING_OCC_FALLBACK = False


def install_occ_fallback() -> bool:
    global USING_OCC_FALLBACK
    """Installs OCC compatibility modules into sys.modules if native OCC is missing."""
    try:
        import OCC.Core.gp  # noqa: F401
        return False
    except ImportError:
        pass

    occ_mod = types.ModuleType("OCC")
    core_mod = types.ModuleType("OCC.Core")
    disp_mod = types.ModuleType("OCC.Display")
    occ_mod.Core = core_mod
    occ_mod.Display = disp_mod

    gp_mod = types.ModuleType("OCC.Core.gp")
    gp_mod.gp_Pnt = gp_Pnt
    gp_mod.gp_Vec = gp_Vec
    gp_mod.gp_Dir = gp_Dir
    gp_mod.gp_Ax1 = gp_Ax1
    gp_mod.gp_Ax2 = gp_Ax2
    gp_mod.gp_Trsf = gp_Trsf

    prim_mod = types.ModuleType("OCC.Core.BRepPrimAPI")
    prim_mod.BRepPrimAPI_MakeBox = BRepPrimAPI_MakeBox
    prim_mod.BRepPrimAPI_MakeCylinder = BRepPrimAPI_MakeCylinder
    prim_mod.BRepPrimAPI_MakeCone = BRepPrimAPI_MakeCone
    prim_mod.BRepPrimAPI_MakeTorus = BRepPrimAPI_MakeTorus
    prim_mod.BRepPrimAPI_MakeSphere = BRepPrimAPI_MakeSphere

    algo_mod = types.ModuleType("OCC.Core.BRepAlgoAPI")
    algo_mod.BRepAlgoAPI_Fuse = BRepAlgoAPI_Fuse
    algo_mod.BRepAlgoAPI_Cut = BRepAlgoAPI_Cut
    algo_mod.BRepAlgoAPI_Common = BRepAlgoAPI_Common

    builder_mod = types.ModuleType("OCC.Core.BRepBuilderAPI")
    builder_mod.BRepBuilderAPI_Transform = BRepBuilderAPI_Transform
    builder_mod.BRepBuilderAPI_Copy = BRepBuilderAPI_Copy

    bnd_mod = types.ModuleType("OCC.Core.Bnd")
    bnd_mod.Bnd_Box = Bnd_Box

    brepbnd_mod = types.ModuleType("OCC.Core.BRepBndLib")
    brepbnd_mod.brepbndlib = brepbndlib

    mesh_mod = types.ModuleType("OCC.Core.BRepMesh")
    mesh_mod.BRepMesh_IncrementalMesh = BRepMesh_IncrementalMesh

    topabs_mod = types.ModuleType("OCC.Core.TopAbs")
    topabs_mod.TopAbs_COMPOUND = TopAbs_COMPOUND
    topabs_mod.TopAbs_COMPSOLID = TopAbs_COMPSOLID
    topabs_mod.TopAbs_SOLID = TopAbs_SOLID
    topabs_mod.TopAbs_SHELL = TopAbs_SHELL
    topabs_mod.TopAbs_FACE = TopAbs_FACE
    topabs_mod.TopAbs_WIRE = TopAbs_WIRE
    topabs_mod.TopAbs_EDGE = TopAbs_EDGE
    topabs_mod.TopAbs_VERTEX = TopAbs_VERTEX

    topexp_mod = types.ModuleType("OCC.Core.TopExp")
    topexp_mod.TopExp_Explorer = TopExp_Explorer

    toploc_mod = types.ModuleType("OCC.Core.TopLoc")
    toploc_mod.TopLoc_Location = TopLoc_Location

    brep_mod = types.ModuleType("OCC.Core.BRep")
    brep_mod.BRep_Tool = BRep_Tool

    aspect_mod = types.ModuleType("OCC.Core.Aspect")
    aspect_mod.Aspect_TOL_SOLID = Aspect_TOL_SOLID

    g3d_mod = types.ModuleType("OCC.Core.Graphic3d")
    g3d_mod.Graphic3d_TypeOfShadingModel_Unlit = Graphic3d_TypeOfShadingModel_Unlit

    quant_mod = types.ModuleType("OCC.Core.Quantity")
    quant_mod.Quantity_Color = Quantity_Color
    quant_mod.Quantity_NOC_GRAY50 = Quantity_NOC_GRAY50
    quant_mod.Quantity_NOC_BLACK = Quantity_NOC_BLACK

    viewer_mod = types.ModuleType("OCC.Display.OCCViewer")
    viewer_mod.Viewer3d = Viewer3d

    simplegui_mod = types.ModuleType("OCC.Display.SimpleGui")
    simplegui_mod.init_display = lambda *a, **kw: (Viewer3d(), lambda: None, lambda *x: None, None)

    backend_mod = types.ModuleType("OCC.Display.backend")
    backend_mod.load_backend = lambda *a, **kw: "fallback"

    qtdisp_mod = types.ModuleType("OCC.Display.qtDisplay")
    qtdisp_mod.qtViewer3d = None

    modules = {
        "OCC": occ_mod,
        "OCC.Core": core_mod,
        "OCC.Core.gp": gp_mod,
        "OCC.Core.BRepPrimAPI": prim_mod,
        "OCC.Core.BRepAlgoAPI": algo_mod,
        "OCC.Core.BRepBuilderAPI": builder_mod,
        "OCC.Core.Bnd": bnd_mod,
        "OCC.Core.BRepBndLib": brepbnd_mod,
        "OCC.Core.BRepMesh": mesh_mod,
        "OCC.Core.TopAbs": topabs_mod,
        "OCC.Core.TopExp": topexp_mod,
        "OCC.Core.TopLoc": toploc_mod,
        "OCC.Core.BRep": brep_mod,
        "OCC.Core.Aspect": aspect_mod,
        "OCC.Core.Graphic3d": g3d_mod,
        "OCC.Core.Quantity": quant_mod,
        "OCC.Display": disp_mod,
        "OCC.Display.OCCViewer": viewer_mod,
        "OCC.Display.SimpleGui": simplegui_mod,
        "OCC.Display.backend": backend_mod,
        "OCC.Display.qtDisplay": qtdisp_mod,
    }
    sys.modules.update(modules)
    USING_OCC_FALLBACK = True
    return True
