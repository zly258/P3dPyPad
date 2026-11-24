# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="ValveActuator", TooltipShort="Ice cone like actuator", TooltipLong="Ice cone like actuator (Decompiled from varmain/valvsub/cpvxsub/cpvx512.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(D=LENGTH, TooltipShort="D")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX512(s, L=345.0, D=225.0, ID='CPVX512', **kw):
    oTH = ELLIPSOIDHEAD(s, R=D / 2.0)
    vT = oTH.parameters()
    vTH = vT['H']
    oTH.translate((0, 0, L - vTH))
    oC1 = ((CONE(s, R1=D / 2.0, R2=0.0, H=L - vTH)).rotateY(180)).translate((0, 0, L - vTH))
    oTH.uniteWith(oC1)
    oC1.erase()
