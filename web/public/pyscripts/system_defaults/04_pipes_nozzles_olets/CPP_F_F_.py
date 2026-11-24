# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpfwo import *
from varmain.pipesub.cpp_util import *


@activate(Group="Pipe", TooltipShort="Nozzle, flanged, C, 1, DIN 2630", TooltipLong="Nozzle, flanged, C, 1, DIN 2630 (Decompiled from varmain/pipesub/cpp_f_f_.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(OF=LENGTH, TooltipShort="OF")
@param(L1=LENGTH, TooltipShort="L1")
@param(B1=LENGTH, TooltipShort="B1")
@param(D12=LENGTH, TooltipShort="D12")
@param(W1=LENGTH, TooltipShort="W1")
@param(D13=LENGTH, TooltipShort="D13")
@param(L2=LENGTH, TooltipShort="L2")
@param(B2=LENGTH, TooltipShort="B2")
@param(D22=LENGTH, TooltipShort="D22")
@param(W2=LENGTH, TooltipShort="W2")
@param(D23=LENGTH, TooltipShort="D23")
@param(ID=STRING, TooltipShort="组件标识")
def CPP_F_F_(s, D=0.84, L=100.0, OF=-1.0, L1=1.81, B1=0.38, D12=3.5, W1=0.0, D13=1.19, L2=33.0, B2=16.0, D22=220.0, W2=0.0, D23=170.0, ID='CPP_F_F_', **kw):
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
                _pc = 66 if not (L2 == -2) else 51
            elif _pc == 51:
                L2 = 0.0
                noRight = 1
                _pc = 87
            elif _pc == 66:
                _pc = 87 if not (L2 == 0) else 78
            elif _pc == 78:
                L2 = L1
                _pc = 87
            elif _pc == 87:
                _pc = 108 if not ((D22 if D22 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 99
            elif _pc == 99:
                D22 = D12
                _pc = 108
            elif _pc == 108:
                xH1 = D12 + (OF * 2.0)
                _pc = 143 if not ((D12 if D12 is not None else -1e30) < (xH1 if xH1 is not None else -1e30)) else 134
            elif _pc == 134:
                D12 = xH1
                _pc = 143
            elif _pc == 143:
                _pc = 164 if not (W1 == -1) else 155
            elif _pc == 155:
                W1 = xH1
                _pc = 185
            elif _pc == 164:
                _pc = 185 if not (W1 == 0.0) else 176
            elif _pc == 176:
                W1 = D12
                _pc = 185
            elif _pc == 185:
                xH2 = D22 + (OF * 2.0)
                _pc = 220 if not ((D22 if D22 is not None else -1e30) < (xH2 if xH2 is not None else -1e30)) else 211
            elif _pc == 211:
                D22 = xH2
                _pc = 220
            elif _pc == 220:
                _pc = 241 if not (W2 == -1.0) else 232
            elif _pc == 232:
                W2 = xH2
                _pc = 262
            elif _pc == 241:
                _pc = 262 if not (W2 == 0.0) else 253
            elif _pc == 253:
                W2 = D22
                _pc = 262
            elif _pc == 262:
                _pc = 283 if not ((D23 if D23 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 274
            elif _pc == 274:
                D23 = D13
                _pc = 283
            elif _pc == 283:
                _pc = 304 if not ((B2 if B2 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 295
            elif _pc == 295:
                B2 = B1
                _pc = 304
            elif _pc == 304:
                _pc = 325 if not (L == 0.0) else 316
            elif _pc == 316:
                L = defaultPipeLength
                _pc = 325
            elif _pc == 325:
                DI = getInsideDiameter(D=D, OF=OF, Ever=1, mustCalc=True)
                DO = getInsideDiameter(D=D, OF=OF, Ever=1)
                _pc = 447 if not ((L if L is not None else -1e30) > (0 if 0 is not None else -1e30)) else 397
            elif _pc == 397:
                oTH = (CYLINDER(s, R=D / 2.0, H=L, O=DO / 2.0)).rotateY(90.0)
                _pc = 460
            elif _pc == 447:
                oTH = None
                L = -L
                _pc = 460
            elif _pc == 460:
                _pc = 561 if not (noLeft == 0) else 472
            elif _pc == 472:
                oF1 = CPFWO(s, L=L1, B=B1, D1=D12, D2=D, D3=D13, W=W1, OF=OF)
                _pc = 561 if not (oTH) else 532
            elif _pc == 532:
                oTH.uniteWith(oF1)
                oF1.erase()
                _pc = 561
            elif _pc == 558:
                _pc = 561
            elif _pc == 561:
                _pc = 689 if not (noRight == 0) else 573
            elif _pc == 573:
                oF2 = CPFWO(s, L=L2, B=B2, D1=D22, D2=D, D3=D23, W=W2, OF=OF).rotateZ(180).translate((L, 0.0, 0.0))
                _pc = 689 if not (oTH) else 660
            elif _pc == 660:
                oTH.uniteWith(oF2)
                oF2.erase()
                _pc = 689
            elif _pc == 686:
                _pc = 689
            elif _pc == 689:
                _pc = 710 if not ((W1 if W1 is not None else -1e30) <= (D12 if D12 is not None else -1e30)) else 701
            elif _pc == 701:
                WA1 = 0.0
                _pc = 716
            elif _pc == 710:
                WA1 = 90.0
                _pc = 716
            elif _pc == 716:
                _pc = 737 if not ((W2 if W2 is not None else -1e30) <= (D22 if D22 is not None else -1e30)) else 728
            elif _pc == 728:
                WA2 = 0.0
                _pc = 743
            elif _pc == 737:
                WA2 = 90.0
                _pc = 743
            elif _pc == 743:
                s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), WA1, 0.0, L1)
                s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0), WA2, 0.0, L1)
                return None
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
