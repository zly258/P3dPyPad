# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgcsub.csgc002 import *


@activate(Group="Support", TooltipShort="CSGB012", TooltipLong="CSGB012", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(SH=LENGTH, TooltipShort="SH")
@param(TI=INT, TooltipShort="TI")
@param(CS=INT, TooltipShort="CS")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB012(s, D=116.0, L=30.0, W=4.0, K=0.0, SL=180.0, SW=100.0, ST=8.0, SH=150.0, TI=0, CS=0, ID='CSGB012', **kw):
    if K <= 0.0:
        K = D + (L * 2.0)
    if SW <= 0.0:
        SW = D
    R1 = D / 2.0
    R2 = R1 + W
    R3 = R1 + (W / 2.0)
    LS = SL - L
    HS = SH - R3
    if ST <= 0.0:
        ST = W
    o9 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90).rotateZ(-45.0)
    if (CS > 0) or (CS == -2):
        o0 = None
        pZ = 0.0
    else:
        o9.translate((0.0, 0.0, -(LS / 2.0)))
        o0 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90).rotateZ(-45.0).translate((0.0, 0.0, LS / 2.0))
        pZ = LS / 2.0
    if (TI > 0) and (TI & 1):
        o1 = None
    else:
        o1 = ((BOX(s, L=ST, W=SL, H=HS).translate(((HS / 2.0) + R3, 0, 0))).rotateZ(90.0)).rotateZ(90.0)
        o2 = ((BOX(s, L=SW, W=SL, H=ST).translate((SH - (ST / 2.0), 0, 0))).rotateZ(90.0)).rotateZ(90.0)
    if (TI > 0) and (TI & 2):
        o3 = None
    else:
        o3 = ((BOX(s, L=ST, W=SL, H=HS).translate(((HS / 2.0) + R3, 0, 0))).rotateZ(90.0)).rotateZ(-90.0)
        o4 = ((BOX(s, L=SW, W=SL, H=ST).translate((SH - (ST / 2.0), 0, 0))).rotateZ(90.0)).rotateZ(-90.0)
    if (TI > 0) and (TI & 4):
        o5 = None
    else:
        o5 = (BOX(s, L=ST, W=SL, H=HS).translate(((HS / 2.0) + R3, 0, 0))).rotateZ(90.0)
        o6 = (BOX(s, L=SW, W=SL, H=ST).translate((SH - (ST / 2.0), 0, 0))).rotateZ(90.0)
    if (TI > 0) and (TI & 8):
        o7 = None
    else:
        o7 = ((BOX(s, L=ST, W=SL, H=HS).translate(((HS / 2.0) + R3, 0, 0))).rotateZ(90.0)).rotateZ(180.0)
        o8 = ((BOX(s, L=SW, W=SL, H=ST).translate((SH - (ST / 2.0), 0, 0))).rotateZ(90.0)).rotateZ(180.0)
    if o1:
        o1.uniteWith(o2)
        o2.erase()
    else:
        o1 = (((CYLINDER(s, R=W * 0.1, H=W * 0.1, O=0.0)).rotateX(90.0)).translate(((K - L) / 2.0, -(W / 2.0), -(LS / 2.0)))).rotateZ(45.0)
    if o3:
        o1.uniteWith(o3)
        o3.erase()
        o1.uniteWith(o4)
        o4.erase()
    if o5:
        o1.uniteWith(o5)
        o5.erase()
        o1.uniteWith(o6)
        o6.erase()
    if o7:
        o1.uniteWith(o7)
        o7.erase()
        o1.uniteWith(o8)
        o8.erase()
    o1.uniteWith(o9)
    o9.erase()
    if o0:
        o1.uniteWith(o0)
        o0.erase()
    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('SH', (0, 0, 0), (-SH, 0, 0))
