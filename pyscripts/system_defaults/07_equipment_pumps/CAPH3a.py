# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.pumpsub.cap_subparts import *
from varmain.pumpsub.cap_util import *


@activate(Group="Equipment", TooltipShort="Built-in CAPH3a", TooltipLong="Built-in CAPH3a (Decompiled from varmain/pumpsub/caph3a.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(SL=LENGTH, TooltipShort="SL")
@param(SB=LENGTH, TooltipShort="SB")
@param(SH=LENGTH, TooltipShort="SH")
@param(SI=LENGTH, TooltipShort="SI")
@param(SO=LENGTH, TooltipShort="SO")
@param(L1BB=LENGTH, TooltipShort="L1BB")
@param(D1BB=LENGTH, TooltipShort="D1BB")
@param(D2BB=LENGTH, TooltipShort="D2BB")
@param(L2BB=LENGTH, TooltipShort="L2BB")
@param(D2MS=LENGTH, TooltipShort="D2MS")
@param(L1MS=LENGTH, TooltipShort="L1MS")
@param(LMS=LENGTH, TooltipShort="LMS")
@param(D1MS=LENGTH, TooltipShort="D1MS")
@param(HC=LENGTH, TooltipShort="HC")
@param(DC=LENGTH, TooltipShort="DC")
@param(LF1C=LENGTH, TooltipShort="LF1C")
@param(LF2C=LENGTH, TooltipShort="LF2C")
@param(HF1C=LENGTH, TooltipShort="HF1C")
@param(HF2C=LENGTH, TooltipShort="HF2C")
@param(BC=LENGTH, TooltipShort="BC")
@param(D1F1C=LENGTH, TooltipShort="D1F1C")
@param(L1F1C=LENGTH, TooltipShort="L1F1C")
@param(BF1C=LENGTH, TooltipShort="BF1C")
@param(D2F1C=LENGTH, TooltipShort="D2F1C")
@param(D1F2C=LENGTH, TooltipShort="D1F2C")
@param(L1F2C=LENGTH, TooltipShort="L1F2C")
@param(BF2C=LENGTH, TooltipShort="BF2C")
@param(D2F2C=LENGTH, TooltipShort="D2F2C")
@param(oldDef=LENGTH, TooltipShort="oldDef")
@param(ID=STRING, TooltipShort="组件标识")
def CAPH3a(s, SL=0.0, SB=0.0, SH=0.0, SI=0.0, SO=0.0, L1BB=361.0, D1BB=105.0, D2BB=62.5, L2BB=130.0, D2MS=24.0, L1MS=100.0, LMS=372.0, D1MS=100.0, HC=140.0, DC=250.0, LF1C=280.0, LF2C=0.0, HF1C=0.0, HF2C=0.0, BC=50.0, D1F1C=220.0, L1F1C=54.0, BF1C=22.0, D2F1C=114.3, D1F2C=250.0, L1F2C=57.0, BF2C=22.0, D2F2C=139.7, oldDef=None, ID='CAPH1a', **kw):
    if HF1C <= 0.0:
        HF1C = DC - (D2F1C / 2.0)
    if HF2C <= 0.0:
        HF2C = DC - (D2F2C / 2.0)
    if LF2C <= 0.0:
        LF2C = LF1C
    if ((SL > 0.0) and (SB > 0.0)) and (SH > 0.0):
        oPS = (BOX(s, L=SL, W=SB, H=SH).rotateX(-90).rotateY(-90).translate((SL / 2.0, SB / 2.0, SH / 2.0))).translate((0.0, -(SB / 2.0), 0.0))
        dX = SI
        dY = -LF2C
    else:
        oPS = None
        dX = 0.0
        dY = 0.0
    oPC = CCASE007a(s, HC=HC, DC=DC, LF1C=LF1C, LF2C=LF2C, D1F1C=D1F1C, L1F1C=L1F1C, HF1C=HF1C, HF2C=HF2C, BC=BC, D1BB=D1BB, PBC='L', BF1C=BF1C, D2F1C=D2F1C, D1F2C=D1F2C, L1F2C=L1F2C, BF2C=BF2C, D2F2C=D2F2C)
    oPC.translate((dX, dY, SO))
    hPCBW = (SO - SH) - (DC - HF2C)
    if (SO > 0.0) and (hPCBW > 0.0):
        dPCBW = DC * 0.75
        oPCL = (((BOX(s, L=HC, W=dPCBW * 2.0, H=hPCBW)).rotateX(-90)).rotateY(-90)).translate((dX, 0.0, SH + (hPCBW / 2.0)))
    else:
        oPCL = None
    oPBB = CBEAR001(s, L1BB=L1BB, D1BB=D1BB, D2BB=D2BB, L2BB=L2BB, D2MS=D2MS)
    oPBB.translate(oPC.pointAt(2))
    oPMS = CAPMOT001(s, L1MS=L1MS, LMS=LMS, D1MS=D1MS, D2MS=D2MS)
    oPMS.translate(oPBB.pointAt(1))
    hPMSBW = (SO - SH) - (D1MS - HF2C)
    if (SO > 0.0) and (hPMSBW > 0.0):
        if L1MS <= 0.0:
            L1MS = LMS / 6.0
        dX = ((((dX + (HC / 2.0)) + BC) + L1BB) + L2BB) + (LMS / 2.0)
        dPMSBW = D1MS * 0.75
        wPMSBW = LMS - (L1MS * 2.0)
        oPMSL = (((BOX(s, L=wPMSBW, W=dPMSBW * 2.0, H=hPMSBW)).rotateX(-90)).rotateY(-90)).translate((dX, 0.0, SH + (hPMSBW / 2.0)))
    else:
        oPMSL = None
    if oldDef:
        s.setPoint(oPC.pointAt(0), oPC.directionAt(0))
        s.setPoint(oPC.pointAt(1), oPC.directionAt(1))
    else:
        s.setPoint(oPC.pointAt(1), oPC.directionAt(1))
        s.setPoint(oPC.pointAt(0), oPC.directionAt(0))
    oTMP = CYLINDER(s, R=0.1, H=0.1, O=0.0).translate((LF2C, 0, 0)).translate((dX, dY, SO))
    if oPS:
        oTMP.uniteWith(oPS)
        oPS.erase()
    oTMP.uniteWith(oPC)
    oPC.erase()
    if oPCL:
        oTMP.uniteWith(oPCL)
        oPCL.erase()
    oTMP.uniteWith(oPBB)
    oPBB.erase()
    oTMP.uniteWith(oPMS)
    oPMS.erase()
    if oPMSL:
        oTMP.uniteWith(oPMSL)
        oPMSL.erase()
