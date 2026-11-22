# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpflo import *
from varmain.valvsub.cpvi064sub.cpvi064_util import *


@activate(Group="Valve", TooltipShort="MAGNETIC FLOW METER, CL 150, RF", TooltipLong="MAGNETIC FLOW METER, CL 150, RF (Decompiled from varmain/valvsub/cpvi064sub/cpvi064000sub/cpvi064000.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(LS=LENGTH, TooltipShort="LS")
@param(H1=LENGTH, TooltipShort="H1")
@param(H2=LENGTH, TooltipShort="H2")
@param(D3=LENGTH, TooltipShort="D3")
@param(H3=LENGTH, TooltipShort="H3")
@param(W1=LENGTH, TooltipShort="W1")
@param(W2=LENGTH, TooltipShort="W2")
@param(OF=LENGTH, TooltipShort="OF")
@param(B1=LENGTH, TooltipShort="B1")
@param(B2=LENGTH, TooltipShort="B2")
@param(ID=STRING, TooltipShort="组件标识")
def CPVI064000(s, D1=21.3, D2=21.3, L=200.0, LS=100.0, H1=90.0, H2=90.0, D3=114.0, H3=120.0, W1=0.0, W2=0.0, OF=-1.0, B1=11.6, B2=11.6, ID='CPVI064000', **kw):
    vC = CPVI064CORRV(D1=D1, D2=D2, L=L, LS=LS, H1=H1, H2=H2, D3=D3, H3=H3, B1=B1, B2=B2, W1=W1, W2=W2, OF=OF, L1=0.0, L2=0.0, I1=0.0, I2=0.0)
    R1 = vC[40] / 2.0
    R2 = vC[42] / 2.0
    R3 = vC[0] / 2.0
    R4 = vC[1] / 2.0
    if vC[32] > 0.0:
        oF1 = (CPFLO(s, L=vC[32], D1=vC[40], D2=(R3 - vC[17]) * 2.0, W=vC[41])).rotateX(vC[38])
    else:
        oF1 = None
    if vC[33] > 0.0:
        oF2 = ((CPFLO(s, L=vC[33], D1=vC[42], D2=(R4 - vC[17]) * 2.0, W=vC[43])).rotateX(vC[39])).translate(((vC[3] + vC[4]) + vC[32], 0, 0))
    else:
        oF2 = None
    oC1 = CYLINDER(s, R=vC[30], H=vC[29], O=0.0).rotateY(90).translate(((vC[32] + vC[3]) - vC[31], 0, 0))
    oC2 = CONE(s, R1=R1, R2=R3, H=vC[34]).rotateY(-90).translate((-vC[32], 0.0, 0.0)).rotateZ(180.0)
    oC3 = CONE(s, R1=R2, R2=R4, H=vC[35]).rotateY(-90).translate((vC[2] - vC[33], 0.0, 0.0))
    oC1.uniteWith(oC2)
    oC2.erase()
    oC1.uniteWith(oC3)
    oC3.erase()
    if oF1:
        oC1.uniteWith(oF1)
        oF1.erase()
    if oF2:
        oC1.uniteWith(oF2)
        oF2.erase()
    if vC[17] > 0.0:
        oC5 = CPVI064000_Drill(s, D1=vC[0], D2=vC[1], L1=vC[3], L2=vC[4], H1=vC[40], H2=vC[42], OF=vC[17]).translate((vC[32], 0.0, 0.0))
        oC1.subtractFrom(oC5)
        oC5.erase()
    s.setPoint(vC[11], vC[12], vC[38])
    s.setPoint(vC[13], vC[14], vC[39])
