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
          TooltipShort=u"90°短半径对焊弯头 1.0D (GB/T 12459)",
          TooltipLong=u"GB/T 12459-2017/ASME B16.9(已核实) 90度短半径对焊弯头 (1.0D, 系列I)，紧凑弯曲半径与贯通内流道",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"90度短半径弯头主要几何参数")
@param(D=LENGTH, TooltipShort=u"管子外径", TooltipLong=u"弯头端部公称外径 D (mm)")
@param(R_BEND=LENGTH, TooltipShort=u"弯曲半径", TooltipLong=u"1.0D 短半径弯头中心弯曲半径 R (mm)", Ask4Dist=True)
@param(WT=LENGTH, TooltipShort=u"壁厚", TooltipLong=u"弯头公称壁厚 T (mm)")
def ELBOW_90_SR_GBT12459(
    s,
    D=114.3,
    R_BEND=102.0,
    WT=6.0,
    ID=u"ELBOW_90_SR_GBT12459",
    **kw
):
    u"""90度短半径对焊弯头 (1.0D, GB/T 12459)。"""
    D = max(15.0, float(D))
    r_out = D / 2.0
    WT = max(1.5, min(r_out - 2.0, float(WT)))
    r_in = r_out - WT
    R_BEND = float(R_BEND)
    if R_BEND < 1.0:
        R_BEND = 1.0

    o_out = ARC3D(s, D=r_out, R=R_BEND, A=90.0)
    o_in = ARC3D(s, D=r_in, R=R_BEND, A=90.0)
    p0 = o_out.pointAt(0)
    v0 = o_out.directionAt(0)
    p1 = o_out.pointAt(1)
    v1 = o_out.directionAt(1)

    o_ext0 = CYLINDER(s, R=r_in, H=6.0, O=0.0).rotateY(90.0).translate((p0.x() - 3.0, p0.y(), p0.z()))
    o_ext1 = CYLINDER(s, R=r_in, H=6.0, O=0.0).rotateX(-90.0).translate((p1.x(), p1.y() - 3.0, p1.z()))
    o_in.uniteWith(o_ext0)
    o_ext0.erase()
    o_in.uniteWith(o_ext1)
    o_ext1.erase()

    o_out.subtractFrom(o_in)
    o_in.erase()

    s.setPoint(p0, v0)
    s.setPoint(p1, v1)
    s.setLinearDimension('R_BEND', (0.0, 0.0, 0.0), (p0.x(), p0.y(), p0.z()))
