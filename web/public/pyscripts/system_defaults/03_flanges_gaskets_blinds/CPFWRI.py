# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpf_util import *


@activate(Group="Flange", TooltipShort="Built-in CPFWRI", TooltipLong="Built-in CPFWRI (Decompiled from varmain/flangesub/cpfwri.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(B=LENGTH, TooltipShort="B")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(IL=LENGTH, TooltipShort="IL")
@param(IH=LENGTH, TooltipShort="IH")
@param(II=LENGTH, TooltipShort="II")
@param(BL=LENGTH, TooltipShort="BL")
@param(BH=LENGTH, TooltipShort="BH")
@param(BI=LENGTH, TooltipShort="BI")
@param(ID=STRING, TooltipShort="组件标识")
def CPFWRI(s, L=54.0, B=38.1, D1=220.0, D2=114.3, D3=0.0, IL=0.0, IH=0.0, II=0.0, BL=0.0, BH=0.0, BI=0.0, ID='CPFWRI', **kw):
    if (L <= 0.0) or (L <= B):
        L = B + 0.0001
    if D3 == 0.0:
        D3 = ((D1 - D2) / 2) + D2
    else:
        if D3 < 0.0:
            D3 = D2
    if IH <= 0.0:
        IH = B / 2.0
    if IL <= 0.0:
        IL = B / 2.0
    if II <= 0.0:
        II = IH
    usePort4 = False
    if ((BH > -2) and (BL > -2)) and (BI > -2):
        if BH <= 0.0:
            BH = IH
        if BL <= 0.0:
            BL = IL
        if BI <= 0.0:
            BI = II
        usePort4 = True
    if D3 == D2:
        O = CON_OF_DIV(D2) / 2.0
        if PnP3dACPAdapterIgnoreWallThickness:
            O = 0.0
        o1 = ((CYLINDER(s, R=D3 / 2.0, H=L - B, O=O)).rotateY(90)).translate((B, 0, 0))
    else:
        O = D2 / 2.0
        if PnP3dACPAdapterIgnoreWallThickness:
            O = 0.0
        o1 = ((CONE(s, R1=D3 / 2.0, R2=D2 / 2.0, H=L - B, E=0)).rotateY(90)).translate((B, 0, 0))
    o0 = (CYLINDER(s, R=D1 / 2.0, H=B, O=O)).rotateY(90)
    tL = (D1 - D2) / 4.0
    o3 = (CYLINDER(s, R=IH / 2.0, H=tL)).translate((IL, 0.0, (D2 / 2.0) + tL))
    o4 = (CYLINDER(s, R=IH / 4.0, H=(D2 / 2.0) + tL, O=0.0)).translate((IL, 0.0, 0.0))
    o3.uniteWith(o4)
    o4.erase()
    if usePort4:
        bL = (D1 - D2) / 4.0
        o5 = (CYLINDER(s, R=BH / 2.0, H=bL)).translate((BL, 0.0, (D2 / 2.0) + bL))
        o6 = (CYLINDER(s, R=BH / 4.0, H=(D2 / 2.0) + bL, O=0.0)).translate((BL, 0.0, 0.0))
        o5.uniteWith(o6)
        o6.erase()
        o5.rotateX(180.0)
    o0.uniteWith(o1)
    o1.erase()
    if not (PnP3dACPAdapterIgnoreWallThickness):
        o2 = ((CYLINDER(s, R=O, H=L - B, O=0.0)).rotateY(90)).translate((B, 0, 0))
        o0.subtractFrom(o2)
        o2.erase()
    o0.subtractFrom(o3)
    o3.erase()
    if usePort4:
        o0.subtractFrom(o5)
        o5.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0)
    s.setPoint((IL, 0.0, (D1 / 2.0) - II), (0.0, 0.0, 1.0), 0.0)
    if usePort4:
        s.setPoint((BL, 0.0, -((D1 / 2.0) - BI)), (0, 0, -1), 0.0)
