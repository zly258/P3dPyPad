# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgrsub.csgr000 import *


@activate(Group="Support", TooltipShort="CSGR001", TooltipLong="CSGR001", LengthUnit="mm", Ports=1)
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
@param(test=LENGTH, TooltipShort="test")
@param(ID=STRING, TooltipShort="组件标识")
def CSGR001(s, D=116.0, SL=250.0, SW=200.0, SH=30.0, ST=10.0, RC=150.0, RD=80.0, RL=150.0, RDI=0.0, RLI=50.0, RTYPE=0, test=False, ID='CSGR001', **kw):
    R1, R2, R3, RM, RD, RDI, RLI, LM = CSGR000_util(D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE)
    sB = (RC - RM) - R2
    if SW <= 0.0:
        SW = SL
    if ST <= 0.0:
        ST = (SW - RL) / 2.0
    if (SH <= 0.0) or (SH <= sB):
        SH = (RC - RM) - R3
    o0 = BOX(s, L=SW, W=SH, H=SL).translate((0.0, 0.0, -(RC - (SH / 2.0))))
    o1 = (BOX(s, L=SW - (ST * 2.0), W=SH - sB, H=SL - (ST * 2.0))).translate((0.0, 0.0, -((RC - (SH / 2.0)) - (sB / 2.0))))
    o0.subtractFrom(o1)
    o1.erase()
    o1 = CSGR000(s, D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RLIU=1, RTYPE=RTYPE, W=0.0, WD=0.0, test=test)
    o0.uniteWith(o1)
    o1.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('RC', (0, 0, 0), (0, 0, -RC))
