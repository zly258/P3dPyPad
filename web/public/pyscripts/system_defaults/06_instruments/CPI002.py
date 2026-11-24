# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Instrument", TooltipShort="Built-in CPI002", TooltipLong="Built-in CPI002 (Decompiled from varmain/instrsub/cpi002sub/cpi002.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(L=LENGTH, TooltipShort="L")
@param(QL=LENGTH, TooltipShort="QL")
@param(QW=LENGTH, TooltipShort="QW")
@param(QH=LENGTH, TooltipShort="QH")
@param(EX=LENGTH, TooltipShort="EX")
@param(EY=LENGTH, TooltipShort="EY")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPI002(s, D1=21.3, L=150.0, QL=100.0, QW=0.0, QH=0.0, EX=0.0, EY=0.0, OF=-1.0, ID='CPI002', **kw):
    if QW <= 0.0:
        QW = QL
    if QH <= 0.0:
        QH = QL
    R1 = D1 / 2.0
    EZ = L - (QH / 2.0)
    oA = BOX(s, L=QL, W=QW, H=QH).rotateY(90.0).translate((EX, EY, EZ))
    oB = CYLINDER(s, R=R1, H=L - QH, O=0.0)
    oA.uniteWith(oB)
    oB.erase()
    if OF == -1:
        OF = getThickness(D=D1, OF=OF)
    if OF > 0.0:
        oC = CYLINDER(s, R=R1 - OF, H=L - QH, O=0.0)
        oA.subtractFrom(oC)
        oC.erase()
    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
