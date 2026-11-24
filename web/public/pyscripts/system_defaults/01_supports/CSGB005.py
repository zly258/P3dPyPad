# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgbsub.csgb004 import *


@activate(Group="Support", TooltipShort="CSGB005", TooltipLong="CSGB005", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(SH=LENGTH, TooltipShort="SH")
@param(SE=LENGTH, TooltipShort="SE")
@param(SC=LENGTH, TooltipShort="SC")
@param(BH=LENGTH, TooltipShort="BH")
@param(CD=LENGTH, TooltipShort="CD")
@param(BL=LENGTH, TooltipShort="BL")
@param(P=INT, TooltipShort="P")
@param(C=INT, TooltipShort="C")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB005(s, D=116.0, SL=180.0, SW=100.0, ST=8.0, SH=75.0, SE=25.0, SC=30.0, BH=75.0, CD=10.0, BL=0.0, P=1, C=1, ID='CSGB005', **kw):
    R1 = D / 2.0
    HS = SH + R1
    if BH <= 0.0:
        BH = SH
    if BL <= 0.0:
        BL = SL / 3.0
    o0 = CSGB004(s, D=D, SL=SL, SW=SW, ST=ST, SH=SH, SE=SE, SC=SC, HL=0.0, HW=0.0, HH=0.0, P=P).rotateY(-90)
    o1 = BOX(s, L=ST, W=SL, H=BH).translate((HS + (BH / 2.0), 0.0, 0.0))
    o2 = (BOX(s, L=ST * 2.0, W=BL, H=BH)).translate((HS + (BH / 2.0), 0.0, 0.0))
    if CD > 0.0:
        R2 = CD / 2.0
        o3 = CYLINDER(s, R=R2, H=SW, O=0.0).rotateX(90.0).translate((HS + R2, SW / 2.0, 0.0))
    else:
        o3 = None
    xD = (SL - BL) / 2.0
    if P > 0:
        xD = xD - ST
        o4 = BOX(s, L=SW, W=ST, H=BH).translate((HS + (BH / 2.0), 0.0, -((BL / 2.0) + (ST / 2.0))))
        o5 = BOX(s, L=SW, W=ST, H=BH).translate((HS + (BH / 2.0), 0.0, (BL / 2.0) + (ST / 2.0)))
    else:
        o4 = None
        o5 = None
    o1.uniteWith(o0)
    o0.erase()
    if o4:
        o1.uniteWith(o4)
        o4.erase()
    if o5:
        o1.uniteWith(o5)
        o5.erase()
    xH = BH / 2.0
    if C > 0:
        if xD < xH:
            xH = xD
        CT = ST * 2.0
        BP = HS + BH
        CC = sqrt(pow(xH, 2.0) * 2.0)
        o8 = BOX(s, L=CT, W=CC, H=CC).rotateY(45.0).translate((BP, 0.0, SL / 2.0))
        o2.uniteWith(o8)
        o8.erase()
        o9 = BOX(s, L=CT, W=CC, H=CC).rotateY(45.0).translate((BP, 0.0, -(SL / 2.0)))
        o2.uniteWith(o9)
        o9.erase()
    o1.subtractFrom(o2)
    o2.erase()
    if o3:
        o1.uniteWith(o3)
        o3.erase()
    o1.rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('BH', (0, 0, (-D / 2.0) - SH), (0, 0, ((-D / 2.0) - SH) - BH))
