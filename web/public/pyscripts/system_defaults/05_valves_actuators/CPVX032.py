# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="ValveActuator", TooltipShort="Hor. Cylinder actuator", TooltipLong="Hor. Cylinder actuator (Decompiled from varmain/valvsub/cpvxsub/cpvx032.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(L1=LENGTH, TooltipShort="L1")
@param(EX=LENGTH, TooltipShort="EX")
@param(EY=LENGTH, TooltipShort="EY")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX032(s, D=225.0, L=345.0, L1=200.0, EX=0.0, EY=0.0, ID='CPVX032', **kw):
    if D <= 0.0:
        D = L * 0.6666
    R = D / 20.0
    R1 = D / 2.0
    o1 = CYLINDER(s, R=R1, H=L1, O=0.0).rotateY(90).translate((-L1 / 2.0, 0, 0))
    o1.translate((EX, EY, L - R1))
    if (L - D) > 0.0:
        o2 = CYLINDER(s, R=R, H=L - R1, O=0.0)
        o1.uniteWith(o2)
        o2.erase()
