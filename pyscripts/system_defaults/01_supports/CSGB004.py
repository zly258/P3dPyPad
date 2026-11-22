# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Support", TooltipShort="CSGB004", TooltipLong="CSGB004", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(SH=LENGTH, TooltipShort="SH")
@param(SE=LENGTH, TooltipShort="SE")
@param(SC=LENGTH, TooltipShort="SC")
@param(HL=LENGTH, TooltipShort="HL")
@param(HW=LENGTH, TooltipShort="HW")
@param(HH=LENGTH, TooltipShort="HH")
@param(P=INT, TooltipShort="P")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB004(s, D=116.0, SL=180.0, SW=100.0, ST=8.0, SH=75.0, SE=25.0, SC=30.0, HL=50.0, HW=160.0, HH=20.0, P=1, ID='CSGB004', **kw):
    R1 = D / 2.0
    HS = SH + R1
    o1 = BOX(s, L=ST, W=SL, H=HS).translate((HS / 2.0, 0.0, 0.0))
    o2 = BOX(s, L=SW, W=SL, H=ST).translate((HS - (ST / 2.0), 0.0, 0.0))
    if (HL > 0.0) and (HW > 0.0):
        if HH <= 0.0:
            HH = ST * 2.0
        o3 = BOX(s, L=HW, W=HL, H=HH).translate((HS - (HH / 2.0), 0.0, 0.0))
    else:
        o3 = None
    if P > 0:
        o4 = BOX(s, L=SW, W=ST, H=HS).translate((HS / 2.0, 0.0, (-(SL / 2.0)) + (ST / 2.0)))
        o5 = BOX(s, L=SW, W=ST, H=HS).translate((HS / 2.0, 0.0, (SL / 2.0) - (ST / 2.0)))
    else:
        o4 = None
        o5 = None
    o1.uniteWith(o2)
    o2.erase()
    if o3:
        o1.uniteWith(o3)
        o3.erase()
    if o4:
        o1.uniteWith(o4)
        o4.erase()
    if o5:
        o1.uniteWith(o5)
        o5.erase()
    o6 = CYLINDER(s, R=R1, H=SL, O=0.0).translate((0.0, 0.0, -(SL / 2.0)))
    o1.subtractFrom(o6)
    o6.erase()
    if SC > 0.0:
        CT = ST * 2.0
        CH = SC + R1
        if (P > 0.0) and (SE <= 0.0):
            SE = ST
        CW = SL - (SE * 2.0)
        o7 = BOX(s, L=CT, W=CW, H=R1).translate((R1 / 2.0, 0.0, 0.0))
        CL = CW - (SC * 2.0)
        CC = sqrt(pow(SC, 2.0) * 2.0)
        o8 = BOX(s, L=CT, W=CC, H=CC).rotateY(45.0).translate((R1, 0.0, CL / 2.0))
        o7.uniteWith(o8)
        o8.erase()
        o9 = BOX(s, L=CT, W=CC, H=CC).rotateY(45.0).translate((R1, 0.0, -(CL / 2.0)))
        o7.uniteWith(o9)
        o9.erase()
        o0 = BOX(s, L=CT, W=CL, H=SC).translate((R1 + (SC / 2.0), 0.0, 0.0))
        o7.uniteWith(o0)
        o0.erase()
        o1.subtractFrom(o7)
        o7.erase()
    o1.rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0, 0, -D / 2.0), (0, 0, -SH - (D / 2.0)))
