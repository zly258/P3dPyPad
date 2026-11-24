# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.valvsub.cpvxsub.cpvx002 import *


@activate(Group="ValveActuator", TooltipShort="Vert. Cylinder actuator w. Handwheel", TooltipLong="Vert. Cylinder actuator w. Handwheel (Decompiled from varmain/valvsub/cpvxsub/cpvx019.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(L1=LENGTH, TooltipShort="L1")
@param(EX=LENGTH, TooltipShort="EX")
@param(EY=LENGTH, TooltipShort="EY")
@param(HD=LENGTH, TooltipShort="HD")
@param(HL=LENGTH, TooltipShort="HL")
@param(HP=LENGTH, TooltipShort="HP")
@param(HA1=ANGLE, TooltipShort="HA1")
@param(HA2=ANGLE, TooltipShort="HA2")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX019(s, D=225.0, L=345.0, L1=200.0, EX=0.0, EY=0.0, HD=225.0, HL=150.0, HP=0.0, HA1=0.0, HA2=0.0, ID='CPVX019', **kw):
    if L1 <= 0.0:
        L1 = L * 0.6666
    R = D / 20.0
    o1 = (CYLINDER(s, R=D / 2.0, H=L1, O=0.0)).translate((EX, EY, L - L1))
    if (L - L1) > 0.0:
        o2 = CYLINDER(s, R=R, H=L - L1, O=0.0)
        o1.uniteWith(o2)
        o2.erase()
    if HD <= 0.0:
        HD = D
    if HL <= 0.0:
        HL = D * 0.6666
    if HP <= 0.0:
        HP = (L1 / 2.0) + (L - L1)
    o3 = (CPVX002(s, D=HD, L=HL).rotateY(90.0).rotateY(-HA2).rotateZ(90.0 - HA1)).translate((EX, EY, HP))
    o1.uniteWith(o3)
    o3.erase()
