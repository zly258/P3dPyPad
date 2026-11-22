# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cnut6_001 import *
from varmain.supportssub.csgcsub.csgc002 import *


@activate(Group="Support", TooltipShort="CSGH003", TooltipLong="CSGH003", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(H=LENGTH, TooltipShort="H")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(HD3=LENGTH, TooltipShort="HD3")
@param(HT4=LENGTH, TooltipShort="HT4")
@param(HL4=LENGTH, TooltipShort="HL4")
@param(HW4=LENGTH, TooltipShort="HW4")
@param(HH4=LENGTH, TooltipShort="HH4")
@param(ID=STRING, TooltipShort="组件标识")
def CSGH003(s, D=116.0, H=500.0, L=30.0, W=4.0, K=0.0, HD3=0.0, HT4=0.0, HL4=0.0, HW4=0.0, HH4=0.0, ID='CSGH003', **kw):
    R1 = D / 2.0
    R2 = R1 + W
    if K <= 0.0:
        K = D + (L * 2.0)
    SL = L - R1
    W1 = W * 3.0
    L1 = (K - D) / 2.0
    oVal = W / 10.0
    if HD3 <= 0.0:
        HD3 = D / 10.0
    if HT4 <= 0.0:
        HT4 = W
    if HL4 <= 0.0:
        HL4 = HD3 + (HT4 * 3.0)
    if HW4 <= 0.0:
        HW4 = HD3
    if HH4 <= 0.0:
        HH4 = HD3
    o0 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90)
    o1 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(90.0).rotateX(90.0).translate((0.0, HD3 + (K / 2.0), 0.0))
    o2 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(-90.0).rotateX(90.0).translate((0.0, (H - HD3) - HH4, 0.0))
    cL3 = (H - R1) - W
    o3 = ((CYLINDER(s, R=HD3 / 2.0, H=cL3, O=0.0)).rotateX(-90.0)).translate((0.0, R1 + W, 0.0))
    xL1 = HL4 + (HT4 * 2.0)
    xH1 = (H - ((HH4 - HT4) / 2.0)) - HT4
    o4a = BOX(s, L=HH4, W=HW4, H=HT4).translate(((HL4 / 2.0) - (HT4 / 2.0), H - (HH4 / 2.0), 0.0))
    o4b = BOX(s, L=HH4, W=HW4, H=HT4).translate((-((HL4 / 2.0) - (HT4 / 2.0)), H - (HH4 / 2.0), 0.0))
    o4c = BOX(s, L=HT4, W=HW4, H=HL4).translate((0.0, H - (HT4 / 2.0), 0.0))
    o4d = CYLINDER(s, R=HT4, H=xL1, O=0.0).rotateY(-90.0).translate((xL1 / 2.0, xH1, 0.0))
    o4d.uniteWith(o4c)
    o4c.erase()
    o4d.uniteWith(o4b)
    o4b.erase()
    o4d.uniteWith(o4a)
    o4a.erase()
    o4d.uniteWith(o3)
    o3.erase()
    o4d.uniteWith(o2)
    o2.erase()
    o4d.uniteWith(o1)
    o1.erase()
    o4d.uniteWith(o0)
    o0.erase()
    o4d.rotateZ(90.0)
    s.setPoint((0, 0, 0), (0, 0, 1))
    s.setLinearDimension('H', (0, 0, 0), (-H, 0, 0))
