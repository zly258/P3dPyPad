# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.pipesub.cpp_util import *


@activate(Group="Pipe", TooltipShort="Nozzle, threaded, ASME B16.11", TooltipLong="Nozzle, threaded, ASME B16.11 (Decompiled from varmain/pipesub/cpp_ofof.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(OF=LENGTH, TooltipShort="OF")
@param(L1=LENGTH, TooltipShort="L1")
@param(I1=LENGTH, TooltipShort="I1")
@param(L2=LENGTH, TooltipShort="L2")
@param(I2=LENGTH, TooltipShort="I2")
@param(ID=STRING, TooltipShort="组件标识")
def CPP_OFOF(s, D=21.3, L=60.0, OF=-1.0, L1=15.0, I1=10.0, L2=15.0, I2=10.0, ID='CPP_OFOF', **kw):
    min_len = (L1 - I1) + (L2 - I2)
    if L <= min_len:
        L = max(60.0, min_len * 1.5 + 10.0)
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                noLeft = 0
                noRight = 0
                _pc = 33 if not ((I2 if I2 is not None else -1e30) <= (0 if 0 is not None else -1e30)) else 24
            elif _pc == 24:
                I2 = I1
                _pc = 33
            elif _pc == 33:
                _pc = 66 if not (L1 == -2) else 45
            elif _pc == 45:
                L1 = 0.0
                I1 = 0.0
                noLeft = 1
                _pc = 66
            elif _pc == 66:
                _pc = 108 if not (L2 == 0.0) else 78
            elif _pc == 78:
                _pc = 99 if not (noLeft == 1) else 90
            elif _pc == 90:
                L2 = -2
                _pc = 108
            elif _pc == 99:
                L2 = L1
                _pc = 108
            elif _pc == 108:
                _pc = 141 if not (L2 == -2) else 120
            elif _pc == 120:
                L2 = 0.0
                I2 = 0.0
                noRight = 1
                _pc = 141
            elif _pc == 141:
                DI = getInsideDiameter(D=D, OF=OF, Ever=1)
                _pc = 268 if not ((L if L is not None else -1e30) > (0 if 0 is not None else -1e30)) else 180
            elif _pc == 180:
                h_th = max(1.0, (L - (L1 - I1)) - (L2 - I2))
                oTH = ((CYLINDER(s, R=D / 2.0, H=h_th, O=DI / 2.0)).rotateY(90)).translate((L1 - I1, 0.0, 0.0))
                _pc = 281
            elif _pc == 268:
                oTH = None
                L = -L
                _pc = 281
            elif _pc == 281:
                _pc = 395 if not (noLeft == 0) else 293
            elif _pc == 293:
                oL1 = CON_OF(s, D1=D, D2=0.0, L=L1, OF=OF).rotateY(180).translate((L1 - I1, 0.0, 0.0))
                _pc = 395 if not (oTH) else 366
            elif _pc == 366:
                oTH.uniteWith(oL1)
                oL1.erase()
                _pc = 395
            elif _pc == 392:
                _pc = 395
            elif _pc == 395:
                _pc = 504 if not (noRight == 0) else 407
            elif _pc == 407:
                oL2 = CON_OF(s, D1=D, D2=0.0, L=L2, OF=OF).translate(((L - L2) + I2, 0.0, 0.0))
                _pc = 504 if not (oTH) else 475
            elif _pc == 475:
                oTH.uniteWith(oL2)
                oL2.erase()
                _pc = 504
            elif _pc == 501:
                _pc = 504
            elif _pc == 504:
                s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0, I1, L1 - I1)
                s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0, I2, L2 - I2)
                return oTH
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
