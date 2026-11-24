# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cste_l import *
from varmain.divsub.cste_t import *
from varmain.supportssub.csgcsub.csgc000 import *


@activate(Group="Support", TooltipShort="CSGE002", TooltipLong="CSGE002", LengthUnit="mm", Ports=1)
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
@param(NO=LENGTH, TooltipShort="NO")
@param(NL=LENGTH, TooltipShort="NL")
@param(NW=LENGTH, TooltipShort="NW")
@param(NT=LENGTH, TooltipShort="NT")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(ID=STRING, TooltipShort="组件标识")
def CSGE002(s, D=116.0, L=400.0, LS=30.0, WS=0.0, BL=80.0, BW=60.0, BH=10.0, MW=0.0, MH=0.0, WT=100.0, HT=0.0, TT=8.0, WL=0.0, HL=0.0, TL=0.0, LL=200.0, NO=10.0, NL=50.0, NW=30.0, NT=0.0, SL=250.0, SW=150.0, ST=0.0, ID='CSGE002', **kw):
    if TL <= 0.0:
        TL = TT
    MD = TL
    if SW <= 0.0:
        SW = SL
    if ST <= 0.0:
        ST = TT
    if NT <= 0.0:
        NT = TT
    if NO < 0.0:
        NO = 0.0
    if HT <= 0.0:
        HT = WT / 2.0
    if WL <= 0.0:
        WL = HT + TL
    if HL <= 0.0:
        HL = WL
    if SW <= 0.0:
        SW = SL
    R = (D / 2.0) + BH
    LT = (L - (TL / 2.0)) - (HL / 2.0)
    TMP1 = -((R + HL) - (HT / 2.0))
    o1 = CSGC000(s, D=D, L=LS, W=WS, BL=BL, BW=BW, BH=BH, MW=MW, MH=MH, MD=MD).rotateY(-90).rotateZ(180.0)
    o2 = CSTE_L(s, W=WL, H=HL, T=TL, L=LL).rotateX(90.0).rotateZ(180).translate((-(R + (HL / 2.0)), -(LL / 2.0), -(TL / 2.0)))
    o3 = CSTE_T(s, W=WT, H=HT, T=TT, L=LT).rotateY(180.0).rotateZ(90.0).translate((TMP1, 0.0, LT - L))
    o4 = None
    if (NL > 0.0) and (NW > 0.0):
        NW = NW + (D / 2.0)
        o4 = BOX(s, L=NT, H=NW, W=NL).translate((-(NW / 2.0), 0.0, ((NL / 2.0) + NO) + ((WL - TL) / 2.0)))
        r4 = CYLINDER(s, R=D / 2.0, H=(HL + NO) + NL, O=0.0)
    o5 = None
    if (SL > 0.0) and (SW > 0.0):
        o5 = BOX(s, L=SL, H=SW, W=ST).translate((TMP1, 0.0, -(L - (ST / 2.0))))
    o0 = (BOX(s, L=TL * 0.01, H=TL * 0.01, W=TL * 0.01)).translate((-(R + (TL / 2.0)), 0.0, 0.0))
    o0.uniteWith(o1)
    o1.erase()
    o0.uniteWith(o2)
    o2.erase()
    o0.uniteWith(o3)
    o3.erase()
    if o4:
        o4.subtractFrom(r4)
        r4.erase()
        o0.uniteWith(o4)
        o4.erase()
    if o5:
        o0.uniteWith(o5)
        o5.erase()
    o0.rotateY(90)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('L', (0, 0, 0), (-L, 0, 0))
