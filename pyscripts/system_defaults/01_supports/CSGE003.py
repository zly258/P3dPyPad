# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cste_l import *
from varmain.supportssub.csgcsub.csgc000 import *


@activate(Group="Support", TooltipShort="CSGE003", TooltipLong="CSGE003", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(LO=LENGTH, TooltipShort="LO")
@param(LS=LENGTH, TooltipShort="LS")
@param(WS=LENGTH, TooltipShort="WS")
@param(BL=LENGTH, TooltipShort="BL")
@param(BW=LENGTH, TooltipShort="BW")
@param(BH=LENGTH, TooltipShort="BH")
@param(MW=LENGTH, TooltipShort="MW")
@param(MH=LENGTH, TooltipShort="MH")
@param(WL=LENGTH, TooltipShort="WL")
@param(HL=LENGTH, TooltipShort="HL")
@param(TL=LENGTH, TooltipShort="TL")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(ID=STRING, TooltipShort="组件标识")
def CSGE003(s, D=116.0, L=400.0, LO=0.0, LS=30.0, WS=0.0, BL=80.0, BW=60.0, BH=10.0, MW=0.0, MH=0.0, WL=60.0, HL=0.0, TL=8.0, SL=250.0, SW=150.0, ST=0.0, ID='CSGE003', **kw):
    MD = TL
    if SW <= 0.0:
        SW = SL
    if HL <= 0.0:
        HL = WL
    if ST <= 0.0:
        ST = TL
    if LO <= 0.0:
        LO = D
    R = (D / 2.0) + BH
    LL = L + LO
    o1 = CSGC000(s, D=D, L=LS, W=WS, BL=BL, BW=BW, BH=BH, MW=MW, MH=MH, MD=MD).rotateY(-90).rotateX(90.0)
    o2 = CSTE_L(s, W=WL, H=HL, T=TL, L=LL).rotateX(180.0).translate((R + (HL / 2.0), TL / 2.0, LO))
    o3 = None
    if (SL > 0.0) and (SW > 0.0):
        o3 = BOX(s, L=SL, H=SW, W=ST).translate((R + (HL / 2.0), TL / 2.0, -(L - (ST / 2.0))))
    o0 = (BOX(s, L=TL * 0.01, H=TL * 0.01, W=TL * 0.01)).translate(((R + (HL / 2.0)) + (TL / 2.0), 0.0, 0.0))
    o0.uniteWith(o1)
    o1.erase()
    o0.uniteWith(o2)
    o2.erase()
    if o3:
        o0.uniteWith(o3)
        o3.erase()
    o0.rotateX(-90.0).rotateZ(90.0).rotateY(90)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('L', (0, 0, 0), (0, 0, -L))
