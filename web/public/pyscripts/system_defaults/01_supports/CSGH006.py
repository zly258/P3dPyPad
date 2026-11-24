# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cnut6_001 import *
from varmain.supportssub.csgcsub.csgc005 import *


@activate(Group="Support", TooltipShort="CSGH006", TooltipLong="CSGH006", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(H=LENGTH, TooltipShort="H")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K1=LENGTH, TooltipShort="K1")
@param(K2=LENGTH, TooltipShort="K2")
@param(HD3=LENGTH, TooltipShort="HD3")
@param(HS=LENGTH, TooltipShort="HS")
@param(HO=LENGTH, TooltipShort="HO")
@param(ID=STRING, TooltipShort="组件标识")
def CSGH006(s, D=116.0, H=500.0, L=30.0, W=4.0, K1=0.0, K2=0.0, HD3=0.0, HS=10.0, HO=0.0, ID='CSGH006', **kw):
    R1 = D / 2.0
    R2 = R1 + W
    if K1 <= 0.0:
        K1 = R1 + L
    if K2 <= 0.0:
        K2 = K1 + L
    SL = L - R1
    W1 = W * 3.0
    oVal = W / 10.0
    if HD3 <= 0.0:
        HD3 = D / 10.0
    o0 = CSGC005(s, D=D, L=L, W=W, K1=K1, K2=K2).rotateY(-90)
    o3 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(90.0).rotateX(90.0).translate((0.0, HD3 + K2, 0.0))
    o4 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateZ(90.0).rotateY(90.0).translate((0.0, H + HS, 0.0))
    MH = abs(o4.pointAt(1).y() - o4.pointAt(0).y())
    if HO <= 0.0:
        HO = MH * 3.0
    if (MH * 3.0) > HO:
        o5 = None
    else:
        o5 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateZ(90.0).translate(o4.pointAt(1))
    cL3 = ((H + HS) + HO) - ((R1 + (K2 - K1)) + W)
    o2 = ((CYLINDER(s, R=HD3 / 2.0, H=cL3, O=0.0)).rotateX(-90.0)).translate((0.0, (R1 + W) + (K2 - K1), 0.0))
    o2.uniteWith(o4)
    o4.erase()
    o2.uniteWith(o3)
    o3.erase()
    if o5:
        o2.uniteWith(o5)
        o5.erase()
    o2.uniteWith(o0)
    o0.erase()
    o2.rotateZ(90.0)
    s.setPoint((0, 0, 0), (0, 0, 1))
    s.setLinearDimension('H', (0, 0, 0), (-H, 0, 0))
