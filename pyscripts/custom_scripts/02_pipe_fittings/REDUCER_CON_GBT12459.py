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
          TooltipShort=u"对焊同心大小头 (GB/T 12459)",
          TooltipLong=u"GB/T 12459-2017/ASME B16.9(已核实) 钢制对焊同心异径管 (系列I)，含两端直边与平滑锥段贯通内腔",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"同心大小头主要几何参数")
@param(D1=LENGTH, TooltipShort=u"大端外径", TooltipLong=u"大端管子公称外径 D1 (mm)")
@param(D2=LENGTH, TooltipShort=u"小端外径", TooltipLong=u"小端管子公称外径 D2 (mm)")
@param(H_LEN=LENGTH, TooltipShort=u"总长度", TooltipLong=u"大小头端面至端面总长度 H (mm)", Ask4Dist=True)
@param(WT1=LENGTH, TooltipShort=u"大端壁厚", TooltipLong=u"大端公称壁厚 T1 (mm)")
@param(WT2=LENGTH, TooltipShort=u"小端壁厚", TooltipLong=u"小端公称壁厚 T2 (mm)")
def REDUCER_CON_GBT12459(
    s,
    D1=114.3,
    D2=60.3,
    H_LEN=102.0,
    WT1=6.0,
    WT2=3.9,
    ID=u"REDUCER_CON_GBT12459",
    **kw
):
    u"""对焊同心大小头 (沿 +X 轴 [0, H_LEN])。"""
    D1 = max(25.0, float(D1))
    D2 = max(15.0, min(D1 - 2.0, float(D2)))
    H_LEN = float(H_LEN)
    if H_LEN < 1.0:
        H_LEN = 1.0
    r1, r2 = D1 / 2.0, D2 / 2.0
    WT1 = max(1.5, min(r1 - 2.0, float(WT1)))
    WT2 = max(1.5, min(r2 - 2.0, float(WT2)))
    r1_in, r2_in = r1 - WT1, r2 - WT2

    lip = min(12.0, H_LEN * 0.14)
    cone_l = max(10.0, H_LEN - 2.0 * lip)

    o_out = CYLINDER(s, R=r1, H=lip, O=0.0).rotateY(90.0)
    o_c = CONE(s, R1=r1, R2=r2, H=cone_l, E=0.0).rotateY(90.0).translate((lip, 0.0, 0.0))
    o_s = CYLINDER(s, R=r2, H=lip, O=0.0).rotateY(90.0).translate((lip + cone_l, 0.0, 0.0))
    o_out.uniteWith(o_c)
    o_c.erase()
    o_out.uniteWith(o_s)
    o_s.erase()

    # 一把贯穿的内锥，两端伸出零件 2mm。不要用端面正好对齐的内锥，ACIS 会在共面处布尔失败，
    # 失败后 Plant 改画系统双锥，看起来就像两只圆锥在一点碰上。
    o_in = CONE(s, R1=r1_in, R2=r2_in, H=H_LEN + 4.0, E=0.0).rotateY(90.0).translate((-2.0, 0.0, 0.0))
    o_out.subtractFrom(o_in)
    o_in.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H_LEN, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_LEN', (0.0, 0.0, 0.0), (H_LEN, 0.0, 0.0))
