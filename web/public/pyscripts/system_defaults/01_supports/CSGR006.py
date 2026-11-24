# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgrsub.csgr005 import *


@activate(Group="Support", TooltipShort="CSGR006", TooltipLong="CSGR006", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(BW=LENGTH, TooltipShort="BW")
@param(BH=LENGTH, TooltipShort="BH")
@param(RD=LENGTH, TooltipShort="RD")
@param(RL=LENGTH, TooltipShort="RL")
@param(RDI=LENGTH, TooltipShort="RDI")
@param(RLI=LENGTH, TooltipShort="RLI")
@param(RTYPE=INT, TooltipShort="RTYPE")
@param(H=LENGTH, TooltipShort="H")
@param(HD3=LENGTH, TooltipShort="HD3")
@param(HS=LENGTH, TooltipShort="HS")
@param(HO=LENGTH, TooltipShort="HO")
@param(HB=LENGTH, TooltipShort="HB")
@param(DOUBROLL=INT, TooltipShort="DOUBROLL")
@param(SD=LENGTH, TooltipShort="SD")
@param(test=LENGTH, TooltipShort="test")
@param(ID=STRING, TooltipShort="组件标识")
def CSGR006(s, D=116.0, BW=220.0, BH=0.0, RD=80.0, RL=150.0, RDI=0.0, RLI=50.0, RTYPE=0, H=230.0, HD3=0.0, HS=10.0, HO=0.0, HB=0.0, DOUBROLL=0, SD=0.0, test=False, ID='CSGR006', **kw):
    R1, R2, R3, RC, RD, RDI, RLI, LM = CSGR000_util(D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE)
    if BH <= 0.0:
        BH = R2
    if HB <= 0.0:
        HB = ((BW - RL) / 2.0) + RL
    if HD3 <= 0.0:
        HD3 = RDI * 0.5
    rD = HD3
    o1 = CSGR005(s, D=D, BW=BW, BH=BH, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE, H=H, HD3=HD3, HS=HS, HO=HO, HB=HB, DOUBROLL=DOUBROLL, test=test, doAllNuts=False)
    if SD <= 0.0:
        SD = HD3 * 4.0
    bD = SD / 2.0
    sX = (H - RC) - BH
    sIP = -RC - BH
    bPY = [-(HB / 2.0), HB / 2.0]
    o0 = ((CYLINDER(s, R=rD * 0.01, H=rD * 0.01, O=0.0)).rotateX(180.0)).translate((0.0, bPY[0], -RC))
    shL = bD * 0.25
    bDI = bD * 0.9
    sX2 = sX - (shL * 2.0)
    dd = 3
    while (sX2 / dd) > (bDI / 2.0):
        dd += 3
    ssD = sX2 / dd
    for pY in bPY:
        o2 = CYLINDER(s, R=bD, H=shL, O=0.0).rotateX(180.0).translate((0.0, pY, sIP))
        sNP = sIP - shL
        for i in range(dd):
            o3 = (TORUS(s, R1=bDI - (ssD / 2.0), R2=ssD / 2.0)).translate((0.0, pY, (sNP - (ssD / 2.0)) - (ssD * i)))
            o0.uniteWith(o3)
            o3.erase()
        o4 = CYLINDER(s, R=bD, H=shL, O=0.0).translate((0.0, pY, sIP - sX))
        o0.uniteWith(o2)
        o2.erase()
        o0.uniteWith(o4)
        o4.erase()
    o0.uniteWith(o1)
    o1.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('H', (0, 0, 0), (0, 0, -H))
