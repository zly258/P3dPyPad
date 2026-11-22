# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgcsub.csgc002 import *


@activate(Group="Support", TooltipShort="CSGB001", TooltipLong="CSGB001", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(SH=LENGTH, TooltipShort="SH")
@param(E=LENGTH, TooltipShort="E")
@param(HL=LENGTH, TooltipShort="HL")
@param(HW=LENGTH, TooltipShort="HW")
@param(HH=LENGTH, TooltipShort="HH")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB001(s, D=116.0, L=30.0, W=4.0, K=0.0, SL=180.0, SW=100.0, ST=8.0, SH=150.0, E=0.0, HL=0.0, HW=0.0, HH=0.0, ID='CSGB001', **kw):
    R1 = D / 2.0
    HS = SH - R1
    o1 = BOX(s, L=ST, W=SL, H=HS).translate(((HS / 2.0) + R1, 0, 0))
    o2 = BOX(s, L=SW, W=SL, H=ST).translate((SH - (ST / 2.0), 0, 0))
    o1.uniteWith(o2)
    o2.erase()
    if (HL > 0.0) and (HW > 0.0):
        if HH <= 0.0:
            HH = ST * 2.0
        o3 = BOX(s, L=HW, W=HL, H=HH).translate((SH - (HH / 2.0), 0, 0))
        o1.uniteWith(o3)
        o3.erase()
    if (L > 0.0) and (W > 0.0):
        LS = (SL - L) - (E * 2.0)
        o4 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90).translate((0, 0, 0 - (LS / 2.0)))
        o1.uniteWith(o4)
        o4.erase()
        o5 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90).translate((0, 0, LS / 2.0))
        o1.uniteWith(o5)
        o5.erase()
    o1.rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0, 0, 0), (0, 0, -SH))
