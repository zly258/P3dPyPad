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

@activate(Group="Cap",
          TooltipShort=u"对焊椭圆形管帽 (GB/T 12459)",
          TooltipLong=u"GB/T 12459-2017/ASME B16.9(已核实) 钢制对焊标准2:1椭圆形管帽，含直边段与中空内腔",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"对焊椭圆形管帽主要几何参数")
@param(D=LENGTH, TooltipShort=u"管子外径", TooltipLong=u"管帽对焊端外径 D (mm)")
@param(E_LEN=LENGTH, TooltipShort=u"总长度", TooltipLong=u"管帽端面至封头顶点总高度 E (mm)", Ask4Dist=True)
@param(WT=LENGTH, TooltipShort=u"壁厚", TooltipLong=u"管帽公称壁厚 T (mm)")
def CAP_BW_GBT12459(
    s,
    D=114.3,
    E_LEN=64.0,
    WT=6.0,
    ID=u"CAP_BW_GBT12459",
    **kw
):
    u"""对焊2:1椭圆形管帽 (开口在 X=0, 沿 +X 轴封闭)。"""
    D = max(15.0, float(D))
    r_out = D / 2.0
    WT = max(1.5, min(r_out - 2.0, float(WT)))
    r_in = r_out - WT
    E_LEN = float(E_LEN)
    if E_LEN < 1.0:
        E_LEN = 1.0

    h_ell = min(r_out * 0.5, E_LEN * 0.72)
    h_cyl = max(4.0, E_LEN - h_ell)

    o_cyl = CYLINDER(s, R=r_out, H=h_cyl, O=0.0).rotateY(90.0)
    o_head = ELLIPSOIDHEAD(s, R=r_out, H=h_ell).rotateY(90.0).translate((h_cyl, 0.0, 0.0))
    o_cyl.uniteWith(o_head)
    o_head.erase()

    h_ell_in = max(2.0, h_ell - WT)
    o_icyl = CYLINDER(s, R=r_in, H=h_cyl + 2.0, O=0.0).rotateY(90.0).translate((-2.0, 0.0, 0.0))
    o_ihead = ELLIPSOIDHEAD(s, R=r_in, H=h_ell_in).rotateY(90.0).translate((h_cyl, 0.0, 0.0))
    o_icyl.uniteWith(o_ihead)
    o_ihead.erase()

    o_cyl.subtractFrom(o_icyl)
    o_icyl.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('E_LEN', (0.0, 0.0, 0.0), (E_LEN, 0.0, 0.0))
