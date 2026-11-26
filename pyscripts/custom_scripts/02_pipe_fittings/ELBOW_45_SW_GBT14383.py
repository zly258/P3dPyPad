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
          TooltipShort=u"锻钢承插焊45°弯头 (GB/T 14383)",
          TooltipLong=u"GB/T 14383-2021/ASME B16.11(已核实) 锻钢承插焊45度弯头 (Class 3000)，含双端加厚承插肩与承插台阶孔",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="SW")
@group("MainDimensions", TooltipLong=u"锻钢承插焊45度弯头主要几何参数")
@param(D_HUB=LENGTH, TooltipShort=u"承插肩外径", TooltipLong=u"承插端加厚肩外径 D_HUB (mm)")
@param(D_BORE=LENGTH, TooltipShort=u"承插孔径", TooltipLong=u"承插口内径 B (mm)")
@param(D_IN=LENGTH, TooltipShort=u"通流内径", TooltipLong=u"弯头内部通流孔径 D_IN (mm)")
@param(A_LEN=LENGTH, TooltipShort=u"中心至端面距", TooltipLong=u"弯头中心至承插端面距 A (mm)", Ask4Dist=True)
@param(J_DEP=LENGTH, TooltipShort=u"承插深度", TooltipLong=u"承插口深度 J (mm)")
def ELBOW_45_SW_GBT14383(
    s,
    D_HUB=45.3,
    D_BORE=33.9,
    D_IN=26.6,
    A_LEN=27.0,
    J_DEP=13.0,
    ID=u"ELBOW_45_SW_GBT14383",
    **kw
):
    u"""锻钢承插焊45度弯头 (两臂夹角135度, 偏转45度)。"""
    D_HUB = max(20.0, float(D_HUB))
    D_BORE = max(12.0, min(D_HUB - 4.0, float(D_BORE)))
    D_IN = max(8.0, min(D_BORE - 2.0, float(D_IN)))
    A_LEN = float(A_LEN)
    if A_LEN < 1.0:
        A_LEN = 1.0
    J_DEP = max(6.0, min(A_LEN - 6.0, float(J_DEP)))

    r_hub = D_HUB / 2.0
    r_body = max(D_BORE / 2.0 + 2.0, r_hub * 0.86)
    r_bore = D_BORE / 2.0
    r_in = D_IN / 2.0
    c_len = A_LEN - J_DEP
    c45 = 0.7071067811865476

    o_body = SPHERE(s, R=r_body)
    o_leg1 = CYLINDER(s, R=r_body, H=c_len + 1.0, O=0.0).rotateY(90.0)
    o_leg2 = CYLINDER(s, R=r_body, H=c_len + 1.0, O=0.0).rotateY(90.0).rotateZ(135.0)
    o_hub1 = CYLINDER(s, R=r_hub, H=J_DEP + 2.0, O=0.0).rotateY(90.0).translate((c_len - 2.0, 0.0, 0.0))
    o_hub2 = CYLINDER(s, R=r_hub, H=J_DEP + 2.0, O=0.0).rotateY(90.0).translate((c_len - 2.0, 0.0, 0.0)).rotateZ(135.0)
    o_body.uniteWith(o_leg1)
    o_leg1.erase()
    o_body.uniteWith(o_leg2)
    o_leg2.erase()
    o_body.uniteWith(o_hub1)
    o_hub1.erase()
    o_body.uniteWith(o_hub2)
    o_hub2.erase()

    o_cut = SPHERE(s, R=r_in)
    o_in1 = CYLINDER(s, R=r_in, H=A_LEN + 2.0, O=0.0).rotateY(90.0)
    o_in2 = CYLINDER(s, R=r_in, H=A_LEN + 2.0, O=0.0).rotateY(90.0).rotateZ(135.0)
    o_sk1 = CYLINDER(s, R=r_bore, H=J_DEP + 2.0, O=0.0).rotateY(90.0).translate((c_len, 0.0, 0.0))
    o_sk2 = CYLINDER(s, R=r_bore, H=J_DEP + 2.0, O=0.0).rotateY(90.0).translate((c_len, 0.0, 0.0)).rotateZ(135.0)
    o_cut.uniteWith(o_in1)
    o_in1.erase()
    o_cut.uniteWith(o_in2)
    o_in2.erase()
    o_cut.uniteWith(o_sk1)
    o_sk1.erase()
    o_cut.uniteWith(o_sk2)
    o_sk2.erase()

    o_body.subtractFrom(o_cut)
    o_cut.erase()

    s.setPoint((A_LEN, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((-A_LEN * c45, A_LEN * c45, 0.0), (-c45, c45, 0.0))
    s.setLinearDimension('A_LEN', (0.0, 0.0, 0.0), (A_LEN, 0.0, 0.0))
