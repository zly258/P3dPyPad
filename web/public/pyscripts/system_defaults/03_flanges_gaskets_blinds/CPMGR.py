# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.gasketsub.cpmg_util import *


@activate(Group="Gasket", TooltipShort="Built-in CPMGR", TooltipLong="Built-in CPMGR (Decompiled from varmain/gasketsub/cpmgr.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(ID=STRING, TooltipShort="组件标识")
def CPMGR(s, D1=6.0, D2=114.3, ID='CPMGR', **kw):
    oTH = ((TORUS(s, R1=(D1 / 2.0) + (D2 / 2.0), R2=D1 / 2.0)).rotateY(90.0)).translate((D1 / 2.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
    s.setPoint((D1, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0)
