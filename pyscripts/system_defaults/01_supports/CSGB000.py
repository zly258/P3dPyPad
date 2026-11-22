# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Support", TooltipShort="CSGB000", TooltipLong="CSGB000", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(SH=LENGTH, TooltipShort="SH")
@param(HL=LENGTH, TooltipShort="HL")
@param(HW=LENGTH, TooltipShort="HW")
@param(HH=LENGTH, TooltipShort="HH")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB000(s, D=116.0, SL=180.0, SW=100.0, ST=8.0, SH=50.0, HL=50.0, HW=160.0, HH=0.0, ID='CSGB000', **kw):
    R1 = D / 2.0
    HS = SH + R1
    o1 = BOX(s, L=ST, W=SL, H=HS).translate((HS / 2.0, 0.0, SL / 2.0))
    o2 = BOX(s, L=SW, W=SL, H=ST).translate((HS - (ST / 2.0), 0.0, SL / 2.0))
    if (HL > 0.0) and (HW > 0.0):
        if HH <= 0.0:
            HH = ST * 2.0
        o3 = BOX(s, L=HW, W=HL, H=HH).translate((HS - (HH / 2.0), 0.0, SL / 2.0))
    else:
        o3 = None
    o1.uniteWith(o2)
    o2.erase()
    if o3:
        o1.uniteWith(o3)
        o3.erase()
    o4 = CYLINDER(s, R=D / 2.0, H=SL, O=0.0)
    o1.subtractFrom(o4)
    o4.erase()
    (o1.translate((0.0, 0.0, -(SL / 2.0)))).rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0, 0, -D / 2.0), (0, 0, -SH - (D / 2.0)))
