# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.valvsub.cpvxsub.cpvx002 import *


@activate(Group="ValveActuator", TooltipShort="Detailed actuator case w. Handwheel", TooltipLong="Detailed actuator case w. Handwheel (Decompiled from varmain/valvsub/cpvxsub/cpvx006.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(HD=LENGTH, TooltipShort="HD")
@param(HL=LENGTH, TooltipShort="HL")
@param(HP=LENGTH, TooltipShort="HP")
@param(HA1=ANGLE, TooltipShort="HA1")
@param(HA2=ANGLE, TooltipShort="HA2")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX006(s, D=225.0, L=345.0, HD=225.0, HL=150.0, HP=300.0, HA1=0.0, HA2=0.0, ID='CPVX006', **kw):
    R0 = D / 2.0
    R1 = D / 15.0
    R2 = D / 20.0
    R3 = (R0 - R1) - R2
    LS = L / 3.0
    LP = LS / 3.0
    oC10 = CYLINDER(s, R=R0, H=R1, O=0.0)
    oC11 = CYLINDER(s, R=R0, H=R1, O=0.0).translate((0, 0, LS - R1))
    oC12 = CYLINDER(s, R=R1, H=LS, O=0.0)
    oC13 = CYLINDER(s, R=R2, H=LS, O=0.0).translate((R3, 0, 0)).rotateZ(45)
    oC14 = CYLINDER(s, R=R2, H=LS, O=0.0).translate((R3, 0, 0)).rotateZ(135)
    oC15 = CYLINDER(s, R=R2, H=LS, O=0.0).translate((R3, 0, 0)).rotateZ(225)
    oC16 = CYLINDER(s, R=R2, H=LS, O=0.0).translate((R3, 0, 0)).rotateZ(315)
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
    oC20 = CYLINDER(s, R=R3, H=LS, O=0.0).translate((0, 0, LS))
    oC30 = (CYLINDER(s, R=(R3 - R2) - R1, H=LP, O=0.0)).translate((0, 0, LS * 2.0))
    oC31 = (CYLINDER(s, R=R3 - R2, H=(LS - LP) - R2, O=0.0)).translate((0, 0, (LS * 2.0) + LP))
    oC32 = (CONE(s, R1=R3 - R2, R2=R3 - (R2 * 3.0), H=R2)).translate((0, 0, (LS * 3.0) - R2))
    if HD <= 0.0:
        HD = D
    if HL <= 0.0:
        HL = D * 0.6666
    if HP <= 0.0:
        HP = ((LS * 2.0) + LP) + (((LS - LP) - R2) / 2.0)
    oC40 = (CPVX002(s, D=HD, L=HL).rotateY(90.0).rotateY(-HA2).rotateZ(90.0 - HA1)).translate((0.0, 0.0, HP))
    oC30.uniteWith(oC31)
    oC31.erase()
    oC30.uniteWith(oC32)
    oC32.erase()
    oC10.uniteWith(oC20)
    oC20.erase()
    oC10.uniteWith(oC30)
    oC30.erase()
    oC10.uniteWith(oC40)
    oC40.erase()
