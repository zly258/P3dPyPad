# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Coupling", TooltipShort="Built-in CPJB", TooltipLong="Built-in CPJB (Decompiled from varmain/couplingsub/cpjb.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPJB(s, D1=114.3, D2=0.0, L=100.0, OF=-1.0, ID='CPJB', **kw):
    if D2 <= 0.0:
        D2 = D1
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    OF = getThickness(D1, OF=OF)
    if areEqual(R1, R2):
        o0 = CYLINDER(s, R=R1, H=L, O=0.0).rotateY(90.0)
    else:
        if R1 > R2:
            o0 = CONE(s, R1=R1, R2=R2, H=L, E=0.0).rotateY(90)
        else:
            o0 = CONE(s, R1=R2, R2=R1, H=L, E=0.0).rotateY(-90).translate((L, 0.0, 0.0))
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
        if areEqual(sR1, sR2):
            o1 = CYLINDER(s, R=sR1, H=L, O=0.0).rotateY(90.0)
        else:
            if R1 > R2:
                o1 = CONE(s, R1=sR1, R2=sR2, H=L, E=0.0).rotateY(90)
            else:
                o1 = CONE(s, R1=sR2, R2=sR1, H=L, E=0.0).rotateY(-90).translate((L, 0.0, 0.0))
        o0.subtractFrom(o1)
        o1.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((L, 0, 0), (1, 0, 0))
