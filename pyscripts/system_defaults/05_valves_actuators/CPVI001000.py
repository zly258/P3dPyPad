# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpflo import *
from varmain.valvsub.cpvi001sub.cpvi001_util import *


@activate(Group="Valve", TooltipShort="CP METRIC Inline Instrument (VALVE)", TooltipLong="CP METRIC Inline Instrument (VALVE) (Decompiled from varmain/valvsub/cpvi001sub/cpvi001000sub/cpvi001000.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(LS=LENGTH, TooltipShort="LS")
@param(H1=LENGTH, TooltipShort="H1")
@param(H2=LENGTH, TooltipShort="H2")
@param(W1=LENGTH, TooltipShort="W1")
@param(W2=LENGTH, TooltipShort="W2")
@param(OF=LENGTH, TooltipShort="OF")
@param(B1=LENGTH, TooltipShort="B1")
@param(B2=LENGTH, TooltipShort="B2")
@param(ID=STRING, TooltipShort="组件标识")
def CPVI001000(s, D1=1016.0, D2=1016.0, L=5080.0, LS=0.0, H1=1320.0, H2=1320.0, W1=0.0, W2=0.0, OF=-1.0, B1=58.0, B2=58.0, ID='CPVI001000', **kw):
    vC = CPVI001CORRV(D1=D1, D2=D2, L=L, LS=LS, H1=H1, H2=H2, B1=B1, B2=B2, W1=W1, W2=W2, OF=OF, L1=0.0, L2=0.0, I1=0.0, I2=0.0)
    R1 = vC[34] / 2.0
    R2 = vC[36] / 2.0
    R3 = vC[0] / 2.0
    R4 = vC[1] / 2.0
    R7 = vC[35] / 2.0
    R8 = vC[37] / 2.0
    if vC[28] > 0.0:
        oF1 = (CPFLO(s, L=vC[28], D1=vC[34], D2=(R3 - vC[17]) * 2.0, W=vC[35])).rotateX(vC[32])
    else:
        oF1 = None
    if vC[29] > 0.0:
        oF2 = ((CPFLO(s, L=vC[29], D1=vC[36], D2=(R4 - vC[17]) * 2.0, W=vC[37])).rotateX(vC[33])).translate(((vC[3] + vC[4]) + vC[28], 0, 0))
    else:
        oF2 = None
    oC1 = CONE(s, R1=R1, R2=0.0, H=vC[3]).rotateY(90).translate((vC[28], 0, 0))
    oC2 = CONE(s, R1=R2, R2=0.0, H=vC[4]).rotateY(-90).translate(((vC[3] + vC[4]) + vC[28], 0, 0))
    oC1.uniteWith(oC2)
    oC2.erase()
    if oF1:
        oC1.uniteWith(oF1)
        oF1.erase()
    if oF2:
        oC1.uniteWith(oF2)
        oF2.erase()
    if vC[17] > 0.0:
        oC5 = CPVI001000_Drill(s, D1=vC[0], D2=vC[1], L1=vC[3], L2=vC[4], H1=vC[34], H2=vC[36], OF=vC[17]).translate((vC[28], 0.0, 0.0))
        oC1.subtractFrom(oC5)
        oC5.erase()
    s.setPoint(vC[11], vC[12], vC[32])
    s.setPoint(vC[13], vC[14], vC[33])
