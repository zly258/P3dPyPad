# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Coupling", TooltipShort="Built-in CYLSTACK003", TooltipLong="Built-in CYLSTACK003 (Decompiled from varmain/cylinderstacksub/cylstack003.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(L3=LENGTH, TooltipShort="L3")
@param(I1=LENGTH, TooltipShort="I1")
@param(I2=LENGTH, TooltipShort="I2")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CYLSTACK003(s, D1=100.0, D2=200.0, D3=300.0, L1=50.0, L2=100.0, L3=150.0, I1=0.0, I2=0.0, OF=-1.0, ID='CYLSTACK003', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                _pc = 57 if not (PnP3dACPAdapterIgnoreWallThickness == False) else 12
            elif _pc == 12:
                _pc = 36 if ((I1 if I1 is not None else -1e30) > (0 if 0 is not None else -1e30)) else 24
            elif _pc == 24:
                _pc = 57 if not ((I2 if I2 is not None else -1e30) > (0 if 0 is not None else -1e30)) else 36
            elif _pc == 36:
                _pc = 57 if not (OF == 0.0) else 48
            elif _pc == 48:
                OF = -1
                _pc = 57
            elif _pc == 57:
                _pc = 78 if not ((D2 if D2 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 69
            elif _pc == 69:
                D2 = D1
                _pc = 78
            elif _pc == 78:
                _pc = 99 if not ((D3 if D3 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 90
            elif _pc == 90:
                D3 = D2
                _pc = 99
            elif _pc == 99:
                o0 = (CYLINDER(s, R=D1 / 2.0, H=L1, O=0.0)).rotateY(90.0)
                o1 = ((CYLINDER(s, R=D2 / 2.0, H=L2, O=0.0)).rotateY(90.0)).translate((L1, 0, 0))
                o0.uniteWith(o1)
                o1.erase()
                o2 = ((CYLINDER(s, R=D3 / 2.0, H=L3, O=0.0)).rotateY(90.0)).translate((L1 + L2, 0, 0))
                o0.uniteWith(o2)
                o2.erase()
                Drill = 1
                _pc = 355 if not (OF == -1) else 332
            elif _pc == 332:
                OF = (D1 - CON_OF_DIV(D1)) / 2.0
                _pc = 376
            elif _pc == 355:
                _pc = 376 if not (OF == 0.0) else 367
            elif _pc == 367:
                Drill = None
                _pc = 376
            elif _pc == 376:
                _pc = 911 if not (Drill) else 382
            elif _pc == 382:
                _pc = 427 if not (D1 == D2) else 394
            elif _pc == 394:
                _pc = 427 if not (D2 == D3) else 406
            elif _pc == 406:
                sL1 = L1
                sL2 = L2
                sL3 = L3
                _pc = 622
            elif _pc == 427:
                _pc = 462 if not ((D1 if D1 is not None else -1e30) > (D2 if D2 is not None else -1e30)) else 439
            elif _pc == 439:
                sL1 = L1 - OF
                sL2 = L2 + OF
                _pc = 482
            elif _pc == 462:
                sL1 = L1 + OF
                sL2 = L2 - OF
                _pc = 482
            elif _pc == 482:
                _pc = 517 if not ((D2 if D2 is not None else -1e30) > (D3 if D3 is not None else -1e30)) else 494
            elif _pc == 494:
                sL2 = sL2 - OF
                sL3 = L3 + OF
                _pc = 622
            elif _pc == 517:
                _pc = 552 if not ((D2 if D2 is not None else -1e30) < (D3 if D3 is not None else -1e30)) else 529
            elif _pc == 529:
                sL2 = sL2 + OF
                sL3 = L3 - OF
                _pc = 622
            elif _pc == 552:
                _pc = 573 if not ((I2 if I2 is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 564
            elif _pc == 564:
                sL3 = L3
                _pc = 622
            elif _pc == 573:
                sL2 = sL2 - OF
                sL3 = None
                _pc = 622 if not ((sL1 if sL1 is not None else -1e30) > (((L1 + L2) + L3) if ((L1 + L2) + L3) is not None else -1e30)) else 609
            elif _pc == 609:
                sL1 = sL1 - OF
                _pc = 622
            elif _pc == 622:
                d0 = (CYLINDER(s, R=(D1 / 2.0) - OF, H=sL1, O=0.0)).rotateY(90.0)
                _pc = 772 if not ((sL2 if sL2 is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 681
            elif _pc == 681:
                d1 = ((CYLINDER(s, R=(D2 / 2.0) - OF, H=sL2, O=0.0)).rotateY(90.0)).translate((sL1, 0, 0))
                d0.uniteWith(d1)
                d1.erase()
                _pc = 772
            elif _pc == 772:
                _pc = 885 if not (sL3) else 778
            elif _pc == 778:
                _pc = 885 if not ((sL3 if sL3 is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 790
            elif _pc == 790:
                d2 = ((CYLINDER(s, R=(D3 / 2.0) - OF, H=sL3, O=0.0)).rotateY(90.0)).translate((sL1 + sL2, 0, 0))
                d0.uniteWith(d2)
                d2.erase()
                _pc = 885
            elif _pc == 885:
                o0.subtractFrom(d0)
                d0.erase()
                _pc = 911
            elif _pc == 911:
                o0.translate((-I1, 0.0, 0.0))
                s.setPoint((0, 0, 0), (-1, 0, 0))
                _pc = 1009 if (areEqual(D2, D3)) else 965
            elif _pc == 965:
                s.setPoint(((((L1 - I1) + L2) + L3) - I2, 0, 0), (1, 0, 0))
                _pc = 1009
            elif _pc == 1009:
                return None
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
