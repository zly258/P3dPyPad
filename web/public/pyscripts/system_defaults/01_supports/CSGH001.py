# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgcsub.csgc002 import *


@activate(Group="Support", TooltipShort="CSGH001", TooltipLong="CSGH001", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(H=LENGTH, TooltipShort="H")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(HL1=LENGTH, TooltipShort="HL1")
@param(HL2=LENGTH, TooltipShort="HL2")
@param(HL21=LENGTH, TooltipShort="HL21")
@param(HL22=LENGTH, TooltipShort="HL22")
@param(HD21=LENGTH, TooltipShort="HD21")
@param(HD22=LENGTH, TooltipShort="HD22")
@param(HD3=LENGTH, TooltipShort="HD3")
@param(HT4=LENGTH, TooltipShort="HT4")
@param(HL4=LENGTH, TooltipShort="HL4")
@param(HW4=LENGTH, TooltipShort="HW4")
@param(HH4=LENGTH, TooltipShort="HH4")
@param(ID=STRING, TooltipShort="组件标识")
def CSGH001(s, D=116.0, H=500.0, L=30.0, W=4.0, K=0.0, HL1=0.0, HL2=0.0, HL21=0.0, HL22=0.0, HD21=0.0, HD22=0.0, HD3=0.0, HT4=0.0, HL4=0.0, HW4=0.0, HH4=0.0, ID='CSGH001', **kw):
    R1 = D / 2.0
    R2 = R1 + W
    if K <= 0.0:
        K = D + (L * 2.0)
    SL = L - R1
    W1 = W * 3.0
    L1 = (K - D) / 2.0
    oVal = W / 10.0
    if HL1 <= 0.0:
        HL1 = (H - R1) / 5.0
    if HL2 <= 0.0:
        HL2 = (H - R1) / 3.0
    if HD21 <= 0.0:
        HD21 = D
    if HD3 <= 0.0:
        HD3 = D / 10.0
    o0 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90)
    xL1 = ((HL1 - L1) + W) - oVal
    xL2 = HL1 - oVal
    o1a = BOX(s, L=xL1, W=L, H=W).translate((W, (((xL1 / 2.0) + R1) + L1) + oVal, 0.0))
    o1b = (BOX(s, L=xL2, W=L - (oVal * 2.0), H=W)).translate((0.0, (((xL2 / 2.0) + R1) + W) + oVal, 0.0))
    o1c = BOX(s, L=xL1, W=L, H=W).translate((-W, (((xL1 / 2.0) + R1) + L1) + oVal, 0.0))
    cR1 = ((sqrt(pow(W1, 2.0) + pow(L, 2.0))) / 2.0) + oVal
    if HL21 <= 0.0:
        HL21 = (HD21 / 2.0) - cR1
    if HL22 <= 0.0:
        HL22 = HL2 / 10.0
    if HD22 <= 0.0:
        HD22 = HD21 * 1.2
    cR2 = HD21 / 2.0
    cR3 = HD22 / 2.0
    o2a = CONE(s, R1=cR1, R2=cR2, H=HL21, E=0.0).rotateX(-90.0).translate((0.0, (R1 + W) + HL1, 0.0))
    o2b = ((CYLINDER(s, R=cR2, H=(HL2 - HL21) - HL22, O=0.0)).rotateX(-90.0)).translate((0.0, ((R1 + W) + HL1) + HL21, 0.0))
    o2c = CYLINDER(s, R=cR3, H=HL22, O=0.0).rotateX(90.0).translate((0.0, ((R1 + W) + HL1) + HL2, 0.0))
    cL3 = (((H - R1) - W) - HL1) - HL2
    o3 = ((CYLINDER(s, R=HD3 / 2.0, H=cL3, O=0.0)).rotateX(-90.0)).translate((0.0, ((R1 + W) + HL1) + HL2, 0.0))
    if HT4 <= 0.0:
        HT4 = W
    if HL4 <= 0.0:
        HL4 = HD3 + (HT4 * 3.0)
    if HW4 <= 0.0:
        HW4 = HD3
    if HH4 <= 0.0:
        HH4 = HD3
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
    o2c.uniteWith(o2b)
    o2b.erase()
    o2c.uniteWith(o2a)
    o2a.erase()
    o1c.uniteWith(o1b)
    o1b.erase()
    o1c.uniteWith(o1a)
    o1a.erase()
    o4d.uniteWith(o3)
    o3.erase()
    o4d.uniteWith(o2c)
    o2c.erase()
    o4d.uniteWith(o1c)
    o1c.erase()
    o4d.uniteWith(o0)
    o0.erase()
    o4d.rotateZ(90.0)
    s.setPoint((0, 0, 0), (0, 0, 1))
    s.setLinearDimension('H', (0, 0, 0), (-H, 0, 0))
