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

@activate(Group="Reducer",
          TooltipShort=u"对焊偏心大小头 (GB/T 12459)",
          TooltipLong=u"GB/T 12459-2017/ASME B16.9(已核实) 钢制对焊偏心异径管 (底平, 系列I)，含两端直边与贯通偏心内腔",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"偏心大小头主要几何参数")
@param(D1=LENGTH, TooltipShort=u"大端外径", TooltipLong=u"大端管子公称外径 D1 (mm)")
@param(D2=LENGTH, TooltipShort=u"小端外径", TooltipLong=u"小端管子公称外径 D2 (mm)")
@param(H_LEN=LENGTH, TooltipShort=u"总长度", TooltipLong=u"大小头端面至端面总长度 H (mm)", Ask4Dist=True)
@param(WT=LENGTH, TooltipShort=u"壁厚", TooltipLong=u"公称壁厚 T (mm)")
def REDUCER_ECC_GBT12459(
    s,
    D1=168.3,
    D2=114.3,
    H_LEN=140.0,
    WT=7.1,
    ID=u"REDUCER_ECC_GBT12459",
    **kw
):
    u"""对焊偏心大小头 (底平, Port 1=(0,0,0), Port 2=(H_LEN,0,-E))。"""
    D1 = max(25.0, float(D1))
    D2 = max(15.0, min(D1 - 2.0, float(D2)))
    H_LEN = float(H_LEN)
    if H_LEN < 1.0:
        H_LEN = 1.0
    WT = max(1.5, min(D2 / 2.0 - 2.0, float(WT)))

    r1, r2 = D1 / 2.0, D2 / 2.0
    ecc = (D1 - D2) / 2.0
    r1_in, r2_in = r1 - WT, r2 - WT
    lip = min(12.0, H_LEN * 0.14)
    cone_l = max(10.0, H_LEN - 2.0 * lip)

    o_out = CYLINDER(s, R=r1, H=lip, O=0.0).rotateY(90.0)
    o_c = CONE(s, R1=r1, R2=r2, H=cone_l, E=ecc).rotateY(90.0).translate((lip, 0.0, 0.0))
    o_s = CYLINDER(s, R=r2, H=lip, O=0.0).rotateY(90.0).translate((lip + cone_l, 0.0, -ecc))
    o_out.uniteWith(o_c)
    o_c.erase()
    o_out.uniteWith(o_s)
    o_s.erase()

    o_in = CONE(s, R1=r1_in, R2=r2_in, H=H_LEN + 4.0, E=ecc).rotateY(90.0).translate((-2.0, 0.0, 0.0))
    o_out.subtractFrom(o_in)
    o_in.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H_LEN, 0.0, -ecc), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_LEN', (0.0, 0.0, 0.0), (H_LEN, 0.0, 0.0))
