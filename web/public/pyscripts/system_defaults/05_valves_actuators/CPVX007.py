# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.valvsub.cpvxsub.cpvx002 import *


@activate(Group="ValveActuator", TooltipShort="Actuator case w. Handwheel", TooltipLong="Actuator case w. Handwheel (Decompiled from varmain/valvsub/cpvxsub/cpvx007.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(H=LENGTH, TooltipShort="H")
@param(HD=LENGTH, TooltipShort="HD")
@param(HL=LENGTH, TooltipShort="HL")
@param(HP=LENGTH, TooltipShort="HP")
@param(HA1=ANGLE, TooltipShort="HA1")
@param(HA2=ANGLE, TooltipShort="HA2")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX007(s, D=225.0, H=345.0, HD=225.0, HL=150.0, HP=0.0, HA1=0.0, HA2=0.0, ID='CPVX007', **kw):
    R0 = D / 2.0
    R1 = D / 15.0
    R2 = D / 20.0
    R3 = (R0 - R1) - R2
    R4 = R0 / 2.0
    R5 = R1 * 1.5
    HS = H / 2.0
    W2 = R1 / 2.0
    oC10 = CYLINDER(s, R=R0, H=R1, O=0.0)
    oC11 = CYLINDER(s, R=R0, H=R1, O=0.0).translate((0, 0, HS - R1))
    oC12 = CYLINDER(s, R=R1, H=HS, O=0.0)
    oC13 = CYLINDER(s, R=R2, H=HS, O=0.0).translate((R3, 0, 0)).rotateZ(45)
    oC14 = CYLINDER(s, R=R2, H=HS, O=0.0).translate((R3, 0, 0)).rotateZ(135)
    oC15 = CYLINDER(s, R=R2, H=HS, O=0.0).translate((R3, 0, 0)).rotateZ(225)
    oC16 = CYLINDER(s, R=R2, H=HS, O=0.0).translate((R3, 0, 0)).rotateZ(315)
    oC10.uniteWith(oC11)
    oC11.erase()
    oC10.uniteWith(oC12)
    oC12.erase()
    oC10.uniteWith(oC13)
    oC13.erase()
    oC10.uniteWith(oC14)
    oC14.erase()
    oC10.uniteWith(oC15)
    oC15.erase()
    oC10.uniteWith(oC16)
    oC16.erase()
    oC20 = (CYLINDER(s, R=R4, H=HS - R2, O=0.0)).translate((0, 0, HS))
    oC21 = (CONE(s, R1=R4, R2=R4 - (R2 * 2.0), H=R2)).translate((0, 0, (HS + HS) - R2))
    oC20.uniteWith(oC21)
    oC21.erase()
    if HD <= 0.0:
        HD = D
    if HL <= 0.0:
        HL = D * 0.6666
    if HP <= 0.0:
        HP = HS + (HS / 2.0)
    oC40 = (CPVX002(s, D=HD, L=HL).rotateY(90.0).rotateY(-HA2).rotateZ(90.0 - HA1)).translate((0.0, 0.0, HP))
    oC10.uniteWith(oC20)
    oC20.erase()
    oC10.uniteWith(oC40)
    oC40.erase()
