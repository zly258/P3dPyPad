# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpfwo import *
from varmain.instrsub.cpi001sub.cpi001 import *


@activate(Group="Instrument", TooltipShort="PRESSURE GAUGE, CL 150, RF", TooltipLong="PRESSURE GAUGE, CL 150, RF (Decompiled from varmain/instrsub/cpi001sub/cpi001_f_.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(L1=LENGTH, TooltipShort="L1")
@param(L3=LENGTH, TooltipShort="L3")
@param(B3=LENGTH, TooltipShort="B3")
@param(D3=LENGTH, TooltipShort="D3")
@param(D4=LENGTH, TooltipShort="D4")
@param(W=LENGTH, TooltipShort="W")
@param(EX=LENGTH, TooltipShort="EX")
@param(EY=LENGTH, TooltipShort="EY")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPI001_F_(s, D1=17.2, D2=139.0, L=191.0, L1=86.0, L3=22.0, B3=16.0, D3=90.0, D4=28.0, W=0.0, EX=0.0, EY=0.0, OF=-1.0, ID='CPI001_F_', **kw):
    if OF == -1:
        OF = getThickness(D=D1, OF=OF)
    if L3 <= 0.0:
        L3 = OF
    if D3 <= 0.0:
        D3 = D1 + (OF * 2.0)
    if areEqual(W, 0.0):
        W = D3
    if D3 < W:
        WA2 = 90.0
    else:
        WA2 = 0.0
    oA = CPI001(s, D1=D1, D2=D2, L=L, L1=L1, EX=EX, EY=EX)
    oB = CPFWO(s, L=L3, B=B3, D1=D3, D2=D1, D3=D4, W=W).rotateY(-90.0).rotateZ(90.0)
    oG = (CYLINDER(s, R=D1 * 0.01, H=D1 * 0.01, O=0.0)).translate((0.0, 0.0, L - (D2 / 2.0)))
    oG.uniteWith(oA)
    oA.erase()
    oG.uniteWith(oB)
    oB.erase()
    s.setPoint((0, 0, 0), (0, 0, -1), WA2)
