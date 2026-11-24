# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="BleedRing", TooltipShort="Built-in CPMH", TooltipLong="Built-in CPMH (Decompiled from varmain/miscellaneoussub/cpmh.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(ILT=LENGTH, TooltipShort="ILT")
@param(IHT=LENGTH, TooltipShort="IHT")
@param(ILB=LENGTH, TooltipShort="ILB")
@param(IHB=LENGTH, TooltipShort="IHB")
@param(I1=LENGTH, TooltipShort="I1")
@param(I2=LENGTH, TooltipShort="I2")
@param(ID=STRING, TooltipShort="组件标识")
def CPMH(s, L=54.0, D1=158.0, D2=114.3, ILT=0.0, IHT=0.0, ILB=0.0, IHB=0.0, I1=10.0, I2=10.0, ID='CPMH', **kw):
    if IHT <= 0.0:
        IHT = L / 2.0
    if ILT <= 0.0:
        ILT = L / 2.0
    usePort4 = False
    if ((IHB > -2) and (ILB > -2)) and (I2 > -2):
        if IHB <= 0.0:
            IHB = L / 2.0
        if ILB <= 0.0:
            ILB = L / 2.0
        usePort4 = True
    O = D2 / 2.0
    o0 = (CYLINDER(s, R=D1 / 2.0, H=L, O=O)).rotateY(90)
    tL = (D1 - D2) / 4.0
    o3 = (CONE(s, R1=IHT / 4.0, R2=IHT / 2.0, H=tL, E=0)).translate((ILT, 0.0, (D2 / 2.0) + tL))
    o4 = (CYLINDER(s, R=IHT / 4.0, H=(D2 / 2.0) + tL, O=0.0)).translate((ILT, 0.0, 0.0))
    o3.uniteWith(o4)
    o4.erase()
    if usePort4:
        bL = (D1 - D2) / 4.0
        o5 = ((CONE(s, R1=IHB / 4.0, R2=IHB / 2.0, H=bL, E=0)).rotateX(180)).translate((ILB, 0.0, (D1 / -2.0) + bL))
        o6 = ((CYLINDER(s, R=IHB / 4.0, H=(D2 / 2.0) + bL, O=0.0)).rotateX(180)).translate((ILB, 0.0, 0.0))
        o5.uniteWith(o6)
        o6.erase()
    o2 = CYLINDER(s, R=O, H=L, O=0.0).rotateY(90).translate((L, 0, 0))
    o0.subtractFrom(o2)
    o2.erase()
    o0.subtractFrom(o3)
    o3.erase()
    if usePort4:
        o0.subtractFrom(o5)
        o5.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((L, 0, 0), (1, 0, 0))
    s.setPoint((ILT, 0.0, (D1 / 2.0) - I1), (0, 0, 1))
    if usePort4:
        s.setPoint((ILB, 0.0, (D1 / -2.0) + I2), (0, 0, -1))
