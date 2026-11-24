# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Support", TooltipShort="CSGH002", TooltipLong="CSGH002", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(H=LENGTH, TooltipShort="H")
@param(W=LENGTH, TooltipShort="W")
@param(HL2=LENGTH, TooltipShort="HL2")
@param(HL21=LENGTH, TooltipShort="HL21")
@param(HL22=LENGTH, TooltipShort="HL22")
@param(HD21=LENGTH, TooltipShort="HD21")
@param(HD3=LENGTH, TooltipShort="HD3")
@param(HT4=LENGTH, TooltipShort="HT4")
@param(HL4=LENGTH, TooltipShort="HL4")
@param(HW4=LENGTH, TooltipShort="HW4")
@param(HH4=LENGTH, TooltipShort="HH4")
@param(ID=STRING, TooltipShort="组件标识")
def CSGH002(s, D=116.0, H=500.0, W=4.0, HL2=0.0, HL21=0.0, HL22=0.0, HD21=0.0, HD3=0.0, HT4=0.0, HL4=0.0, HW4=0.0, HH4=0.0, ID='CSGH002', **kw):
    R1 = D / 2.0
    R2 = R1 + W
    W1 = W * 3.0
    oVal = W / 10.0
    if HL2 <= 0.0:
        HL2 = (H - R1) / 2.0
    if HD21 <= 0.0:
        HD21 = D * 0.66666666
    if HL21 <= 0.0:
        HL21 = (HL2 - R1) * 0.66666666
    if HL22 <= 0.0:
        HL22 = (HL2 - R1) * 0.15
    if HD3 <= 0.0:
        HD3 = D / 10.0
    mR1 = R1 + W
    mR2 = HD21 / 2.0
    o0a = ((CYLINDER(s, R=mR1, H=mR1 * 2.0, O=0.0)).rotateX(90.0)).translate((0.0, mR1, 0.0))
    o0b = SPHERE(s, R=mR1)
    o0c = (CYLINDER(s, R=mR1, H=HL2 - HL21, O=0.0)).rotateX(-90.0)
    o0d = ((CYLINDER(s, R=R1, H=mR1 * 4.0, O=0.0)).rotateZ(90.0)).translate((0.0, 0.0, -(mR1 * 2.0)))
    o0e = ((CONE(s, R1=mR1, R2=mR2, H=HL21 - HL22, E=0.0)).rotateX(-90.0)).translate((0.0, HL2 - HL21, 0.0))
    xH = HL22 / 3.0
    o0f = CYLINDER(s, R=mR2, H=xH, O=0.0).rotateX(90.0).translate((0.0, HL2 - (xH * 2.0), 0.0))
    o0g = CYLINDER(s, R=mR2, H=xH, O=0.0).rotateX(90.0).translate((0.0, HL2, 0.0))
    cL3 = H - R1
    o3 = ((CYLINDER(s, R=HD3 / 2.0, H=cL3, O=0.0)).rotateX(-90.0)).translate((0.0, R1, 0.0))
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
    o0a.intersectWith(o0b)
    o0b.erase()
    o0a.uniteWith(o0c)
    o0c.erase()
    o0a.uniteWith(o0e)
    o0e.erase()
    o0a.uniteWith(o0f)
    o0f.erase()
    o0a.uniteWith(o0g)
    o0g.erase()
    o0a.uniteWith(o4d)
    o4d.erase()
    o0a.uniteWith(o4c)
    o4c.erase()
    o0a.uniteWith(o4b)
    o4b.erase()
    o0a.uniteWith(o4a)
    o4a.erase()
    o0a.uniteWith(o3)
    o3.erase()
    o0a.subtractFrom(o0d)
    o0d.erase()
    o0a.rotateZ(90.0)
    s.setPoint((0, 0, 0), (0, 0, 1))
    s.setLinearDimension('H', (0, 0, 0), (-H, 0, 0))
