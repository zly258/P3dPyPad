# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgcsub.csgc002 import *
from varmain.supportssub.csgbsub.csgb010 import *


@activate(Group="Support", TooltipShort="CSGB011", TooltipLong="CSGB011", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(SH=LENGTH, TooltipShort="SH")
@param(SM=LENGTH, TooltipShort="SM")
@param(SD=LENGTH, TooltipShort="SD")
@param(E=LENGTH, TooltipShort="E")
@param(BL=LENGTH, TooltipShort="BL")
@param(BW=LENGTH, TooltipShort="BW")
@param(BH=LENGTH, TooltipShort="BH")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB011(s, D=116.0, L=40.0, W=4.0, K=0.0, SL=180.0, SW=80.0, ST=0.0, SH=300.0, SM=20.0, SD=-1.0, E=90.0, BL=220.0, BW=60.0, BH=2.0, ID='CSGB011', **kw):
    R1 = D / 2.0
    R2 = R1 + W
    if SW <= 0.0:
        SW = SL
    if K <= 0.0:
        K = D + (L * 2.0)
    if BL <= 0.0:
        BL = SL
    if BW <= 0.0:
        BW = L
    if ST <= 0.0:
        ST = W
    if E <= 0.0:
        E = (SH / 2.0) - R2
    E2 = (SH - (R2 * 2.0)) - E
    o0 = CSGB010_Sub(s, D=D, SL=SL, SW=SW, ST=ST, SM=SM, SD=SD, E=E2).translate(((D / 2.0) + W, 0.0, 0.0))
    o1 = ((CYLINDER(s, R=E * 0.01, H=ST, O=0.0)).rotateY(180.0)).translate((-(((D + E) / 2.0) + W), 0.0, 0.0))
    o2 = CSGB010(s, D=D, L=L, W=W, K=K, SL=SL, SW=SW, ST=ST, SM=SM, SD=SD, E=E, BL=BL, BW=BW, BH=BH)
    o3 = CSGB010_Rem(s, D=D, L=L, W=W, SL=SL, SD=SD, SW=SW, ST=ST)
    o1.uniteWith(o0)
    o0.erase()
    o1.subtractFrom(o3)
    o3.erase()
    o1.translate((0.0, 0.0, ST))
    o1.uniteWith(o2)
    o2.erase()
    s.setPoint((0, 0, (ST + (SL / 2.0)) + (L / 2.0)), (0.0, 0.0, -1.0))
