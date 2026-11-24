# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.instrsub.cpi002sub.cpi002 import *


@activate(Group="Instrument", TooltipShort="TEMPERATURE TRANSMITTER, FPT", TooltipLong="TEMPERATURE TRANSMITTER, FPT (Decompiled from varmain/instrsub/cpi002sub/cpi002_of.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(L=LENGTH, TooltipShort="L")
@param(QL=LENGTH, TooltipShort="QL")
@param(QW=LENGTH, TooltipShort="QW")
@param(QH=LENGTH, TooltipShort="QH")
@param(L2=LENGTH, TooltipShort="L2")
@param(I=LENGTH, TooltipShort="I")
@param(EX=LENGTH, TooltipShort="EX")
@param(EY=LENGTH, TooltipShort="EY")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPI002_OF(s, D1=17.2, L=229.0, QL=111.8, QW=129.9, QH=110.0, L2=16.2552, I=15.2552, EX=0.0, EY=0.0, OF=-1.0, ID='CPI002_OF', **kw):
    if OF == -1:
        OF = getThickness(D=D1, OF=OF)
    oA = (CPI002(s, D1=D1, L=L - (L2 - I), QL=QL, QW=QW, QH=QH, EX=EX, EY=EX)).translate((0.0, 0.0, L2 - I))
    oB = CON_OF(s, D1=D1, D2=0.0, L=L2, OF=OF).rotateY(90.0).translate((0.0, 0.0, L2 - I))
    oG = (CYLINDER(s, R=D1 * 0.01, H=D1 * 0.01, O=0.0)).translate((0.0, 0.0, L - (QH / 2.0)))
    oG.uniteWith(oA)
    oA.erase()
    oG.uniteWith(oB)
    oB.erase()
    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
