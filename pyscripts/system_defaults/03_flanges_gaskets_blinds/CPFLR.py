# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpf_util import *


@activate(Group="Flange", TooltipShort="Built-in CPFLR", TooltipLong="Built-in CPFLR (Decompiled from varmain/flangesub/cpflr.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(ID=STRING, TooltipShort="组件标识")
def CPFLR(s, L=22.0, D1=220.0, D2=114.3, ID='CPFLR', **kw):
    o0 = (CYLINDER(s, R=D1 / 2.0, H=L, O=D2 / 2.0)).rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
    s.setPoint((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0)
