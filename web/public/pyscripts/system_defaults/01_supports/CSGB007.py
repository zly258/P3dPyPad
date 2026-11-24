# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Support", TooltipShort="CSGB007", TooltipLong="CSGB007", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(SH=LENGTH, TooltipShort="SH")
@param(HW=LENGTH, TooltipShort="HW")
@param(LL=LENGTH, TooltipShort="LL")
@param(LW=LENGTH, TooltipShort="LW")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB007(s, D=116.0, SL=70.0, SW=0.0, ST=8.0, SH=25.0, HW=250.0, LL=30.0, LW=0.0, ID='CSGB007', **kw):
    R1 = D / 2.0
    HS = SH + R1
    if SW <= 0.0:
        SW = D
    if LW <= 0.0:
        LW = LL
    HS2 = HS / 2.0
    LL2 = LL / 2.0
    LW2 = LW / 2.0
    ST2 = ST / 2.0
    SW2 = SW / 2.0
    o1 = BOX(s, L=LL, W=ST, H=HS).translate((HS2 - SH, SW2 + LL2, LW2 - ST2))
    o2 = BOX(s, L=ST, W=LW, H=HS).translate((HS2 - SH, SW2 + ST2, -ST2 + ST2))
    o3 = BOX(s, L=LL, W=ST, H=HS).translate((HS2 - SH, -(SW2 + LL2), LW2 - ST2))
    o4 = BOX(s, L=ST, W=LW, H=HS).translate((HS2 - SH, -(SW2 + ST2), -ST2 + ST2))
    o1.uniteWith(o2)
    o2.erase()
    o1.uniteWith(o3)
    o3.erase()
    o1.uniteWith(o4)
    o4.erase()
    if (HW > 0.0) and (SL > 0.0):
        o5 = BOX(s, L=HW, W=SL, H=ST).translate((R1 + (ST / 2.0), 0.0, 0.0))
        o1.uniteWith(o5)
        o5.erase()
    else:
        ST = 0.0
    o1.rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    bs = R1 + ST
    if bs != 0.0:
        s.setLinearDimension('#', (0, 0, -bs), (0, 0, -bs))
