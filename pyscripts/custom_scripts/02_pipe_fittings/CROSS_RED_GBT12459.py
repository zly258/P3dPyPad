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
          TooltipShort=u"对焊异径四通 (GB/T 12459)",
          TooltipLong=u"GB/T 12459-2017/ASME B16.9(已核实) 钢制对焊异径四通 (系列I)，主管大径、两侧支管缩径，先并外壳再并内芯一次差集",
          LengthUnit="mm",
          Ports="4",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"对焊异径四通主要几何参数")
@param(D1=LENGTH, TooltipShort=u"主管外径", TooltipLong=u"主管公称外径 D1 (mm)")
@param(D2=LENGTH, TooltipShort=u"支管外径", TooltipLong=u"两侧支管公称外径 D2 (mm)")
@param(C_LEN=LENGTH, TooltipShort=u"主管中心距", TooltipLong=u"中心至主管端面距 C (mm)", Ask4Dist=True)
@param(M_LEN=LENGTH, TooltipShort=u"支管中心距", TooltipLong=u"中心至支管端面距 M (mm)")
@param(WT1=LENGTH, TooltipShort=u"主管壁厚", TooltipLong=u"主管公称壁厚 T1 (mm)")
@param(WT2=LENGTH, TooltipShort=u"支管壁厚", TooltipLong=u"支管公称壁厚 T2 (mm)")
def CROSS_RED_GBT12459(
    s,
    D1=114.3,
    D2=60.3,
    C_LEN=105.0,
    M_LEN=89.0,
    WT1=6.0,
    WT2=3.9,
    ID=u"CROSS_RED_GBT12459",
    **kw
):
    u"""对焊异径四通 (主管沿 X 轴, 两侧支管沿 +-Z 轴)。"""
    D1 = max(20.0, float(D1))
    D2 = max(15.0, min(D1 - 1.0, float(D2)))
    r1 = D1 / 2.0
    r2 = D2 / 2.0
    C_LEN = float(C_LEN)
    if C_LEN < 1.0:
        C_LEN = 1.0
    M_LEN = float(M_LEN)
    if M_LEN < 1.0:
        M_LEN = 1.0
    WT1 = max(1.5, min(r1 - 2.0, float(WT1)))
    WT2 = max(1.5, min(r2 - 2.0, float(WT2)))
    r1_in = r1 - WT1
    r2_in = r2 - WT2

    o_run = CYLINDER(s, R=r1, H=2.0 * C_LEN, O=0.0).rotateY(90.0).translate((-C_LEN, 0.0, 0.0))
    o_br = CYLINDER(s, R=r2, H=2.0 * M_LEN, O=0.0).translate((0.0, 0.0, -M_LEN))
    o_run.uniteWith(o_br)
    o_br.erase()

    o_irun = CYLINDER(s, R=r1_in, H=2.0 * C_LEN + 8.0, O=0.0).rotateY(90.0).translate((-C_LEN - 4.0, 0.0, 0.0))
    o_ibr = CYLINDER(s, R=r2_in, H=2.0 * M_LEN + 8.0, O=0.0).translate((0.0, 0.0, -M_LEN - 4.0))
    o_irun.uniteWith(o_ibr)
    o_ibr.erase()

    o_run.subtractFrom(o_irun)
    o_irun.erase()

    s.setPoint((-C_LEN, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((C_LEN, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, M_LEN), (0.0, 0.0, 1.0))
    s.setPoint((0.0, 0.0, -M_LEN), (0.0, 0.0, -1.0))
    s.setLinearDimension('C_LEN', (0.0, 0.0, 0.0), (C_LEN, 0.0, 0.0))
    s.setLinearDimension('M_LEN', (0.0, 0.0, 0.0), (0.0, 0.0, M_LEN))
