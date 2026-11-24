# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Collar", TooltipShort="CP METRIC Collar", TooltipLong="CP METRIC Collar (Decompiled from varmain/miscellaneoussub/cpmu_.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(B=LENGTH, TooltipShort="B")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(I=LENGTH, TooltipShort="I")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPMU_(s, B=46.181818, D1=1108.363636, D2=1016.0, I=11.545455, OF=-1.0, ID='CPMU_', **kw):
    if (I <= 0.0) and (OF <= 0.0):
        I = getThickness(D=D2, OF=I, Ever=1)
    else:
        if OF > 0.0:
            I = OF
    o0 = (CYLINDER(s, R=D1 / 2.0, H=B, O=D2 / 2.0)).rotateY(90)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((I, 0, 0), (1, 0, 0))


@activate(Group="Collar", TooltipShort="CP METRIC Collar", TooltipLong="CP METRIC Collar (Decompiled from varmain/miscellaneoussub/cpmu_.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(B=LENGTH, TooltipShort="B")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPMU(s, B=18.0, D1=158.0, D2=114.3, OF=-1.0, ID='CPMU', **kw):
    OF = getThickness(D=D2, OF=OF, Ever=1)
    o0 = (CYLINDER(s, R=D1 / 2.0, H=B, O=D2 / 2.0)).rotateY(90)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((OF, 0, 0), (1, 0, 0))
