# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Support", TooltipShort="CSGB013", TooltipLong="CSGB013", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(T=LENGTH, TooltipShort="T")
@param(L=LENGTH, TooltipShort="L")
@param(A=ANGLE, TooltipShort="A")
@param(TW=LENGTH, TooltipShort="TW")
@param(N=INT, TooltipShort="N")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB013(s, D=114.3, T=114.3, L=304.8, A=120.0, TW=2.54, N=3, ID='CSGB013', **kw):
    if N < 2:
        N = 2
    if TW <= 0:
        TW = D * 0.05
    DI = D + (2.0 * T)
    DO = DI + (2.0 * TW)
    outerShell = CYLINDER(s, R=DO / 2.0, H=L, O=DI / 2.0)
    b1 = ((BOX(s, H=DO, L=DO * 1.1, W=L * 1.1)).translate(((DO + TW) / 2.0, 0.0, L / 2.0))).rotateZ(A / 2.0)
    outerShell.subtractFrom(b1)
    b1.erase()
    b2 = ((BOX(s, H=DO, L=DO * 1.1, W=L * 1.1)).translate(((DO + TW) / 2.0, 0.0, L / 2.0))).rotateZ(180.0 - (A / 2.0))
    outerShell.subtractFrom(b2)
    b2.erase()
    ad = A / (N - 1)
    a = 270.0 - (A / 2)
    for i in range(N):
        b1 = ((BOX(s, H=DI / 2.0, L=TW, W=L)).translate((DI / 4.0, 0.0, L / 2.0))).rotateZ(a)
        outerShell.uniteWith(b1)
        b1.erase()
        a += ad
    pipe = CYLINDER(s, R=D / 2.0, H=L, O=0.0)
    outerShell.subtractFrom(pipe)
    pipe.erase()
    ((outerShell.translate((0.0, 0.0, -L / 2.0))).rotateY(90.0)).rotateX(90.0)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
