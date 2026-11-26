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
          TooltipShort=u"同心异径短节 Swage Nipple (MSS SP-95)",
          TooltipLong=u"MSS SP-95 锻钢同心异径短节 Swage Nipple，含加长两端直管段、平滑锥段与贯通内流道",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="PL")
@group("MainDimensions", TooltipLong=u"同心异径短节主要几何参数")
@param(D1=LENGTH, TooltipShort=u"大端外径", TooltipLong=u"大端公称外径 D1 (mm)")
@param(D2=LENGTH, TooltipShort=u"小端外径", TooltipLong=u"小端公称外径 D2 (mm)")
@param(L_LEN=LENGTH, TooltipShort=u"总长度", TooltipLong=u"异径短节总长度 L (mm)", Ask4Dist=True)
@param(WT1=LENGTH, TooltipShort=u"大端壁厚", TooltipLong=u"大端公称壁厚 T1 (mm)")
@param(WT2=LENGTH, TooltipShort=u"小端壁厚", TooltipLong=u"小端公称壁厚 T2 (mm)")
def SWAGE_NIPPLE_CON(
    s,
    D1=60.3,
    D2=33.4,
    L_LEN=165.0,
    WT1=5.5,
    WT2=4.5,
    ID=u"SWAGE_NIPPLE_CON",
    **kw
):
    u"""同心异径短节 Swage Nipple (加长两端直边 + 平滑锥段, 沿 +X 轴)。"""
    D1 = max(20.0, float(D1))
    D2 = max(12.0, min(D1 - 2.0, float(D2)))
    L_LEN = float(L_LEN)
    if L_LEN < 1.0:
        L_LEN = 1.0
    r1, r2 = D1 / 2.0, D2 / 2.0
    WT1 = max(1.5, min(r1 - 2.0, float(WT1)))
    WT2 = max(1.5, min(r2 - 2.0, float(WT2)))
    r1_in, r2_in = r1 - WT1, r2 - WT2

    # Swage Nipple 特征：两端加长直管段各占约 30%，中间平滑锥段约占 40%
    l_stub = L_LEN * 0.30
    l_cone = L_LEN - 2.0 * l_stub

    o_out = CYLINDER(s, R=r1, H=l_stub, O=0.0).rotateY(90.0)
    o_c = CONE(s, R1=r1, R2=r2, H=l_cone, E=0.0).rotateY(90.0).translate((l_stub, 0.0, 0.0))
    o_s = CYLINDER(s, R=r2, H=l_stub, O=0.0).rotateY(90.0).translate((l_stub + l_cone, 0.0, 0.0))
    o_out.uniteWith(o_c)
    o_c.erase()
    o_out.uniteWith(o_s)
    o_s.erase()

    o_in = CONE(s, R1=r1_in, R2=r2_in, H=L_LEN + 4.0, E=0.0).rotateY(90.0).translate((-2.0, 0.0, 0.0))
    o_out.subtractFrom(o_in)
    o_in.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L_LEN, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_LEN', (0.0, 0.0, 0.0), (L_LEN, 0.0, 0.0))
