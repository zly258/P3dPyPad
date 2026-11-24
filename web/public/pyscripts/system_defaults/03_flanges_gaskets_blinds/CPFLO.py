# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpf_util import *


@activate(Group="Flange", TooltipShort="Built-in CPFLO", TooltipLong="Built-in CPFLO (Decompiled from varmain/flangesub/cpflo.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(W=LENGTH, TooltipShort="W")
@param(ID=STRING, TooltipShort="组件标识")
def CPFLO(s, L=22.0, D1=220.0, D2=114.3, W=0.0, ID='CPFLO', **kw):
    if (W <= 0.0) or (W < D2):
        OF = getThickness(D=D2, OF=-1, Ever=1, mustCalc=True)
        W = D2 + (OF * 2.0)
    o0 = (CYLINDER(s, R1=W / 2.0, R2=D1 / 2.0, H=L, O=0.0)).rotateY(90)
    if D2 > 0.0:
        ow = (CYLINDER(s, R=D2 / 2.0, H=L, O=0.0)).rotateY(90)
        o0.subtractFrom(ow)
        ow.erase()
    if D1 < W:
        WA = 90.0
    else:
        WA = 0.0
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), W)
    s.setPoint((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), W)
