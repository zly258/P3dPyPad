# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.pipesub.cpp_util import *


@activate(Group="Pipe", TooltipShort="Nozzle, threaded (M), ASME IMPERIAL", TooltipLong="Nozzle, threaded (M), ASME IMPERIAL (Decompiled from varmain/pipesub/cpp_omom.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(OF=LENGTH, TooltipShort="OF")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(ID=STRING, TooltipShort="组件标识")
def CPP_OMOM(s, D=21.3, L=60.0, OF=-1.0, L1=15.0, L2=15.0, ID='CPP_OMOM', **kw):
    if L <= L1 + L2:
        L = max(60.0, (L1 + L2) * 1.5)
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                noLeft = 0
                noRight = 0
                _pc = 39 if not (L1 == -2) else 24
            elif _pc == 24:
                L1 = 0.0
                noLeft = 1
                _pc = 39
            elif _pc == 39:
                _pc = 81 if not (L2 == 0.0) else 51
            elif _pc == 51:
                _pc = 72 if not (noLeft == 1) else 63
            elif _pc == 63:
                L2 = -2
                _pc = 81
            elif _pc == 72:
                L2 = L1
                _pc = 81
            elif _pc == 81:
                _pc = 108 if not (L2 == -2) else 93
            elif _pc == 93:
                L2 = 0.0
                noRight = 1
                _pc = 108
            elif _pc == 108:
                _pc = 129 if not (L == 0.0) else 120
            elif _pc == 120:
                L = defaultPipeLength
                _pc = 129
            elif _pc == 129:
                DI = getInsideDiameter(D=D, OF=OF, Ever=1)
                _pc = 244 if not ((L if L is not None else -1e30) > (0 if 0 is not None else -1e30)) else 168
            elif _pc == 168:
                h_th = max(1.0, (L - L1) - L2)
                oTH = ((CYLINDER(s, R=D / 2.0, H=h_th, O=DI / 2.0)).rotateY(90)).translate((L1, 0.0, 0.0))
                _pc = 257
            elif _pc == 244:
                oTH = None
                L = -L
                _pc = 257
            elif _pc == 257:
                _pc = 367 if not (noLeft == 0) else 269
            elif _pc == 269:
                oL1 = CON_OM(s, D1=D, D2=0.0, L=L1, OF=OF).rotateY(180).translate((L1, 0.0, 0.0))
                _pc = 367 if not (oTH) else 338
            elif _pc == 338:
                oTH.uniteWith(oL1)
                oL1.erase()
                _pc = 367
            elif _pc == 364:
                _pc = 367
            elif _pc == 367:
                _pc = 472 if not (noRight == 0) else 379
            elif _pc == 379:
                oL2 = CON_OM(s, D1=D, D2=0.0, L=L2, OF=OF).translate((L - L2, 0.0, 0.0))
                _pc = 472 if not (oTH) else 443
            elif _pc == 443:
                oTH.uniteWith(oL2)
                oL2.erase()
                _pc = 472
            elif _pc == 469:
                _pc = 472
            elif _pc == 472:
                s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0, 0.0, L1)
                s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0, 0.0, L2)
                return oTH
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
