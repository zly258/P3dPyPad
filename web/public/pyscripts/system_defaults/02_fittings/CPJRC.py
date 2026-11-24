# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Reducer", TooltipShort="CP METRIC Reducer conc.", TooltipLong="CP METRIC Reducer conc. (Decompiled from varmain/reducersub/cpjrcsub/cpjrc.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPJRC(s, D1=1016.0, D2=508.0, L=610.0, OF=-1.0, ID='CPJRC', **kw):
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    OF = getThickness(D1, OF=OF)
    o0 = CONE(s, R1=R1, R2=R2, H=L, E=0.0).rotateY(90)
    Drill = 1
    if OF > 0.0:
        sR1 = R1 - OF
        sR2 = R2 - OF
    else:
        if OF == -1:
            sR1 = getInsideDiameter(D1, OF=OF, Ever=None) / 2.0
            sR2 = getInsideDiameter(D2, OF=OF, Ever=None) / 2.0
        else:
            Drill = None
    if Drill:
        o1 = CONE(s, R1=sR1, R2=sR2, H=L, E=0.0).rotateY(90)
        o0.subtractFrom(o1)
        o1.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((L, 0, 0), (1, 0, 0))
