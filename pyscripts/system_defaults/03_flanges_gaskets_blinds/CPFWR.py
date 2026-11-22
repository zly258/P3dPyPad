# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpf_util import *


@activate(Group="Flange", TooltipShort="CP METRIC Flange", TooltipLong="CP METRIC Flange (Decompiled from varmain/flangesub/cpfwr.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(B=LENGTH, TooltipShort="B")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(ID=STRING, TooltipShort="组件标识")
def CPFWR(s, L=35.0, B=16.0, D1=90.0, D2=17.2, D3=0.0, ID='CPFWR', **kw):
    if (L <= 0.0) or (L <= B):
        L = B + 0.0001
    if D3 == 0.0:
        D3 = ((D1 - D2) / 2) + D2
    else:
        if D3 < 0.0:
            D3 = D2
    if D3 == D2:
        O = CON_OF_DIV(D2) / 2.0
        if PnP3dACPAdapterIgnoreWallThickness:
            O = 0.0
        o1 = ((CYLINDER(s, R=D3 / 2.0, H=L - B, O=O)).rotateY(90)).translate((B, 0, 0))
    else:
        O = D2 / 2.0
        o1 = ((CONE(s, R1=D3 / 2.0, R2=D2 / 2.0, H=L - B, E=0)).rotateY(90)).translate((B, 0, 0))
    o0 = (CYLINDER(s, R=D1 / 2.0, H=B, O=O)).rotateY(90)
    o0.uniteWith(o1)
    o1.erase()
    if not (PnP3dACPAdapterIgnoreWallThickness):
        o2 = ((CYLINDER(s, R=O, H=L - B, O=0.0)).rotateY(90)).translate((B, 0, 0))
        o0.subtractFrom(o2)
        o2.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0)
