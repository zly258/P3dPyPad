# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.gasketsub.cpmg_util import *


@activate(Group="Gasket", TooltipShort="Built-in CPMGO", TooltipLong="Built-in CPMGO (Decompiled from varmain/gasketsub/cpmgo.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(W=LENGTH, TooltipShort="W")
@param(L=LENGTH, TooltipShort="L")
@param(ID=STRING, TooltipShort="组件标识")
def CPMGO(s, D1=220.0, D2=114.3, W=0.0, L=3.0, ID='CPMGO', **kw):
    if W > D1:
        xW = D1
        D1 = W
        W = xW
    else:
        if W <= 0.0:
            OF = getThickness(D=D2, OF=-1, Ever=1)
            W = D2 + (OF * 2.0)
    oTH = (CYLINDER(s, R1=W / 2.0, R2=D1 / 2.0, H=L, O=0.0)).rotateY(90.0)
    oTw = (CYLINDER(s, R=D2 / 2.0, H=L, O=0.0)).rotateY(90.0)
    oTH.subtractFrom(oTw)
    oTw.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0)
