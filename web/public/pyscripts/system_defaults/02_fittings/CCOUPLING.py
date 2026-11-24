# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Coupling", TooltipShort="CP METRIC Coupling", TooltipLong="CP METRIC Coupling (Decompiled from varmain/couplingsub/ccoupling.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(I1=LENGTH, TooltipShort="I1")
@param(I2=LENGTH, TooltipShort="I2")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CCOUPLING(s, D=1016.0, L=610.0, I1=152.5, I2=152.5, OF=-1.0, ID='CCOUPLING', **kw):
    OF = getThickness(D=D, OF=OF, Ever=1)
    sF = getThickness(D=D, OF=OF, Ever=1, mustCalc=True)
    DO = D + (sF * 2.0)
    RI = 0.0
    if OF > 0.0:
        RI = D / 2.0
    oTH = (CYLINDER(s, R=DO / 2.0, H=L, O=RI)).rotateY(90.0)
    s.setPoint((I1, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
    s.setPoint((L - I2, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0)
