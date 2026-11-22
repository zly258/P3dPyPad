# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgrsub.csgr002 import *
from varmain.divsub.cnut6_001 import *
from varmain.divsub.cbolt6_001 import *


@activate(Group="Support", TooltipShort="CSGR004", TooltipLong="CSGR004", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(SH=LENGTH, TooltipShort="SH")
@param(ST=LENGTH, TooltipShort="ST")
@param(RC=LENGTH, TooltipShort="RC")
@param(RD=LENGTH, TooltipShort="RD")
@param(RL=LENGTH, TooltipShort="RL")
@param(RDI=LENGTH, TooltipShort="RDI")
@param(RLI=LENGTH, TooltipShort="RLI")
@param(RTYPE=INT, TooltipShort="RTYPE")
@param(TRAV=LENGTH, TooltipShort="TRAV")
@param(H=LENGTH, TooltipShort="H")
@param(HD3=LENGTH, TooltipShort="HD3")
@param(HS=LENGTH, TooltipShort="HS")
@param(HO=LENGTH, TooltipShort="HO")
@param(HB=LENGTH, TooltipShort="HB")
@param(test=LENGTH, TooltipShort="test")
@param(ID=STRING, TooltipShort="组件标识")
def CSGR004(s, D=116.0, SL=50.0, SW=200.0, SH=100.0, ST=10.0, RC=150.0, RD=80.0, RL=150.0, RDI=0.0, RLI=50.0, RTYPE=0, TRAV=0.0, H=230.0, HD3=0.0, HS=10.0, HO=0.0, HB=0.0, test=False, ID='CSGR004', **kw):
    R1, R2, R3, RM, RD, RDI, RLI, LM = CSGR000_util(D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE)
    if SW <= 0.0:
        SW = SL
    if SH <= 0.0:
        SH = (RC - RM) + R3
    if ST <= 0.0:
        ST = (RC - RM) - R2
    tM = 0.0
    if TRAV > 0.0:
        mX = (SW - (ST * 2.0)) - RL
        if TRAV > mX:
            TRAV = mX
        tM = TRAV - (mX / 2.0)
    o1 = CSGR002(s, D=D, SL=SL, SW=SW, SH=SH, ST=ST, RC=RC, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE, TRAV=TRAV, HL=0.0, HW=0.0, HH=0.0, test=test)
    if HD3 <= 0.0:
        rD = RDI * 0.5
    else:
        rD = HD3
    nH = (round(rD * 750)) / 1000
    rW = (round(rD * 1500)) / 1000
    tP = -RC - nH
    bL = (H - RC) - nH
    tP1 = tP - bL
    tP2 = tP1 - HS
    if HO <= 0.0:
        HO = nH * 1.5
    if HB < 0.0:
        HB = SW / 3.0
    if HB == 0.0:
        bPY = [0.0]
    else:
        bPY = [-(HB / 2.0), HB / 2.0]
    bL += HO + HS
    o0 = ((CYLINDER(s, R=rD * 0.01, H=rD * 0.01, O=0.0)).rotateX(180.0)).translate((0.0, bPY[0] - tM, tP))
    o0.uniteWith(o1)
    o1.erase()
    for pY in bPY:
        o1 = CNUT6_001(s, D=rD, W=rW, H=nH).rotateY(-90.0).translate((0.0, pY - tM, tP1))
        o0.uniteWith(o1)
        o1.erase()
        if (nH * 1.5) > HO:
            o1 = None
        else:
            o1 = CNUT6_001(s, D=rD, W=rW, H=nH).rotateY(90.0).translate((0.0, pY - tM, tP2))
            o0.uniteWith(o1)
            o1.erase()
        o1 = CBOLT6_001(s, D=rD, L=bL, W=rW, H=nH).rotateY(90.0).translate((0.0, pY - tM, tP))
        o0.uniteWith(o1)
        o1.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('H', (0, 0, 0), (0, 0, -H))
