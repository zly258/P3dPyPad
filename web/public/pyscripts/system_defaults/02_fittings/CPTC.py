# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.crossoversub.cpjc import *


@activate(Group="Tee", TooltipShort="Built-in CPTC", TooltipLong="Built-in CPTC (Decompiled from varmain/teesub/cptcsub/cptc.pyc)", LengthUnit="mm", Ports=1)
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
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPTC(s, D1=114.3, D2=0.0, D3=0.0, D4=0.0, L1=105.0, L2=0.0, L3=0.0, L4=0.0, A=90.0, OF=-1.0, ID='CPTC', **kw):
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
    if D4 == 0.0:
        D4 = D1
    if A == 0.0:
        A = 90.0
    Lx = 2.0 * (sin(asRadiants(60.0)) * (D3 + D4))
    if L2 == 0.0:
        L2 = L1
    if L3 == 0.0:
        L3 = Lx
    if L4 <= 0.0:
        L4 = L3 / 2.0
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
    o1 = ((CPJC_Sub(s, D1=R3 * 2.0, D2=D4, L1=L4, L2=L3 - L4, OF=0.0, I1=0.0, I2=I3)).translate((L4, 0.0, 0.0))).rotateZ(A)
    pP3 = o1.pointAt(1)
    pD3 = o1.directionAt(1)
    if Drill:
        OF = getThickness(D=D1, OF=OF)
        o4 = ((CPJC_Sub(s, D1=R3 * 2.0, D2=D4, L1=L4, L2=L3 - L4, OF=R3 - O3, I1=0.0, I2=I3)).translate((L4, 0.0, 0.0))).rotateZ(A)
    o0.uniteWith(o1)
    o1.erase()
    if Drill:
        o3.uniteWith(o4)
        o4.erase()
        o0.subtractFrom(o3)
        o3.erase()
    s.setPoint((-L1 - I1, 0, 0), (-1, 0, 0))
    s.setPoint((L2 + I2, 0, 0), (1, 0, 0))
    s.setPoint(pP3, pD3)
