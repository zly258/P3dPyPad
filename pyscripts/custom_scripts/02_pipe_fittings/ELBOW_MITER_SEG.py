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
          TooltipShort=u"90°多节虾米腰弯头 (Miter Elbow)",
          TooltipLong=u"大口径90度多节焊接虾米腰弯头 (3~5节)，清晰表达斜切焊缝节段与贯通内流道",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"虾米腰弯头主要几何参数")
@param(D=LENGTH, TooltipShort=u"管子外径", TooltipLong=u"虾米腰弯头外径 D (mm)")
@param(R_BEND=LENGTH, TooltipShort=u"弯曲半径", TooltipLong=u"虾米腰弯头中心弯曲半径 R (mm)", Ask4Dist=True)
@param(WT=LENGTH, TooltipShort=u"壁厚", TooltipLong=u"管壁厚度 T (mm)")
@param(N_SEG=INT, TooltipShort=u"节数", TooltipLong=u"斜切拼接节数 N_SEG (3~6)")
def ELBOW_MITER_SEG(
    s,
    D=323.9,
    R_BEND=457.2,
    WT=8.0,
    N_SEG=4,
    ID=u"ELBOW_MITER_SEG",
    **kw
):
    u"""90度多节焊接虾米腰弯头 (ARC3DS)。"""
    D = max(80.0, float(D))
    r_out = D / 2.0
    WT = max(2.0, min(r_out - 4.0, float(WT)))
    r_in = r_out - WT
    R_BEND = float(R_BEND)
    if R_BEND < 1.0:
        R_BEND = 1.0
    n_seg = max(2, min(8, int(round(float(N_SEG)))))

    o_out = ARC3DS(s, D=r_out, D2=r_out, R=R_BEND, A=90.0, S=n_seg)
    o_in = ARC3DS(s, D=r_in, D2=r_in, R=R_BEND, A=90.0, S=n_seg)
    p0 = o_out.pointAt(0)
    v0 = o_out.directionAt(0)
    p1 = o_out.pointAt(1)
    v1 = o_out.directionAt(1)

    o_ext0 = CYLINDER(s, R=r_in, H=10.0, O=0.0).rotateY(90.0).translate((p0.x() - 5.0, p0.y(), p0.z()))
    o_ext1 = CYLINDER(s, R=r_in, H=10.0, O=0.0).rotateX(-90.0).translate((p1.x(), p1.y() - 5.0, p1.z()))
    o_in.uniteWith(o_ext0)
    o_ext0.erase()
    o_in.uniteWith(o_ext1)
    o_ext1.erase()

    o_out.subtractFrom(o_in)
    o_in.erase()

    s.setPoint(p0, v0)
    s.setPoint(p1, v1)
    s.setLinearDimension('R_BEND', (0.0, 0.0, 0.0), (p0.x(), p0.y(), p0.z()))
