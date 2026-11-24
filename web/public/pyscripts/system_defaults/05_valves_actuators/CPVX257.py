# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.valvsub.cpvxsub.cpvx002 import *


@activate(Group="ValveActuator", TooltipShort="Pyramid actuator w. Handwheel", TooltipLong="Pyramid actuator w. Handwheel (Decompiled from varmain/valvsub/cpvxsub/cpvx257.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(L1=LENGTH, TooltipShort="L1")
@param(HD=LENGTH, TooltipShort="HD")
@param(HL=LENGTH, TooltipShort="HL")
@param(HP=LENGTH, TooltipShort="HP")
@param(HA1=ANGLE, TooltipShort="HA1")
@param(HA2=ANGLE, TooltipShort="HA2")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX257(s, L=345.0, W=100.0, L1=150.0, HD=225.0, HL=150.0, HP=300.0, HA1=0.0, HA2=0.0, ID='CPVX257', **kw):
    oC1 = PYRAMID(s, L=W, W=L1, H=L).rotateY(180).translate((0, 0, L))
    if HD <= 0.0:
        HD = L1
    if HL <= 0.0:
        HL = W
    if HP <= 0.0:
        HP = L * 0.75
    oC2 = CPVX002(s, D=HD, L=HL).rotateY(90.0).rotateY(-HA2).rotateZ(-HA1).translate((0.0, 0.0, HP))
    oC1.uniteWith(oC2)
    oC2.erase()
