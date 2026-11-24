# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="ValveActuator", TooltipShort="Box actuator", TooltipLong="Box actuator (Decompiled from varmain/valvsub/cpvxsub/cpvx064.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(L1=LENGTH, TooltipShort="L1")
@param(W=LENGTH, TooltipShort="W")
@param(H=LENGTH, TooltipShort="H")
@param(EX=LENGTH, TooltipShort="EX")
@param(EY=LENGTH, TooltipShort="EY")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX064(s, L=345.0, L1=200.0, W=150.0, H=100.0, EX=0.0, EY=0.0, ID='CPVX064', **kw):
    R = (W + H) / 30.0
    o1 = BOX(s, L=W, W=L1, H=H)
    o1.translate((EX, EY, L - (L1 / 2.0)))
    if (L - L1) > 0.0:
        o2 = CYLINDER(s, R=R, H=L - L1, O=0.0)
        o1.uniteWith(o2)
        o2.erase()
