# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.teesub.cptssub.cpts import *
from varmain.crosssub.cpxxsub.cpxx import *
from varmain.arcsub.cpbsub.cpb import *


@activate(Group="Elbow", TooltipShort="Built-in CDBBEND", TooltipLong="Built-in CDBBEND (Decompiled from varmain/dummy_var.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(L=LENGTH, TooltipShort="L")
@param(ID=STRING, TooltipShort="组件标识")
def CDUMMY(s, D1=220.0, L=-1.0, ID='CDUMMY', **kw):
    if L <= 0.0:
        xVal = ''
        while xVal == '':
            try:
                xVal = '1'
                if len(xVal) == 0:
                    L = D1
                    break
                try:
                    L = float(xVal)
                except Exception:
                    xVal = ''
            except Exception:
                L = D1
    o1 = BOX(s, W=D1, H=L, L=D1).translate((L / 2.0, 0.0, 0.0))
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((L, 0, 0), (1, 0, 0))


@activate(Group="Elbow", TooltipShort="Built-in CDBBEND", TooltipLong="Built-in CDBBEND (Decompiled from varmain/dummy_var.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(ID=STRING, TooltipShort="组件标识")
def CDBOX(s, D=116.0, L=300.0, ID='CDBOX', **kw):
    o1 = BOX(s, W=D, H=L, L=D).translate((L / 2.0, 0.0, 0.0))
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((L, 0, 0), (1, 0, 0))


@activate(Group="Elbow", TooltipShort="Built-in CDBBEND", TooltipLong="Built-in CDBBEND (Decompiled from varmain/dummy_var.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(ID=STRING, TooltipShort="组件标识")
def CDCYLINDER(s, D=116.0, L=300.0, ID='CDCYLINDER', **kw):
    o1 = (CYLINDER(s, R=D / 2.0, H=L, O=0.0)).rotateY(90.0)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((L, 0, 0), (1, 0, 0))


@activate(Group="Elbow", TooltipShort="Built-in CDBBEND", TooltipLong="Built-in CDBBEND (Decompiled from varmain/dummy_var.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(L3=LENGTH, TooltipShort="L3")
@param(A=ANGLE, TooltipShort="A")
@param(ID=STRING, TooltipShort="组件标识")
def CDCTEE(s, D1=116.0, D2=0.0, D3=0.0, L1=150.0, L2=0.0, L3=0.0, A=90.0, ID='CDCTEE', **kw):
    if D2 == 0.0:
        D2 = D1
    if D3 == 0.0:
        D3 = D1
    if L2 == 0.0:
        L2 = L1
    if L3 == 0.0:
        L3 = L1
    o0 = CYLINDER(s, R=D1 * 0.01, H=D1 * 0.01, O=0.0)
    o1 = CPTS(s, D1=D1, D2=D2, D3=D3, L1=L1, L2=L2, L3=L3, A=A, OF=0)
    pA1 = o1.pointAt(0)
    pD1 = o1.directionAt(0)
    pA2 = o1.pointAt(1)
    pD2 = o1.directionAt(1)
    pA3 = o1.pointAt(2)
    pD3 = o1.directionAt(2)
    o0.uniteWith(o1)
    s.setPoint(pA1, pD1)
    s.setPoint(pA2, pD2)
    s.setPoint(pA3, pD3)


@activate(Group="Elbow", TooltipShort="Built-in CDBBEND", TooltipLong="Built-in CDBBEND (Decompiled from varmain/dummy_var.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(L3=LENGTH, TooltipShort="L3")
@param(A=ANGLE, TooltipShort="A")
@param(ID=STRING, TooltipShort="组件标识")
def CDBTEE(s, D1=116.0, D2=0.0, D3=0.0, L1=150.0, L2=0.0, L3=0.0, A=90.0, ID='CDBTEE', **kw):
    if D2 == 0.0:
        D2 = D1
    if D3 == 0.0:
        D3 = D1
    if L2 == 0.0:
        L2 = L1
    if L3 == 0.0:
        L3 = L1
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    R3 = D3 / 2.0
    o0 = CYLINDER(s, R=D1 * 0.01, H=D1 * 0.01, O=0.0)
    H = L1 + L2
    if D1 == D2:
        o1 = BOX(s, W=H, H=D1, L=D1).rotateY(270).translate(((H / 2.0) - L1, 0, 0))
    else:
        if D2 > D1:
            o1 = ((PYRAMID(s, L=D2, W=D2, H=H, HT=(H * D2) / (D2 - D1))).rotateY(-90.0)).translate((L2, 0, 0))
        else:
            o1 = ((PYRAMID(s, L=D1, W=D1, H=H, HT=(H * D1) / (D1 - D2))).rotateY(90.0)).translate((-L1, 0, 0))
    A = A - 90.0
    if (D3 <= D1) and (D3 <= D2):
        o2 = (BOX(s, W=D3, H=D3, L=L3).translate((0, L3 / 2.0, 0))).rotateZ(A)
        o3 = None
    else:
        if D1 > D2:
            D4 = D2
        else:
            D4 = D1
        H = D4 / 2.0
        L = L3 - H
        o2 = (BOX(s, W=D3, H=D3, L=L).translate((0, (L / 2.0) + H, 0))).rotateZ(A)
        o3 = (((PYRAMID(s, L=D3, W=D3, H=H, HT=(H * D3) / (D3 - D4))).rotateX(90.0)).translate((0, H, 0))).rotateZ(A)
    o0.uniteWith(o1)
    o1.erase()
    o0.uniteWith(o2)
    o2.erase()
    if o3:
        o0.uniteWith(o3)
        o3.erase()
    pP3 = mTransform().rotateZ(asRadiants(A)) * mPoint(0, L3, 0)
    pD3 = mTransform().rotateZ(asRadiants(A)) * mVector(0, 1, 0)
    s.setPoint((-L1, 0, 0), (-1, 0, 0))
    s.setPoint((L2, 0, 0), (1, 0, 0))
    s.setPoint(pP3, pD3)


@activate(Group="Elbow", TooltipShort="Built-in CDBBEND", TooltipLong="Built-in CDBBEND (Decompiled from varmain/dummy_var.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(D4=LENGTH, TooltipShort="D4")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(L3=LENGTH, TooltipShort="L3")
@param(L4=LENGTH, TooltipShort="L4")
@param(A=ANGLE, TooltipShort="A")
@param(ID=STRING, TooltipShort="组件标识")
def CDCCROSS(s, D1=114.3, D2=0.0, D3=0.0, D4=0.0, L1=150.0, L2=0.0, L3=0.0, L4=0.0, A=90.0, ID='CDCCROSS', **kw):
    if D2 == 0.0:
        D2 = D1
    if D3 == 0.0:
        D3 = D1
    if D4 == 0.0:
        D4 = D3
    if L2 == 0.0:
        L2 = L1
    if L3 == 0.0:
        L3 = L1
    if L4 == 0.0:
        L4 = L3
    o0 = CYLINDER(s, R=D1 * 0.01, H=D1 * 0.01, O=0.0)
    o1 = CPXX(s, D1=D1, D2=D2, D3=D3, D4=D4, L1=L1, L2=L2, L3=L3, L4=L4, A=A, OF=0.0)
    pA1 = o1.pointAt(0)
    pD1 = o1.directionAt(0)
    pA2 = o1.pointAt(1)
    pD2 = o1.directionAt(1)
    pA3 = o1.pointAt(2)
    pD3 = o1.directionAt(2)
    pA4 = o1.pointAt(3)
    pD4 = o1.directionAt(3)
    o0.uniteWith(o1)
    s.setPoint(pA1, pD1)
    s.setPoint(pA2, pD2)
    s.setPoint(pA3, pD3)
    s.setPoint(pA4, pD4)


@activate(Group="Elbow", TooltipShort="Built-in CDBBEND", TooltipLong="Built-in CDBBEND (Decompiled from varmain/dummy_var.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(D4=LENGTH, TooltipShort="D4")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(L3=LENGTH, TooltipShort="L3")
@param(L4=LENGTH, TooltipShort="L4")
@param(A=ANGLE, TooltipShort="A")
@param(ID=STRING, TooltipShort="组件标识")
def CDBCROSS(s, D1=114.3, D2=0.0, D3=0.0, D4=0.0, L1=150.0, L2=0.0, L3=0.0, L4=0.0, A=90.0, ID='CDBCROSS', **kw):
    if D2 == 0.0:
        D2 = D1
    if D3 == 0.0:
        D3 = D1
    if D4 == 0.0:
        D4 = D3
    if L2 == 0.0:
        L2 = L1
    if L3 == 0.0:
        L3 = L1
    if L4 == 0.0:
        L4 = L3
    vC = CPXXCORRV(D1=D1, D2=D2, D3=D3, D4=D4, L1=L1, L2=L2, L3=L3, L4=L4, A=A, OF=0.0, L11=0.0, I1=0.0, L12=0.0, I2=0.0, L13=0.0, I3=0.0, L14=0.0, I4=0.0, Ever=None, FN=None, CPSTYPE=None)
    o0 = CYLINDER(s, R=D1 * 0.01, H=D1 * 0.01, O=0.0)
    if vC[0] == vC[1]:
        o1 = BOX(s, W=vC[15], H=D1, L=D1).rotateY(270).translate(((vC[15] / 2.0) - vC[4], 0, 0))
    else:
        if D2 > D1:
            o1 = ((PYRAMID(s, L=D2, W=D2, H=vC[15], HT=(vC[15] * D2) / (D2 - D1))).rotateY(-90.0)).translate((vC[5], 0, 0))
        else:
            o1 = ((PYRAMID(s, L=D1, W=D1, H=vC[15], HT=(vC[15] * D1) / (D1 - D2))).rotateY(90.0)).translate((-vC[4], 0, 0))
    if vC[2] == vC[3]:
        o2 = (BOX(s, W=D3, H=D3, L=vC[16]).translate((0, (vC[16] / 2.0) - vC[7], 0))).rotateZ(vC[17])
    else:
        if D4 > D3:
            o2 = (((PYRAMID(s, L=D4, W=D4, H=vC[16], HT=(vC[16] * D4) / (D4 - D3))).rotateX(-90.0)).translate((0, -vC[7], 0))).rotateZ(vC[17])
        else:
            o2 = (((PYRAMID(s, L=D3, W=D3, H=vC[16], HT=(vC[16] * D3) / (D3 - D4))).rotateX(90.0)).translate((0, vC[6], 0))).rotateZ(vC[17])
    o0.uniteWith(o1)
    o1.erase()
    o0.uniteWith(o2)
    o2.erase()
    s.setPoint(vC[18], vC[22], vC[66])
    s.setPoint(vC[19], vC[23], vC[67])
    s.setPoint(vC[20], vC[24], vC[68])
    s.setPoint(vC[21], vC[25], vC[69])


@activate(Group="Elbow", TooltipShort="Built-in CDBBEND", TooltipLong="Built-in CDBBEND (Decompiled from varmain/dummy_var.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(R=LENGTH, TooltipShort="R")
@param(A=ANGLE, TooltipShort="A")
@param(ID=STRING, TooltipShort="组件标识")
def CDCBEND(s, D=114.3, R=150.0, A=90.0, ID='CDCBEND', **kw):
    if R <= (D / 2.0):
        R = (D / 2.0) + 0.0001
    o1 = CPB(s, D=D, D2=D, R=R, A=A, OF=0.0)
    pA1 = o1.pointAt(0)
    pD1 = o1.directionAt(0)
    pA2 = o1.pointAt(1)
    pD2 = o1.directionAt(1)
    o0 = ((CYLINDER(s, R=(D * 0.01) / 2.0, H=R * 0.01)).rotateY(-90)).translate(pA1)
    o0.uniteWith(o1)
    o1.erase()
    s.setPoint(pA1, pD1, 0.0)
    s.setPoint(pA2, pD2, 0.0)


@activate(Group="Elbow", TooltipShort="Built-in CDBBEND", TooltipLong="Built-in CDBBEND (Decompiled from varmain/dummy_var.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(R=LENGTH, TooltipShort="R")
@param(A=ANGLE, TooltipShort="A")
@param(ID=STRING, TooltipShort="组件标识")
def CDBBEND(s, D=114.3, R=150.0, A=90.0, ID='CDBBEND', **kw):
    if R <= (D / 2.0):
        R = (D / 2.0) + 0.0001
    if A > 180.0:
        A = 180.0
    mY = R
    if areEqual(A, 90.0):
        mX = R
        sX = 0.0
        sY = R
        dX = 0.0
        dY = 1.0
    else:
        if areEqual(A, 180.0):
            mX = R
            sX = R
            sY = R * 2.0
            dX = 1.0
            dY = 0.0
        else:
            mX = (tan(asRadiants(A) / 2.0)) * R
            bA = 180.0 - ((90.0 - (A / 2.0)) * 2.0)
            sX = -cos(asRadiants(bA)) * mX
            sY = sin(asRadiants(bA)) * mX
            if A > 90.0:
                dX = cos(asRadiants(180.0 - A))
                dY = sqrt(pow(1.0, 2.0) - pow(dX, 2.0))
            else:
                dY = cos(asRadiants((180.0 - A) - 90.0))
                dX = -(sqrt(pow(1.0, 2.0) - pow(dY, 2.0)))
    o1 = (CYLINDER(s, R=R + (D / 2.0), H=D)).translate((mX, mY, -(D / 2.0)))
    o2 = (CYLINDER(s, R=R - (D / 2.0), H=D)).translate((mX, mY, -(D / 2.0)))
    o1.subtractFrom(o2)
    o2.erase()
    sL = R + (D / 2.0)
    sL2 = sL / 2.0
    s1 = BOX(s, W=D, H=sL, L=sL).translate((sL2 + mX, sL2 - (D / 2.0), 0.0))
    s2 = (BOX(s, W=D, H=sL, L=sL).translate((sL2, sL2, 0.0)).rotateZ(180.0 - A)).translate((mX, (-(D / 2.0)) + sL, 0.0))
    s1.uniteWith(s2)
    s2.erase()
    if A < 180.0:
        s2 = BOX(s, W=D, H=sL, L=sL).translate((sL2 + mX, (sL2 - (D / 2.0)) + sL, 0.0))
        s1.uniteWith(s2)
        s2.erase()
    if A < 90.0:
        s2 = BOX(s, W=D, H=sL, L=sL).translate((-sL2 + mX, (sL2 - (D / 2.0)) + sL, 0.0))
        s1.uniteWith(s2)
        s2.erase()
    o1.subtractFrom(s1)
    s1.erase()
    s.setPoint(mPoint(mX, 0.0, 0.0), mVector(1.0, 0.0, 0.0), 0.0)
    s.setPoint(mPoint(sX, sY, 0.0), mVector(dX, dY, 0.0), 0.0)
