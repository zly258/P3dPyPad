# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Coupling", TooltipShort="Built-in CYLSTACK002", TooltipLong="Built-in CYLSTACK002 (Decompiled from varmain/cylinderstacksub/cylstack002.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(I1=LENGTH, TooltipShort="I1")
@param(I2=LENGTH, TooltipShort="I2")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CYLSTACK002(s, D1=100.0, D2=200.0, L1=50.0, L2=100.0, I1=0.0, I2=0.0, OF=-1.0, ID='CYLSTACK002', **kw):
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
                o0 = (CYLINDER(s, R=D1 / 2.0, H=L1, O=0.0)).rotateY(90.0)
                o1 = ((CYLINDER(s, R=D2 / 2.0, H=L2, O=0.0)).rotateY(90.0)).translate((L1, 0, 0))
                o0.uniteWith(o1)
                o1.erase()
                Drill = 1
                _pc = 246 if not (OF == -1) else 223
            elif _pc == 223:
                OF = (D1 - CON_OF_DIV(D1)) / 2.0
                _pc = 267
            elif _pc == 246:
                _pc = 267 if not (OF == 0.0) else 258
            elif _pc == 258:
                Drill = None
                _pc = 267
            elif _pc == 267:
                _pc = 584 if not (Drill) else 273
            elif _pc == 273:
                sL1 = L1
                sL2 = L2
                _pc = 320 if not ((D1 if D1 is not None else -1e30) > (D2 if D2 is not None else -1e30)) else 297
            elif _pc == 297:
                sL1 = L1 - OF
                sL2 = L2 + OF
                _pc = 402
            elif _pc == 320:
                _pc = 355 if not ((D1 if D1 is not None else -1e30) < (D2 if D2 is not None else -1e30)) else 332
            elif _pc == 332:
                sL1 = L1 + OF
                sL2 = L2 - OF
                _pc = 402
            elif _pc == 355:
                _pc = 382 if not ((I2 if I2 is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 367
            elif _pc == 367:
                sL1 = L1
                sL2 = L2
                _pc = 402
            elif _pc == 382:
                sL1 = (L1 + L2) - OF
                sL2 = None
                _pc = 402
            elif _pc == 402:
                d0 = (CYLINDER(s, R=(D1 / 2.0) - OF, H=sL1, O=0.0)).rotateY(90.0)
                _pc = 558 if not (sL2) else 455
            elif _pc == 455:
                _pc = 558 if not ((sL2 if sL2 is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 467
            elif _pc == 467:
                d1 = ((CYLINDER(s, R=(D2 / 2.0) - OF, H=sL2, O=0.0)).rotateY(90.0)).translate((sL1, 0, 0))
                d0.uniteWith(d1)
                d1.erase()
                _pc = 558
            elif _pc == 558:
                o0.subtractFrom(d0)
                d0.erase()
                _pc = 584
            elif _pc == 584:
                o0.translate((-I1, 0.0, 0.0))
                s.setPoint((0, 0, 0), (-1, 0, 0))
                _pc = 678 if (areEqual(D1, D2)) else 638
            elif _pc == 638:
                s.setPoint((((L1 - I1) + L2) - I2, 0, 0), (1, 0, 0))
                _pc = 678
            elif _pc == 678:
                return None
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
