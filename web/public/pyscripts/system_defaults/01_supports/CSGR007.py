# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgrsub.csgr000 import *
from varmain.divsub.cnut6_001 import *
from varmain.divsub.cbolt_001 import *


@activate(Group="Support", TooltipShort="CSGR007", TooltipLong="CSGR007", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(SH=LENGTH, TooltipShort="SH")
@param(SO=LENGTH, TooltipShort="SO")
@param(ST=LENGTH, TooltipShort="ST")
@param(RC=LENGTH, TooltipShort="RC")
@param(RD=LENGTH, TooltipShort="RD")
@param(RL=LENGTH, TooltipShort="RL")
@param(RDI=LENGTH, TooltipShort="RDI")
@param(RLI=LENGTH, TooltipShort="RLI")
@param(RLIU=INT, TooltipShort="RLIU")
@param(RTYPE=INT, TooltipShort="RTYPE")
@param(TRAV=LENGTH, TooltipShort="TRAV")
@param(test=LENGTH, TooltipShort="test")
@param(ID=STRING, TooltipShort="组件标识")
def CSGR007(s, D=116.0, SL=50.0, SW=200.0, SH=100.0, SO=300.0, ST=10.0, RC=150.0, RD=80.0, RL=150.0, RDI=0.0, RLI=50.0, RLIU=1, RTYPE=0, TRAV=0.0, test=False, ID='CSGR007', **kw):
    R1, R2, R3, RM, RD, RDI, RLI, LM = CSGR000_util(D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE)
    if (SH <= 0.0) or (SH <= ((RC - RM) - R2)):
        SH = (RC - RM) + R3
    if ST <= 0.0:
        ST = (RC - RM) - R2
    if SW <= 0.0:
        SW = SL
    if SW < (RL + TRAV):
        SW = RL + TRAV
    if SO < (SW + (ST * 2.0)):
        SO = SW + (SH * 2.0)
    SWx = (SO - SW) / 2.0
    HS = SH / 2.0
    o0 = BOX(s, L=ST, W=SL, H=SH).translate((HS, (SW / 2.0) + (ST / 2.0), 0.0))
    o1 = BOX(s, L=ST, W=SL, H=SH).translate((HS, (-(SW / 2.0)) - (ST / 2.0), 0.0))
    o2 = BOX(s, L=SWx, W=SL, H=ST).translate((SH - (ST / 2.0), (SWx + SW) / 2.0, 0.0))
    o3 = BOX(s, L=SWx, W=SL, H=ST).translate((SH - (ST / 2.0), (-(SWx + SW)) / 2.0, 0.0))
    o0.uniteWith(o1)
    o1.erase()
    o0.uniteWith(o2)
    o2.erase()
    o0.uniteWith(o3)
    o3.erase()
    tM = 0.0
    if TRAV > 0.0:
        mX = SW - RL
        if TRAV > mX:
            TRAV = mX
        tM = TRAV - (mX / 2.0)
    o0.rotateY(90.0).translate((0.0, -tM, -(RC - SH)))
    o1 = CSGR000(s, D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RLIU=RLIU, RTYPE=RTYPE, W=0.0, WD=0.0, test=test)
    o0.uniteWith(o1)
    o1.erase()
    rD = RDI * 0.5
    nH = (round(rD * 750)) / 1000
    rL = ((nH * 2.5) + SW) + (ST * 2.0)
    xH = (((rD / 2.0) * 0.1) + ((rL - SW) / 2.0)) + ((SW - RL) / 2.0)
    o5 = CNUT6_001(s, D=rD, W=0.0, H=nH).rotateZ(90.0).translate((0.0, ((SW / 2.0) - tM) + ST, -RM))
    o6 = CBOLT_001(s, D=rD, L=xH).rotateZ(90.0).translate((0.0, (-(rL / 2.0)) - tM, -RM))
    o7 = ((CBOLT_001(s, D=rD, L=xH + TRAV)).rotateZ(-90.0)).translate((0.0, (rL / 2.0) - tM, -RM))
    o8 = CNUT6_001(s, D=rD, W=0.0, H=nH).rotateZ(-90.0).translate((0.0, ((-(SW / 2.0)) - tM) - ST, -RM))
    o0.uniteWith(o5)
    o5.erase()
    o0.uniteWith(o6)
    o6.erase()
    o0.uniteWith(o7)
    o7.erase()
    o0.uniteWith(o8)
    o8.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('RC', (0, 0, 0), (0, 0, -RC))
