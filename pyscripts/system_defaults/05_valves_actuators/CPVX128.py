# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="ValveActuator", TooltipShort="Cone actuator", TooltipLong="Cone actuator (Decompiled from varmain/valvsub/cpvxsub/cpvx128.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(D=LENGTH, TooltipShort="D")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX128(s, L=345.0, D=225.0, ID='CPVX128', **kw):
    oC1 = ((CONE(s, R1=D / 2.0, R2=0.0, H=L)).rotateY(180)).translate((0, 0, L))
