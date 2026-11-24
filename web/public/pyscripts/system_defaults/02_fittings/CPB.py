# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.arcsub.cpb_util import *


@activate(Group="Elbow", TooltipShort="CP METRIC Elbow 90.0°", TooltipLong="CP METRIC Elbow 90.0° (Decompiled from varmain/arcsub/cpbsub/cpb.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(D2=LENGTH, TooltipShort="D2")
@param(R=LENGTH, TooltipShort="R")
@param(L2=LENGTH, TooltipShort="L2")
@param(L1=LENGTH, TooltipShort="L1")
@param(A=ANGLE, TooltipShort="A")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPB(s, D=10.2, D2=10.2, R=15.3, L2=0.0, L1=0.0, A=90.0, OF=-1.0, ID='CPB', **kw):
    if R <= (D / 2.0):
        R = (D / 2.0) + 0.0001
    if D2 <= 0.0:
        D2 = D
    o0 = ARC3D2(s, D=D / 2.0, D2=D2 / 2.0, R=R, A=A)
    Pts = CPB_CalcPts(o0, A, None, None)
    a1 = Pts[1]
    a0 = Pts[0]
    Pts4 = Pts[4]
    Pts5 = Pts[5]
    Pts6 = Pts[6]
    Pts7 = Pts[7]
    Pts = CPB_CalcPts(o0, A, (L1 + a1) - a1, (L2 + a0) - a0)
    HLeft = L2
    HRight = L1
    if HLeft <= R:
        Pts[5] = Pts5
        Pts[7] = Pts7
        HLeft = R * 0.01
        arc3d2TMP = ((CYLINDER(s, R=(D * 0.01) / 2.0, H=R * 0.01)).rotateY(-90)).translate(Pts[8])
        arc3d2TMP.uniteWith(o0)
        o0.erase()
        o0 = arc3d2TMP
    else:
        arc3d2TMP = (((CYLINDER(s, R=D2 / 2.0, H=HLeft - a1)).rotateX(-90)).rotateZ(90 - A)).translate(Pts[9])
        arc3d2TMP.uniteWith(o0)
        o0.erase()
        o0 = arc3d2TMP
    if HRight <= R:
        Pts[4] = Pts4
        Pts[6] = Pts6
        HRight = R * 0.01
    else:
        arc3d2TMP = ((CYLINDER(s, R=D / 2.0, H=HRight - a0)).rotateY(90)).translate(Pts[8])
        arc3d2TMP.uniteWith(o0)
        o0.erase()
        o0 = arc3d2TMP
    OF = getThickness(D=D, OF=OF)
    if OF > 0.0:
        O1 = getInsideDiameter(D=D, OF=OF)
        O2 = getInsideDiameter(D=D2, OF=OF)
        o1 = ARC3D2(s, D=O1 / 2.0, D2=O2 / 2.0, R=R, A=A)
        o0.subtractFrom(o1)
        o1.erase()
    s.setPoint(Pts[4], Pts[6], 0.0)
    s.setPoint(Pts[5], Pts[7], 0.0)
