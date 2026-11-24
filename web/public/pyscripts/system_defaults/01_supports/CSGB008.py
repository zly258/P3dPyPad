# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgcsub.csgc002 import *


@activate(Group="Support", TooltipShort="CSGB008", TooltipLong="CSGB008", LengthUnit="mm", Ports=1)
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
def CSGB008(s, D=116.0, L=120.0, W=4.0, K=0.0, SL=180.0, SW=100.0, ST=8.0, SH=150.0, ID='CSGB008', **kw):
    R1 = D / 2.0
    R2 = R1 + W
    if SW <= 0.0:
        SW = SL
    if SL > SW:
        D2 = SW
    else:
        D2 = SL
    if D2 > D:
        D2 = D
    D2 -= ST * 2.0
    R3 = D2 / 2.0
    L1 = L / 3.0
    LS = L - L1
    HS = SH - R1
    if K <= 0.0:
        K = D + (L1 * 2.0)
    o1 = CYLINDER(s, R=R2, H=L, O=0.0).translate((0, 0, -(L / 2.0)))
    o3 = CYLINDER(s, R=R3, H=SH, O=0.0).rotateY(90.0)
    o4 = BOX(s, L=SW, W=SL, H=ST).translate((SH - (ST / 2.0), 0.0, 0.0))
    if W > 0.0:
        o2 = BOX(s, L=K, W=L, H=W * 3.0)
        o1.uniteWith(o2)
        o2.erase()
        o5 = CSGC002(s, D=D, L=L1, W=W, K=K).rotateY(-90).translate((0, 0, 0 - (LS / 2.0)))
        o6 = CSGC002(s, D=D, L=L1, W=W, K=K).rotateY(-90).translate((0, 0, LS / 2.0))
    else:
        o5 = None
        o6 = None
    o7 = CYLINDER(s, R=R1, H=L, O=0.0).translate((0, 0, -(L / 2.0)))
    o8 = (BOX(s, L=K, W=L, H=W + D)).translate((-(D / 2.0), 0.0, 0.0))
    o1.uniteWith(o3)
    o3.erase()
    o1.uniteWith(o4)
    o4.erase()
    o7.uniteWith(o8)
    o8.erase()
    o1.subtractFrom(o7)
    o7.erase()
    if (o5) and (o6):
        o1.uniteWith(o5)
        o5.erase()
        o1.uniteWith(o6)
        o6.erase()
    o1.rotateY(90)
    s.setPoint((0, 0, 0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0, 0, 0), (0, 0, -SH))
