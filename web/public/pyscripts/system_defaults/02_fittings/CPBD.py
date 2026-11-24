# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.arcsub.cpb_util import *
from varmain.divsub.cste_t import *


@activate(Group="Elbow", TooltipShort="Built-in CPBD", TooltipLong="Built-in CPBD (Decompiled from varmain/arcsub/cpbdsub/cpbd.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(D2=LENGTH, TooltipShort="D2")
@param(R=LENGTH, TooltipShort="R")
@param(A=ANGLE, TooltipShort="A")
@param(DFH=LENGTH, TooltipShort="DFH")
@param(DFD=LENGTH, TooltipShort="DFD")
@param(DFT=INT, TooltipShort="DFT")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPBD(s, D=114.3, D2=0.0, R=175.0, A=90.0, DFH=0.0, DFD=0.0, DFT=0, OF=-1.0, ID='CPBD', **kw):
    if R <= (D / 2.0):
        R = (D / 2.0) + 0.0001
    if D2 <= 0.0:
        D2 = D
    o0 = ARC3D2(s, D=D / 2.0, D2=D2 / 2.0, R=R, A=A)
    Pts = CPB_CalcPts(o0, A, None, None)
    OF = getThickness(D=D, OF=OF)
    arc3d2TMP = ((CYLINDER(s, R=(D * 0.01) / 2.0, H=R * 0.01)).rotateY(-90)).translate(Pts[8])
    arc3d2TMP.uniteWith(o0)
    o0.erase()
    o0 = arc3d2TMP
    if DFH <= 0.0:
        DFH = D + D2
    if DFD <= 0.0:
        DFD = D
    if D2 <= D:
        xR = D2 / 2.0
    else:
        xR = D / 2.0
    sPY = (sqrt((pow(R + xR, 2.0)) - (pow(R * (tan(asRadiants(A) / 2.0)), 2.0)))) - R
    sH = DFH - sPY
    sT = DFD * 0.1
    stH = xR
    if DFD <= (xR * 2.0):
        stH = DFD / 2.0
    oD2 = None
    if (DFT == 0) or (DFT == 1):
        stT2 = sT / 2.0
        stH = sqrt(pow(stH, 2.0) - (pow(sT / 2.0, 2.0)))
        sPX = (sqrt((pow(R + xR, 2.0)) - (pow((R * (tan(asRadiants(A) / 2.0))) + stH, 2.0)))) - R
        oD1 = (CSTE_T(s, H=stH + stT2, W=stH * 2.0, L=DFH - sPX, T=sT)).translate((0, (stH / 2.0) - (stT2 / 2.0), -DFH))
        oD3 = ((CSTE_T(s, H=(stH + stT2) + sPX, W=stH * 2.0, L=DFH - sPX, T=sT)).translate((0, (stH / 2.0) - (stT2 / 2.0), -DFH))).rotateZ(180.0)
        if DFT == 0:
            oD2 = ((CYLINDER(s, R=DFD / 2.0, H=sT)).rotateX(180.0)).translate((0, 0, -(DFH - sT)))
        else:
            if DFT == 1:
                oD2 = BOX(s, L=DFD, W=DFD, H=sT).rotateX(-90).rotateY(-90).translate((0.0, 0.0, -(DFH - (sT / 2.0))))
        oD2.uniteWith(oD1)
        oD1.erase()
        oD1 = oD2
        oD2 = oD3
    else:
        if DFT == 2:
            oD1 = (CYLINDER(s, R=sT / 2.0, H=sH + (sT / 2.0))).translate((0.0, 0.0, ((sT / 2.0) - sH) - sPY))
            oD2 = ((CYLINDER(s, R=DFD / 2.0, H=sT)).rotateX(180.0)).translate((0, 0, -(DFH - sT)))
        else:
            if DFT == 3:
                oD1 = (CYLINDER(s, R=sT / 2.0, H=sH + (sT / 2.0))).translate((0.0, 0.0, ((sT / 2.0) - sH) - sPY))
                oD2 = BOX(s, L=DFD, W=DFD, H=sT).rotateX(-90).rotateY(-90).translate((0.0, 0.0, -(DFH - (sT / 2.0))))
            else:
                if DFT == 4:
                    oD1 = (CONE(s, R1=DFD / 2.0, R2=0.0, H=sH)).translate((0, 0, -sH - sPY))
                else:
                    if DFT == 5:
                        oD1 = PYRAMID(s, L=DFD, W=DFD, H=sH).translate((0, 0, -sH - sPY))
    if oD2:
        oD1.uniteWith(oD2)
        oD2.erase()
    oD1.rotateX(-90.0)
    o0.uniteWith(oD1)
    oD1.erase()
    if OF > 0.0:
        O1 = getInsideDiameter(D=D, OF=OF)
        O2 = getInsideDiameter(D=D2, OF=OF)
        o1 = ARC3D2(s, D=O1 / 2.0, D2=O2 / 2.0, R=R, A=A)
        o0.subtractFrom(o1)
        o1.erase()
    s.setPoint(Pts[4], Pts[6], 0.0)
    s.setPoint(Pts[5], Pts[7], 0.0)
