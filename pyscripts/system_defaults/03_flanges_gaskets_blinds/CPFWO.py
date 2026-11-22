# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpf_util import *


@activate(Group="Flange", TooltipShort="Built-in CPFWO", TooltipLong="Built-in CPFWO (Decompiled from varmain/flangesub/cpfwo.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(B=LENGTH, TooltipShort="B")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(W=LENGTH, TooltipShort="W")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPFWO(s, L=54.0, B=22.0, D1=220.0, D2=114.3, D3=0.0, W=0.0, OF=-1.0, ID='CPFWO', **kw):
    if (L <= 0.0) or (L <= B):
        L = B + 0.0001
    if (W <= 0.0) or (W < D2):
        OF = getThickness(D=D2, OF=-1, Ever=1, mustCalc=True)
        W = D2 + (OF * 2.0)
    if (D3 == 0.0) or (D3 > W):
        D3 = W
    if D3 > D1:
        D3 = D1
    if D3 < 0.0:
        D3 = D2
    if D3 == D2:
        O = CON_OF_DIV(D2) / 2.0
        if PnP3dACPAdapterIgnoreWallThickness:
            O = 0.0
        o1 = ((CYLINDER(s, R=D3 / 2.0, H=L - B, O=O)).rotateY(90)).translate((B, 0, 0))
    else:
        O = getInsideDiameter(D2, OF) / 2.0
        if PnP3dACPAdapterIgnoreWallThickness:
            O = 0.0
        o1 = ((CONE(s, R1=D3 / 2.0, R2=D2 / 2.0, H=L - B, E=0)).rotateY(90)).translate((B, 0, 0))
    o0 = (CYLINDER(s, R1=W / 2.0, R2=D1 / 2.0, H=B, O=0.0)).rotateY(90)
    if not (PnP3dACPAdapterIgnoreWallThickness):
        ow = CYLINDER(s, R=O, H=L, O=0.0).rotateY(90)
        o0.subtractFrom(ow)
        ow.erase()
    o0.uniteWith(o1)
    o1.erase()
    if not (PnP3dACPAdapterIgnoreWallThickness):
        o2 = ((CYLINDER(s, R=O, H=L - B, O=0.0)).rotateY(90)).translate((B, 0, 0))
        o0.subtractFrom(o2)
        o2.erase()
    if D1 < W:
        WA = 90.0
    else:
        WA = 0.0
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), WA)
    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0), WA)
