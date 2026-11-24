# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.arcsub.cpb_util import *
from varmain.flangesub.cpfwo import *


@activate(Group="Elbow", TooltipShort="Nozzle, angle (45°, ASME B16.9), flanged, FF, 150, ASME B16.47", TooltipLong="Nozzle, angle (45°, ASME B16.9), flanged, FF, 150, ASME B16.47 (Decompiled from varmain/arcsub/cpbsub/cpb_f_f_.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(D2=LENGTH, TooltipShort="D2")
@param(R=LENGTH, TooltipShort="R")
@param(A=ANGLE, TooltipShort="A")
@param(OF=LENGTH, TooltipShort="OF")
@param(L2=LENGTH, TooltipShort="L2")
@param(L1=LENGTH, TooltipShort="L1")
@param(L31=LENGTH, TooltipShort="L31")
@param(B31=LENGTH, TooltipShort="B31")
@param(D31=LENGTH, TooltipShort="D31")
@param(D41=LENGTH, TooltipShort="D41")
@param(W1=LENGTH, TooltipShort="W1")
@param(O31=INT, TooltipShort="O31")
@param(L32=LENGTH, TooltipShort="L32")
@param(B32=LENGTH, TooltipShort="B32")
@param(D32=LENGTH, TooltipShort="D32")
@param(D42=LENGTH, TooltipShort="D42")
@param(W2=LENGTH, TooltipShort="W2")
@param(O32=INT, TooltipShort="O32")
@param(ID=STRING, TooltipShort="组件标识")
def CPB_F_F_(s, D=0.84, D2=0.0, R=1.4968, A=45.0, OF=-1.0, L2=0.0, L1=0.0, L31=1.81, B31=0.38, D31=3.5, D41=1.19, W1=0.0, O31=0, L32=44.0, B32=20.0, D32=200.0, D42=165.0, W2=0.0, O32=0, ID='CPB_F_F_', **kw):
    noLeft = 0
    noRight = 0
    if D2 <= 0.0:
        D2 = D
    OF = getThickness(D=D, OF=OF, Ever=1)
    if L31 == -2:
        noLeft = 1
        L31 = 0.0
    if L32 == 0.0:
        L32 = L31
    if (L32) and (L32 == -2):
        noRight = 1
        L32 = 0.0
    if D32 <= 0.0:
        D32 = D31
    if D42 <= 0.0:
        D42 = D41
    if B32 <= 0.0:
        B32 = B31
    if R <= (D / 2.0):
        R = (D / 2.0) + 0.0001
    if W1 == -1:
        W1 = D + (OF * 2.0)
    else:
        if W1 <= 0.0:
            W1 = D31
    if W2 == -1:
        W2 = D2 + (OF * 2.0)
    else:
        if W2 <= 0.0:
            W2 = D32
    o0 = ARC3D2(s, D=D / 2.0, D2=D2 / 2.0, R=R, A=A)
    Pts = CPB_CalcPts(o0, A, None, None)
    xL31 = Pts[0]
    yL31 = L31
    zL31 = 0.0
    xL32 = Pts[1]
    yL32 = L32
    zL32 = 0.0
    if (L31) and (O31 == 0):
        xL31 = Pts[0] + L31
    else:
        if L31:
            yL31 = 0.0
            zL31 = -L31
    if (L32) and (O32 == 0):
        xL32 = Pts[1] + L32
    else:
        if L32:
            yL32 = 0.0
            zL32 = -L32
    if OF > 0.0:
        DI1 = getInsideDiameter(D=D, OF=OF, Ever=1)
        DI2 = getInsideDiameter(D=D2, OF=OF, Ever=1)
    else:
        DI1 = D
        DI2 = D2
    HLeft = L2 - xL32
    HRight = L1 - xL31
    Pts8 = Pts[8]
    Pts9 = Pts[9]
    if HLeft > 0:
        xL32 = HLeft + xL32
    if HRight > 0:
        xL31 = HRight + xL31
    Pts = CPB_CalcPts(o0, A, xL31 - L31, xL32 - L32)
    Pts10 = Pts[10]
    Pts11 = Pts[11]
    Pts = CPB_CalcPts(o0, A, xL31, xL32)
    if HLeft > 0:
        Pts9 = Pts[9]
        arc3d2TMP = (((CYLINDER(s, R=D2 / 2.0, H=HLeft)).rotateX(-90)).rotateZ(90 - A)).translate(Pts9)
        arc3d2TMP.uniteWith(o0)
        o0.erase()
        o0 = arc3d2TMP
    if HRight > 0:
        Pts8 = Pts[8]
        arc3d2TMP = ((CYLINDER(s, R=D / 2.0, H=HRight)).rotateY(90)).translate(Pts8)
        arc3d2TMP.uniteWith(o0)
        o0.erase()
        o0 = arc3d2TMP
    arc3d2TMP = ((CYLINDER(s, R=(D * 0.01) / 2.0, H=R * 0.01)).rotateY(-90)).translate(Pts8)
    arc3d2TMP.uniteWith(o0)
    o0.erase()
    o0 = arc3d2TMP
    if noLeft == 0:
        if O31 == 0:
            DO = D
        else:
            DO = DI1
        if HRight > 0:
            Pts8 = Pts10
        oF1 = CPFWO(s, L=L31, B=B31, D1=D31, D2=DO, D3=D41, W=W1).rotateX(90.0).rotateZ(180.0).translate((yL31, 0.0, 0.0)).rotateZ(asDegrees(Pts[2])).translate(Pts8)
        if O31 == 0:
            oC1 = ((((CYLINDER(s, R=D / 2.0, H=L31, O=DI1 / 2.0)).rotateY(90)).translate((zL31, 0.0, 0.0))).rotateZ(asDegrees(Pts[2]))).translate(Pts8)
            oC1.uniteWith(oF1)
            oF1.erase()
            oF1 = oC1
        o0.uniteWith(oF1)
        oF1.erase()
    if noRight == 0:
        if O32 == 0:
            DO = D2
        else:
            DO = DI2
        if HLeft > 0:
            Pts9 = Pts11
        oF2 = CPFWO(s, L=L32, B=B32, D1=D32, D2=DO, D3=D42, W=W2).rotateX(90.0).rotateZ(180.0).translate((yL32, 0.0, 0.0)).rotateZ(asDegrees(Pts[3])).translate(Pts9)
        if O32 == 0:
            oC2 = ((((CYLINDER(s, R=D2 / 2.0, H=L32, O=DI2 / 2.0)).rotateY(90)).translate((zL32, 0.0, 0.0))).rotateZ(asDegrees(Pts[3]))).translate(Pts9)
            oC2.uniteWith(oF2)
            oF2.erase()
            oF2 = oC2
        o0.uniteWith(oF2)
        oF2.erase()
    if OF > 0.0:
        o3 = ARC3D2(s, D=DI1 / 2.0, D2=DI2 / 2.0, R=R, A=A)
        o0.subtractFrom(o3)
        o3.erase()
    if W1 >= D31:
        wA1 = 0.0
    else:
        wA1 = 90.0
    if W2 >= D32:
        wA2 = 0.0
    else:
        wA2 = 90.0
    s.setPoint(Pts[4], Pts[6], wA1)
    s.setPoint(Pts[5], Pts[7], wA2)
