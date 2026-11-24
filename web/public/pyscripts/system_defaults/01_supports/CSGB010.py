# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgcsub.csgc002 import *


@activate(Group="Support", TooltipShort="CSGB010", TooltipLong="CSGB010", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(SM=LENGTH, TooltipShort="SM")
@param(SD=LENGTH, TooltipShort="SD")
@param(E=LENGTH, TooltipShort="E")
@param(BL=LENGTH, TooltipShort="BL")
@param(BW=LENGTH, TooltipShort="BW")
@param(BH=LENGTH, TooltipShort="BH")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB010(s, D=116.0, L=40.0, W=4.0, K=0.0, SL=180.0, SW=80.0, ST=0.0, SM=20.0, SD=-1.0, E=90.0, BL=220.0, BW=60.0, BH=2.0, ID='CSGB010', **kw):
    R1 = D / 2.0
    R2 = R1 + W
    if SW <= 0.0:
        SW = SL
    if K <= 0.0:
        K = D + (L * 2.0)
    if BL <= 0.0:
        BL = SL
    if BW <= 0.0:
        BW = L
    if ST <= 0.0:
        ST = W
    o0 = CSGB010_Sub(s, D=D, SL=SL, SW=SW, ST=ST, SM=SM, SD=SD, E=E).rotateZ(180.0).translate((-((D / 2.0) + W), 0.0, 0.0))
    o1 = ((CYLINDER(s, R=E * 0.01, H=ST, O=0.0)).rotateY(180.0)).translate((-(((D + E) / 2.0) + W), 0.0, 0.0))
    o2 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90).translate((0.0, 0.0, L / 2.0))
    o3 = CSGC002(s, D=D, L=L, W=W, K=K).rotateY(-90).translate((0.0, 0.0, SL - (L / 2.0)))
    o4 = CSGB010_Rem(s, D=D, L=L, W=W, SL=SL, SD=SD, SW=SW, ST=ST)
    if BH > 0.0:
        o5 = CYLINDER(s, R=R1, H=BL, O=R1 - BH)
        o6 = BOX(s, L=BW, W=BL, H=D).translate((0.0, 0.0, BL / 2.0))
    else:
        o5 = None
    o1.uniteWith(o0)
    o0.erase()
    o1.subtractFrom(o4)
    o4.erase()
    o1.uniteWith(o2)
    o2.erase()
    o1.uniteWith(o3)
    o3.erase()
    if o5:
        o5.intersectWith(o6)
        o6.erase()
        o1.uniteWith(o5)
        o5.erase()
    o1.translate((0.0, 0.0, ST))
    s.setPoint((0, 0, ST + (SL / 2.0)), (0.0, 0.0, -1.0))


