# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.valvsub.cpvxsub.cpvx002 import *


@activate(Group="ValveActuator", TooltipShort="Vert. Cylinder actuator w. Extension and extra Handwheel", TooltipLong="Vert. Cylinder actuator w. Extension and extra Handwheel (Decompiled from varmain/valvsub/cpvxsub/cpvx021.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(L1=LENGTH, TooltipShort="L1")
@param(DO=LENGTH, TooltipShort="DO")
@param(LO=LENGTH, TooltipShort="LO")
@param(DU=LENGTH, TooltipShort="DU")
@param(LU=LENGTH, TooltipShort="LU")
@param(HU1=LENGTH, TooltipShort="HU1")
@param(HU2=LENGTH, TooltipShort="HU2")
@param(A=ANGLE, TooltipShort="A")
@param(EX=LENGTH, TooltipShort="EX")
@param(EY=LENGTH, TooltipShort="EY")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX021(s, D=225.0, L=345.0, L1=200.0, DO=0.0, LO=0.0, DU=225.0, LU=120.0, HU1=0.0, HU2=0.0, A=0.0, EX=0.0, EY=0.0, ID='CPVX021', **kw):
    if L1 <= 0.0:
        L1 = L * 0.6666
    sL = L - L1
    if sL <= 0.0:
        sL = L / 100.0
        L1 = L - sL
    if DO <= 0.0:
        R = D / 20.0
    else:
        R = DO / 2.0
    if DU <= 0.0:
        DU = D
    if LU <= 0.0:
        LU = L - L1
    if LO <= 0.0:
        LO = L1
    if HU1 <= 0.0:
        HU1 = LU
    if HU2 <= 0.0:
        HU2 = HU1
    o1 = (CYLINDER(s, R=D / 2.0, H=L1, O=0.0)).translate((EX, EY, sL))
    if sL > 0.0:
        o2 = CYLINDER(s, R=R, H=sL, O=0.0).translate((EX, EY, 0.0))
        o1.uniteWith(o2)
        o2.erase()
    o3 = CYLINDER(s, R=R, H=LO, O=0.0).translate((EX, EY, -LO))
    o1.uniteWith(o3)
    o3.erase()
    o4 = CYLINDER(s, R=R, H=LU, O=0.0).translate((0.0, 0.0, L))
    o5 = ((CPVX002(s, D=DU, L=HU1 + HU2)).rotateY(-90.0)).translate((HU2, 0.0, L + LU))
    o4.uniteWith(o5)
    o5.erase()
    o4.rotateZ(A).translate((EX, EY, 0.0))
    o1.uniteWith(o4)
    o4.erase()
