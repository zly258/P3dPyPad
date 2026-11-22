# -*- coding: utf-8 -*-
import math
from math import *
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Trsf, gp_Ax1

mcPi = math.pi


def sqrt(x):
    """Domain-safe square root for parametric CAD scripts."""
    return math.sqrt(max(0.0, float(x)))


def acos(x):
    """Domain-safe arccos for parametric CAD scripts."""
    return math.acos(max(-1.0, min(1.0, float(x))))


def asin(x):
    """Domain-safe arcsin for parametric CAD scripts."""
    return math.asin(max(-1.0, min(1.0, float(x))))


def areEqual(a, b, tol=1e-10):
    """浮点容差比较。"""
    return abs(float(a) - float(b)) <= tol


def asRadiants(deg):
    """角度转弧度（与 Plant 3D 原厂拼写 asRadiants 完全对齐）。"""
    return math.radians(float(deg))


def asDegrees(rad):
    """弧度转角度。"""
    return math.degrees(float(rad))


class mPoint(object):
    """模拟 aqa.math.mPoint 三维点（兼容 tuple 下标、解包及 .x()/.y()/.z()/.r()/.theta()/.fi()）。"""

    def __init__(self, x=0.0, y=0.0, z=0.0):
        if hasattr(x, "__len__"):
            self._x = float(x[0])
            self._y = float(x[1])
            self._z = float(x[2]) if len(x) > 2 else 0.0
        elif hasattr(x, "x") and callable(x.x):
            self._x = float(x.x())
            self._y = float(x.y())
            self._z = float(x.z())
        else:
            self._x = float(x)
            self._y = float(y)
            self._z = float(z)

    def x(self):
        return self._x

    def y(self):
        return self._y

    def z(self):
        return self._z

    def r(self):
        return math.sqrt(self._x * self._x + self._y * self._y + self._z * self._z)

    def length(self):
        return self.r()

    def theta(self):
        return math.atan2(self._y, self._x)

    def fi(self):
        rad = self.r()
        if rad <= 1e-12:
            return 0.0
        return math.acos(max(-1.0, min(1.0, self._z / rad)))

    def __len__(self):
        return 3

    def __iter__(self):
        yield self._x
        yield self._y
        yield self._z

    def __getitem__(self, idx):
        if idx == 0:
            return self._x
        if idx == 1:
            return self._y
        if idx == 2:
            return self._z
        if isinstance(idx, slice):
            return (self._x, self._y, self._z)[idx]
        raise IndexError("mPoint index out of range (0-2)")

    def __add__(self, other):
        return mPoint(self._x + float(other[0]), self._y + float(other[1]), self._z + float(other[2]))

    def __sub__(self, other):
        return mVector(self._x - float(other[0]), self._y - float(other[1]), self._z - float(other[2]))

    def __mul__(self, scalar):
        s = float(scalar)
        return mPoint(self._x * s, self._y * s, self._z * s)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __eq__(self, other):
        if hasattr(other, "__len__") and len(other) == 3:
            return (
                abs(self._x - float(other[0])) <= 1e-7
                and abs(self._y - float(other[1])) <= 1e-7
                and abs(self._z - float(other[2])) <= 1e-7
            )
        return False

    def __repr__(self):
        return "mPoint(%.4f, %.4f, %.4f)" % (self._x, self._y, self._z)


