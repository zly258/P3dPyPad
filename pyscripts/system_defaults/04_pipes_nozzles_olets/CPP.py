# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.pipesub.cpp_util import *


@activate(Group="Pipe", TooltipShort="CP METRIC Pipe", TooltipLong="CP METRIC Pipe (Decompiled from varmain/pipesub/cpp.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPP(s, D=10.2, L=100.0, OF=-1.0, ID='CPP', **kw):
    if L == 0.0:
        L = defaultPipeLength
    DI = getInsideDiameter(D=D, OF=OF)
    if L > 0:
        oTH = (CYLINDER(s, R=D / 2.0, H=L, O=DI / 2.0)).rotateY(90.0)
    else:
        L = -L
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0)
