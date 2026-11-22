# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
import math


@activate(Group="ReinforcementRing", TooltipShort="Built-in CPMV", TooltipLong="Built-in CPMV (Decompiled from varmain/weldentsub/cpmvsub/cpmv.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(W=LENGTH, TooltipShort="W")
@param(D2=LENGTH, TooltipShort="D2")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPMV(s, D=76.1, W=20.0, D2=114.3, OF=-1.0, ID='CPMV', **kw):
    if D2 == 0.0:
        D2 = D
    if D2 < D:
        D2 = D
    OF = getThickness(D2, OF=OF, Ever=1, mustCalc=True)
    if W == 0.0:
        W = OF
    R = D / 2.0
    R2 = D2 / 2.0
    L1 = R + W
    R3 = R2 + OF
    B1 = ((asDegrees(2.0 * (asin((D / 2.0) / R2)))) * R2) * 0.01745
    A1 = (B1 + (W * 2.0)) / (R2 * 0.01745)
    A2 = A1 / 2.0
    H1 = L1 * 2.0
    o1 = CYLINDER(s, R=R3, H=H1, O=0.0).rotateY(90.0).translate((-L1, 0.0, 0.0))
    s1 = CYLINDER(s, R=R2, H=H1, O=0.0).rotateY(90.0).translate((-L1, 0.0, 0.0))
    s2 = CYLINDER(s, R=R, H=R3, O=0.0).rotateX(-90.0).translate((0.0, 0.0, 0.0))
    if 180.0 >= A1:
        A3 = 90.0 - A2
        L2 = (R2 * sin(asRadiants(A2))) / sin(asRadiants(90.0))
        L3 = (R2 * sin(asRadiants(A3))) / sin(asRadiants(90.0))
        L4 = ((((R2 * sin(asRadiants(90.0))) / sin(asRadiants(A3))) - L3) * sin(asRadiants(90.0))) / sin(asRadiants(A3))
        L5 = sqrt((pow(R2, 2.0) + pow(R2, 2.0)) - (((2.0 * R2) * R2) * cos(asRadiants(A2))))
        H1 = R3
        H2 = H1 + L4
        H3 = L2 * 2.0
        H4 = L1 * 2.0
        s4 = CYLINDER(s, R1=L1, R2=L5, H=H2, O=0.0).rotateX(-90.0).translate((-L5, -L4, 0.0)).rotateZ(-A2).rotateY(90.0).translate((0.0, L3, -L2))
        s5 = BOX(s, L=H2, W=H3, H=H4).translate((0.0, (H2 / 2.0) + L3, +L2))
        s6 = (BOX(s, L=H2, W=H3, H=H4).translate((0.0, H2 / 2.0, +L2))).rotateX(+A2)
        s5.uniteWith(s6)
        s6.erase()
        s4.subtractFrom(s5)
        s5.erase()
        s7 = CYLINDER(s, R1=L1, R2=L5, H=H2, O=0.0).rotateX(-90.0).translate((L5, -L4, 0.0)).rotateZ(+A2).rotateY(90.0).translate((0.0, L3, +L2))
        s8 = BOX(s, L=H2, W=H3, H=H4).translate((0.0, (H2 / 2.0) + L3, -L2))
        s9 = (BOX(s, L=H2, W=H3, H=H4).translate((0.0, H2 / 2.0, -L2))).rotateX(-A2)
        s8.uniteWith(s9)
        s9.erase()
        s7.subtractFrom(s8)
        s8.erase()
        s4.uniteWith(s7)
        s7.erase()
    else:
        H2 = H1 + R2
        H3 = R2 * 2.0
        H4 = L1 * 2.0
        s4 = CYLINDER(s, R1=L1, R2=R2, H=H2, O=0.0).rotateX(-90.0).translate((0.0, -R2, -0.0)).rotateX(A2).translate((0.0, R2, 0.0))
        s5 = BOX(s, L=H2, W=H3, H=H4).translate((0.0, (H2 / 2.0) - OF, -R2))
        s4.subtractFrom(s5)
        s5.erase()
        s7 = CYLINDER(s, R1=L1, R2=R2, H=H2, O=0.0).rotateX(-90.0).translate((0.0, -R2, 0.0)).rotateX(-A2).translate((0.0, R2, 0.0))
        s8 = BOX(s, L=H2, W=H3, H=H4).translate((0.0, (H2 / 2.0) - OF, R2))
        s7.subtractFrom(s8)
        s8.erase()
        s4.uniteWith(s7)
        s7.erase()
    o1.subtractFrom(s1)
    s1.erase()
    o1.subtractFrom(s2)
    s2.erase()
    o1.intersectWith(s4)
    s4.erase()
    o1.rotateZ(90.0)