class mVector(object):
    """模拟 aqa.math.mVector 三维向量。"""

    def __init__(self, x=0.0, y=0.0, z=0.0):
        if hasattr(x, "__len__"):
            self._x = float(x[0])
            self._y = float(x[1])
            self._z = float(x[2]) if len(x) > 2 else 0.0
        elif hasattr(x, "x") and callable(x.x):
            self._x = float(x.x())
            self._y = float(x.y())
            self._z = float(x.z())
        else:
            self._x = float(x)
            self._y = float(y)
            self._z = float(z)

    def x(self):
        return self._x

    def y(self):
        return self._y

    def z(self):
        return self._z

    def r(self):
        return math.sqrt(self._x * self._x + self._y * self._y + self._z * self._z)

    def length(self):
        return self.r()

    def normalized(self):
        l = self.length()
        if l > 1e-9:
            return mVector(self._x / l, self._y / l, self._z / l)
        return mVector(0.0, 0.0, 0.0)

    def theta(self):
        """返回 XY 平面内的方位角弧度。"""
        return math.atan2(self._y, self._x)

    def fi(self):
        """返回与 +Z 轴的极角弧度。"""
        l = self.length()
        if l <= 1e-12:
            return 0.0
        return math.acos(max(-1.0, min(1.0, self._z / l)))

    def __len__(self):
        return 3

    def __iter__(self):
        yield self._x
        yield self._y
        yield self._z

    def __getitem__(self, idx):
        if idx == 0:
            return self._x
        if idx == 1:
            return self._y
        if idx == 2:
            return self._z
        if isinstance(idx, slice):
            return (self._x, self._y, self._z)[idx]
        raise IndexError("mVector index out of range (0-2)")

    def __add__(self, other):
        return mVector(self._x + float(other[0]), self._y + float(other[1]), self._z + float(other[2]))

    def __sub__(self, other):
        return mVector(self._x - float(other[0]), self._y - float(other[1]), self._z - float(other[2]))

    def __mul__(self, scalar):
        s = float(scalar)
        return mVector(self._x * s, self._y * s, self._z * s)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __eq__(self, other):
        if hasattr(other, "__len__") and len(other) == 3:
            return (
                abs(self._x - float(other[0])) <= 1e-7
                and abs(self._y - float(other[1])) <= 1e-7
                and abs(self._z - float(other[2])) <= 1e-7
            )
        return False

    def __repr__(self):
        return "mVector(%.4f, %.4f, %.4f)" % (self._x, self._y, self._z)


class mTransform(object):
    """模拟 aqa.math.mTransform 空间 4x4 刚体变换矩阵。"""

    def __init__(self, trsf=None):
        self._trsf = trsf if trsf is not None else gp_Trsf()

    def translate(self, offset, dy=None, dz=None):
        if dy is not None and dz is not None:
            dx, dy_f, dz_f = float(offset), float(dy), float(dz)
        elif hasattr(offset, "x") and callable(offset.x):
            dx, dy_f, dz_f = offset.x(), offset.y(), offset.z()
        else:
            dx, dy_f, dz_f = float(offset[0]), float(offset[1]), float(offset[2])
        t = gp_Trsf()
        t.SetTranslation(gp_Vec(dx, dy_f, dz_f))
        self._trsf = self._trsf.Multiplied(t)
        return self

    def rotateX(self, rad):
        axis = gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0))
        t = gp_Trsf()
        t.SetRotation(axis, float(rad))
        self._trsf = self._trsf.Multiplied(t)
        return self

    def rotateY(self, rad):
        axis = gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 1.0, 0.0))
        t = gp_Trsf()
        t.SetRotation(axis, float(rad))
        self._trsf = self._trsf.Multiplied(t)
        return self

    def rotateZ(self, rad):
        axis = gp_Ax1(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
        t = gp_Trsf()
        t.SetRotation(axis, float(rad))
        self._trsf = self._trsf.Multiplied(t)
        return self

    def to_occ_trsf(self):
        return self._trsf

    def __mul__(self, other):
        """矩阵乘点、向量或另一个变换矩阵。"""
        if isinstance(other, mPoint):
            p = gp_Pnt(other.x(), other.y(), other.z()).Transformed(self._trsf)
            return mPoint(p.X(), p.Y(), p.Z())
        elif isinstance(other, mVector):
            v = gp_Vec(other.x(), other.y(), other.z()).Transformed(self._trsf)
            return mVector(v.X(), v.Y(), v.Z())
        elif isinstance(other, mTransform):
            return mTransform(self._trsf.Multiplied(other._trsf))
        elif hasattr(other, "__len__") and len(other) == 3:
            p = gp_Pnt(float(other[0]), float(other[1]), float(other[2])).Transformed(self._trsf)
            return mPoint(p.X(), p.Y(), p.Z())
        return self


def _p2_cmp(a, op, b):
    """Python 2.7 compatible comparison where None < any number."""
    if op == "==":
        return a == b
    if op == "!=":
        return a != b
    if op == "is":
        return a is b
    if op == "is not":
        return a is not b
    if op == "in":
        return a in b
    if op == "not in":
        return a not in b
    if a is None and b is None:
        return op in ("<=", ">=")
    if a is None:
        return op in ("<", "<=")
    if b is None:
        return op in (">", ">=")
    if op == "<":
        return a < b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    if op == ">=":
        return a >= b
    return a == b
