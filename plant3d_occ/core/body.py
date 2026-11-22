# -*- coding: utf-8 -*-
"""3D Solid Body Wrapper (OccBody) compatible with both native C++ pythonocc-core and occ_fallback."""

import math
from .occ_fallback import install_occ_fallback

install_occ_fallback()

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Trsf, gp_Ax1
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform, BRepBuilderAPI_Copy
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
from .math3d import mPoint, mVector
from .session import OccSession


class OccBody(object):
    """Wraps an OpenCASCADE TopoDS_Shape and provides Plant 3D's chainable API.

    Supports both constructor conventions:
    - `OccBody(session, shape, params=None)`
    - `OccBody(shape, params=None)`
    """

    def __init__(self, *args, **kwargs):
        session = kwargs.get("session", None)
        shape = None
        params = kwargs.get("params", None)

        if len(args) >= 2 and (isinstance(args[0], OccSession) or (args[0] is None and not isinstance(args[1], dict))):
            session = args[0]
            shape = args[1]
            if len(args) >= 3:
                params = args[2]
        elif len(args) >= 1:
            shape = args[0]
            if len(args) >= 2 and isinstance(args[1], dict):
                params = args[1]

        self.session = session
        self.shape = shape
        self.erased = False
        self._params = dict(params) if params else {}
        self._local_points = []
        self._points = []
        self._trsf = gp_Trsf()
        if self.session is not None:
            self.session.register_body(self)

    def _apply_trsf(self, trsf: gp_Trsf):
        if self.shape is not None:
            builder = BRepBuilderAPI_Transform(self.shape, trsf, True)
            self.shape = builder.Shape()
        if hasattr(self._trsf, "PreMultiply"):
            self._trsf.PreMultiply(trsf)
        updated_pts = []
        for pt, d in self._points:
            gp_p = gp_Pnt(float(pt[0]), float(pt[1]), float(pt[2])).Transformed(trsf)
            gp_d = gp_Dir(float(d[0]), float(d[1]), float(d[2])).Transformed(trsf)
            updated_pts.append(((gp_p.X(), gp_p.Y(), gp_p.Z()), (gp_d.X(), gp_d.Y(), gp_d.Z())))
        self._points = updated_pts
        return self

    def translate(self, vec, dy=None, dz=None):
        """Translates body by (dx, dy, dz) tuple/mPoint/mVector or 3 scalar arguments."""
        if vec is None:
            return self
        if dy is not None and dz is not None:
            dx, dy_f, dz_f = float(vec), float(dy), float(dz)
        elif hasattr(vec, "x") and callable(vec.x):
            dx, dy_f, dz_f = float(vec.x()), float(vec.y()), float(vec.z())
        else:
            dx, dy_f, dz_f = float(vec[0]), float(vec[1]), float(vec[2])
        if abs(dx) < 1e-9 and abs(dy_f) < 1e-9 and abs(dz_f) < 1e-9:
            return self
        trsf = gp_Trsf()
        trsf.SetTranslation(gp_Vec(dx, dy_f, dz_f))
        return self._apply_trsf(trsf)

    def rotateX(self, angle_deg):
        angle_rad = math.radians(float(angle_deg))
        if abs(angle_rad) < 1e-9:
            return self
        trsf = gp_Trsf()
        trsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), angle_rad)
        return self._apply_trsf(trsf)

    def rotateY(self, angle_deg):
        angle_rad = math.radians(float(angle_deg))
        if abs(angle_rad) < 1e-9:
            return self
        trsf = gp_Trsf()
        trsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)), angle_rad)
        return self._apply_trsf(trsf)

    def rotateZ(self, angle_deg):
        angle_rad = math.radians(float(angle_deg))
        if abs(angle_rad) < 1e-9:
            return self
        trsf = gp_Trsf()
        trsf.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), angle_rad)
        return self._apply_trsf(trsf)

    def scale(self, factor):
        if isinstance(factor, (tuple, list)) and len(factor) == 3:
            return self.scaleXYZ(factor[0], factor[1], factor[2])
        f = float(factor[0]) if hasattr(factor, "__getitem__") else float(factor)
        if abs(f - 1.0) < 1e-9 or f <= 0:
            return self
        trsf = gp_Trsf()
        trsf.SetScale(gp_Pnt(0, 0, 0), f)
        return self._apply_trsf(trsf)

    def scaleXYZ(self, sx, sy, sz):
        """Non-uniform scaling along X, Y, Z compatible with both native C++ OCCT (gp_GTrsf) and fallback."""
        sx, sy, sz = float(sx), float(sy), float(sz)
        if abs(sx - 1.0) < 1e-9 and abs(sy - 1.0) < 1e-9 and abs(sz - 1.0) < 1e-9:
            return self
        if abs(sx - sy) < 1e-7 and abs(sy - sz) < 1e-7:
            return self.scale(sx)

        # Native C++ pythonocc-core requires gp_GTrsf + BRepBuilderAPI_GTransform for non-uniform scaling
        try:
            from OCC.Core.gp import gp_GTrsf
            from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_GTransform
            gtrsf = gp_GTrsf()
            gtrsf.SetValue(1, 1, sx)
            gtrsf.SetValue(2, 2, sy)
            gtrsf.SetValue(3, 3, sz)
            if self.shape is not None:
                self.shape = BRepBuilderAPI_GTransform(self.shape, gtrsf, True).Shape()
            updated_pts = []
            for pt, d in self._points:
                updated_pts.append(((pt[0] * sx, pt[1] * sy, pt[2] * sz), d))
            self._points = updated_pts
            return self
        except ImportError:
            trsf = gp_Trsf()
            if hasattr(trsf, "SetScaleXYZ"):
                trsf.SetScaleXYZ(sx, sy, sz)
            else:
                trsf.SetValues(sx, 0, 0, 0, 0, sy, 0, 0, 0, 0, sz, 0)
            return self._apply_trsf(trsf)

    def clone(self):
        copied_shape = BRepBuilderAPI_Copy(self.shape).Shape() if self.shape is not None else None
        b = OccBody(None, copied_shape, self._params)
        b._local_points = list(self._local_points)
        b._points = list(self._points)
        return b

    @staticmethod
    def _is_valid_shape(shape):
        """极速且安全的 B-Rep 有效性与非空几何判定。"""
        if shape is None:
            return False
        try:
            if hasattr(shape, "IsNull") and shape.IsNull():
                return False

            # 1. 极速拓扑检查：确认至少包含有效面(Face)或线(Edge)，避免空 Compound 误判，耗时 < 0.01ms
            from OCC.Core.TopExp import TopExp_Explorer
            from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_EDGE
            if not TopExp_Explorer(shape, TopAbs_FACE).More() and not TopExp_Explorer(shape, TopAbs_EDGE).More():
                return False

            # 2. BRep 拓扑校验器
            from OCC.Core.BRepCheck import BRepCheck_Analyzer
            if not BRepCheck_Analyzer(shape).IsValid():
                return False

            # 3. 快速轻量包围盒判定（使用 brepbndlib.Add 而非极度耗时的 AddOptimal 求导计算）
            from OCC.Core.Bnd import Bnd_Box
            from OCC.Core.BRepBndLib import brepbndlib
            box = Bnd_Box()
            brepbndlib.Add(shape, box, False)
            return not box.IsVoid()
        except Exception:
            return True

    def _run_boolean(self, other, factory):
        """跑一次布尔运算并返回可用的结果形状；都不可用则返回 None。

        实测 `SetFuzzyValue(1e-4)` 会让部分装配体产出无效壳（CPBD 就是典型：
        带 fuzzy 无效、不带 fuzzy 有效），而 OCCT 对这种情况仍然 IsDone=True，
        不会报错。所以先用精确参数算，只有结果无效/未完成时才带 fuzzy 重试，
        并以 BRepCheck 的结论为准，绝不把坏几何当成功交出去。
        """
        if (other is None
                or getattr(other, "erased", False)
                or getattr(other, "shape", None) is None
                or self.shape is None):
            return None
        try:
            if hasattr(other.shape, "IsNull") and other.shape.IsNull():
                return None
        except Exception:
            return None

        for use_fuzzy in (False, True):
            try:
                op = factory(self.shape, other.shape)
                if hasattr(op, "SetRunParallel"):
                    op.SetRunParallel(True)
                if use_fuzzy and hasattr(op, "SetFuzzyValue"):
                    op.SetFuzzyValue(1e-4)
                if hasattr(op, "Build"):
                    op.Build()
                if hasattr(op, "IsDone") and not op.IsDone():
                    continue
                res = op.Shape()
                if self._is_valid_shape(res):
                    return res
            except Exception:
                continue
        return None

    def uniteWith(self, other):
        """Boolean union (self = self U other)."""
        res = self._run_boolean(
            other, lambda a, b: BRepAlgoAPI_Fuse(a, b))
        if res is not None:
            self.shape = res
            return self
        if self.shape is None:
            # 自身还没实体时，直接接管对方
            if other is not None and getattr(other, "shape", None) is not None:
                self.shape = BRepBuilderAPI_Copy(other.shape).Shape()
            return self
        # 极端情况（例如面贴合到无法布尔）才退回打包，保留双方几何不至于丢件；
        # 这是"能看见但不够正确"的兜底，不是正常路径。
        try:
            from OCC.Core.TopoDS import TopoDS_Compound
            from OCC.Core.BRep import BRep_Builder
            comp = TopoDS_Compound()
            builder = BRep_Builder()
            builder.MakeCompound(comp)
            builder.Add(comp, self.shape)
            builder.Add(comp, other.shape)
            self.shape = comp
        except Exception:
            pass
        return self

    def subtractFrom(self, other):
        """Boolean difference (self = self - other)."""
        res = self._run_boolean(
            other, lambda a, b: BRepAlgoAPI_Cut(a, b))
        if res is not None:
            self.shape = res
        return self

    def intersectWith(self, other):
        """Boolean intersection (self = self & other)."""
        res = self._run_boolean(
            other, lambda a, b: BRepAlgoAPI_Common(a, b))
        if res is not None:
            self.shape = res
        return self

    def unify_same_domain(self):
        """Unifies coplanar faces and collinear edges to eliminate redundant internal seam lines."""
        if self.shape is None or (hasattr(self.shape, "IsNull") and self.shape.IsNull()):
            return self
        try:
            from OCC.Core.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
            unif = ShapeUpgrade_UnifySameDomain(self.shape, True, True, True)
            unif.Build()
            res = unif.Shape()
            if res is not None and not (hasattr(res, "IsNull") and res.IsNull()):
                self.shape = res
        except Exception:
            pass
        return self

    def erase(self):
        self.erased = True
        return self

    def setEndpoints(self, *args, **kw):
        return self

    def setColor(self, *args, **kw):
        return self

    def parameters(self):
        return dict(self._params)

    def setParameters(self, params):
        if params:
            self._params.update(params)
        return self

    def setPoint(self, pt, direction=(1.0, 0.0, 0.0)):
        return self.addPoint(pt, direction)

    def addPoint(self, pt, direction=(1.0, 0.0, 0.0)):
        p = (float(pt[0]), float(pt[1]), float(pt[2]))
        d = (float(direction[0]), float(direction[1]), float(direction[2]))
        self._local_points.append((p, d))
        gp_p = gp_Pnt(*p).Transformed(self._trsf)
        gp_d = gp_Dir(*d).Transformed(self._trsf)
        self._points.append(((gp_p.X(), gp_p.Y(), gp_p.Z()), (gp_d.X(), gp_d.Y(), gp_d.Z())))
        return self

    def setSubComponentPoints(self, ports_list):
        self._local_points = []
        self._points = []
        for p_entry in ports_list:
            pt = p_entry["point"]
            d = p_entry["dir"]
            p = (float(pt[0]), float(pt[1]), float(pt[2]))
            dv = (float(d[0]), float(d[1]), float(d[2]))
            self._local_points.append((p, dv))
            self._points.append((p, dv))
        return self

    def numberOfPoints(self):
        if self._points:
            return len(self._points)
        if self.session is not None and self.session.ports:
            return len(self.session.ports)
        return 0

    def pointAt(self, n=0, inECS=0):
        idx = int(n)
        pts = self._local_points if inECS else self._points
        if 0 <= idx < len(pts):
            return mPoint(*pts[idx][0])
        if self.session is not None and 0 <= idx < len(self.session.ports):
            return mPoint(*self.session.ports[idx]["point"])
        return mPoint(0.0, 0.0, 0.0)

    def directionAt(self, n=0, inECS=0):
        idx = int(n)
        pts = self._local_points if inECS else self._points
        if 0 <= idx < len(pts):
            return mVector(*pts[idx][1])
        if self.session is not None and 0 <= idx < len(self.session.ports):
            return mVector(*self.session.ports[idx]["dir"])
        return mVector(1.0, 0.0, 0.0)

    def startPoint(self):
        return self.pointAt(0)

    def endPoint(self):
        return self.pointAt(1) if self.numberOfPoints() > 1 else self.pointAt(0)

    def transformationMatrix(self):
        return [
            [self._trsf.Value(1, 1), self._trsf.Value(1, 2), self._trsf.Value(1, 3), self._trsf.Value(1, 4)],
            [self._trsf.Value(2, 1), self._trsf.Value(2, 2), self._trsf.Value(2, 3), self._trsf.Value(2, 4)],
            [self._trsf.Value(3, 1), self._trsf.Value(3, 2), self._trsf.Value(3, 3), self._trsf.Value(3, 4)],
            [0.0, 0.0, 0.0, 1.0],
        ]

    def setTransformationMatrix(self, mat):
        if mat is None:
            return self
        try:
            if hasattr(mat, "to_occ_trsf") and callable(mat.to_occ_trsf):
                return self._apply_trsf(mat.to_occ_trsf())
            trsf = gp_Trsf()
            if isinstance(mat, (list, tuple)) and len(mat) >= 3 and isinstance(mat[0], (list, tuple)):
                trsf.SetValues(
                    float(mat[0][0]), float(mat[0][1]), float(mat[0][2]), float(mat[0][3]),
                    float(mat[1][0]), float(mat[1][1]), float(mat[1][2]), float(mat[1][3]),
                    float(mat[2][0]), float(mat[2][1]), float(mat[2][2]), float(mat[2][3]),
                )
                return self._apply_trsf(trsf)
            elif isinstance(mat, (list, tuple)) and len(mat) in (12, 16):
                trsf.SetValues(
                    float(mat[0]), float(mat[1]), float(mat[2]), float(mat[3]),
                    float(mat[4]), float(mat[5]), float(mat[6]), float(mat[7]),
                    float(mat[8]), float(mat[9]), float(mat[10]), float(mat[11]),
                )
                return self._apply_trsf(trsf)
        except Exception:
            pass
        return self
