# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.arcsub.cpb_util import *


@activate(Group="Crossover", TooltipShort="Built-in CPJC", TooltipLong="Built-in CPJC (Decompiled from varmain/crossoversub/cpjc.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(OF=LENGTH, TooltipShort="OF")
@param(I1=LENGTH, TooltipShort="I1")
@param(I2=LENGTH, TooltipShort="I2")
@param(ID=STRING, TooltipShort="组件标识")
def CPJC(s, D1=114.3, D2=0.0, L1=0.0, L2=0.0, OF=-1.0, I1=0.0, I2=0.0, ID='CPJC', **kw):
    if D2 <= 0.0:
        D2 = D1
    o0 = CPJC_Sub(s, D1=D1, D2=D2, L1=L1, L2=L2, I1=I1, I2=I2)
    pD0 = o0.directionAt(0)
    pD1 = o0.directionAt(1)
    pT0 = o0.pointAt(0)
    pT1 = o0.pointAt(1)
    arc3d2TMP = ((CYLINDER(s, R=(D1 * 0.01) / 2.0, H=D1 * 0.01)).rotateY(-90.0)).translate(pT0)
    arc3d2TMP.uniteWith(o0)
    o0.erase()
    o0 = arc3d2TMP
    if not (OF == 0.0):
        OF = getThickness(D=D1, OF=OF)
        o1 = CPJC_Sub(s, D1=D1, D2=D2, L1=L1, L2=L2, OF=OF, I1=I1, I2=I2)
        o0.subtractFrom(o1)
        o1.erase()
    s.setPoint(pT0, pD0)
    s.setPoint(pT1, pD1)
    return o0


@activate(Group="Crossover", TooltipShort="Built-in CPJC", TooltipLong="Built-in CPJC (Decompiled from varmain/crossoversub/cpjc.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(OF=LENGTH, TooltipShort="OF")
@param(I1=LENGTH, TooltipShort="I1")
@param(I2=LENGTH, TooltipShort="I2")
@param(ID=STRING, TooltipShort="组件标识")
def CPJC_Sub(s, D1=114.3, D2=0.0, L1=0.0, L2=0.0, OF=0.0, I1=0.0, I2=0.0, ID='CPJC_Sub', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                _pc = 21 if not ((D2 if D2 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 12
            elif _pc == 12:
                D2 = D1
                _pc = 21
            elif _pc == 21:
                A1 = 60.0
                Lx = sin(asRadiants(A1)) * (D1 + D2)
                _pc = 74 if not ((L1 if L1 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 65
            elif _pc == 65:
                L1 = Lx
                _pc = 74
            elif _pc == 74:
                _pc = 95 if not ((L2 if L2 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 86
            elif _pc == 86:
                L2 = L1
                _pc = 95
            elif _pc == 95:
                _pc = 116 if not ((L1 if L1 is not None else -1e30) <= (L2 if L2 is not None else -1e30)) else 107
            elif _pc == 107:
                L0 = L1
                _pc = 122
            elif _pc == 116:
                L0 = L2
                _pc = 122
            elif _pc == 122:
                _pc = 143 if not ((Lx if Lx is not None else -1e30) < (L0 if L0 is not None else -1e30)) else 134
            elif _pc == 134:
                L0 = Lx
                _pc = 143
            elif _pc == 143:
                R1 = D1 / 2.0
                R2 = (D1 + D2) / 2.0
                OF = getThickness(D=D1, OF=OF)
                A1 = None
                LO = L0
                mult = 1.1
                multD = 0.9
                xD = D1
                _pc = 221
            elif _pc == 221:
                _pc = 475 if not (A1 == None) else 233
            elif _pc == 233:
                _exc_stk.append(284)
                _pc = 236
            elif _pc == 236:
                R3 = R1 * mult
                A1 = asDegrees(asin((LO * 2.0) / ((R2 + R3) * 2.0)))
                _pc = 381
            elif _pc == 284:
                _tmp = _stk.pop()
                _stk.append(_tmp)
                _pc = 380 if not (issubclass(_tmp, ValueError)) else 294
            elif _pc == 294:
                _stk.pop()
                _stk.pop()
                _stk.pop()
                _exc_stk.append(344)
                _pc = 300
            elif _pc == 300:
                R3 = R2
                A1 = asDegrees(asin((LO * 2.0) / ((R2 + R3) * 2.0)))
                _pc = 381
            elif _pc == 344:
                _tmp = _stk.pop()
                _stk.append(_tmp)
                _pc = 376 if not (issubclass(_tmp, ValueError)) else 354
            elif _pc == 354:
                _stk.pop()
                _stk.pop()
                _stk.pop()
                A1 = None
                mult = mult + 0.1
                _pc = 381
            elif _pc == 376:
                _pc = 381
            elif _pc == 380:
                _pc = 381
            elif _pc == 381:
                H0 = R3 - ((R3 + R2) * cos(asRadiants(A1)))
                _pc = 221 if not ((H0 if H0 is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 423
            elif _pc == 423:
                mult = 1.1
                xD = xD * multD
                R2 = (D2 + xD) / 2.0
                A1 = None
                multD = multD - 0.1
                _pc = 221
            elif _pc == 472:
                _pc = 221
            elif _pc == 475:
                _pc = 476
            elif _pc == 476:
                A2 = 180.0 - ((90.0 - A1) * 2.0)
                _pc = 527 if not (OF) else 500
            elif _pc == 500:
                R4 = R1 - OF
                R5 = (D2 / 2.0) + OF
                _pc = 543
            elif _pc == 527:
                R4 = R1
                R5 = D2 / 2.0
                _pc = 543
            elif _pc == 543:
                o0 = ARC3D2_(s, D=R4, D2=R4, R=R3, A=A1).rotateY(180.0).rotateX(90.0)
                o1 = ((ARC3D2_(s, D=R4, D2=R4, R=R2, A=A2).rotateZ(-(180.0 - A1))).rotateX(90.0)).rotateZ(180.0)
                o2 = None
                o3 = ARC3D2_(s, D=R4, D2=R4, R=R3, A=A1).rotateX(90.0)
                Pts0 = CPB_CalcPts(oA=o0, A=A1, L1=None, L2=None)
                p0 = Pts0[5]
                Pts1 = CPB_CalcPts(oA=o1, A=A2, L1=None, L2=None)
                p1 = Pts1[4]
                tX = abs(p0.x()) + abs(p1.x())
                tZ = abs(p0.z()) + abs(p1.z())
                o0.translate((-tX, 0.0, 0.0))
                o1.translate((0.0, 0.0, tZ))
                o3.translate((tX, 0.0, 0.0))
                o4 = None
                o5 = None
                _pc = 1020 if not ((LO if LO is not None else -1e30) < (L1 if L1 is not None else -1e30)) else 961
            elif _pc == 961:
                o4 = ((CYLINDER(s, R=R4, H=L1 - LO)).rotateY(-90.0)).translate((-LO, 0.0, 0.0))
                _pc = 1020
            elif _pc == 1020:
                _pc = 1090 if not ((LO if LO is not None else -1e30) < (L2 if L2 is not None else -1e30)) else 1032
            elif _pc == 1032:
                o5 = ((CYLINDER(s, R=R4, H=L2 - LO)).rotateY(90.0)).translate((LO, 0.0, 0.0))
                _pc = 1090
            elif _pc == 1090:
                arc3d2TMP = (((CYLINDER(s, R=(R4 * 0.01) / 2.0, H=R4 * 0.01)).rotateY(-90.0)).translate(Pts0[8])).translate((-tX, 0.0, 0.0))
                arc3d2TMP.uniteWith(o0)
                o0.erase()
                o0 = arc3d2TMP
                o0.uniteWith(o1)
                o1.erase()
                _pc = 1251 if not (o2) else 1225
            elif _pc == 1225:
                o0.uniteWith(o2)
                o2.erase()
                _pc = 1251
            elif _pc == 1251:
                o0.uniteWith(o3)
                o3.erase()
                _pc = 1306 if not (o4) else 1280
            elif _pc == 1280:
                o0.uniteWith(o4)
                o4.erase()
                _pc = 1306
            elif _pc == 1306:
                _pc = 1338 if not (o5) else 1312
            elif _pc == 1312:
                o0.uniteWith(o5)
                o5.erase()
                _pc = 1338
            elif _pc == 1338:
                L3 = R4 * 2.0
                L4 = L3 * 2.0
                L5 = LO * 2.0
                R6 = ((pow(LO, 2) + pow(R4, 2)) - pow(R5, 2)) / (((2 * R5) + R4) + (D1 / 2.0))
                xH = R5 * (sin(acos(LO / (R6 + R5))))
                o6 = CYLINDER(s, R=R6, H=L4).rotateX(90.0).translate((-LO, L3, R6 - R4))
                o7 = CYLINDER(s, R=R6, H=L4).rotateX(90.0).translate((LO, L3, R6 - R4))
                o8 = CYLINDER(s, R=R5, H=L4).rotateX(90.0).translate((0.0, L3, 0.0))
                o9 = (BOX(s, L=L4, W=R4 + xH, H=L5)).translate((0.0, 0.0, (-(R4 / 2.0)) + (xH / 2.0)))
                o8.uniteWith(o9)
                o9.erase()
                o8.subtractFrom(o6)
                o6.erase()
                o8.subtractFrom(o7)
                o7.erase()
                o0.subtractFrom(o8)
                o8.erase()
                s.setPoint((-L1 - I1, 0, 0), (-1, 0, 0))
                s.setPoint((L2 + I2, 0, 0), (1, 0, 0))
                return o0
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
