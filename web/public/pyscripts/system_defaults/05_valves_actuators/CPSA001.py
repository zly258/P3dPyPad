# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.filtersub.cpsasub.cpsa_util import *


@activate(Group="Strainer", TooltipShort="Built-in CPSA001", TooltipLong="Built-in CPSA001 (Decompiled from varmain/filtersub/cpsasub/cpsa001sub/cpsa001.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(LS=LENGTH, TooltipShort="LS")
@param(LP=LENGTH, TooltipShort="LP")
@param(D3=LENGTH, TooltipShort="D3")
@param(H3=LENGTH, TooltipShort="H3")
@param(D4=LENGTH, TooltipShort="D4")
@param(H4=LENGTH, TooltipShort="H4")
@param(H5=LENGTH, TooltipShort="H5")
@param(D6=LENGTH, TooltipShort="D6")
@param(H6=LENGTH, TooltipShort="H6")
@param(I6=LENGTH, TooltipShort="I6")
@param(HO1=LENGTH, TooltipShort="HO1")
@param(HO2=LENGTH, TooltipShort="HO2")
@param(A=ANGLE, TooltipShort="A")
@param(OF=LENGTH, TooltipShort="OF")
@param(H1=LENGTH, TooltipShort="H1")
@param(H2=LENGTH, TooltipShort="H2")
@param(B1=LENGTH, TooltipShort="B1")
@param(B2=LENGTH, TooltipShort="B2")
@param(ID=STRING, TooltipShort="组件标识")
def CPSA001(s, D1=114.3, D2=0.0, LS=200.0, LP=0.0, D3=0.0, H3=500.0, D4=0.0, H4=0.0, H5=100.0, D6=50.0, H6=75.0, I6=30.0, HO1=0.0, HO2=0.0, A=0.0, OF=-1.0, H1=220.0, H2=0.0, B1=22.0, B2=0.0, ID='CPSA001', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                vC = CPSACORRV(D1=D1, D2=D2, LS=LS, LP=LP, D3=D3, H3=H3, D4=D4, H4=H4, H5=H5, D6=D6, H6=H6, I6=I6, HO1=HO1, HO2=HO2, A=A, OF=OF, H1=H1, H2=H2, B1=B1, B2=B2, L1=0.0, L2=0.0, I1=None, I2=None, CPSTYPE=1)
                R1 = vC[5] / 2.0
                R2 = vC[6] / 2.0
                R3 = vC[0] / 2.0
                R4 = vC[1] / 2.0
                oC0 = CYLINDER(s, R=vC[30], H=vC[29], O=0.0).translate((0.0, 0.0, -vC[36]))
                _pc = 357 if not (vC[51]) else 286
            elif _pc == 286:
                oC1 = CYLINDER(s, R=vC[39], H=vC[37], O=0.0).translate((0.0, 0.0, vC[34] - vC[37]))
                _pc = 363
            elif _pc == 357:
                oC1 = None
                _pc = 363
            elif _pc == 363:
                _pc = 481 if not ((H5 if H5 is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 375
            elif _pc == 375:
                _pc = 400 if not ((D6 if D6 is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 387
            elif _pc == 387:
                R5 = vC[46]
                _pc = 406
            elif _pc == 400:
                R5 = 0.0
                _pc = 406
            elif _pc == 406:
                oC2 = CONE(s, R1=vC[30], R2=R5, H=H5, O=0.0).rotateY(180.0).translate((0.0, 0.0, -vC[36]))
                _pc = 487
            elif _pc == 481:
                oC2 = None
                _pc = 487
            elif _pc == 487:
                _pc = 557 if not (vC[45]) else 497
            elif _pc == 497:
                oC3 = CYLINDER(s, R=vC[46], H=H6, O=0.0).translate((0.0, 0.0, -vC[42]))
                _pc = 563
            elif _pc == 557:
                oC3 = None
                _pc = 563
            elif _pc == 563:
                oC4 = CYLINDER(s, R=R3, H=vC[3], O=0.0).rotateY(90.0)
                _pc = 690 if not ((vC[32] if vC[32] is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 622
            elif _pc == 622:
                oF1 = CYLINDER(s, R=R1, H=vC[32], O=0.0).rotateY(-90.0).translate((vC[3], 0.0, 0.0))
                _pc = 696
            elif _pc == 690:
                oF1 = None
                _pc = 696
            elif _pc == 696:
                oC5 = CYLINDER(s, R=R4, H=vC[4], O=0.0).rotateY(90.0).translate((0.0, 0.0, vC[31])).rotateZ(vC[48])
                _pc = 875 if not ((vC[33] if vC[33] is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 790
            elif _pc == 790:
                oF2 = CYLINDER(s, R=R2, H=vC[33], O=0.0).rotateY(-90.0).translate((vC[4], 0.0, vC[31])).rotateZ(vC[48])
                _pc = 881
            elif _pc == 875:
                oF2 = None
                _pc = 881
            elif _pc == 881:
                oC6 = None
                oC7 = None
                oCC4 = None
                oCC1 = None
                oCC2 = None
                oCC3 = None
                oCC4 = None
                oCC5 = None
                _pc = 1484 if not ((vC[17] if vC[17] is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 945
            elif _pc == 945:
                R6 = R3 - vC[17]
                oC6 = CYLINDER(s, R=R6, H=vC[3], O=0.0).rotateY(90.0)
                oCC1 = SPHERE(s, R=R6).translate((0.0, 0.0, 0.0))
                R7 = R4 - vC[17]
                oC7 = CYLINDER(s, R=R7, H=vC[4], O=0.0).rotateY(90.0).translate((0.0, 0.0, vC[31])).rotateZ(vC[48])
                oCC2 = SPHERE(s, R=R7).translate((0.0, 0.0, vC[31])).rotateZ(vC[48])
                _pc = 1352 if not (vC[31] != 0.0) else 1190
            elif _pc == 1190:
                _pc = 1251 if not (R6 != R7) else 1202
            elif _pc == 1202:
                oCC3 = CONE(s, R1=R7, R2=R6, H=abs(vC[31]), O=0.0)
                _pc = 1291
            elif _pc == 1251:
                oCC3 = CYLINDER(s, R=R6, H=abs(vC[31]), O=0.0)
                _pc = 1291
            elif _pc == 1291:
                _pc = 1323 if not ((vC[31] if vC[31] is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 1307
            elif _pc == 1307:
                oCC3.rotateY(180.0)
                _pc = 1323
            elif _pc == 1323:
                oCC3.translate((0.0, 0.0, vC[31]))
                _pc = 1358
            elif _pc == 1352:
                oCC3 = None
                _pc = 1358
            elif _pc == 1358:
                _pc = 1484 if not (vC[45]) else 1368
            elif _pc == 1368:
                oCC4 = CYLINDER(s, R=vC[47], H=vC[42], O=0.0).translate((0.0, 0.0, -vC[42]))
                _pc = 1481 if not ((vC[47] if vC[47] is not None else -1e30) > (((R6 - R7) + R6) if ((R6 - R7) + R6) is not None else -1e30)) else 1453
            elif _pc == 1453:
                oCC5 = SPHERE(s, R=vC[47])
                _pc = 1481
            elif _pc == 1478:
                _pc = 1484
            elif _pc == 1481:
                _pc = 1484
            elif _pc == 1484:
                _pc = 1516 if not (oC1) else 1490
            elif _pc == 1490:
                oC0.uniteWith(oC1)
                oC1.erase()
                _pc = 1516
            elif _pc == 1516:
                _pc = 1548 if not (oC2) else 1522
            elif _pc == 1522:
                oC0.uniteWith(oC2)
                oC2.erase()
                _pc = 1548
            elif _pc == 1548:
                _pc = 1580 if not (oC3) else 1554
            elif _pc == 1554:
                oC0.uniteWith(oC3)
                oC3.erase()
                _pc = 1580
            elif _pc == 1580:
                _pc = 1612 if not (oF1) else 1586
            elif _pc == 1586:
                oC4.uniteWith(oF1)
                oF1.erase()
                _pc = 1612
            elif _pc == 1612:
                oC0.uniteWith(oC4)
                oC4.erase()
                _pc = 1667 if not (oF2) else 1641
            elif _pc == 1641:
                oC5.uniteWith(oF2)
                oF2.erase()
                _pc = 1667
            elif _pc == 1667:
                oC0.uniteWith(oC5)
                oC5.erase()
                _pc = 1893 if not (oC6) else 1696
            elif _pc == 1696:
                oC6.uniteWith(oCC1)
                oCC1.erase()
                _pc = 1757 if not (oCC3) else 1725
            elif _pc == 1725:
                oC6.uniteWith(oCC3)
                oCC3.erase()
                oCC3 = None
                _pc = 1757
            elif _pc == 1757:
                oC7.uniteWith(oCC2)
                oCC2.erase()
                oC6.uniteWith(oC7)
                oC7.erase()
                _pc = 1867 if not (oCC4) else 1809
            elif _pc == 1809:
                oC6.uniteWith(oCC4)
                oCC4.erase()
                _pc = 1867 if not (oCC5) else 1838
            elif _pc == 1838:
                oC6.uniteWith(oCC5)
                oCC5.erase()
                _pc = 1867
            elif _pc == 1864:
                _pc = 1867
            elif _pc == 1867:
                oC0.subtractFrom(oC6)
                oC6.erase()
                _pc = 1893
            elif _pc == 1893:
                oC0.translate((-vC[3], 0.0, 0.0))
                s.setPoint(vC[11], vC[12])
                s.setPoint(vC[13], vC[14])
                _pc = 2005 if not (vC[45]) else 1978
            elif _pc == 1978:
                s.setPoint(vC[43], vC[44])
                _pc = 2005
            elif _pc == 2005:
                return None
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
