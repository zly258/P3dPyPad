# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cbolt6_001 import *
from varmain.divsub.cnut6_001 import *


@activate(Group="Support", TooltipShort="CSGF001", TooltipLong="CSGF001", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(AL=LENGTH, TooltipShort="AL")
@param(MD=LENGTH, TooltipShort="MD")
@param(MH=LENGTH, TooltipShort="MH")
@param(MW=LENGTH, TooltipShort="MW")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(IL=LENGTH, TooltipShort="IL")
@param(ID=STRING, TooltipShort="组件标识")
def CSGF001(s, D=114.3, L=500.0, AL=0.0, MD=0.0, MH=0.0, MW=0.0, SL=250.0, SW=200.0, ST=10.0, IL=0.0, ID='CSGF001', **kw):
    if L <= 0.0:
        L = defaultPipeLength * 2.0
    OF = getThickness(D=D, OF=0.0, Ever=1, mustCalc=True)
    if AL <= 0.0:
        AL = L / 3.0
    if MD <= 0.0:
        MD = D - (OF * 4.0)
    if SW <= 0.0:
        SW = SL
    R = D / 2.0
    cL = L - AL
    if AL > 0.0:
        cL = cL + IL
    o1 = (CYLINDER(s, R=D / 2.0, H=cL, O=0.0)).translate((0.0, 0.0, -L + AL))
    o2 = CBOLT6_001(s, D=MD, L=AL, W=MW, H=MH, P=1).rotateY(-90.0).translate((0.0, 0.0, -L))
    o3 = CNUT6_001(s, D=MD, W=MW, H=MH).rotateY(90.0).translate((0.0, 0.0, -L + AL))
    if MH <= 0.0:
        MH = abs(o3.pointAt(1).z() - o3.pointAt(0).z())
    o4 = None
    if (MH * 3.0) < (AL - ST):
        o4 = CNUT6_001(s, D=MD, W=MW, H=MH).rotateY(90.0).rotateZ(90.0).translate(o3.pointAt(1))
    o5 = (CYLINDER(s, R=R + (OF * 4.0), H=OF, O=0.0)).translate((0.0, 0.0, -L + AL))
    o6 = None
    if ((SL > 0.0) and (SW > 0.0)) and (ST > 0.0):
        o6 = BOX(s, L=SL, H=SW, W=ST).translate((0.0, 0.0, -(L - (ST / 2.0))))
        o2.translate((0.0, 0.0, ST))
    o1.uniteWith(o2)
    o2.erase()
    o1.uniteWith(o3)
    o3.erase()
    if o4:
        o1.uniteWith(o4)
        o4.erase()
    o1.uniteWith(o5)
    o5.erase()
    if o6:
        o1.uniteWith(o6)
        o6.erase()
    CSGCutOut(s, o1, D, kw)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('L', (0, 0, 0), (0, 0, -L))
