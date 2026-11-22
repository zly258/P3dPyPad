# -*- coding: utf-8 -*-
"""Plant 3D Basic Utility Functions (`varmain.var_basic`).

Aligned 100% with the disassembled bytecode in AutoCAD Plant 3D's `variants.zip`
(`varmain/var_basic.pyc` & `varmain/primitiv.pyc`).
"""

import math
from math import pow, atan, tan, cos, pi
from ..core.math3d import mPoint, mVector, areEqual, asDegrees, asRadiants, sqrt, acos, asin
from .native import BOX, CYLINDER, CONE, HALFSPHERE
from .extended import ARC3D, ARC3D2, ARC3DS, SPHERE, ELLIPSE, LOFT

defaultPipeLength = 100.0
defaultNozzleLength = 100.0
defaultTolerance = 0.001
PnP3dACPAdapterIgnoreWallThickness = True


def PIPE(s, D=114.3, L=100.0, ID="PIPE", **kw):
    """Plant 3D PIPE(s, D, L, ID='PIPE') from varmain/primitiv.pyc."""
    D = max(1e-3, float(D))
    if L is None or float(L) <= 0.0:
        L = defaultPipeLength
    L = max(1e-3, float(L))
    o = CYLINDER(s, R=D / 2.0, H=L, O=0.0).rotateY(90.0)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0))
    return o


def linkFuncToDbman(func):
    return None


def CORNERBOX(s, L=300.0, W=200.0, H=100.0, ID="CORNERBOX", **kw):
    """Exact Plant 3D CORNERBOX (`varmain/var_basic.pyc`):
    `BOX(s, L=L, W=W, H=H).rotateX(-90).rotateY(-90).translate((L / 2.0, W / 2.0, H / 2.0))`
    Places the minimum corner at (0, 0, 0), extending [0, L] along X, [0, W] along Y, [0, H] along Z.
    """
    L = float(L)
    W = float(W)
    H = float(H)
    return BOX(s, L=L, W=W, H=H).rotateX(-90).rotateY(-90).translate((L / 2.0, W / 2.0, H / 2.0))


def CON_OF_MULT(Val=100.0):
    return float(Val) * 1.1


def CON_OF_DIV(Val=100.0):
    return (float(Val) / CON_OF_MULT(100.0)) * 100.0


def CON_OM_MULT(Val=100.0):
    return CON_OF_DIV(Val)


def CON_OM_DIV(Val=100.0):
    return (float(Val) / CON_OM_MULT(100.0)) * 100.0


def getThickness(D=114.3, OF=0.0, Ever=None, mustCalc=False, **kw):
    D = float(D) if D is not None else 0.0
    OF = float(OF) if OF is not None else 0.0
    if PnP3dACPAdapterIgnoreWallThickness and not mustCalc:
        Ever = None
        OF = 0.0
    if (Ever and OF == 0.0) or OF < 0.0:
        OF = (D - CON_OF_DIV(D)) / 2.0
    return OF if OF > 0.0 else 0.0


def getInsideDiameter(D=114.3, OF=0.0, Ever=None, mustCalc=False, **kw):
    D = float(D) if D is not None else 0.0
    OF = getThickness(D=D, OF=OF, Ever=Ever, mustCalc=mustCalc)
    if OF > 0.0:
        retVal = D - (OF * 2.0)
        if retVal <= 0.0:
            OF = getThickness(D=D, OF=-1.0, Ever=Ever, mustCalc=mustCalc)
            retVal = D - (OF * 2.0)
        return retVal
    return 0.0


def CON_OF(s, D1=114.3, D2=0.0, L=100.0, OF=0.0, NOEXT=None, ID="CON_OF", **kw):
    OF = getThickness(D=D1, OF=OF, Ever=1)
    sF = getThickness(D=D1, OF=OF, Ever=1, mustCalc=True)
    if D2 is None or D2 <= 0.0 or D2 < D1:
        D2 = D1 + (sF * 2.0)
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    expand = 0.0 if NOEXT else sF
    if OF <= 0.0:
        R1 = 0.0
    return CYLINDER(s, R=R2, H=L + expand, O=R1).rotateY(90).translate((-expand, 0.0, 0.0))


def CON_OM(s, D1=114.3, D2=0.0, L=100.0, OF=0.0, ID="CON_OM", **kw):
    OF = getThickness(D=D1, OF=OF, Ever=1)
    if D2 is None or D2 <= 0.0 or D2 > D1:
        D2 = getInsideDiameter(D=D1, OF=OF, Ever=1, mustCalc=True)
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    o0 = CONE(s, R1=R1, R2=R2, H=L, E=0.0).rotateY(90)
    if OF > 0.0:
        o1 = CYLINDER(s, R=R2, H=L, O=0.0).rotateY(90)
        o0.subtractFrom(o1)
        o1.erase()
    return o0


