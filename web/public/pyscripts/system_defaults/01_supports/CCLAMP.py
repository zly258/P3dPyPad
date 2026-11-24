# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cnut6_001 import *
from varmain.divsub.cbolt6_001 import *


@activate(Group="Support", TooltipShort="CCLAMP", TooltipLong="CCLAMP", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(ID=STRING, TooltipShort="组件标识")
def CCLAMP(s, D=116.0, L=0.0, W=0.0, K=0.0, ID='CCLAMP', **kw):
    W = getThickness(D, OF=W, Ever=True, mustCalc=True)
    if L <= 0.0:
        L = D * 0.25
    R1 = D / 2.0
    R2 = R1 + W
    if K <= 0.0:
        K = D + (L * 3.0)
    o1 = TORUS(s, R1=R1, R2=L / 2.0)
    o2 = BOX(s, L=K, W=L, H=W * 3.0)
    o3 = CYLINDER(s, R=R1, H=L, O=0.0).translate((0, 0, -(L / 2.0)))
    o4 = BOX(s, L=K, W=L, H=W)
    blTmp = W * 3.0
    bd = L / 2.0
    bH = (round(750 * bd)) / 1000
    bW = (round(bd * 1500)) / 1000
    wH = bH / 5.0
    wTmp = sqrt((pow(bW * tan(asRadiants(30.0)), 2)) + pow(bW, 2))
    wD = wTmp + ((L - wTmp) / 2.0)
    bl = (blTmp + (wH * 2.0)) + (bH * 1.5)
    o5 = CBOLT6_001(s, D=bd, L=bl, W=0.0, H=0.0).rotateY(90.0).rotateZ(-15.0).translate((0.0, (K / 2.0) - (L / 2.0), (blTmp / 2.0) + wH))
    o6 = (CYLINDER(s, R=wD / 2.0, H=wH, O=0.0)).translate((0.0, (K / 2.0) - (L / 2.0), blTmp / 2.0))
    o7 = (CYLINDER(s, R=wD / 2.0, H=wH, O=0.0)).translate((0.0, (K / 2.0) - (L / 2.0), (-(blTmp / 2.0)) - wH))
    o8 = CNUT6_001(s, D=bd, W=0.0, H=0.0).rotateY(90.0).rotateZ(15.0).translate((0.0, (K / 2.0) - (L / 2.0), (-(blTmp / 2.0)) - wH))
    o9 = CBOLT6_001(s, D=bd, L=bl, W=0.0, H=0.0).rotateY(90.0).rotateZ(-15.0).translate((0.0, -((K / 2.0) - (L / 2.0)), (blTmp / 2.0) + wH))
    o10 = (CYLINDER(s, R=wD / 2.0, H=wH, O=0.0)).translate((0.0, -((K / 2.0) - (L / 2.0)), blTmp / 2.0))
    o11 = (CYLINDER(s, R=wD / 2.0, H=wH, O=0.0)).translate((0.0, -((K / 2.0) - (L / 2.0)), (-(blTmp / 2.0)) - wH))
    o12 = CNUT6_001(s, D=bd, W=0.0, H=0.0).rotateY(90.0).rotateZ(15.0).translate((0.0, -((K / 2.0) - (L / 2.0)), (-(blTmp / 2.0)) - wH))
    o1.uniteWith(o2)
    o2.erase()
    o3.uniteWith(o4)
    o4.erase()
    o1.subtractFrom(o3)
    o3.erase()
    o1.rotateY(90)
    for obj in [o5, o6, o7, o8, o9, o10, o11, o12]:
        o1.uniteWith(obj)
        obj.erase()
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((0, 0, 0), (1, 0, 0))
