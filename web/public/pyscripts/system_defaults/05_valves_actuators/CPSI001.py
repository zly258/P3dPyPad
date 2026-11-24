# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.filtersub.cpsisub.cpsi_util import *


@activate(Group="Strainer", TooltipShort="Built-in CPSI001", TooltipLong="Built-in CPSI001 (Decompiled from varmain/filtersub/cpsisub/cpsi001sub/cpsi001.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(LS=LENGTH, TooltipShort="LS")
@param(D3=LENGTH, TooltipShort="D3")
@param(H3=LENGTH, TooltipShort="H3")
@param(D4=LENGTH, TooltipShort="D4")
@param(H4=LENGTH, TooltipShort="H4")
@param(H5=LENGTH, TooltipShort="H5")
@param(D6=LENGTH, TooltipShort="D6")
@param(H6=LENGTH, TooltipShort="H6")
@param(I6=LENGTH, TooltipShort="I6")
@param(HO1=LENGTH, TooltipShort="HO1")
@param(OF=LENGTH, TooltipShort="OF")
@param(H1=LENGTH, TooltipShort="H1")
@param(H2=LENGTH, TooltipShort="H2")
@param(B1=LENGTH, TooltipShort="B1")
@param(B2=LENGTH, TooltipShort="B2")
@param(ID=STRING, TooltipShort="组件标识")
def CPSI001(s, D1=114.3, D2=0.0, L=450.0, LS=0.0, D3=0.0, H3=500.0, D4=0.0, H4=0.0, H5=100.0, D6=50.0, H6=75.0, I6=30.0, HO1=0.0, OF=-1.0, H1=220.0, H2=0.0, B1=22.0, B2=0.0, ID='CPSI001', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                vC = CPSICORRV(D1=D1, D2=D2, L=L, LS=LS, D3=D3, H3=H3, D4=D4, H4=H4, H5=H5, D6=D6, H6=H6, I6=I6, HO1=HO1, HO2=None, OF=OF, H1=H1, H2=H2, B1=B1, B2=B2, L1=0.0, L2=0.0, I1=None, I2=None, CPSTYPE=1)
                R1 = vC[5] / 2.0
                R2 = vC[6] / 2.0
                R3 = vC[0] / 2.0
                R4 = vC[1] / 2.0
                oC0 = CYLINDER(s, R=vC[30], H=vC[29], O=0.0).translate((0.0, 0.0, -vC[36]))
                _pc = 351 if not (vC[51]) else 280
            elif _pc == 280:
                oC1 = CYLINDER(s, R=vC[39], H=vC[37], O=0.0).translate((0.0, 0.0, vC[34] - vC[37]))
                _pc = 357
            elif _pc == 351:
                oC1 = None
                _pc = 357
            elif _pc == 357:
                _pc = 475 if not ((H5 if H5 is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 369
            elif _pc == 369:
                _pc = 394 if not ((D6 if D6 is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 381
            elif _pc == 381:
                R5 = vC[46]
                _pc = 400
            elif _pc == 394:
                R5 = 0.0
                _pc = 400
            elif _pc == 400:
                oC2 = CONE(s, R1=vC[30], R2=R5, H=H5, O=0.0).rotateY(180.0).translate((0.0, 0.0, -vC[36]))
                _pc = 481
            elif _pc == 475:
                oC2 = None
                _pc = 481
            elif _pc == 481:
                _pc = 551 if not (vC[45]) else 491
            elif _pc == 491:
                oC3 = CYLINDER(s, R=vC[46], H=H6, O=0.0).translate((0.0, 0.0, -vC[42]))
                _pc = 557
            elif _pc == 551:
                oC3 = None
                _pc = 557
            elif _pc == 557:
                oC4 = CYLINDER(s, R=R3, H=vC[3], O=0.0).rotateY(-90.0)
                _pc = 685 if not ((vC[32] if vC[32] is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 616
            elif _pc == 616:
                oF1 = CYLINDER(s, R=R1, H=vC[32], O=0.0).rotateY(90.0).translate((-vC[3], 0.0, 0.0))
                _pc = 691
            elif _pc == 685:
                oF1 = None
                _pc = 691
            elif _pc == 691:
                oC5 = CYLINDER(s, R=R4, H=vC[4], O=0.0).rotateY(90.0).translate((0.0, 0.0, vC[31]))
                _pc = 844 if not ((vC[33] if vC[33] is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 772
            elif _pc == 772:
                oF2 = CYLINDER(s, R=R2, H=vC[33], O=0.0).rotateY(-90.0).translate((vC[4], 0.0, vC[31]))
                _pc = 850
            elif _pc == 844:
                oF2 = None
                _pc = 850
            elif _pc == 850:
                oC6 = None
                oC7 = None
                oCC1 = None
                oCC2 = None
                oCC3 = None
                oCC4 = None
                oCC5 = None
                _pc = 1284 if not ((vC[17] if vC[17] is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 908
            elif _pc == 908:
                R6 = R3 - vC[17]
                oC6 = CYLINDER(s, R=R6, H=vC[3], O=0.0).rotateY(-90.0)
                oCC1 = SPHERE(s, R=R6).translate((0.0, 0.0, 0.0))
                R7 = R4 - vC[17]
                oC7 = CYLINDER(s, R=R7, H=vC[4], O=0.0).rotateY(90.0).translate((0.0, 0.0, vC[31]))
                oCC2 = SPHERE(s, R=R7).translate((0.0, 0.0, vC[31]))
                _pc = 1275 if not (vC[31] != 0.0) else 1127
            elif _pc == 1127:
                _pc = 1210 if not (R6 != R7) else 1139
            elif _pc == 1139:
                oCC3 = CONE(s, R1=R7, R2=R6, H=abs(vC[31]), O=0.0).translate((0.0, 0.0, vC[31]))
                _pc = 1281
            elif _pc == 1210:
                oCC3 = CYLINDER(s, R=R6, H=abs(vC[31]), O=0.0).translate((0.0, 0.0, vC[31]))
                _pc = 1284
            elif _pc == 1275:
                oCC3 = None
                _pc = 1281
            elif _pc == 1281:
                _pc = 1284
            elif _pc == 1284:
                _pc = 1407 if not (vC[45]) else 1294
            elif _pc == 1294:
                oCC4 = CYLINDER(s, R=vC[47], H=vC[42], O=0.0).translate((0.0, 0.0, -vC[42]))
                _pc = 1407 if not ((vC[47] if vC[47] is not None else -1e30) > (((R6 - R7) + R6) if ((R6 - R7) + R6) is not None else -1e30)) else 1379
            elif _pc == 1379:
                oCC5 = SPHERE(s, R=vC[47])
                _pc = 1407
            elif _pc == 1404:
                _pc = 1407
            elif _pc == 1407:
                _pc = 1439 if not (oC1) else 1413
            elif _pc == 1413:
                oC0.uniteWith(oC1)
                oC1.erase()
                _pc = 1439
            elif _pc == 1439:
                _pc = 1471 if not (oC2) else 1445
            elif _pc == 1445:
                oC0.uniteWith(oC2)
                oC2.erase()
                _pc = 1471
            elif _pc == 1471:
                _pc = 1503 if not (oC3) else 1477
            elif _pc == 1477:
                oC0.uniteWith(oC3)
                oC3.erase()
                _pc = 1503
            elif _pc == 1503:
                _pc = 1535 if not (oF1) else 1509
            elif _pc == 1509:
                oC4.uniteWith(oF1)
                oF1.erase()
                _pc = 1535
            elif _pc == 1535:
                oC0.uniteWith(oC4)
                oC4.erase()
                _pc = 1590 if not (oF2) else 1564
            elif _pc == 1564:
                oC5.uniteWith(oF2)
                oF2.erase()
                _pc = 1590
            elif _pc == 1590:
                oC0.uniteWith(oC5)
                oC5.erase()
                _pc = 1816 if not (oC6) else 1619
            elif _pc == 1619:
                oC6.uniteWith(oCC1)
                oCC1.erase()
                _pc = 1680 if not (oCC3) else 1648
            elif _pc == 1648:
                oC6.uniteWith(oCC3)
                oCC3.erase()
                oCC3 = None
                _pc = 1680
            elif _pc == 1680:
                oC7.uniteWith(oCC2)
                oCC2.erase()
                oC6.uniteWith(oC7)
                oC7.erase()
                _pc = 1790 if not (oCC4) else 1732
            elif _pc == 1732:
                oC6.uniteWith(oCC4)
                oCC4.erase()
                _pc = 1790 if not (oCC5) else 1761
            elif _pc == 1761:
                oC6.uniteWith(oCC5)
                oCC5.erase()
                _pc = 1790
            elif _pc == 1787:
                _pc = 1790
            elif _pc == 1790:
                oC0.subtractFrom(oC6)
                oC6.erase()
                _pc = 1816
            elif _pc == 1816:
                oC0.translate((vC[3], 0.0, 0.0))
                s.setPoint(vC[11], vC[12])
                s.setPoint(vC[13], vC[14])
                _pc = 1927 if not (vC[45]) else 1900
            elif _pc == 1900:
                s.setPoint(vC[43], vC[44])
                _pc = 1927
            elif _pc == 1927:
                return None
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
