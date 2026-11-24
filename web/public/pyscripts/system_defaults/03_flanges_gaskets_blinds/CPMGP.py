# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.gasketsub.cpmg_util import *


@activate(Group="Gasket", TooltipShort="CP METRIC Gasket", TooltipLong="CP METRIC Gasket (Decompiled from varmain/gasketsub/cpmgp.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(ID=STRING, TooltipShort="组件标识")
def CPMGP(s, D1=1049.5, D2=914.0, L=6.75, ID='CPMGP', **kw):
    oTH = (CYLINDER(s, R=D1 / 2.0, H=L, O=D2 / 2.0)).rotateY(90.0)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0))
