# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Tee", TooltipShort="CP METRIC Lateral", TooltipLong="CP METRIC Lateral (Decompiled from varmain/teesub/cptssub/cpts.pyc)", LengthUnit="mm", Ports=3)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(L3=LENGTH, TooltipShort="L3")
@param(A=ANGLE, TooltipShort="A")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPTS(s, D1=1016.0, D2=1016.0, D3=1016.0, L1=508.0, L2=1524.0, L3=1734.42049, A=45.0, OF=-1.0, ID='CPTS', **kw):
    try:
        I1 = float(kw['I1'])
    except Exception:
        I1 = 0.0
    try:
        I2 = float(kw['I2'])
    except Exception:
        I2 = 0.0
    try:
        I3 = float(kw['I3'])
    except Exception:
        I3 = 0.0
    if D2 == 0.0:
        D2 = D1
    if D3 == 0.0:
        D3 = D1
    if L2 == 0.0:
        L2 = L1
    if L3 == 0.0:
        L3 = L1
    if A == 0.0:
        A = 90.0
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    R3 = D3 / 2.0
    Drill = 1
    if OF > 0.0:
        O1 = (D1 / 2.0) - OF
        if O1 <= 0.0:
            O1 = CON_OF_DIV(D1) / 2.0
        O2 = (D2 / 2.0) - OF
        if O2 <= 0.0:
            O2 = CON_OF_DIV(D2) / 2.0
        O3 = (D3 / 2.0) - OF
        if O3 <= 0.0:
            O3 = CON_OF_DIV(D3) / 2.0
    else:
        if OF == -1:
            O1 = CON_OF_DIV(D1) / 2.0
            O2 = CON_OF_DIV(D2) / 2.0
            O3 = CON_OF_DIV(D3) / 2.0
        else:
            O1 = 0.0
            O2 = 0.0
            O3 = 0.0
            Drill = None
    if D1 == D2:
        o0 = ((CYLINDER(s, R=R1, H=L1 + L2, O=0.0)).rotateY(270)).translate((L2, 0, 0))
        if Drill:
            o3 = ((CYLINDER(s, R=O1, H=L1 + L2, O=0.0)).rotateY(270)).translate((L2, 0, 0))
    else:
        o0 = ((CONE(s, R1=R1, R2=R2, H=L1 + L2, E=0.0)).rotateY(90)).translate((-L1, 0, 0))
        if Drill:
            o3 = ((CONE(s, R1=O1, R2=O2, H=L1 + L2, E=0.0)).rotateY(90)).translate((-L1, 0, 0))
    A = A - 90.0
    if (D3 <= D1) and (D3 <= D2):
        o1 = CYLINDER(s, R=R3, H=L3, O=0.0).rotateX(270).rotateZ(A)
        if Drill:
            o4 = CYLINDER(s, R=O3, H=L3, O=0.0).rotateX(270).rotateZ(A)
    else:
        if D1 > D2:
            L4 = D2
        else:
            L4 = D1
        L4 = L4 / 2.0
        o1 = (((CYLINDER(s, R=D3 / 2.0, H=L3 - L4, O=0.0)).rotateX(270)).translate((0, L4, 0))).rotateZ(A)
        o2 = ((CONE(s, R1=L4, R2=D3 / 2.0, H=L4, E=0.0)).rotateX(-90)).rotateZ(A)
        o1.uniteWith(o2)
        o2.erase()
        if Drill:
            if D1 > D2:
                O4 = O2
            else:
                O4 = O1
            o4 = (((CYLINDER(s, R=O3, H=L3 - L4, O=0.0)).rotateX(270)).translate((0, L4, 0))).rotateZ(A)
            o5 = CONE(s, R1=O4, R2=O3, H=L4, E=0.0).rotateX(-90).rotateZ(A)
            o4.uniteWith(o5)
            o5.erase()
    o0.uniteWith(o1)
    o1.erase()
    if Drill:
        o3.uniteWith(o4)
        o4.erase()
        o0.subtractFrom(o3)
        o3.erase()
    pP3 = mTransform().rotateZ(asRadiants(A)) * (mPoint(0, L3 + I3, 0))
    pD3 = mTransform().rotateZ(asRadiants(A)) * mVector(0, 1, 0)
    s.setPoint((-L1 - I1, 0, 0), (-1, 0, 0))
    s.setPoint((L2 + I2, 0, 0), (1, 0, 0))
    s.setPoint(pP3, pD3)


def CPTS_tmp(s, D1=114.3, D2=114.3, D3=114.3, I1=0.0, I2=0.0, I3=0.0, pA1=None, pA2=None, pA3=None, pD1=None, pD2=None, pD3=None, ID='CPTS_tmp', **kw):
    if PnP3dACPAdapterIgnoreWallThickness == False:
        xI1 = 0.0
        xI2 = 0.0
        xI3 = 0.0
    else:
        xI1 = I1
        xI2 = I2
        xI3 = I3
    c1 = (((CYLINDER(s, R=D1 / 2.0, H=D1, O=0.0)).rotateY(-90)).rotateZ(180.0)).translate((xI1, 0.0, 0.0))
    c1.rotateZ(asDegrees(pD1.theta())).translate(pA1)
    c2 = (((CYLINDER(s, R=D2 / 2.0, H=D2, O=0.0)).rotateY(-90)).rotateZ(180.0)).translate((xI2, 0.0, 0.0))
    c2.rotateZ(asDegrees(pD2.theta())).translate(pA2)
    c3 = (((CYLINDER(s, R=D3 / 2.0, H=D3, O=0.0)).rotateY(-90)).rotateZ(180.0)).translate((xI3, 0.0, 0.0))
    c3.rotateZ(asDegrees(pD3.theta())).translate(pA3)
    c1.uniteWith(c2)
    c2.erase()
    c1.uniteWith(c3)
    c3.erase()
    return c1