def CON_MJ(s, D1=114.3, D2=0.0, L=100.0, OF=0.0, NOEXT=None, ID="CON_MJ", **kw):
    OF = getThickness(D=D1, OF=OF, Ever=1)
    sF = getThickness(D=D1, OF=OF, Ever=1, mustCalc=True)
    if D2 is None or D2 <= 0.0 or D2 < D1:
        D2 = D1 + (sF * 2.0)
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    R3 = R2 + (R2 - R1)
    expand = 0.0 if NOEXT else sF
    if OF <= 0.0:
        R1 = 0.0
    o0 = CYLINDER(s, R=R2, H=L + expand, O=R1).rotateY(90).translate((-expand, 0.0, 0.0))
    o1 = CYLINDER(s, R=R3, H=sF, O=R2).rotateY(90).translate((L - sF, 0.0, 0.0))
    o0.uniteWith(o1)
    o1.erase()
    return o0


def CON_PL(s, D1=114.3, D2=0.0, L=100.0, OF=0.0, ID="CON_PL", **kw):
    OF = getThickness(D=D1, OF=OF, Ever=1)
    if D2 is None or D2 <= 0.0 or D2 > D1:
        D2 = getInsideDiameter(D=D1, OF=OF, Ever=1, mustCalc=True)
    R1 = D1 / 2.0
    R2 = D2 / 2.0
    o0 = CYLINDER(s, R=R1, H=L, O=0.0).rotateY(90)
    if OF > 0.0:
        o1 = CYLINDER(s, R=R2, H=L, O=0.0).rotateY(90)
        o0.subtractFrom(o1)
        o1.erase()
    return o0


def ARC3D2_(s, D=100.0, D2=0.0, R=300.0, A=90.0, ID="ARC3D2_", **kw):
    sT = ARC3D2(s, D=D, D2=D2, R=R, A=A)
    s.setPoint(sT.pointAt(0), sT.directionAt(0))
    s.setPoint(sT.pointAt(1), sT.directionAt(1))
    return sT


def CON_Q__Calc(CW=40.0, CH=0.0, CC=0.0, O=20.0):
    retVal = [CW]
    if CH <= 0.0:
        CH = CW * 0.2
    retVal.append(CH)
    if CC <= 0.0:
        CC = CH - (CH * 0.25)
    retVal.append(CC)
    D2 = CW * 0.75
    if O <= 0.0 or O >= D2:
        O = getInsideDiameter(D2, OF=0.0, Ever=1)
    retVal.append(O)
    R1 = CW / 2.0
    retVal.append(R1)
    R2 = (CW * 0.75) / 2.0
    retVal.append(R2)
    L1 = CC + CH
    retVal.append(L1)
    L2 = L1 + CH
    retVal.append(L2)
    L3 = L1 - CC
    retVal.append(L3)
    R3 = O / 2.0
    retVal.append(R3)
    L4 = ((CH * 2.0) + CW) / 2.0
    retVal.append(L4)
    H1 = (CH * 2.0) + CC
    retVal.append(H1)
    L5 = L4 / 2.0
    retVal.append(L5)
    L6 = CH / 2.0
    retVal.append(L6)
    L7 = H1 / 2.0
    retVal.append(L7)
    H2 = CH + ((CH - CC) / 2.0)
    retVal.append(H2)
    L8 = sqrt(pow(CH, 2.0) + pow(H2, 2.0))
    retVal.append(L8)
    A0 = asDegrees(atan(CH / H2))
    retVal.append(A0)
    H3 = H1 - H2
    retVal.append(H3)
    retVal.append(L4)
    A1 = asDegrees(atan(CH / H3))
    retVal.append(A1)
    H4 = (H2 + CH) - ((CH - CC) / 2.0)
    retVal.append(H4)
    L9 = L6 / 2.0
    retVal.append(L9)
    H5 = H1 + ((CH - CC) / 2.0)
    retVal.append(H5)
    x1 = L6 + R1
    retVal.append(x1)
    x2 = (H5 / 2.0) - ((CH - CC) / 2.0)
    retVal.append(x2)
    x3 = R1 - R3
    retVal.append(x3)
    x4 = (x3 / 2.0) + R3
    retVal.append(x4)
    x5 = CH * 2.0
    retVal.append(x5)
    x6 = (x5 / 2.0) + CC
    retVal.append(x6)
    x7 = R2 + CC
    x7 = x7 + ((L4 - x7) / 2.0)
    retVal.append(x7)
    x8 = x5 + CC
    retVal.append(x8)
    sF = getThickness(D2, OF=0.0, Ever=True, mustCalc=True)
    retVal.append(sF)
    OF = getThickness(D2, OF=0.0, Ever=True)
    retVal.append(OF)
    return retVal


