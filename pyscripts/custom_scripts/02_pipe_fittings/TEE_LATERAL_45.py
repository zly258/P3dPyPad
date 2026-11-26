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

@activate(Group="Tee",
          TooltipShort=u"45°斜三通 (Lateral Tee)",
          TooltipLong=u"钢制对焊45度斜三通 (Y型斜支管)，精准交点偏距与三端贯通内流道",
          LengthUnit="mm",
          Ports="3",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"45度斜三通主要几何参数")
@param(D1=LENGTH, TooltipShort=u"主管外径", TooltipLong=u"主管公称外径 D1 (mm)")
@param(D2=LENGTH, TooltipShort=u"支管外径", TooltipLong=u"45度斜支管公称外径 D2 (mm)")
@param(L1=LENGTH, TooltipShort=u"交点至后端距", TooltipLong=u"轴线交点至主管后端面距离 L1 (mm)")
@param(L2=LENGTH, TooltipShort=u"交点至前端距", TooltipLong=u"轴线交点至主管前端面距离 L2 (mm)", Ask4Dist=True)
@param(L_BR=LENGTH, TooltipShort=u"支管长度", TooltipLong=u"轴线交点至45度支管端面距离 L_BR (mm)")
@param(WT=LENGTH, TooltipShort=u"壁厚", TooltipLong=u"公称壁厚 T (mm)")
def TEE_LATERAL_45(
    s,
    D1=114.3,
    D2=114.3,
    L1=76.0,
    L2=229.0,
    L_BR=229.0,
    WT=6.0,
    ID=u"TEE_LATERAL_45",
    **kw
):
    u"""45度斜三通 (主管沿 X 轴, 支管沿 +45° XZ 平面)。"""
    D1 = max(20.0, float(D1))
    D2 = max(15.0, min(D1, float(D2)))
    r1 = D1 / 2.0
    r2 = D2 / 2.0
    L1 = float(L1)
    if L1 < 1.0:
        L1 = 1.0
    L2 = float(L2)
    if L2 < 1.0:
        L2 = 1.0
    L_BR = max(r1 * 2.5, float(L_BR))
    WT = max(1.5, min(r2 - 2.0, float(WT)))
    r1_in = r1 - WT
    r2_in = r2 - WT

    c45 = 0.7071067811865476
    o_run = CYLINDER(s, R=r1, H=L1 + L2, O=0.0).rotateY(90.0).translate((-L1, 0.0, 0.0))
    o_br = CYLINDER(s, R=r2, H=L_BR, O=0.0).rotateY(45.0)
    o_run.uniteWith(o_br)
    o_br.erase()

    o_irun = CYLINDER(s, R=r1_in, H=L1 + L2 + 8.0, O=0.0).rotateY(90.0).translate((-L1 - 4.0, 0.0, 0.0))
    o_ibr = CYLINDER(s, R=r2_in, H=L_BR + 6.0, O=0.0).rotateY(45.0)
    o_irun.uniteWith(o_ibr)
    o_ibr.erase()

    o_run.subtractFrom(o_irun)
    o_irun.erase()

    s.setPoint((-L1, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L2, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((L_BR * c45, 0.0, L_BR * c45), (c45, 0.0, c45))
    s.setLinearDimension('L2', (0.0, 0.0, 0.0), (L2, 0.0, 0.0))
    s.setLinearDimension('L1', (-L1, 0.0, 0.0), (0.0, 0.0, 0.0))
