# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except (NameError, AttributeError):
    pass

from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *

@activate(Group="Elbow",
          TooltipShort=u"90°变径对焊弯头 (Reducing Elbow)",
          TooltipLong=u"90度长半径变径对焊弯头，基于 ARC3D2 实现大端进小端出平滑渐缩与贯通内流道",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"90度变径对焊弯头主要几何参数")
@param(D1=LENGTH, TooltipShort=u"大端外径", TooltipLong=u"大端公称外径 D1 (mm)")
@param(D2=LENGTH, TooltipShort=u"小端外径", TooltipLong=u"小端公称外径 D2 (mm)")
@param(R_BEND=LENGTH, TooltipShort=u"弯曲半径", TooltipLong=u"中心弯曲半径 R (mm)", Ask4Dist=True)
@param(WT1=LENGTH, TooltipShort=u"大端壁厚", TooltipLong=u"大端公称壁厚 T1 (mm)")
@param(WT2=LENGTH, TooltipShort=u"小端壁厚", TooltipLong=u"小端公称壁厚 T2 (mm)")
def ELBOW_RED_90_BW(
    s,
    D1=114.3,
    D2=88.9,
    R_BEND=152.0,
    WT1=6.0,
    WT2=5.5,
    ID=u"ELBOW_RED_90_BW",
    **kw
):
    u"""90度变径对焊弯头 (大端进小端出, ARC3D2)。"""
    D1 = max(25.0, float(D1))
    D2 = max(15.0, min(D1 - 1.0, float(D2)))
    r1 = D1 / 2.0
    r2 = D2 / 2.0
    WT1 = max(1.5, min(r1 - 2.0, float(WT1)))
    WT2 = max(1.5, min(r2 - 2.0, float(WT2)))
    r1_in = r1 - WT1
    r2_in = r2 - WT2
    R_BEND = float(R_BEND)
    if R_BEND < 1.0:
        R_BEND = 1.0

    o_out = ARC3D2(s, D=r1, D2=r2, R=R_BEND, A=90.0)
    o_in = ARC3D2(s, D=r1_in, D2=r2_in, R=R_BEND, A=90.0)
    p0 = o_out.pointAt(0)
    v0 = o_out.directionAt(0)
    p1 = o_out.pointAt(1)
    v1 = o_out.directionAt(1)

    o_ext0 = CYLINDER(s, R=r1_in, H=6.0, O=0.0).rotateY(90.0).translate((p0.x() - 3.0, p0.y(), p0.z()))
    o_ext1 = CYLINDER(s, R=r2_in, H=6.0, O=0.0).rotateX(-90.0).translate((p1.x(), p1.y() - 3.0, p1.z()))
    o_in.uniteWith(o_ext0)
    o_ext0.erase()
    o_in.uniteWith(o_ext1)
    o_ext1.erase()

    o_out.subtractFrom(o_in)
    o_in.erase()

    s.setPoint(p0, v0)
    s.setPoint(p1, v1)
    s.setLinearDimension('R_BEND', (0.0, 0.0, 0.0), (p0.x(), p0.y(), p0.z()))
