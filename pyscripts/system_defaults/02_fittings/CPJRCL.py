# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.reducersub.cpjrcsub.cpjrc import *


@activate(Group="Reducer", TooltipShort="Built-in CPJRCL", TooltipLong="Built-in CPJRCL (Decompiled from varmain/reducersub/cpjrclsub/cpjrcl.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(LL=LENGTH, TooltipShort="LL")
@param(LR=LENGTH, TooltipShort="LR")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPJRCL(s, D1=114.3, D2=60.3, L=210.0, LL=0.0, LR=0.0, OF=-1.0, ID='CPJRCL', **kw):
    if (LL == 0.0) and (LR == 0.0):
        LL = L / 3.0
        LR = LL
    else:
        if LL == 0.0:
            LL = (L - LR) / 2.0
        else:
            if LR == 0.0:
                LR = (L - LL) / 2.0
    OF = getThickness(D1, OF=OF)
    noLeft = 0
    noRight = 0
    if LL == -2:
        LL = 0.0
        noLeft = 1
    if LR == -2:
        LR = 0.0
        noRight = 1
    LM = L - (LL + LR)
    if OF == 0.0:
        OF = -1
    o0 = CPJRC(s, D1=D1, D2=D2, L=LM, OF=OF).translate((LL, 0, 0))
    oTMP = ((CYLINDER(s, R=D1 / 2.0, H=0.001, O=(D1 - 1.0) / 2.0)).rotateY(90)).translate((LL, 0, 0))
    oTMP.uniteWith(o0)
    o0.erase()
    if noLeft == 0:
        DI1 = getInsideDiameter(D=D1, OF=OF, Ever=1)
        oI1 = ((CYLINDER(s, R=D1 / 2.0, H=LL, O=DI1 / 2.0)).rotateY(270)).translate((LL, 0, 0))
        oTMP.uniteWith(oI1)
        oI1.erase()
    if noRight == 0:
        DI2 = getInsideDiameter(D=D2, OF=OF, Ever=1)
        oI2 = ((CYLINDER(s, R=D2 / 2.0, H=LR, O=DI2 / 2.0)).rotateY(90)).translate((L - LR, 0, 0))
        oTMP.uniteWith(oI2)
        oI2.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((L, 0, 0), (1, 0, 0))
