# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgcsub.csgc002 import *


@activate(Group="Support", TooltipShort="CSGB009", TooltipLong="CSGB009", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(SH=LENGTH, TooltipShort="SH")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB009(s, D=116.0, L=40.0, W=4.0, K=0.0, SL=180.0, SW=100.0, ST=8.0, SH=150.0, ID='CSGB009', **kw):
    R1 = D / 2.0
    R2 = R1 + W
    if SW <= 0.0:
        SW = SL
    HS = SH - R1
    if K <= 0.0:
        K = D + (L * 2.0)
    L1 = D + (W * 2)
    tL0 = L / 2.0
    tL1 = SH - ST
    tL2 = sqrt(pow(tL1, 2.0) + pow(tL0, 2.0))
    tL3 = sqrt(pow(tL2, 2.0) - pow(R2, 2.0))
    tA = 90.0 - ((180.0 - (90.0 - asDegrees(atan2(tL0, tL1)))) - (90.0 - (asDegrees(acos(R2 / tL2)))))
    tL4 = tL3 * (sin(asRadiants(tA + 90.0)))
    o1 = (BOX(s, L=L1, W=L, H=SH - ST)).translate(((SH / 2.0) - (ST / 2.0), 0.0, 0.0))
    o2 = BOX(s, L=SW, W=SL, H=ST).translate((SH - (ST / 2.0), 0.0, 0.0))
    o4 = CYLINDER(s, R=R1, H=L, O=0.0).translate((0, 0, -tL0))
    o5 = (((BOX(s, L=tL3, W=L, H=tL3 * 2.0)).translate((-tL3, tL3 / 2.0, 0.0))).rotateZ(-tA)).translate((tL1, tL0, 0.0))
    o6 = (((BOX(s, L=tL3, W=L, H=tL3 * 2.0)).translate((-tL3, -(tL3 / 2.0), 0.0))).rotateZ(tA)).translate((tL1, -tL0, 0.0))
    o7 = BOX(s, L=K, W=L, H=K).translate((((-(K / 2.0)) + tL1) - tL4, 0.0, 0.0))
    o5.uniteWith(o6)
    o6.erase()
    o5.uniteWith(o7)
    o7.erase()
    o1.subtractFrom(o5)
    o5.erase()
    o1.subtractFrom(o4)
    o4.erase()
    o1.uniteWith(o2)
    o2.erase()
    if W > 0.0:
        o3 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90)
        o1.uniteWith(o3)
        o3.erase()
    o1.rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0, 0, 0), (0, 0, -SH))
