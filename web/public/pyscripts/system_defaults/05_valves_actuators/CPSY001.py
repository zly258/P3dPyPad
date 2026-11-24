# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.filtersub.cpsysub.cpsy_util import *


@activate(Group="Strainer", TooltipShort="CP METRIC Strainer", TooltipLong="CP METRIC Strainer (Decompiled from varmain/filtersub/cpsysub/cpsy001sub/cpsy001.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(LS=LENGTH, TooltipShort="LS")
@param(DS=LENGTH, TooltipShort="DS")
@param(H=LENGTH, TooltipShort="H")
@param(D4=LENGTH, TooltipShort="D4")
@param(H4=LENGTH, TooltipShort="H4")
@param(OF=LENGTH, TooltipShort="OF")
@param(A=ANGLE, TooltipShort="A")
@param(N=LENGTH, TooltipShort="N")
@param(P=INT, TooltipShort="P")
@param(PD=LENGTH, TooltipShort="PD")
@param(PL=LENGTH, TooltipShort="PL")
@param(PI=LENGTH, TooltipShort="PI")
@param(H1=LENGTH, TooltipShort="H1")
@param(B1=LENGTH, TooltipShort="B1")
@param(H2=LENGTH, TooltipShort="H2")
@param(B2=LENGTH, TooltipShort="B2")
@param(ID=STRING, TooltipShort="组件标识")
def CPSY001(s, D1=1016.0, D2=1016.0, L=5080.0, LS=0.0, DS=1270.0, H=1980.0, D4=0.0, H4=0.0, OF=-1.0, A=45.0, N=1, P=1, PD=0.0, PL=0.0, PI=0.0, H1=1320.0, B1=58.0, H2=1320.0, B2=58.0, ID='CPSY001', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                vC = CPSYCORRV(D1=D1, D2=D2, L=L, LS=LS, DS=DS, H=H, D4=D4, H4=H4, A=A, OF=OF, N=N, P=P, PD=PD, PL=PL, PI=PI, H1=H1, B1=B1, H2=H2, B2=B2, L1=0.0, L2=0.0, I1=None, I2=None, CPSTYPE=1)
                R1 = vC[0] / 2.0
                R2 = vC[1] / 2.0
                _pc = 271 if not ((vC[28] if vC[28] is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 197
            elif _pc == 197:
                oF1 = (CYLINDER(s, R=vC[5] / 2.0, H=vC[28], O=R1)).rotateY(90)
                R3 = R1 + vC[17]
                R4 = R1
                _pc = 297
            elif _pc == 271:
                oF1 = None
                R3 = R1
                R4 = R1 - vC[17]
                _pc = 297
            elif _pc == 297:
                _pc = 426 if not ((vC[29] if vC[29] is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 313
            elif _pc == 313:
                oF2 = (((CYLINDER(s, R=vC[6] / 2.0, H=vC[29], O=R2)).rotateY(90.0)).translate((vC[2] - vC[28], 0, 0))).rotateX(180)
                R5 = R2 + vC[17]
                R6 = R2
                _pc = 452
            elif _pc == 426:
                oF2 = None
                R5 = R2
                R6 = R2 - vC[17]
                _pc = 452
            elif _pc == 452:
                oC3 = None
                _pc = 604 if not (vC[0] == vC[1]) else 478
            elif _pc == 478:
                oC1 = CYLINDER(s, R=R3, H=vC[2], O=0.0).rotateY(90).translate((0, 0, 0))
                _pc = 727 if not ((vC[17] if vC[17] is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 546
            elif _pc == 546:
                oC3 = CYLINDER(s, R=R4, H=vC[2], O=0.0).rotateY(90).translate((0, 0, 0))
                _pc = 727
            elif _pc == 601:
                _pc = 727
            elif _pc == 604:
                oC1 = CONE(s, R1=R3, R2=R5, H=vC[2]).rotateY(90).translate((0, 0, 0))
                _pc = 727 if not ((vC[17] if vC[17] is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 672
            elif _pc == 672:
                oC3 = CONE(s, R1=R4, R2=R6, H=vC[2]).rotateY(90).translate((0, 0, 0))
                _pc = 727
            elif _pc == 727:
                oC2 = (((CYLINDER(s, R=vC[4] / 2.0, H=vC[31], O=0.0)).rotateY(90.0 - vC[30])).translate((vC[3] + vC[28], 0, 0))).rotateX(180.0)
                _pc = 917 if not ((vC[37] if vC[37] is not None else -1e30) < (1 if 1 is not None else -1e30)) else 841
            elif _pc == 841:
                oC4 = ((CYLINDER(s, R=vC[34] / 2.0, H=vC[33], O=0.0)).rotateY(-(90.0 - vC[30]))).translate(vC[35])
                _pc = 923
            elif _pc == 917:
                oC4 = None
                _pc = 923
            elif _pc == 923:
                oC5 = None
                oC6 = None
                _pc = 1029 if not (vC[39] == 0) else 951
            elif _pc == 951:
                oC5 = ((CYLINDER(s, R=PD / 2.0, H=abs(vC[40]), O=0.0)).rotateY(-(90.0 - vC[30]))).translate(vC[35])
                _pc = 1215
            elif _pc == 1029:
                _pc = 1215 if not (vC[39] == 1) else 1045
            elif _pc == 1045:
                _pc = 1136 if not ((PI if PI is not None else -1e30) > (0 if 0 is not None else -1e30)) else 1057
            elif _pc == 1057:
                oC6 = CON_OF(s, D1=PD, D2=0.0, L=abs(vC[40]), OF=vC[17]).rotateY(vC[30]).translate(vC[35])
                _pc = 1215
            elif _pc == 1136:
                oC6 = CON_OM(s, D1=PD, D2=0.0, L=abs(vC[40]), OF=vC[17]).rotateY(vC[30]).translate(vC[35])
                _pc = 1215
            elif _pc == 1215:
                oC1.uniteWith(oC2)
                oC2.erase()
                _pc = 1270 if not (oF1) else 1244
            elif _pc == 1244:
                oC1.uniteWith(oF1)
                oF1.erase()
                _pc = 1270
            elif _pc == 1270:
                _pc = 1302 if not (oF2) else 1276
            elif _pc == 1276:
                oC1.uniteWith(oF2)
                oF2.erase()
                _pc = 1302
            elif _pc == 1302:
                _pc = 1334 if not (oC4) else 1308
            elif _pc == 1308:
                oC1.uniteWith(oC4)
                oC4.erase()
                _pc = 1334
            elif _pc == 1334:
                _pc = 1366 if not (oC3) else 1340
            elif _pc == 1340:
                oC1.subtractFrom(oC3)
                oC3.erase()
                _pc = 1366
            elif _pc == 1366:
                _pc = 1398 if not (oC5) else 1372
            elif _pc == 1372:
                oC1.subtractFrom(oC5)
                oC5.erase()
                _pc = 1398
            elif _pc == 1398:
                _pc = 1430 if not (oC6) else 1404
            elif _pc == 1404:
                oC1.uniteWith(oC6)
                oC6.erase()
                _pc = 1430
            elif _pc == 1430:
                s.setPoint(vC[11], vC[12])
                s.setPoint(vC[13], vC[14])
                _pc = 1517 if not ((P if P is not None else -1e30) > (0 if 0 is not None else -1e30)) else 1490
            elif _pc == 1490:
                s.setPoint(vC[38], vC[36])
                _pc = 1517
            elif _pc == 1517:
                return None
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
