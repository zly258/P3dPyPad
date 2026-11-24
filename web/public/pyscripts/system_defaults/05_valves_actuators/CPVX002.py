# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="ValveActuator", TooltipShort="Hand Wheel", TooltipLong="Hand Wheel (Decompiled from varmain/valvsub/cpvxsub/cpvx002.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX002(s, D=225.0, L=345.0, ID='CPVX002', **kw):
    R1 = D / 30.0
    R2 = D / 40.0
    R3 = (D / 2.0) - R1
    L = L - R1
    oT0 = TORUS(s, R1=R3, R2=R1).translate((0, 0, L))
    oC1 = (((CYLINDER(s, R=R2, H=R3 * 2, O=0.0)).rotateX(90)).translate((0, R3, L))).rotateZ(45)
    oC2 = (((CYLINDER(s, R=R2, H=R3 * 2, O=0.0)).rotateY(90)).translate((-R3, 0, L))).rotateZ(45)
    oC3 = CYLINDER(s, R=R2, H=L, O=0.0)
    oC4 = SPHERE(s, R=R2)
    oC1.uniteWith(oC2)
    oC2.erase()
    oC1.uniteWith(oC3)
    oC3.erase()
    oC1.uniteWith(oC4)
    oC4.erase()
    oC1.uniteWith(oT0)
    oT0.erase()
