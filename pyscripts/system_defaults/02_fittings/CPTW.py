# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Tee", TooltipShort="CP METRIC Elbow Side Outlet", TooltipLong="CP METRIC Elbow Side Outlet (Decompiled from varmain/teesub/cptwsub/cptw.pyc)", LengthUnit="mm", Ports=3)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(L3=LENGTH, TooltipShort="L3")
@param(A=LENGTH, TooltipShort="A")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPTW(s, D1=1016.0, D2=1016.0, D3=1016.0, L1=749.0, L2=749.0, L3=749.0, A=90.0, OF=-1.0, ID='CPTW', **kw):
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
        O1 = R1 - OF
        if O1 <= 0.0:
            O1 = CON_OF_DIV(R1)
        O2 = R2 - OF
        if O2 <= 0.0:
            O2 = CON_OF_DIV(R2)
        O3 = R3 - OF
        if O3 <= 0.0:
            O3 = CON_OF_DIV(R3)
    else:
        if OF == -1:
            O1 = CON_OF_DIV(R1)
            O2 = CON_OF_DIV(R2)
            O3 = CON_OF_DIV(R3)
        else:
            O1 = 0.0
            O2 = 0.0
            O3 = 0.0
            Drill = None
    o0 = CYLINDER(s, R=R1, H=L1, O=0.0).rotateY(270.0)
    if Drill:
        o4 = CYLINDER(s, R=O1, H=L1, O=0.0).rotateY(270.0)
    if D2 == D1:
        o1 = CYLINDER(s, R=R2, H=L2, O=0.0).rotateY(90.0).rotateZ(0.0 - (A / 2.0))
        if Drill:
            o5 = CYLINDER(s, R=O2, H=L2, O=0.0).rotateY(90.0).rotateZ(0.0 - (A / 2.0))
    else:
        o1 = CONE(s, R1=R1, R2=R2, H=L2, E=0.0).rotateY(90.0).rotateZ(0.0 - (A / 2.0))
        if Drill:
            o5 = CONE(s, R1=O1, R2=O2, H=L2, E=0.0).rotateY(90.0).rotateZ(0.0 - (A / 2.0))
    if D3 == D1:
        o2 = CYLINDER(s, R=R3, H=L3, O=0.0).rotateY(90.0).rotateZ(A / 2.0)
        if Drill:
            o6 = CYLINDER(s, R=O3, H=L3, O=0.0).rotateY(90.0).rotateZ(A / 2.0)
    else:
        o2 = CONE(s, R1=R1, R2=R3, H=L3, E=0.0).rotateY(90.0).rotateZ(A / 2.0)
        if Drill:
            o6 = CONE(s, R1=O1, R2=O3, H=L3, E=0.0).rotateY(90.0).rotateZ(A / 2.0)
    o3 = SPHERE(s, R=R1)
    if Drill:
        o7 = SPHERE(s, R=O1)
    o1.uniteWith(o2)
    o2.erase()
    o1.rotateY(180.0 + A)
    o0.uniteWith(o1)
    o1.erase()
    o0.uniteWith(o3)
    o3.erase()
    if Drill:
        o5.uniteWith(o6)
        o6.erase()
        o5.rotateY(180.0 + A)
        o4.uniteWith(o5)
        o5.erase()
        o0.subtractFrom(o4)
        o4.erase()
        o0.subtractFrom(o7)
        o7.erase()
    pP2 = ((mTransform().rotateZ(asRadiants(0.0 - (A / 2.0)))).rotateY(asRadiants(180.0 + A))) * (mPoint(L2 + I2, 0, 0))
    pD2 = ((mTransform().rotateZ(asRadiants(0.0 - (A / 2.0)))).rotateY(asRadiants(180.0 + A))) * mVector(1, 0, 0)
    pP3 = ((mTransform().rotateZ(asRadiants(A / 2.0))).rotateY(asRadiants(180.0 + A))) * (mPoint(L3 + I3, 0, 0))
    pD3 = ((mTransform().rotateZ(asRadiants(A / 2.0))).rotateY(asRadiants(180.0 + A))) * mVector(1, 0, 0)
    s.setPoint((-L1 - I1, 0, 0), (-1, 0, 0))
    s.setPoint(pP2, pD2)
    s.setPoint(pP3, pD3)
