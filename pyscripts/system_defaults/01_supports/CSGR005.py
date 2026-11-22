# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgrsub.csgr000 import *
from varmain.divsub.cnut6_001 import *
from varmain.divsub.cbolt_001 import *


@activate(Group="Support", TooltipShort="CSGR005", TooltipLong="CSGR005", LengthUnit="mm", Ports=1)
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
@param(test=LENGTH, TooltipShort="test")
@param(doAllNuts=LENGTH, TooltipShort="doAllNuts")
@param(ID=STRING, TooltipShort="组件标识")
def CSGR005(s, D=116.0, BW=220.0, BH=0.0, RD=80.0, RL=150.0, RDI=0.0, RLI=50.0, RTYPE=0, H=230.0, HD3=0.0, HS=10.0, HO=0.0, HB=0.0, DOUBROLL=0, test=False, doAllNuts=True, ID='CSGR005', **kw):
    R1, R2, R3, RC, RD, RDI, RLI, LM = CSGR000_util(D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE)
    if BH <= 0.0:
        BH = R2
    if HB <= 0.0:
        HB = ((BW - RL) / 2.0) + RL
    if HD3 <= 0.0:
        rD = RDI * 0.5
    else:
        rD = HD3
    nH = (round(rD * 750)) / 1000
    rW = (round(rD * 1500)) / 1000
    tP = -RC - nH
    bL = (H - RC) - BH
    tP1 = tP - ((H - RC) - nH)
    tP2 = tP1 - HS
    if HO <= 0.0:
        HO = nH * 1.5
    if HB < 0.0:
        HB = SW / 3.0
    rP = -RC - BH
    bPY = [-(HB / 2.0), HB / 2.0]
    bPZ = [0.0]
    if DOUBROLL:
        bPZ.append(RC * 2.0)
    bL += HO + HS
    bD = (BW - HB) / 2.0
    rE = (BH + R3) + (nH * 1.5)
    extRod = False
    o0 = ((CYLINDER(s, R=rD * 0.01, H=rD * 0.01, O=0.0)).rotateX(180.0)).translate((0.0, bPY[0], tP))
    for pY in bPY:
        for pZ in bPZ:
            if (pZ != bPZ[0]) and (not extRod):
                rE += pZ
                extRod = True
            o1 = CNUT6_001(s, D=rD, W=rW, H=nH).rotateY(-90.0).translate((0.0, pY, (-RC + R3) + pZ))
            o2 = (CYLINDER(s, R=bD, H=BH * 0.2, O=0.0)).translate((0.0, pY, (-RC - BH) + pZ))
            o3 = (CYLINDER(s, R=bD * 0.75, H=BH + R3, O=0.0)).translate((0.0, pY, (-RC - BH) + pZ))
            if pY != bPY[0]:
                rotAng = 90.0
            else:
                rotAng = -90.0
            o4 = ((CYLINDER(s, R=bD * 0.75, H=(HB - RL) / 2.0, O=0.0)).rotateX(rotAng)).translate((0.0, pY, -RC + pZ))
            if (doAllNuts) or (pZ != bPZ[0]):
                o5 = CNUT6_001(s, D=rD, W=rW, H=nH).rotateY(90.0).translate((0.0, pY, (-RC - BH) + pZ))
                o0.uniteWith(o5)
                o5.erase()
            o0.uniteWith(o1)
            o1.erase()
            o0.uniteWith(o2)
            o2.erase()
            o0.uniteWith(o3)
            o3.erase()
            o0.uniteWith(o4)
            o4.erase()
        o5 = ((CBOLT_001(s, D=rD, L=bL + rE, W=rW, H=nH)).rotateY(90.0)).translate((0.0, pY, rP + rE))
        if doAllNuts:
            o6 = CNUT6_001(s, D=rD, W=rW, H=nH).rotateY(-90.0).translate((0.0, pY, tP1))
            o0.uniteWith(o6)
            o6.erase()
        if not ((nH * 1.5) > HO):
            o7 = CNUT6_001(s, D=rD, W=rW, H=nH).rotateY(90.0).translate((0.0, pY, tP2))
            o0.uniteWith(o7)
            o7.erase()
        o0.uniteWith(o5)
        o5.erase()
    for pZ in bPZ:
        if pZ == bPZ[0]:
            xtest = test
        else:
            xtest = False
        o1 = CSGR000(s, D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RLIU=1, RTYPE=RTYPE, W=0.0, WD=0.0, test=xtest).translate((0.0, 0.0, pZ))
        o0.uniteWith(o1)
        o1.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('H', (0, 0, 0), (0, 0, -H))
