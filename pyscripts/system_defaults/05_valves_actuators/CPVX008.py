# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="ValveActuator", TooltipShort="L-Lever", TooltipLong="L-Lever (Decompiled from varmain/valvsub/cpvxsub/cpvx008.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(H=LENGTH, TooltipShort="H")
@param(DO=LENGTH, TooltipShort="DO")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX008(s, L=225.0, H=345.0, DO=0.0, ID='CPVX008', **kw):
    if DO <= 0.0:
        DO = (L + H) / 50.0
    L1 = (DO * 20.0) / 15.0
    L2 = DO
    H1 = H - L1
    o1 = ((((BOX(s, L=L + (L1 / 2.0), W=L1, H=L1)).rotateX(-90)).rotateY(-90)).translate(((L + (L1 / 2.0)) / 2.0, L1 / 2.0, L1 / 2.0))).translate((-L1 / 2.0, -L1 / 2.0, H1))
    if H1 > 0.0:
        o2 = (BOX(s, L=L2, W=L2, H=H1).rotateX(-90).rotateY(-90).translate((L2 / 2.0, L2 / 2.0, H1 / 2.0))).translate((-L2 / 2.0, -L2 / 2.0, 0))
        o1.uniteWith(o2)
        o2.erase()
