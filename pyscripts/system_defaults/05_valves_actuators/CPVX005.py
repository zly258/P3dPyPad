# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="ValveActuator", TooltipShort="Actuator case w.Crank", TooltipLong="Actuator case w.Crank (Decompiled from varmain/valvsub/cpvxsub/cpvx005.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(H=LENGTH, TooltipShort="H")
@param(L=LENGTH, TooltipShort="L")
@param(A=ANGLE, TooltipShort="A")
@param(ID=STRING, TooltipShort="组件标识")
def CPVX005(s, D=225.0, H=345.0, L=180, A=0.0, ID='CPVX005', **kw):
    if L <= 0.0:
        L = D * 0.8
    R0 = D / 2.0
    R1 = D / 15.0
    R2 = D / 20.0
    R3 = (R0 - R1) - R2
    R4 = R0 / 2.0
    R5 = R1 * 1.5
    HS = H / 2.0
    HP = HS / 2.0
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
    oC20 = (CYLINDER(s, R=R4, H=HP - R2, O=0.0)).translate((0, 0, HS))
    oC21 = (CONE(s, R1=R4, R2=R4 - (R2 * 2.0), H=R2)).translate((0, 0, (HS + HP) - R2))
    oC20.uniteWith(oC21)
    oC21.erase()
    oC30 = BOX(s, L=R1, W=R1, H=R1).translate((0, 0, (HS + HP) - W2))
    oC31 = ((((BOX(s, L=L - W2, W=R1, H=R1)).rotateX(-90)).rotateY(-90)).translate(((L - W2) / 2.0, R1 / 2.0, R1 / 2.0))).translate((-W2, -W2, (HS + HP) - R1))
    oC32 = ((((BOX(s, L=R1, W=R1, H=(HP - R5) + R1)).rotateX(-90)).rotateY(-90)).translate((R1 / 2.0, R1 / 2.0, ((HP - R5) + R1) / 2.0))).translate(((L - W2) - R5, -W2, (HS + HP) - R1))
    oC33 = SPHERE(s, R=R5).translate((L - R5, 0, H - R5))
    oC30.uniteWith(oC31)
    oC31.erase()
    oC30.uniteWith(oC32)
    oC32.erase()
    oC30.uniteWith(oC33)
    oC33.erase()
    oC30.rotateZ(A)
    oC10.uniteWith(oC20)
    oC20.erase()
    oC10.uniteWith(oC30)
    oC30.erase()
