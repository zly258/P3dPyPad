# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="StubEnd", TooltipShort="Built-in CPMB", TooltipLong="Built-in CPMB (Decompiled from varmain/miscellaneoussub/cpmb.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(B=LENGTH, TooltipShort="B")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(ID=STRING, TooltipShort="组件标识")
def CPMB(s, L=54.0, B=4.0, D1=158.0, D2=114.3, ID='CPMB', **kw):
    if PnP3dACPAdapterIgnoreWallThickness:
        O = D2
    else:
        O = CON_OF_DIV(D2) / 2.0
    o1 = ((CYLINDER(s, R=D2 / 2.0, H=L - B, O=O)).rotateY(90)).translate((B, 0, 0))
    o0 = (CYLINDER(s, R=D1 / 2.0, H=B, O=O)).rotateY(90)
    o0.uniteWith(o1)
    o1.erase()
    if (D2 > O) and (O > 0):
        o2 = ((CYLINDER(s, R=O, H=L - B, O=0.0)).rotateY(90)).translate((B, 0, 0))
        o0.subtractFrom(o2)
        o2.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((L, 0, 0), (1, 0, 0))
