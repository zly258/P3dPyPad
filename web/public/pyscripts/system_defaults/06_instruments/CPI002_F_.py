# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpfwo import *
from varmain.instrsub.cpi002sub.cpi002 import *


@activate(Group="Instrument", TooltipShort="TEMPERATURE TRANSMITTER, CL 150, RF", TooltipLong="TEMPERATURE TRANSMITTER, CL 150, RF (Decompiled from varmain/instrsub/cpi002sub/cpi002_f_.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(L=LENGTH, TooltipShort="L")
@param(QL=LENGTH, TooltipShort="QL")
@param(QW=LENGTH, TooltipShort="QW")
@param(QH=LENGTH, TooltipShort="QH")
@param(L3=LENGTH, TooltipShort="L3")
@param(B3=LENGTH, TooltipShort="B3")
@param(D3=LENGTH, TooltipShort="D3")
@param(D4=LENGTH, TooltipShort="D4")
@param(W=LENGTH, TooltipShort="W")
@param(EX=LENGTH, TooltipShort="EX")
@param(EY=LENGTH, TooltipShort="EY")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPI002_F_(s, D1=17.2, L=229.0, QL=111.8, QW=129.9, QH=110.0, L3=22.0, B3=16.0, D3=90.0, D4=28.0, W=0.0, EX=0.0, EY=0.0, OF=-1.0, ID='CPI002_F_', **kw):
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
    oA = CPI002(s, D1=D1, L=L, QL=QL, QW=QW, QH=QH, EX=EX, EY=EX)
    oB = CPFWO(s, L=L3, B=B3, D1=D3, D2=D1, D3=D4, W=W).rotateY(-90.0).rotateZ(90.0)
    oG = (CYLINDER(s, R=D1 * 0.01, H=D1 * 0.01, O=0.0)).translate((0.0, 0.0, L - (QH / 2.0)))
    oG.uniteWith(oA)
    oA.erase()
    oG.uniteWith(oB)
    oB.erase()
    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0), WA2)
