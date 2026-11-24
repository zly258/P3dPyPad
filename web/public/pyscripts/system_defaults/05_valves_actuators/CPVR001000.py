# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpflo import *
from varmain.valvsub.cpva001sub.cpva001000sub.cpva001000 import *
from varmain.valvsub.cpva001sub.cpva001_util import *
from varmain.valvsub.cpvxsub.cpvx201 import *
from varmain.valvsub.cpvxsub.cpvx202 import *


@activate(Group="Valve", TooltipShort="Built-in CPVR001000", TooltipLong="Built-in CPVR001000 (Decompiled from varmain/valvsub/cpvr001sub/cpvr001000sub/cpvr001000.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(X1=LENGTH, TooltipShort="X1")
@param(X2=LENGTH, TooltipShort="X2")
@param(H1=LENGTH, TooltipShort="H1")
@param(H2=LENGTH, TooltipShort="H2")
@param(W1=LENGTH, TooltipShort="W1")
@param(W2=LENGTH, TooltipShort="W2")
@param(A=ANGLE, TooltipShort="A")
@param(OF=LENGTH, TooltipShort="OF")
@param(B1=LENGTH, TooltipShort="B1")
@param(B2=LENGTH, TooltipShort="B2")
@param(DA=LENGTH, TooltipShort="DA")
@param(HA=LENGTH, TooltipShort="HA")
@param(isPilot=INT, TooltipShort="isPilot")
@param(ID=STRING, TooltipShort="组件标识")
def CPVR001000(s, D1=114.3, D2=0.0, L1=175.0, L2=0.0, X1=-2.0, X2=-2.0, H1=220.0, H2=0.0, W1=0.0, W2=0.0, A=0.0, OF=-1.0, B1=22.0, B2=0.0, DA=225.0, HA=345.0, isPilot=0, ID='CPVR001000', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                vC = CPVA001CORRV(D1=D1, D2=D2, L1=L1, L2=L2, H1=H1, H2=H2, X1=X1, X2=X2, B1=B1, B2=B2, W1=W1, W2=W2, A=A, OF=OF, L3=0.0, L4=0.0, I1=None, I2=None)
                oV = CPVA001000(s, D1=vC[1], D2=vC[0], L1=vC[3], L2=vC[2], H1=vC[5], H2=vC[4], X1=X2, X2=X1, B1=vC[30], B2=vC[29], W1=vC[32], W2=vC[31], A=vC[11], OF=vC[18])
                pP1 = oV.pointAt(1)
                pD1 = oV.directionAt(1)
                pP2 = oV.pointAt(0)
                pD2 = oV.directionAt(0)
                s.setPoint(pP1, pD1, vC[34])
                s.setPoint(pP2, pD2, vC[33])
                oA = None
                _pc = 487 if not ((HA if HA is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 385
            elif _pc == 385:
                _pc = 442 if not ((isPilot if isPilot is not None else -1e30) > (0 if 0 is not None else -1e30)) else 397
            elif _pc == 397:
                oA = CPVX202(s, D=DA, H=HA).rotateX(-90.0).rotateY(90.0)
                _pc = 487
            elif _pc == 442:
                oA = CPVX201(s, D=DA, H=HA).rotateX(-90.0).rotateY(90.0)
                _pc = 487
            elif _pc == 487:
                oTMP = HALFSPHERE(s, R=vC[0] * 0.0001)
                oTMP2 = (HALFSPHERE(s, R=vC[0] * 0.0001)).rotateY(180)
                oTMP.uniteWith(oTMP2)
                oTMP2.erase()
                oTMP.uniteWith(oV)
                oV.erase()
                _pc = 626 if not (oA) else 600
            elif _pc == 600:
                oTMP.uniteWith(oA)
                oA.erase()
                _pc = 626
            elif _pc == 626:
                return None
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
