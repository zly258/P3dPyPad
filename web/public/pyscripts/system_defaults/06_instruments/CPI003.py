# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Instrument", TooltipShort="Built-in CPI003", TooltipLong="Built-in CPI003 (Decompiled from varmain/instrsub/cpi003sub/cpi003.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(L1=LENGTH, TooltipShort="L1")
@param(EX=LENGTH, TooltipShort="EX")
@param(EY=LENGTH, TooltipShort="EY")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPI003(s, D1=21.3, D2=100.0, L=150.0, L1=50.0, EX=0.0, EY=0.0, OF=-1.0, ID='CPI003', **kw):
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    oA = CYLINDER(s, R=R2, H=L1, O=0.0).translate((EX, EY, L - L1))
    o2 = CYLINDER(s, R=R1, H=L - L1, O=0.0)
    oA.uniteWith(o2)
    o2.erase()
    if OF == -1:
        OF = getThickness(D=D1, OF=OF)
    if OF != 0.0:
        oC = CYLINDER(s, R=R1 - OF, H=L - L1, O=0.0)
        oA.subtractFrom(oC)
        oC.erase()
    s.setPoint((0, 0, 0), (0, 0, -1))
