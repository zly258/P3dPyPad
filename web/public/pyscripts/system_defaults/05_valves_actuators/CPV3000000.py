# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpflo import *
from varmain.valvsub.cpv3000sub.cpv3000_util import *


@activate(Group="Valve", TooltipShort="Built-in CPV3000000", TooltipLong="Built-in CPV3000000 (Decompiled from varmain/valvsub/cpv3000sub/cpv3000000sub/cpv3000000.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(L3=LENGTH, TooltipShort="L3")
@param(H1=LENGTH, TooltipShort="H1")
@param(H2=LENGTH, TooltipShort="H2")
@param(H3=LENGTH, TooltipShort="H3")
@param(W1=LENGTH, TooltipShort="W1")
@param(W2=LENGTH, TooltipShort="W2")
@param(W3=LENGTH, TooltipShort="W3")
@param(D4=LENGTH, TooltipShort="D4")
@param(OF=LENGTH, TooltipShort="OF")
@param(B1=LENGTH, TooltipShort="B1")
@param(B2=LENGTH, TooltipShort="B2")
@param(B3=LENGTH, TooltipShort="B3")
@param(P=LENGTH, TooltipShort="P")
@param(ID=STRING, TooltipShort="组件标识")
def CPV3000000(s, D1=114.3, D2=0.0, D3=0.0, L1=175.0, L2=0.0, L3=0.0, H1=220.0, H2=0.0, H3=0.0, W1=0.0, W2=0.0, W3=0.0, D4=200.0, OF=-1.0, B1=22.0, B2=0.0, B3=0.0, P=0.0, ID='CPV3000000', **kw):
    vC = CPV3000CORRV(D1=D1, D2=D2, D3=D3, L1=L1, L2=L2, L3=L3, H1=H1, H2=H2, H3=H3, B1=B1, B2=B2, B3=B3, W1=W1, W2=W2, W3=W3, D4=D4, OF=OF, L4=0.0, L5=0.0, L6=0.0, I1=None, I2=None, I3=None)
    R01 = vC[0] / 2.0
    R04 = R01 - getThickness(D=vC[0], OF=vC[23], Ever=1)
    R07 = vC[46] / 2.0
    R02 = vC[1] / 2.0
    R05 = R02 - getThickness(D=vC[1], OF=vC[23], Ever=1)
    R08 = vC[48] / 2.0
    R03 = vC[2] / 2.0
    R06 = R03 - getThickness(D=vC[2], OF=vC[23], Ever=1)
    R09 = vC[50] / 2.0
    L1 = vC[3]
    L2 = vC[4]
    L3 = vC[5]
    oF1 = None
    oF2 = None
    oF3 = None
    if vC[37] > 0.0:
        oF1 = (((CPFLO(s, L=vC[37], D1=vC[46], D2=R04 * 2.0, W=vC[47])).rotateX(vC[43])).rotateZ(180.0)).translate((-(L1 - vC[37]), 0.0, 0.0))
    if vC[38] > 0.0:
        oF2 = ((CPFLO(s, L=vC[38], D1=vC[48], D2=R05 * 2.0, W=vC[49])).rotateX(vC[44])).translate((L2 - vC[38], 0.0, 0.0))
    if vC[39] > 0.0:
        oF3 = (((CPFLO(s, L=vC[39], D1=vC[50], D2=R06 * 2.0, W=vC[51])).rotateX(vC[45])).translate((L3 - vC[39], 0.0, 0.0))).rotateZ(vC[15])
    oC1 = CYLINDER(s, R=R01, H=L1, O=0.0).rotateY(90.0).translate((-L1, 0.0, 0.0))
    oC2 = CYLINDER(s, R=R02, H=L2, O=0.0).rotateY(-90.0).translate((L2, 0.0, 0.0))
    oC3 = CYLINDER(s, R=R03, H=L3, O=0.0).rotateY(-90.0).translate((L3, 0.0, 0.0)).rotateZ(vC[15])
    oC4 = SPHERE(s, R=vC[19] / 2.0)
    oC5 = BOX(s, L=vC[36], W=vC[19], H=vC[19])
    oC5.intersectWith(oC4)
    oC4.erase()
    oC1.uniteWith(oC2)
    oC2.erase()
    oC1.uniteWith(oC3)
    oC3.erase()
    oC1.uniteWith(oC5)
    oC5.erase()
    if oF1:
        oC1.uniteWith(oF1)
        oF1.erase()
    if oF2:
        oC1.uniteWith(oF2)
        oF2.erase()
    if oF3:
        oC1.uniteWith(oF3)
        oF3.erase()
    if vC[23] > 0.0:
        oC5 = CPV3000000_Drill(s, D1=vC[0], D2=vC[1], D3=vC[2], L1=vC[3], L2=vC[4], L3=vC[5], OF=vC[23], A=vC[15])
        oC1.subtractFrom(oC5)
        oC5.erase()
    s.setPoint((-vC[3], 0.0, 0.0), (-1.0, 0.0, 0.0), vC[43])
    s.setPoint((vC[4], 0.0, 0.0), (1.0, 0.0, 0.0), vC[44])
    s.setPoint(vC[16], vC[17], vC[45])
