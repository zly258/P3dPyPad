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
          TooltipShort=u"3D/5D大半径煨制弯管 90° (SH/T 3408)",
          TooltipLong=u"SH/T 3408 石油化工3D/5D大半径中频感应煨制弯管 90度，含两端直管段与贯通内流道",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"3D/5D煨制弯管主要几何参数")
@param(D=LENGTH, TooltipShort=u"管子外径", TooltipLong=u"弯管公称外径 D (mm)")
@param(R_BEND=LENGTH, TooltipShort=u"弯曲半径", TooltipLong=u"3D或5D大半径弯曲半径 R (mm)", Ask4Dist=True)
@param(L_TAN=LENGTH, TooltipShort=u"直段长度", TooltipLong=u"弯管两端直管切线长度 L_TAN (mm)")
@param(WT=LENGTH, TooltipShort=u"壁厚", TooltipLong=u"弯管公称壁厚 T (mm)")
def BEND_3D_5D_SHT3408(
    s,
    D=114.3,
    R_BEND=305.0,
    L_TAN=150.0,
    WT=6.0,
    ID=u"BEND_3D_5D_SHT3408",
    **kw
):
    u"""3D/5D大半径煨制弯管 90度 (SH/T 3408)，含两端直段。"""
    D = max(20.0, float(D))
    r_out = D / 2.0
    WT = max(1.5, min(r_out - 2.0, float(WT)))
    r_in = r_out - WT
    R_BEND = float(R_BEND)
    if R_BEND < 1.0:
        R_BEND = 1.0
    L_TAN = float(L_TAN)
    if L_TAN < 1.0:
        L_TAN = 1.0

    o_out = ARC3D(s, D=r_out, R=R_BEND, A=90.0)
    p0 = o_out.pointAt(0)
    p1 = o_out.pointAt(1)

    o_tan0 = CYLINDER(s, R=r_out, H=L_TAN, O=0.0).rotateY(90.0).translate((p0.x(), p0.y(), p0.z()))
    o_tan1 = CYLINDER(s, R=r_out, H=L_TAN, O=0.0).rotateX(-90.0).translate((p1.x(), p1.y(), p1.z()))
    o_out.uniteWith(o_tan0)
    o_tan0.erase()
    o_out.uniteWith(o_tan1)
    o_tan1.erase()

    o_in = ARC3D(s, D=r_in, R=R_BEND, A=90.0)
    o_itan0 = CYLINDER(s, R=r_in, H=L_TAN + 6.0, O=0.0).rotateY(90.0).translate((p0.x() - 2.0, p0.y(), p0.z()))
    o_itan1 = CYLINDER(s, R=r_in, H=L_TAN + 6.0, O=0.0).rotateX(-90.0).translate((p1.x(), p1.y() - 2.0, p1.z()))
    o_in.uniteWith(o_itan0)
    o_itan0.erase()
    o_in.uniteWith(o_itan1)
    o_itan1.erase()

    o_out.subtractFrom(o_in)
    o_in.erase()

    pt0 = (p0.x() + L_TAN, p0.y(), p0.z())
    pt1 = (p1.x(), p1.y() + L_TAN, p1.z())
    s.setPoint(pt0, (1.0, 0.0, 0.0))
    s.setPoint(pt1, (0.0, 1.0, 0.0))
    s.setLinearDimension('R_BEND', (0.0, 0.0, 0.0), (p0.x(), p0.y(), p0.z()))
    s.setLinearDimension('L_TAN', (p0.x(), p0.y(), p0.z()), pt0)
