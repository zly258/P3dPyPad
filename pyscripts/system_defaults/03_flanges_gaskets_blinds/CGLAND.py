# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Gland", TooltipShort="Built-in CGLAND", TooltipLong="Built-in CGLAND (Decompiled from varmain/divsub/cgland.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(G=LENGTH, TooltipShort="G")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CGLAND(s, L=-1.0, D1=-1.0, D2=114.3, G=-1.0, OF=-1.0, ID='CGLAND', **kw):
    sF = getThickness(D2, OF=OF, Ever=True, mustCalc=True)
    if G < 0.0:
        G = sF
    if L <= 0.0:
        L = sF
    if D1 <= 0.0:
        D1 = D2 + (sF * 4.0)
    D3 = D2 + (sF * 2.0)
    O = D2 / 2.0
    o0 = (CYLINDER(s, R=D1 / 2.0, H=L, O=O)).rotateY(90)
    if G > 0.0:
        o1 = ((CONE(s, R1=D3 / 2.0, R2=(D2 + sF) / 2.0, H=G, E=0)).rotateY(90)).translate((L, 0, 0))
    if G > 0.0:
        o0.uniteWith(o1)
        o1.erase()
    o2 = (CYLINDER(s, R=O, H=L + G, O=0.0)).rotateY(90)
    o0.subtractFrom(o2)
    o2.erase()
    o0.rotateY(180).translate((G + L, 0.0, 0.0))
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
    s.setPoint((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0)
