# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpf_util import *


@activate(Group="Flange", TooltipShort="Built-in CPFBO", TooltipLong="Built-in CPFBO (Decompiled from varmain/flangesub/cpfbo.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(D=LENGTH, TooltipShort="D")
@param(W=LENGTH, TooltipShort="W")
@param(ID=STRING, TooltipShort="组件标识")
def CPFBO(s, L=22.0, D=220.0, W=120.0, ID='CPFBO', **kw):
    if W <= 0.0:
        OF = getThickness(D=D, OF=-1, Ever=1, mustCalc=True)
        W = D + (OF * 2.0)
    o0 = (CYLINDER(s, R1=W / 2.0, R2=D / 2.0, H=L, O=0.0)).rotateY(90)
    if D < W:
        WA = 90.0
    else:
        WA = 0.0
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), WA)
