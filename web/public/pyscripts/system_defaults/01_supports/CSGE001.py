# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cste_l import *
from varmain.divsub.cste_t import *
from varmain.supportssub.csgcsub.csgc000 import *


@activate(Group="Support", TooltipShort="CSGE001", TooltipLong="CSGE001", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(LS=LENGTH, TooltipShort="LS")
@param(WS=LENGTH, TooltipShort="WS")
@param(BL=LENGTH, TooltipShort="BL")
@param(BW=LENGTH, TooltipShort="BW")
@param(BH=LENGTH, TooltipShort="BH")
@param(MW=LENGTH, TooltipShort="MW")
@param(MH=LENGTH, TooltipShort="MH")
@param(WT=LENGTH, TooltipShort="WT")
@param(HT=LENGTH, TooltipShort="HT")
@param(TT=LENGTH, TooltipShort="TT")
@param(WL=LENGTH, TooltipShort="WL")
@param(HL=LENGTH, TooltipShort="HL")
@param(TL=LENGTH, TooltipShort="TL")
@param(LL=LENGTH, TooltipShort="LL")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(ID=STRING, TooltipShort="组件标识")
def CSGE001(s, D=116.0, L=400.0, LS=30.0, WS=0.0, BL=80.0, BW=60.0, BH=10.0, MW=0.0, MH=0.0, WT=100.0, HT=0.0, TT=8.0, WL=0.0, HL=0.0, TL=0.0, LL=200.0, SL=250.0, SW=150.0, ST=0.0, ID='CSGE001', **kw):
    if TL <= 0.0:
        TL = TT
    MD = TL
    if SW <= 0.0:
        SW = SL
    if ST <= 0.0:
        ST = TT
    if HT <= 0.0:
        HT = WT / 2.0
    if WL <= 0.0:
        WL = HT + TL
    if HL <= 0.0:
        HL = WL
    if SW <= 0.0:
        SW = SL
    R = (D / 2.0) + BH
    LT = L - R
    o1 = CSGC000(s, D=D, L=LS, W=WS, BL=BL, BW=BW, BH=BH, MW=MW, MH=MH, MD=MD)
    o2 = CSTE_L(s, W=WL, H=HL, T=TL, L=LL).rotateX(-90.0).rotateZ(180).translate((TL / 2.0, LL / 2.0, -(R + (HL / 2.0))))
    o3 = CSTE_T(s, W=WT, H=HT, T=TT, L=LT).rotateY(180.0).rotateZ(90.0).translate((0.0, 0.0, -R))
    o4 = None
    if (SL > 0.0) and (SW > 0.0):
        o4 = BOX(s, L=SL, H=SW, W=ST).translate((0.0, 0.0, -(L - (ST / 2.0))))
    o0 = (BOX(s, L=TL * 0.01, H=TL * 0.01, W=TL * 0.01)).translate((0.0, 0.0, -(R + (TL / 2.0))))
    o0.uniteWith(o1)
    o1.erase()
    o0.uniteWith(o2)
    o2.erase()
    o0.uniteWith(o3)
    o3.erase()
    if o4:
        o0.uniteWith(o4)
        o4.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('L', (0, 0, 0), (0, 0, -L))