def CON_Q__Sub(s, CW=40.0, CH=0.0, CC=0.0, ID="CON_Q__Sub", **kw):
    vC = CON_Q__Calc(CW=CW, CH=CH, CC=CC, O=0.0)
    p2 = BOX(s, L=vC[10], W=vC[1], H=vC[11]).rotateX(-90).rotateY(-90).translate((-vC[12], -vC[13], vC[14]))
    p3 = CORNERBOX(s, L=vC[16], W=vC[16], H=vC[11]).rotateZ(180).rotateY(-vC[17]).translate((-vC[4], 0.0, 0.0))
    p4 = CORNERBOX(s, L=vC[1], W=vC[1], H=vC[19]).rotateZ(180).rotateY(vC[20]).translate((-vC[10], 0.0, vC[21]))
    p3.uniteWith(p4)
    p4.erase()
    p2.subtractFrom(p3)
    p3.erase()
    p2.translate((0.0, 0.0, vC[2]))
    return p2


def CON_Q_(s, CW=40.0, CH=0.0, CC=0.0, O=20.0, ID="CON_Q_", **kw):
    vC = CON_Q__Calc(CW=CW, CH=CH, CC=CC, O=O / 2.0)
    o1 = CYLINDER(s, R=vC[5], H=vC[6], O=0.0)
    p2 = CON_Q__Sub(s, CW=vC[0], CH=vC[1], CC=vC[2])
    p3 = CON_Q__Sub(s, CW=vC[0], CH=vC[1], CC=vC[2]).rotateZ(180.0)
    o1.uniteWith(p2)
    p2.erase()
    o1.uniteWith(p3)
    p3.erase()
    p7 = CYLINDER(s, R=vC[4], H=vC[2], O=0.0).translate((0.0, 0.0, vC[8]))
    p8 = CORNERBOX(s, L=vC[7], W=vC[4], H=vC[7])
    p9 = CORNERBOX(s, L=vC[7], W=vC[4], H=vC[7]).rotateZ(180)
    p7.subtractFrom(p8)
    p8.erase()
    p7.subtractFrom(p9)
    p9.erase()
    if vC[4] > vC[7]:
        p8a = CORNERBOX(s, L=vC[7], W=vC[4], H=vC[7]).translate((vC[7], vC[1], 0.0))
        p9a = CORNERBOX(s, L=vC[7], W=vC[4], H=vC[7]).translate((vC[7], vC[1], 0.0)).rotateZ(180.0)
        p7.subtractFrom(p8a)
        p8a.erase()
        p7.subtractFrom(p9a)
        p9a.erase()
    o1.uniteWith(p7)
    p7.erase()
    if vC[32] > 0.0:
        p4 = CYLINDER(s, R=vC[4], H=vC[1], O=0.0).translate((0.0, 0.0, vC[6]))
        p5 = CYLINDER(s, R=vC[5], H=vC[1], O=0.0).translate((0.0, 0.0, vC[7]))
        p4.uniteWith(p5)
        p5.erase()
        if (O > 0.0) and (vC[33] > 0.0):
            p6 = CYLINDER(s, R=vC[9], H=vC[7], O=0.0)
            p4.uniteWith(p6)
            p6.erase()
        o1.subtractFrom(p4)
        p4.erase()
    o1.rotateY(90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((vC[6], 0.0, 0.0), (1.0, 0.0, 0.0))
    return o1


def CON_HM(s, D=25.0, H=38.5, O2=0.0, OF=-1.0, ID="CON_HM", **kw):
    sF = getThickness(D, OF=OF, Ever=True, mustCalc=True)
    OF = getThickness(D, OF=OF, Ever=True)
    O = getInsideDiameter(D, OF=sF, Ever=1, mustCalc=True)
    if O2 is None or O2 <= 0.0:
        O2 = getInsideDiameter(O, OF=OF, Ever=1)
    o0 = CYLINDER(s, R=O / 2.0, H=H, O=0.0).rotateY(90.0)
    mCnt = max(1, int(round((H / (D * 0.3333)) + 0.49999999)))
    xH = H / mCnt
    for cnt in range(mCnt):
        oX = CONE(s, R1=D / 2.0, R2=O / 2.0, H=xH, E=0).rotateY(-90.0).translate((xH * (cnt + 1), 0.0, 0.0))
        o0.uniteWith(oX)
        oX.erase()
    o0.translate((-H, 0.0, 0.0))
    if OF > 0.0 and O2 > 0.0:
        o2 = CYLINDER(s, R=O2 / 2.0, H=H, O=0.0).rotateY(90.0).translate((-H, 0.0, 0.0))
        o0.subtractFrom(o2)
        o2.erase()
    return o0


def CSGCutOut(s, obj, D=0.0, kwdict=None, **kw):
    """Exact Plant 3D CSGCutOut(s, obj, D, kwdict) from varmain/var_basic.pyc."""
    if not isinstance(kwdict, dict):
        # Legacy 4-body call fallback
        if hasattr(obj, "subtractFrom") and hasattr(D, "subtractFrom") and hasattr(kwdict, "subtractFrom"):
            Base, Down, Out = obj, D, kwdict
            Down.subtractFrom(Base)
            Out.subtractFrom(Base)
            Base.subtractFrom(Down)
            Down.erase()
            Base.uniteWith(Out)
            Out.erase()
            return Base
        return obj
    OD = float(kwdict.get("OD", 0.0) or 0.0)
    if not OD:
        return obj
    r = OD / 2.0
    OR = float(kwdict.get("OR", 0.0) or 0.0)
    OO = kwdict.get("OO", None)
    if OR > 0:
        if OO == "B":
            offZ = OR
            offX = (OD - D) / 2.0
            oh = ARC3D(s, D=r, R=OR, A=90.0).rotateX(90.0).translate((offX, 0, -offZ))
        elif OO == "b":
            R = OR + r
            Q = (OR - r) + D
            offZ = OR - sqrt(max(0.0, (R * R) - (Q * Q)))
            offX = (OD - D) / 2.0
            oh = ARC3D(s, D=r, R=OR, A=90.0).rotateX(90.0).translate((-offX, 0, -offZ))
        elif OO == "f1":
            offZ = OR
            offY = (OD - D) / 2.0
            oh = ARC3D(s, D=r, R=OR, A=90.0).rotateX(90.0).translate((0, offY, -offZ))
        elif OO == "f2":
            offZ = OR
            offY = (OD - D) / 2.0
            oh = ARC3D(s, D=r, R=OR, A=90.0).rotateX(90.0).translate((0, -offY, -offZ))
        elif OO == "F":
            oh = BOX(s, L=OR, W=OD, H=OR)
        else:
            offZ = OR - sqrt(max((OR * (OD - D)) + (((OD * OD) - (D * D)) / 4.0), 0.0))
            oh = ARC3D(s, D=r, R=OR, A=90.0).rotateX(90.0).translate((0, 0, -offZ))
    else:
        oh = CYLINDER(s, R=r, H=4.0 * D, O=0.0).rotateY(90.0).translate((-2.0 * D, 0, 0))
        if OD > D:
            if OO == "B":
                oh.translate((0, (-(OD - D)) / 2.0, 0))
            if OO == "C":
                oh.translate((0, 0, sqrt(max(0.0, (OD * OD) - (D * D))) / 2.0))
    obj.subtractFrom(oh)
    oh.erase()
    return obj


def ARC3DS2(s, D=114.3, D2=88.9, R=175.0, A=90.0, S=4, ID="CPBS", **kw):
    if R <= (D / 2.0):
        R = (D / 2.0) + 0.0001
    if S <= 0:
        S = 4
    elif S == 1 and A > 90.0:
        S = 2
    if D2 <= 0.0:
        D2 = D
    if areEqual(A, 180.0):
        calcCenter = mPoint(R, R, 0.0)
        pP1 = mPoint(R, 0.0, 0.0)
        pD1 = mVector(1.0, 0.0, 0.0)
        pP2 = mPoint(R, R * 2.0, 0.0)
        pD2 = mVector(1.0, 0.0, 0.0)
    else:
        xAxis = R * tan(asRadiants(A / 2.0))
        calcCenter = mPoint(xAxis, R, 0.0)
        pP1 = mPoint(xAxis, 0.0, 0.0)
        pD1 = mVector(1.0, 0.0, 0.0)
        if areEqual(A, 90.0):
            pP2 = mPoint(0.0, R, 0.0)
            pD2 = mVector(0.0, 1.0, 0.0)
        else:
            alpha = A if A < 90.0 else 180.0 - A
            yCord = xAxis * cos(asRadiants(90.0 - alpha))
            xCord = sqrt(max(0.0, pow(xAxis, 2.0) - pow(yCord, 2.0)))
            lVec = 1.0
            yVec = lVec * cos(asRadiants(90.0 - alpha))
            xVec = sqrt(max(0.0, pow(lVec, 2.0) - pow(yVec, 2.0)))
            if A < 90.0:
                pP2 = mPoint(-xCord, yCord, 0.0)
                pD2 = mVector(-xVec, yVec, 0.0)
            else:
                pP2 = mPoint(xCord, yCord, 0.0)
                pD2 = mVector(xVec, yVec, 0.0)
    o0 = ARC3DS(s, D=D / 2.0, R=R, A=A, S=int(S))
    s.setPoint(pP1, pD1, 0.0)
    s.setPoint(pP2, pD2, 0.0)
    return o0
