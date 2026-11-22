# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Support", TooltipShort="CSGF003", TooltipLong="CSGF003", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(AL=LENGTH, TooltipShort="AL")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(OF=LENGTH, TooltipShort="OF")
@param(IL=LENGTH, TooltipShort="IL")
@param(ID=STRING, TooltipShort="组件标识")
def CSGF003(s, D=114.3, L=500.0, AL=0.0, SL=250.0, SW=200.0, ST=10.0, OF=-1.0, IL=0.0, ID='CSGF003', **kw):
    if L <= 0.0:
        L = defaultPipeLength * 2.0
    if SW <= 0.0:
        SW = SL
    if AL <= 0.0:
        AL = L / 3.0
    R = D / 2.0
    cL = L + IL
    DI = getInsideDiameter(D=D, OF=OF, Ever=None)
    DX = getInsideDiameter(D=DI, OF=OF, Ever=None)
    D2 = DI
    if D2 <= 0.0:
        D2 = getInsideDiameter(D=D, OF=OF, Ever=True, mustCalc=True)
    o1 = (CYLINDER(s, R=D / 2.0, H=cL - AL, O=DI / 2.0)).translate((0.0, 0.0, -L + AL))
    xL = (L / 3.0) * 2.0
    if xL < AL:
        xL = AL
    o2 = (CYLINDER(s, R=D2 / 2.0, H=xL, O=DX / 2.0)).translate((0.0, 0.0, -L))
    o3 = None
    if ((SL > 0.0) and (SW > 0.0)) and (ST > 0.0):
        o3 = BOX(s, L=SL, H=SW, W=ST).translate((0.0, 0.0, -(L - (ST / 2.0))))
    o1.uniteWith(o2)
    o2.erase()
    if o3:
        o1.uniteWith(o3)
        o3.erase()
    CSGCutOut(s, o1, D, kw)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('L', (0, 0, 0), (0, 0, -L))
