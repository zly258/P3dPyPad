# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.arcsub.cpb_util import *


@activate(Group="Elbow", TooltipShort="Built-in CPBN", TooltipLong="Built-in CPBN (Decompiled from varmain/arcsub/cpbnsub/cpbn.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(D2=LENGTH, TooltipShort="D2")
@param(R=LENGTH, TooltipShort="R")
@param(A=ANGLE, TooltipShort="A")
@param(OF=LENGTH, TooltipShort="OF")
@param(ND=LENGTH, TooltipShort="ND")
@param(NL=LENGTH, TooltipShort="NL")
@param(NOF=LENGTH, TooltipShort="NOF")
@param(ID=STRING, TooltipShort="组件标识")
def CPBN(s, D=114.3, D2=0.0, R=175.0, A=90.0, OF=-1.0, ND=76.1, NL=0.0, NOF=-1.0, ID='CPBN', **kw):
    if D2 <= 0.0:
        D2 = D
    if R <= (D / 2.0):
        R = (D / 2.0) + 0.0001
    o0 = ARC3D2(s, D=D / 2.0, D2=D2 / 2.0, R=R, A=A)
    Pts = CPB_CalcPts(oA=o0, A=A, L1=None, L2=None, D=D, NL=NL)
    arc3d2TMP = ((CYLINDER(s, R=(D * 0.01) / 2.0, H=R * 0.01)).rotateY(-90)).translate(Pts[8])
    arc3d2TMP.uniteWith(o0)
    o0.erase()
    o0 = arc3d2TMP
    if ND > 0.0:
        if ND > D:
            o1 = ((CONE(s, R1=ND / 2.0, R2=D / 2.0, H=Pts[12], E=0.0)).rotateY(90)).translate((Pts[4].x() - Pts[12], Pts[4].y(), Pts[4].z()))
        else:
            o1 = ((CYLINDER(s, R=ND / 2.0, H=Pts[12], O=0.0)).rotateY(-90.0)).translate(Pts[4])
        o0.uniteWith(o1)
        o1.erase()
    if PnP3dACPAdapterIgnoreWallThickness:
        NOF = 0.0
    OF = getThickness(D=D, OF=OF)
    if (not (OF == 0.0)) or (not (NOF == 0.0)):
        O1 = getInsideDiameter(D=D, OF=OF, Ever=1)
        O2 = getInsideDiameter(D=D2, OF=OF, Ever=1)
        o2 = ARC3D2(s, D=O1 / 2.0, D2=O2 / 2.0, R=R, A=A)
        arc3d2TMP = ((CYLINDER(s, R=(O1 * 0.01) / 2.0, H=R * 0.01)).rotateY(-90)).translate(Pts[8])
        arc3d2TMP.uniteWith(o2)
        o2.erase()
        o2 = arc3d2TMP
    else:
        o2 = None
    if ((o2) and (ND > 0.0)) and (not (NOF == 0.0)):
        NO = getInsideDiameter(D=ND, OF=NOF, Ever=1)
        if ND > D:
            o3 = ((CONE(s, R1=NO / 2.0, R2=O1 / 2.0, H=Pts[12], E=0.0)).rotateY(90)).translate((Pts[4].x() - Pts[12], Pts[4].y(), Pts[4].z()))
        else:
            o3 = ((CYLINDER(s, R=NO / 2.0, H=Pts[12], O=0.0)).rotateY(-90.0)).translate(Pts[4])
        o2.uniteWith(o3)
        o3.erase()
    if o2:
        o0.subtractFrom(o2)
        o2.erase()
    s.setPoint(Pts[4], Pts[6], 0.0)
    s.setPoint(Pts[5], Pts[7], 0.0)
    s.setPoint(Pts[13], Pts[14])
