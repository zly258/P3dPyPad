# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.valvsub.cpvxsub.cpvx002 import *


@activate(Group="ValveActuator", TooltipShort="Cone actuator w. Handwheel", TooltipLong="Cone actuator w. Handwheel (Decompiled from varmain/valvsub/cpvxsub/cpvx129.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(HD=LENGTH, TooltipShort="HD")
@param(HL=LENGTH, TooltipShort="HL")
@param(HP=LENGTH, TooltipShort="HP")
@param(HA1=ANGLE, TooltipShort="HA1")
@param(HA2=ANGLE, TooltipShort="HA2")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX129(s, D=225.0, L=345.0, HD=225.0, HL=150.0, HP=300.0, HA1=0.0, HA2=0.0, ID='CPVX129', **kw):
    oC1 = ((CONE(s, R1=D / 2.0, R2=0.0, H=L)).rotateY(180)).translate((0, 0, L))
    if HD <= 0.0:
        HD = D
    if HL <= 0.0:
        HL = D * 0.6666
    if HP <= 0.0:
        HP = L * 0.75
    oC2 = (CPVX002(s, D=HD, L=HL).rotateY(90.0).rotateY(-HA2).rotateZ(90.0 - HA1)).translate((0.0, 0.0, HP))
    oC1.uniteWith(oC2)
    oC2.erase()
