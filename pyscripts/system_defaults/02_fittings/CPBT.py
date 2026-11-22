# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.arcsub.cpb_util import *


@activate(Group="Elbow", TooltipShort="Built-in CPBT", TooltipLong="Built-in CPBT (Decompiled from varmain/arcsub/cpbtsub/cpbt.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(D2=LENGTH, TooltipShort="D2")
@param(R=LENGTH, TooltipShort="R")
@param(A=ANGLE, TooltipShort="A")
@param(OF=LENGTH, TooltipShort="OF")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(S=INT, TooltipShort="S")
@param(ID=STRING, TooltipShort="组件标识")
def CPBT(s, D=114.3, D2=0.0, R=175.0, A=90.0, OF=-1.0, L1=200.0, L2=300.0, S=4, ID='CPBT', **kw):
    noLeft = 0
    noRight = 0
    if D2 <= 0.0:
        D2 = D
    if L1 == -2:
        noLeft = 1
        L1 = None
    if L2 == 0.0:
        L2 = L1
    if (L2) and (L2 == -2):
        noRight = 1
        L2 = None
    if S == 0:
        S = 4
    if R <= (D / 2.0):
        R = (D / 2.0) + 0.0001
    o0 = ARC3DS2(s, D=D, D2=D2, R=R, A=A, S=S)
    Pts = CPB_CalcPts(o0, A, L1, L2, 0.0, 0.0)
    OF = getThickness(D=D, OF=OF)
    sD = getInsideDiameter(D=D, OF=OF, Ever=1, mustCalc=True) * 0.0001
    o1 = ((CYLINDER(s, R=D / 2.0, H=sD, O=(D - sD) / 2.0)).rotateY(-90)).translate(o0.pointAt(0))
    o1.uniteWith(o0)
    o0.erase()
    o0 = o1
    if not (OF == 0.0):
        O = getInsideDiameter(D=D, OF=OF)
        O2 = getInsideDiameter(D=D2, OF=OF)
        o1 = ARC3DS2(s, D=O, D2=O2, R=R, A=A, S=S)
        o0.subtractFrom(o1)
        o1.erase()
    else:
        O = 0.0
        O2 = 0.0
    if (noLeft == 0) and (Pts[0] > 0.0):
        oL1 = (((CYLINDER(s, R=D / 2.0, H=Pts[0], O=O / 2.0)).rotateY(90.0)).rotateZ(asDegrees(Pts[2]))).translate(Pts[8])
        o0.uniteWith(oL1)
        oL1.erase()
    if (noRight == 0) and (Pts[1] > 0.0):
        oL2 = (((CYLINDER(s, R=D2 / 2.0, H=Pts[1], O=O2 / 2.0)).rotateY(90.0)).rotateZ(asDegrees(Pts[3]))).translate(Pts[9])
        o0.uniteWith(oL2)
        oL2.erase()
    s.setPoint(Pts[4], Pts[6], 0.0)
    s.setPoint(Pts[5], Pts[7], 0.0)
