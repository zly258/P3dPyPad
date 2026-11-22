# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cste_l import *


@activate(Group="Support", TooltipShort="CSGE004", TooltipLong="CSGE004", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(B=LENGTH, TooltipShort="B")
@param(L=LENGTH, TooltipShort="L")
@param(DI=LENGTH, TooltipShort="DI")
@param(DO=LENGTH, TooltipShort="DO")
@param(LO=LENGTH, TooltipShort="LO")
@param(LC=LENGTH, TooltipShort="LC")
@param(LL=LENGTH, TooltipShort="LL")
@param(WL=LENGTH, TooltipShort="WL")
@param(HL=LENGTH, TooltipShort="HL")
@param(TL=LENGTH, TooltipShort="TL")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(ID=STRING, TooltipShort="组件标识")
def CSGE004(s, D=290.0, B=26.0, L=400.0, DI=60.0, DO=0.0, LO=0.0, LC=0.0, LL=200.0, WL=90.0, HL=0.0, TL=10.0, SL=250.0, SW=150.0, ST=0.0, ID='CSGE004', **kw):
    if DI <= 0.0:
        DI = WL
    if DO <= 0.0:
        DO = DI + (getThickness(D=DI, OF=0.0, Ever=1) * 2.0)
    if LC <= 0.0:
        LC = LL / 4.0
    if HL <= 0.0:
        HL = WL
    if ST <= 0.0:
        ST = TL
    if SW <= 0.0:
        SW = SL
    R = D / 2.0
    if LO <= 0.0:
        LO = ((L - R) - TL) / 2.0
    cW = sqrt((LC ** 2) * 2.0)
    tranX = (WL / 2.0) - (B + TL)
    tranZ = (HL / 2.0) - (R + TL)
    o1 = (CYLINDER(s, R=DI / 2.0, H=L - R, O=0.0)).translate((tranX, 0.0, -L))
    o2 = (CYLINDER(s, R=DO / 2.0, H=LO, O=0.0)).translate((tranX, 0.0, -L))
    o3 = CSTE_L(s, W=WL, H=HL, T=TL, L=LL).rotateX(90.0).translate((tranX, LL / 2.0, tranZ))
    o4 = None
    if (SL > 0.0) and (SW > 0.0):
        o4 = BOX(s, L=SL, H=SW, W=ST).translate((tranX, TL / 2.0, -(L - (ST / 2.0))))
    o5 = BOX(s, L=cW, H=cW, W=cW).rotateX(45.0).translate((-(B + TL), 0.0, -((R - HL) + TL)))
    cH = HL - (TL * 2.0)
    o6 = None
    if LC > cH:
        xH = LC
        while xH > cH:
            xH = xH - TL
        xH = (((L - R) - xH) - TL) + HL
        o6 = BOX(s, L=xH, H=xH, W=xH).translate((-(B + TL), 0.0, -(L - (xH / 2.0))))
    o1.uniteWith(o2)
    o2.erase()
    o1.uniteWith(o3)
    o3.erase()
    if o4:
        o1.uniteWith(o4)
        o4.erase()
    if o6:
        o5.subtractFrom(o6)
        o6.erase()
    o1.subtractFrom(o5)
    o5.erase()
    o1.rotateZ(-90.0).rotateX(-90.0).rotateZ(90.0).rotateY(90)
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('L', (0, 0, 0), (0, 0, -L))
