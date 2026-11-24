# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cnut6_001 import *


@activate(Group="Support", TooltipShort="CSGC000", TooltipLong="CSGC000", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(BL=LENGTH, TooltipShort="BL")
@param(BW=LENGTH, TooltipShort="BW")
@param(BH=LENGTH, TooltipShort="BH")
@param(MW=LENGTH, TooltipShort="MW")
@param(MH=LENGTH, TooltipShort="MH")
@param(MD=LENGTH, TooltipShort="MD")
@param(ID=STRING, TooltipShort="组件标识")
def CSGC000(s, D=116.0, L=30.0, W=0.0, BL=80.0, BW=60.0, BH=10.0, MW=0.0, MH=0.0, MD=0.0, ID='CSGC000', **kw):
    if W <= 0.0:
        W = 2.0 * getThickness(D=D, OF=0.0, Ever=1, mustCalc=True)
    R1 = D / 2.0
    R2 = W / 2.0
    R3 = R1 + R2
    sL = (R1 + BH) + L
    sS = sL + W
    if MW == 0.0:
        MW = 2.0 * W
    if MH == 0.0:
        MH = W
    if MD == 0.0:
        MD = L / 3.0
    o1 = TORUS(s, R1=R3, R2=R2).translate((0.0, 0.0, 0.0))
    o2 = CYLINDER(s, R=R2, H=sL, O=0.0).rotateY(90.0).translate((0.0, R1 + R2, 0.0))
    o3 = CYLINDER(s, R=R2, H=sL, O=0.0).rotateY(90.0).translate((0.0, -(R1 + R2), 0.0))
    o4 = (BOX(s, L=(R1 + W) * 2.0, W=L, H=sS + W)).translate(((sS + W) / 2.0, 0.0, 0.0))
    if BL > 0.0:
        if BW <= 0.0:
            BW = L
        o5 = BOX(s, L=BL, W=BW, H=sL).translate(((sL / 2.0) - L, 0.0, 0.0))
        o6 = CYLINDER(s, R=R1, H=BW, O=0.0).translate((0.0, 0.0, -(BW / 2.0)))
    else:
        o5 = None
    if ((MW > 0.0) and (MH > 0.0)) and (L > 0.0):
        o7 = CNUT6_001(s, D=W, W=MW, H=MH).translate(((MD + R1) + BH, R1 + R2, 0.0))
        o8 = CNUT6_001(s, D=W, W=MW, H=MH).translate(((MD + R1) + BH, -(R1 + R2), 0.0))
    else:
        o7 = None
        o8 = None
    o1.subtractFrom(o4)
    o4.erase()
    o1.uniteWith(o2)
    o2.erase()
    o1.uniteWith(o3)
    o3.erase()
    if o5:
        o5.subtractFrom(o6)
        o6.erase()
        o1.uniteWith(o5)
        o5.erase()
    if o7:
        o1.uniteWith(o7)
        o7.erase()
    if o8:
        o1.uniteWith(o8)
        o8.erase()
    o1.rotateY(90)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('BH', (0, 0, -D / 2.0), (0, 0, -BH - (D / 2.0)))
