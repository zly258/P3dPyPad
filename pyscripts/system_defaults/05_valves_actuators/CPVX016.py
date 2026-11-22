# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="ValveActuator", TooltipShort="Vert. Cylinder actuator", TooltipLong="Vert. Cylinder actuator (Decompiled from varmain/valvsub/cpvxsub/cpvx016.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(L1=LENGTH, TooltipShort="L1")
@param(EX=LENGTH, TooltipShort="EX")
@param(EY=LENGTH, TooltipShort="EY")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX016(s, D=225.0, L=345.0, L1=200.0, EX=0.0, EY=0.0, ID='CPVX016', **kw):
    R = D / 20.0
    if L1 <= 0.0:
        L1 = L * 0.6666
    o1 = (CYLINDER(s, R=D / 2.0, H=L1, O=0.0)).translate((EX, EY, L - L1))
    if (L - L1) > 0.0:
        o2 = CYLINDER(s, R=R, H=L - L1, O=0.0)
        o1.uniteWith(o2)
        o2.erase()
