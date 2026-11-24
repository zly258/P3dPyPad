# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Support", TooltipShort="CSGC001", TooltipLong="CSGC001", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(BL=LENGTH, TooltipShort="BL")
@param(BW=LENGTH, TooltipShort="BW")
@param(BH=LENGTH, TooltipShort="BH")
@param(ID=STRING, TooltipShort="组件标识")
def CSGC001(s, D=116.0, L=30.0, W=0.0, K=0.0, BL=0.0, BW=0.0, BH=0.0, ID='CSGC001', **kw):
    W = getThickness(D=D, OF=W, Ever=1, mustCalc=True)
    R1 = D / 2.0
    R2 = R1 + W
    if K <= 0.0:
        K = D + (L * 2.0)
    sL = R1 + BH
    sS = sL + W
    o1 = CYLINDER(s, R=R2, H=L, O=0.0).translate((0.0, 0.0, -(L / 2.0)))
    o2 = (BOX(s, L=R2 * 2.0, W=L, H=sL)).translate((sL / 2.0, 0.0, 0.0))
    o3 = BOX(s, L=K, W=L, H=W).translate((sL - (W / 2.0), 0.0, 0.0))
    o4 = CYLINDER(s, R=R1, H=L, O=0.0).translate((0.0, 0.0, -(L / 2.0)))
    o5 = (BOX(s, L=R1 * 2.0, W=L, H=sS)).translate((sS / 2.0, 0.0, 0.0))
    if BL > 0.0:
        if BW <= 0.0:
            BW = L
        o6 = BOX(s, L=BL, W=BW, H=sL).translate((sL / 2.0, 0.0, 0.0))
        o7 = CYLINDER(s, R=R1, H=BW, O=0.0).translate((0.0, 0.0, -(BW / 2.0)))
    else:
        o6 = None
    o1.uniteWith(o2)
    o2.erase()
    o1.uniteWith(o3)
    o3.erase()
    o4.uniteWith(o5)
    o5.erase()
    o1.subtractFrom(o4)
    o4.erase()
    if o6:
        o6.subtractFrom(o7)
        o7.erase()
        o1.uniteWith(o6)
        o6.erase()
    o1.rotateY(90)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('BH', (0, 0, -D / 2.0), (0, 0, -BH - (D / 2.0)))
