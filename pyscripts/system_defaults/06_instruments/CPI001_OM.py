# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.instrsub.cpi001sub.cpi001 import *


@activate(Group="Instrument", TooltipShort="PRESSURE GAUGE, MPT", TooltipLong="PRESSURE GAUGE, MPT (Decompiled from varmain/instrsub/cpi001sub/cpi001_om.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(EX=LENGTH, TooltipShort="EX")
@param(EY=LENGTH, TooltipShort="EY")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPI001_OM(s, D1=17.2, D2=139.0, L=191.0, L1=86.0, L2=15.2552, EX=0.0, EY=0.0, OF=-1.0, ID='CPI001_OM', **kw):
    if OF == -1:
        OF = getThickness(D=D1, OF=OF)
    oA = (CPI001(s, D1=D1, D2=D2, L=L - L2, L1=L1, EX=EX, EY=EX)).translate((0.0, 0.0, L2))
    oB = CON_OM(s, D1=D1, D2=0.0, L=L2, OF=OF).rotateY(90.0).translate((0.0, 0.0, L2))
    oG = (CYLINDER(s, R=D1 * 0.01, H=D1 * 0.01, O=0.0)).translate((0.0, 0.0, L - (D2 / 2.0)))
    oG.uniteWith(oA)
    oA.erase()
    oG.uniteWith(oB)
    oB.erase()
    s.setPoint((0, 0, 0), (0, 0, -1))
