# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpflo import *
from varmain.valvsub.cpva001sub.cpva001_util import *


@activate(Group="Valve", TooltipShort="Built-in CPVA001000", TooltipLong="Built-in CPVA001000 (Decompiled from varmain/valvsub/cpva001sub/cpva001000sub/cpva001000.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(H1=LENGTH, TooltipShort="H1")
@param(H2=LENGTH, TooltipShort="H2")
@param(W1=LENGTH, TooltipShort="W1")
@param(W2=LENGTH, TooltipShort="W2")
@param(A=ANGLE, TooltipShort="A")
@param(OF=LENGTH, TooltipShort="OF")
@param(B1=LENGTH, TooltipShort="B1")
@param(B2=LENGTH, TooltipShort="B2")
@param(X1=LENGTH, TooltipShort="X1")
@param(X2=LENGTH, TooltipShort="X2")
@param(ID=STRING, TooltipShort="组件标识")
def CPVA001000(s, D1=114.3, D2=0.0, L1=175.0, L2=0.0, H1=220.0, H2=0.0, W1=0.0, W2=0.0, A=0.0, OF=-1.0, B1=22.0, B2=0.0, X1=-2.0, X2=-2.0, ID='CPVA001000', **kw):
    vC = CPVA001CORRV(D1=D1, D2=D2, L1=L1, L2=L2, H1=H1, H2=H2, B1=B1, B2=B2, W1=W1, W2=W2, A=A, OF=OF, L3=0.0, L4=0.0, I1=None, I2=None, X1=X1, X2=X2)
    R1 = vC[35] / 2.0
    R2 = vC[37] / 2.0
    R3 = vC[0] / 2.0
    R4 = vC[1] / 2.0
    if vC[29] > 0.0:
        L1 = vC[2] - vC[29]
        oF1 = (((CPFLO(s, L=vC[29], D1=vC[35], D2=(R3 - vC[18]) * 2.0, W=vC[36])).rotateX(vC[36])).translate((L1 - vC[41], 0, 0))).rotateZ(vC[10])
    else:
        L1 = vC[2]
        oF1 = None
    if vC[30] > 0.0:
        L2 = vC[3] - vC[30]
        oF2 = (((CPFLO(s, L=vC[30], D1=vC[37], D2=(R4 - vC[18]) * 2.0, W=vC[38])).rotateX(vC[37])).rotateZ(-90.0)).translate((0, -(L2 - vC[42]), 0))
    else:
        L2 = vC[3]
        oF2 = None
    oC1 = (((CONE(s, R1=R1, R2=0, H=L1 - vC[41])).rotateY(-90)).translate((L1 - vC[41], 0, 0))).rotateZ(vC[10])
    if vC[41] > 0.0:
        oTMP = (((CYLINDER(s, R=R3 + vC[18], H=vC[41], O=0.0)).rotateY(-90.0)).translate((vC[2], 0, 0))).rotateZ(vC[10])
        oC1.uniteWith(oTMP)
        oTMP.erase()
    oC2 = ((CONE(s, R1=R2, R2=0, H=L2 - vC[42])).rotateX(-90)).translate((0, -(L2 - vC[42]), 0))
    if vC[42] > 0.0:
        oTMP = (((CYLINDER(s, R=R4 + vC[18], H=vC[42], O=0.0)).rotateY(-90.0)).translate((vC[3], 0, 0))).rotateZ(-90.0)
        oC2.uniteWith(oTMP)
        oTMP.erase()
    oC1.uniteWith(oC2)
    oC2.erase()
    if oF1:
        oC1.uniteWith(oF1)
        oF1.erase()
    if oF2:
        oC1.uniteWith(oF2)
        oF2.erase()
    if vC[18] > 0.0:
        oC7 = CPVA001000_Drill(s, D1=vC[0], D2=vC[1], OF=vC[18], L1=vC[2], L2=vC[3], H1=vC[35], H2=vC[37], A=vC[10])
        oC1.subtractFrom(oC7)
        oC7.erase()
    s.setPoint(vC[12], vC[13], vC[33])
    s.setPoint(vC[14], vC[15], vC[34])
