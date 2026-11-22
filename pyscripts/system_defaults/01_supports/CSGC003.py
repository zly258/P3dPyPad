# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgcsub.csgc002 import *


@activate(Group="Support", TooltipShort="CSGC003", TooltipLong="CSGC003", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(H=LENGTH, TooltipShort="H")
@param(ID=STRING, TooltipShort="组件标识")
def CSGC003(s, D=116.0, L=30.0, W=4.0, K=0.0, H=0.0, ID='CSGC003', **kw):
    R1 = D / 2.0
    R2 = R1 + W
    if H == 0.0:
        H = W * 2.0
    H1 = R1 + H
    o1 = BOX(s, L=L, W=L, H=H1).translate((0.0 - (H1 / 2.0), 0.0, 0.0))
    o2 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90)
    o3 = CYLINDER(s, R=R1, H=L, O=0.0).translate((0, 0, -(L / 2.0)))
    o4 = (BOX(s, L=L - (W * 2.0), W=L, H=H1 - W)).translate((0.0 - ((H1 - W) / 2.0), 0.0, 0.0))
    o1.uniteWith(o2)
    o2.erase()
    o3.uniteWith(o4)
    o4.erase()
    o1.subtractFrom(o3)
    o3.erase()
    o1.rotateZ(180.0)
    o1.rotateY(90)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('H', (0, 0, -D / 2.0), (0, 0, -H - (D / 2.0)))
