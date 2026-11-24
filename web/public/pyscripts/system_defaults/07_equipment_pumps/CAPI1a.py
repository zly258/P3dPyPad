# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.pumpsub.cap_subparts import *
from varmain.pumpsub.cap_util import *


@activate(Group="Equipment", TooltipShort="Built-in CAPI1a", TooltipLong="Built-in CAPI1a (Decompiled from varmain/pumpsub/capi1a.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(LC=LENGTH, TooltipShort="LC")
@param(DC=LENGTH, TooltipShort="DC")
@param(CC=LENGTH, TooltipShort="CC")
@param(H1C=LENGTH, TooltipShort="H1C")
@param(H2C=LENGTH, TooltipShort="H2C")
@param(D1F1C=LENGTH, TooltipShort="D1F1C")
@param(D2F1C=LENGTH, TooltipShort="D2F1C")
@param(LF1C=LENGTH, TooltipShort="LF1C")
@param(BF1C=LENGTH, TooltipShort="BF1C")
@param(D1F2C=LENGTH, TooltipShort="D1F2C")
@param(D2F2C=LENGTH, TooltipShort="D2F2C")
@param(LF2C=LENGTH, TooltipShort="LF2C")
@param(BF2C=LENGTH, TooltipShort="BF2C")
@param(D1MS=LENGTH, TooltipShort="D1MS")
@param(HM=LENGTH, TooltipShort="HM")
@param(L1MS=LENGTH, TooltipShort="L1MS")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(SH=LENGTH, TooltipShort="SH")
@param(oldDef=LENGTH, TooltipShort="oldDef")
@param(ID=STRING, TooltipShort="组件标识")
def CAPI1a(s, LC=500.0, DC=0.0, CC=0.0, H1C=0.0, H2C=0.0, D1F1C=220.0, D2F1C=114.3, LF1C=50.0, BF1C=22.0, D1F2C=0.0, D2F2C=0.0, LF2C=50.0, BF2C=0.0, D1MS=250.0, HM=750.0, L1MS=0.0, SL=0.0, SW=0.0, SH=0.0, oldDef=None, ID='CAPI1a', **kw):
    if CC <= 0.0:
        CC = LC / 2.0
    if D1F2C <= 0.0:
        D1F2C = D1F1C
    if D2F2C <= 0.0:
        D2F2C = D2F1C
    if BF2C <= 0.0:
        BF2C = BF1C
    if LF1C <= 0.0:
        LF1C = (BF1C + BF2C) / 2.0
    if LF2C <= 0.0:
        LF2C = LF1C
    if H1C <= 0.0:
        H1C = (((D2F1C + D2F2C) / 2.0) + ((D1F1C + D1F2C) / 2.0)) / 4.0
    if H2C <= 0.0:
        H2C = H1C
    if DC <= 0.0:
        DC = (D1F1C + D1F2C) / 2.0
    oPC = CCASE003a(s, LC=LC, DC=DC, CC=CC, H1C=H1C, H2C=H2C, D1F1C=D1F1C, D2F1C=D2F1C, LF1C=LF1C, BF1C=BF1C, D1F2C=D1F2C, D2F2C=D2F2C, LF2C=LF2C, BF2C=BF2C)
    DC2 = (DC / 3.0) * 2.0
    oPBB = (CYLINDER(s, R=DC2 / 2.0, H=(HM - H2C) / 2.0, O=0.0)).translate((CC, 0.0, H2C))
    oPMS = ((CAPMOT001(s, L1MS=L1MS, LMS=HM - H2C, D1MS=D1MS / 2.0, D3MS=0.0)).rotateY(-90)).translate((CC, 0.0, H2C))
    if (SL > 0.0) and (SH > 0.0):
        if SW <= 0.0:
            SW = SL
        oPS = BOX(s, L=SW, W=SH, H=SL).translate((CC, 0.0, -(H1C + (SH / 2.0))))
    else:
        oPS = None
    if oldDef:
        s.setPoint(oPC.pointAt(0), oPC.directionAt(0))
        s.setPoint(oPC.pointAt(1), oPC.directionAt(1))
    else:
        s.setPoint(oPC.pointAt(1), oPC.directionAt(1))
        s.setPoint(oPC.pointAt(0), oPC.directionAt(0))
    oPBB.uniteWith(oPC)
    oPC.erase()
    oPBB.uniteWith(oPMS)
    oPMS.erase()
    if oPS:
        oPBB.uniteWith(oPS)
        oPS.erase()
