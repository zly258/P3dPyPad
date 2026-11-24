# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Support", TooltipShort="CSGPRIM", TooltipLong="CSGPRIM", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(ID=STRING, TooltipShort="组件标识")
def CSGPRIM(s, D=114.3, L=50.0, W=2.0, ID='CSGPRIM', **kw):
    R1 = D / 2.0
    R2 = R1 + W
    o1 = CYLINDER(s, R=R2, H=L, O=R1).translate((0, 0, -(L / 2.0)))
    s.setPoint((0, 0, 0), (0, 0, -1))