@activate(Group="Support", TooltipShort="CSGB010", TooltipLong="CSGB010", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(SM=LENGTH, TooltipShort="SM")
@param(SD=LENGTH, TooltipShort="SD")
@param(E=LENGTH, TooltipShort="E")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB010_Sub(s, D=124.0, SL=180.0, SW=80.0, ST=0.0, SM=20.0, SD=-1.0, E=90.0, ID='CSGB010_Sub', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                _pc = 52 if not ((ST if ST is not None else -1e30) <= (0 if 0 is not None else -1e30)) else 12
            elif _pc == 12:
                ST = getThickness(D=SL, OF=0.0, Ever=1, mustCalc=True) / 2.0
                _pc = 52
            elif _pc == 52:
                o1 = BOX(s, L=SW, W=ST, H=E).translate((E / 2.0, 0.0, -(ST / 2.0)))
                o2 = CSGB010_Tmp(s, D=D, SL=SL, ST=ST, SM=SM, E=E)
                _pc = 175 if not ((SD if SD is not None else -1e30) >= (-1.0 if -1.0 is not None else -1e30)) else 163
            elif _pc == 163:
                _pc = 187 if ((SD if SD is not None else -1e30) < (0.0 if 0.0 is not None else -1e30)) else 175
            elif _pc == 175:
                _pc = 345 if not ((SD if SD is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 187
            elif _pc == 187:
                _pc = 216 if not ((SD if SD is not None else -1e30) < (0.0 if 0.0 is not None else -1e30)) else 199
            elif _pc == 199:
                SD = SW - (ST * 4.0)
                _pc = 216
            elif _pc == 216:
                _pc = 241 if not ((SD if SD is not None else -1e30) > (D if D is not None else -1e30)) else 228
            elif _pc == 228:
                SD = D - ST
                _pc = 241
            elif _pc == 241:
                mL = (SD / 2.0) + (ST / 2.0)
                o2.translate((0.0, mL, 0.0))
                o3 = CSGB010_Tmp(s, D=D, SL=SL, ST=ST, SM=SM, E=E).translate((0.0, -mL, 0.0))
                _pc = 351
            elif _pc == 345:
                o3 = None
                _pc = 351
            elif _pc == 351:
                o1.uniteWith(o2)
                o2.erase()
                _pc = 406 if not (o3) else 380
            elif _pc == 380:
                o1.uniteWith(o3)
                o3.erase()
                _pc = 406
            elif _pc == 406:
                return None
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise


@activate(Group="Support", TooltipShort="CSGB010", TooltipLong="CSGB010", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(SL=LENGTH, TooltipShort="SL")
@param(ST=LENGTH, TooltipShort="ST")
@param(SM=LENGTH, TooltipShort="SM")
@param(E=LENGTH, TooltipShort="E")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB010_Tmp(s, D=124.0, SL=180.0, ST=0.0, SM=20.0, E=90.0, ID='CSGB010_Tmp', **kw):
    if ST <= 0:
        ST = getThickness(D=SL, OF=0.0, Ever=1, mustCalc=True) / 2.0
    xE = E + (D / 2.0)
    o1 = BOX(s, L=ST, W=SL, H=xE).translate(((xE / 2.0) - (D / 2.0), 0.0, SL / 2.0))
    if SM > 0.0:
        tE = E - SM
        tH = SL - SM
    else:
        tE = E
        tH = SL
    tL = sqrt(pow(tE, 2.0) + pow(tH, 2.0))
    tA = asDegrees(asin(tE / tL))
    o2 = ((BOX(s, L=ST, W=tL, H=tL).translate((tL / 2.0, 0.0, tL / 2.0))).rotateY(-tA)).translate((E, 0.0, SM))
    o1.subtractFrom(o2)
    o2.erase()


@activate(Group="Support", TooltipShort="CSGB010", TooltipLong="CSGB010", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(SL=LENGTH, TooltipShort="SL")
@param(SD=LENGTH, TooltipShort="SD")
@param(SW=LENGTH, TooltipShort="SW")
@param(ST=LENGTH, TooltipShort="ST")
@param(ID=STRING, TooltipShort="组件标识")
def CSGB010_Rem(s, D=124.0, L=40.0, W=4.0, SL=180.0, SD=-1.0, SW=80.0, ST=0.0, ID='CSGB010_Tmp', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                R1 = D / 2.0
                R2 = R1 + W
                _pc = 41 if not ((ST if ST is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 32
            elif _pc == 32:
                ST = W
                _pc = 41
            elif _pc == 41:
                o4 = CYLINDER(s, R=R1, H=SL, O=0.0)
                tL = R2 * 2.0
                tH = SL - (L * 2.0)
                _pc = 230 if not (SD != 0) else 107
            elif _pc == 107:
                _pc = 230 if not ((SD if SD is not None else -1e30) >= (-1.0 if -1.0 is not None else -1e30)) else 119
            elif _pc == 119:
                _pc = 143 if ((SD if SD is not None else -1e30) < (0.0 if 0.0 is not None else -1e30)) else 131
            elif _pc == 131:
                _pc = 185 if not ((SD if SD is not None else -1e30) >= (D if D is not None else -1e30)) else 143
            elif _pc == 143:
                SD = SW - (ST * 4.0)
                _pc = 185 if not ((SD if SD is not None else -1e30) > (D if D is not None else -1e30)) else 169
            elif _pc == 169:
                SD = D - ST
                _pc = 185
            elif _pc == 182:
                _pc = 185
            elif _pc == 185:
                tW = (sqrt(pow(R1, 2.0) - (pow(SD / 2.0, 2.0)))) * 2.0
                _pc = 236
            elif _pc == 230:
                tW = D
                _pc = 236
            elif _pc == 236:
                o5 = BOX(s, L=tL, W=tH, H=tW).translate((0.0, 0.0, SL / 2.0))
                o4.uniteWith(o5)
                o5.erase()
                return o4
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
