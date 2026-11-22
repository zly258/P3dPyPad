# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Support", TooltipShort="CSGC005", TooltipLong="CSGC005", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K1=LENGTH, TooltipShort="K1")
@param(K2=LENGTH, TooltipShort="K2")
@param(ID=STRING, TooltipShort="组件标识")
def CSGC005(s, D=116.0, L=30.0, W=4.0, K1=0.0, K2=0.0, ID='CSGC005', **kw):
    R1 = D / 2.0
    R2 = R1 + W
    if K1 <= 0.0:
        K1 = R1 + L
    if K2 <= 0.0:
        K2 = K1 + L
    K = K1 + K2
    o1 = CYLINDER(s, R=R2, H=L, O=0.0).translate((0, 0, -(L / 2.0)))
    o2 = (BOX(s, L=K, W=L, H=W * 3.0)).translate((0.0, (K2 - K1) / 2.0, 0.0))
    o3 = CYLINDER(s, R=R1, H=L, O=0.0).translate((0, 0, -(L / 2.0)))
    o4 = BOX(s, L=K, W=L, H=W).translate((0.0, (K2 - K1) / 2.0, 0.0))
    o1.uniteWith(o2)
    o2.erase()
    o3.uniteWith(o4)
    o4.erase()
    o1.subtractFrom(o3)
    o3.erase()
    o1.rotateY(90)
    s.setPoint((0, 0, 0), (-1, 0, 0))
