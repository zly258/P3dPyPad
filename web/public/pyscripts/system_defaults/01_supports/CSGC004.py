# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
import math
from varmain.supportssub.csgcsub.csgc003 import *


@activate(Group="Support", TooltipShort="CSGC004", TooltipLong="CSGC004", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(H=LENGTH, TooltipShort="H")
@param(M1=LENGTH, TooltipShort="M1")
@param(M2=LENGTH, TooltipShort="M2")
@param(ID=STRING, TooltipShort="组件标识")
def CSGC004(s, D=116.0, L=30.0, W=4.0, K=0.0, H=95.0, M1=10.0, M2=0.0, ID='CSGC004', **kw):
    R1 = D / 2.0
    R2 = R1 + W
    H1 = H - M2
    if (H1 < (R2 + W)) or (M2 == 0.0):
        H1 = R2 + W
    KWdt = M1 * math.tan(aqa.math.asRadiants(30.0))
    H2 = H - H1
    o1a = BOX(s, L=M1, W=KWdt, H=H2).translate(((0.0 - (H2 / 2.0)) - H1, 0.0, 0.0))
    o1b = (BOX(s, L=M1, W=KWdt, H=H2).translate(((0.0 - (H2 / 2.0)) - H1, 0.0, 0.0))).rotateX(60.0)
    o1c = (BOX(s, L=M1, W=KWdt, H=H2).translate(((0.0 - (H2 / 2.0)) - H1, 0.0, 0.0))).rotateX(-60.0)
    o2 = (CSGC003(s, D=D, L=L, W=W, K=K, H=H1 - R1)).rotateY(-90)
    o1a.uniteWith(o1b)
    o1b.erase()
    o1a.uniteWith(o1c)
    o1c.erase()
    o1a.rotateZ(180.0)
    o1a.uniteWith(o2)
    o2.erase()
    o1a.rotateY(90)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('H', (0, 0, 0), (0, 0, -H))
