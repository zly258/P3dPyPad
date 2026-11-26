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

@activate(Group="Cross",
          TooltipShort=u"对焊等径四通 (GB/T 12459)",
          TooltipLong=u"GB/T 12459-2017/ASME B16.9(已核实) 钢制对焊等径四通 (系列I)，四端对称中心距与十字贯通内流道",
          LengthUnit="mm",
          Ports="4",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"对焊等径四通主要几何参数")
@param(D=LENGTH, TooltipShort=u"管子外径", TooltipLong=u"四通公称外径 D (mm)")
@param(C_LEN=LENGTH, TooltipShort=u"中心至端面距", TooltipLong=u"四通中心至各端面距离 C (mm)", Ask4Dist=True)
@param(WT=LENGTH, TooltipShort=u"壁厚", TooltipLong=u"四通公称壁厚 T (mm)")
def CROSS_BW_GBT12459(
    s,
    D=114.3,
    C_LEN=105.0,
    WT=6.0,
    ID=u"CROSS_BW_GBT12459",
    **kw
):
    u"""对焊等径四通 (主管沿 X 轴, 支管沿 Z 轴)。"""
    D = max(15.0, float(D))
    r_out = D / 2.0
    C_LEN = float(C_LEN)
    if C_LEN < 1.0:
        C_LEN = 1.0
    WT = max(1.5, min(r_out - 2.0, float(WT)))
    r_in = r_out - WT

    o_x = CYLINDER(s, R=r_out, H=2.0 * C_LEN, O=0.0).rotateY(90.0).translate((-C_LEN, 0.0, 0.0))
    o_z = CYLINDER(s, R=r_out, H=2.0 * C_LEN, O=0.0).translate((0.0, 0.0, -C_LEN))
    o_x.uniteWith(o_z)
    o_z.erase()

    o_ix = CYLINDER(s, R=r_in, H=2.0 * C_LEN + 8.0, O=0.0).rotateY(90.0).translate((-C_LEN - 4.0, 0.0, 0.0))
    o_iz = CYLINDER(s, R=r_in, H=2.0 * C_LEN + 8.0, O=0.0).translate((0.0, 0.0, -C_LEN - 4.0))
    o_ix.uniteWith(o_iz)
    o_iz.erase()

    o_x.subtractFrom(o_ix)
    o_ix.erase()

    s.setPoint((-C_LEN, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((C_LEN, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, C_LEN), (0.0, 0.0, 1.0))
    s.setPoint((0.0, 0.0, -C_LEN), (0.0, 0.0, -1.0))
    s.setLinearDimension('C_LEN', (0.0, 0.0, 0.0), (C_LEN, 0.0, 0.0))
