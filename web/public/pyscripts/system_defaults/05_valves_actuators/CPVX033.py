# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.valvsub.cpvxsub.cpvx002 import *


@activate(Group="ValveActuator", TooltipShort="Hor. Cylinder actuator w. Handwheel", TooltipLong="Hor. Cylinder actuator w. Handwheel (Decompiled from varmain/valvsub/cpvxsub/cpvx033.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(L1=LENGTH, TooltipShort="L1")
@param(EX=LENGTH, TooltipShort="EX")
@param(EY=LENGTH, TooltipShort="EY")
@param(HD=LENGTH, TooltipShort="HD")
@param(HL=LENGTH, TooltipShort="HL")
@param(HA1=ANGLE, TooltipShort="HA1")
@param(HA2=ANGLE, TooltipShort="HA2")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX033(s, D=225.0, L=345.0, L1=200.0, EX=0.0, EY=0.0, HD=225.0, HL=150.0, HA1=0.0, HA2=0.0, ID='CPVX033', **kw):
    if D <= 0.0:
        D = L * 0.6666
    R = D / 20.0
    R1 = D / 2.0
    o1 = CYLINDER(s, R=R1, H=L1, O=0.0).rotateY(90).translate((-L1 / 2.0, 0, 0))
    o1.translate((EX, EY, L - R1))
    if (L - D) > 0.0:
        o2 = CYLINDER(s, R=R, H=L - R1, O=0.0)
        o1.uniteWith(o2)
        o2.erase()
    if HD <= 0.0:
        HD = D
    if HL <= 0.0:
        HL = L * 0.45
    o3 = (CPVX002(s, D=HD, L=HL).rotateX(-90.0).rotateX(HA2).rotateZ(90.0 - HA1)).translate((EX, EY, L - R1))
    o1.uniteWith(o3)
    o3.erase()
