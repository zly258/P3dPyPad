# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpf_util import *


@activate(Group="Flange", TooltipShort="CP METRIC Flange blind", TooltipLong="CP METRIC Flange blind (Decompiled from varmain/flangesub/cpfbr.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(D=LENGTH, TooltipShort="D")
@param(ID=STRING, TooltipShort="组件标识")
def CPFBR(s, L=18.0, D=105.0, ID='CPFBR', **kw):
    o0 = (CYLINDER(s, R=D / 2.0, H=L, O=0.0)).rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
