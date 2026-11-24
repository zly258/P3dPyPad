# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgrsub.csgr000 import *
from varmain.divsub.cnut6_001 import *
from varmain.divsub.cbolt_001 import *


@activate(Group="Support", TooltipShort="CSGR002", TooltipLong="CSGR002", LengthUnit="mm", Ports=1)
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
@param(HL=LENGTH, TooltipShort="HL")
@param(HW=LENGTH, TooltipShort="HW")
@param(HH=LENGTH, TooltipShort="HH")
@param(test=LENGTH, TooltipShort="test")
@param(ID=STRING, TooltipShort="组件标识")
def CSGR002(s, D=116.0, SL=250.0, SW=200.0, SH=100.0, ST=10.0, RC=150.0, RD=80.0, RL=150.0, RDI=0.0, RLI=50.0, RTYPE=0, TRAV=0.0, HL=0.0, HW=0.0, HH=0.0, test=False, ID='CSGR002', **kw):
    R1, R2, R3, RM, RD, RDI, RLI, LM = CSGR000_util(D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE)
    if SW <= 0.0:
        SW = SL
    if (SH <= 0.0) or (SH <= ((RC - RM) - R2)):
        SH = (RC - RM) + R3
    if ST <= 0.0:
        ST = (RC - RM) - R2
    if (SW - (ST * 2.0)) < (RL + TRAV):
        SW = (RL + TRAV) + (ST * 2.0)
    SWx = SW - ST
    HS = SH
    o0 = BOX(s, L=ST, W=SL, H=HS).translate((SH - (HS / 2.0), SWx / 2.0, 0))
    o1 = BOX(s, L=ST, W=SL, H=HS).translate((SH - (HS / 2.0), 0 - (SWx / 2.0), 0))
    o2 = BOX(s, L=SWx, W=SL, H=ST).translate((SH - (ST / 2.0), 0, 0))
    if (HL > 0.0) and (HW > 0.0):
        if HH <= 0.0:
            HH = ST * 2.0
        HW1 = HW - SL
        o3 = (BOX(s, L=HW1, W=HL, H=HH).translate((SH - (HH / 2.0), SL / 2.0, 0))).rotateX(90.0)
        o4 = (BOX(s, L=HW1, W=HL, H=HH).translate((SH - (HH / 2.0), 0 - (SL / 2.0), 0))).rotateX(90.0)
    else:
        o3 = None
    o0.uniteWith(o1)
    o1.erase()
    o0.uniteWith(o2)
    o2.erase()
    if o3:
        o0.uniteWith(o3)
        o3.erase()
        o0.uniteWith(o4)
        o4.erase()
    tM = 0.0
    if TRAV > 0.0:
        mX = (SW - (ST * 2.0)) - RL
        if TRAV > mX:
            TRAV = mX
        tM = TRAV - (mX / 2.0)
    o0.rotateY(90.0).translate((0.0, -tM, -(RC - SH)))
    o1 = CSGR000(s, D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RLIU=1, RTYPE=RTYPE, W=0.0, WD=0.0, test=test)
    o0.uniteWith(o1)
    o1.erase()
    rD = RDI * 0.5
    nH = (round(rD * 750)) / 1000
    rL = (nH * 2.5) + SW
    o5 = CNUT6_001(s, D=rD, W=0.0, H=nH).rotateZ(90.0).translate((0.0, (SW / 2.0) - tM, -RM))
    o6 = CBOLT_001(s, D=rD, L=rL).rotateZ(90.0).rotateY(33.3).translate((0.0, (-(rL / 2.0)) - tM, -RM))
    o7 = CNUT6_001(s, D=rD, W=0.0, H=nH).rotateZ(-90.0).translate((0.0, (-(SW / 2.0)) - tM, -RM))
    o0.uniteWith(o5)
    o5.erase()
    o0.uniteWith(o6)
    o6.erase()
    o0.uniteWith(o7)
    o7.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('RC', (0, 0, 0), (0, 0, -RC))
