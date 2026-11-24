# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Tee", TooltipShort="Built-in CPTE", TooltipLong="Built-in CPTE (Decompiled from varmain/teesub/cptesub/cpte.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(L1=LENGTH, TooltipShort="L1")
@param(LP1=LENGTH, TooltipShort="LP1")
@param(L2=LENGTH, TooltipShort="L2")
@param(LP2=LENGTH, TooltipShort="LP2")
@param(L3=LENGTH, TooltipShort="L3")
@param(LP3=LENGTH, TooltipShort="LP3")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPTE(s, D1=114.3, D2=114.3, D3=114.3, L1=200.0, LP1=0.0, L2=0.0, LP2=0.0, L3=0.0, LP3=0.0, OF=-1.0, ID='CPTE', **kw):
    A = 90.0
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
    OF = getThickness(D=D1, OF=OF)
    if D2 == 0.0:
        D2 = D1
    if D3 == 0.0:
        D3 = D1
    if L2 == 0.0:
        L2 = L1
    if L3 == 0.0:
        L3 = L1
    if LP1 <= 0.0:
        LP1 = L1 - D1
    if LP2 <= 0.0:
        LP2 = LP1
    if LP3 <= 0.0:
        LP3 = LP1
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
    sF = getThickness(D=D1, OF=OF, Ever=1, mustCalc=True)
    s1 = L1 - LP1
    b1 = L1 - LP1
    s2 = L2 - LP2
    b2 = L2 - LP2
    b3 = L3 - LP3
    s3 = (b3 + R1) + sF
    sH = D1 + (sF * 2.0)
    c1 = (b1 - R3) - sF
    c2 = (b2 - R3) - sF
    c3 = (b3 - R1) - sF
    if areEqual(D1, D2):
        o0 = ((CYLINDER(s, R=R1, H=L1 + L2, O=0.0)).rotateY(270)).translate((L2, 0, 0))
        if Drill:
            o3 = ((CYLINDER(s, R=O1, H=L1 + L2, O=0.0)).rotateY(270)).translate((L2, 0, 0))
    else:
        o0 = ((CONE(s, R1=R1, R2=R2, H=s1 + s2, E=0.0)).rotateY(90)).translate((-s1, 0, 0))
        o0a = ((CYLINDER(s, R=R1, H=L1 - s1, O=0.0)).rotateY(270)).translate((-s1, 0, 0))
        o0b = ((CYLINDER(s, R=R2, H=L2 - s2, O=0.0)).rotateY(270)).translate((L2, 0, 0))
        o0.uniteWith(o0a)
        o0a.erase()
        o0.uniteWith(o0b)
        o0b.erase()
        if Drill:
            o3 = ((CONE(s, R1=O1, R2=O2, H=s1 + s2, E=0.0)).rotateY(90)).translate((-s1, 0, 0))
            o3a = ((CYLINDER(s, R=O1, H=L1 - s1, O=0.0)).rotateY(270)).translate((-s1, 0, 0))
            o3b = ((CYLINDER(s, R=O2, H=L2 - s2, O=0.0)).rotateY(270)).translate((L2, 0, 0))
            o3.uniteWith(o3a)
            o3a.erase()
            o3.uniteWith(o3b)
            o3b.erase()
    A = A - 90.0
    o1 = CYLINDER(s, R=R3, H=L3, O=0.0).rotateX(270).rotateZ(A)
    if Drill:
        o4 = CYLINDER(s, R=O3, H=L3, O=0.0).rotateX(270).rotateZ(A)
    o0.uniteWith(o1)
    o1.erase()
    oC0 = (CORNERBOX(s, L=s1 + s2, W=s3, H=sH)).translate((-s1, (-(D1 / 2.0)) - sF, -sH / 2.0))
    oC1 = CYLINDER(s, R=sF * 0.01, H=sF * 0.01, O=0.0)
    oC1.uniteWith(oC0)
    oC0.erase()
    oC3 = None
    pX = (R3 + sF) + c3
    pY = (R1 + sF) + c3
    if areEqual(c1, c3):
        cR = c3
    else:
        if c1 > c3:
            cR = c3
            xL = ((s1 - cR) - R3) - sF
            oC3 = CORNERBOX(s, L=xL, W=cR, H=sH).translate((-pX - xL, pY - cR, -(sH / 2.0)))
        else:
            if c1 < c3:
                cR = c1
                xH = ((s3 - cR) - D1) - (sF * 2.0)
                pX = (R3 + sF) + c1
                pY = (R1 + sF) + c1
                oC3 = CORNERBOX(s, L=cR, W=xH, H=sH).translate((-pX, pY, -(sH / 2.0)))
    oC2 = CYLINDER(s, R=cR, H=sH, O=0.0).translate((-pX, pY, -(sH / 2.0)))
    if oC3 != None:
        oC2.uniteWith(oC3)
        oC3.erase()
    oC1.subtractFrom(oC2)
    oC2.erase()
    oC5 = None
    pX = (R3 + sF) + c3
    pY = (R1 + sF) + c3
    if areEqual(c2, c3):
        cR = c3
    else:
        if c2 > c3:
            cR = c3
            xL = ((s2 - cR) - R3) - sF
            oC5 = CORNERBOX(s, L=xL, W=cR, H=sH).translate((pX, pY - cR, -(sH / 2.0)))
        else:
            if c2 < c3:
                cR = c2
                xH = ((s3 - cR) - D1) - (sF * 2.0)
                pX = (R3 + sF) + c2
                pY = (R1 + sF) + c2
                oC5 = CORNERBOX(s, L=cR, W=xH, H=sH).translate((pX - cR, pY, -(sH / 2.0)))
    oC4 = CYLINDER(s, R=cR, H=sH, O=0.0).translate((pX, pY, -(sH / 2.0)))
    if oC5 != None:
        oC4.uniteWith(oC5)
        oC5.erase()
    oC1.subtractFrom(oC4)
    oC4.erase()
    o0.uniteWith(oC1)
    oC1.erase()
    if Drill:
        o3.uniteWith(o4)
        o4.erase()
        o0.subtractFrom(o3)
        o3.erase()
    pP3 = mTransform().rotateZ(asRadiants(A)) * (mPoint(0, L3 + I3, 0))
    pD3 = mTransform().rotateZ(asRadiants(A)) * mVector(0, 1, 0)
    s.setPoint((-L1 - I1, 0, 0), (-1, 0, 0), 0.0)
    s.setPoint((L2 + I2, 0, 0), (1, 0, 0), 0.0)
    s.setPoint(pP3, pD3, 0.0)


def CPTE_tmp(s, D1=114.3, D2=114.3, D3=114.3, I1=0.0, I2=0.0, I3=0.0, pA1=None, pA2=None, pA3=None, pD1=None, pD2=None, pD3=None, ID='CPTE_tmp', **kw):
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
