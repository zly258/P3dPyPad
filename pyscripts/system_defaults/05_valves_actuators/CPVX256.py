# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="ValveActuator", TooltipShort="Pyramid actuator", TooltipLong="Pyramid actuator (Decompiled from varmain/valvsub/cpvxsub/cpvx256.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(L1=LENGTH, TooltipShort="L1")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX256(s, L=345.0, W=225.0, L1=275.0, ID='CPVX256', **kw):
    oC1 = PYRAMID(s, L=W, W=L1, H=L).rotateY(180).translate((0, 0, L))
