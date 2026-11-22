# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.arcsub.cpb_util import *


@activate(Group="Adapter", TooltipShort="Built-in CPJO", TooltipLong="Built-in CPJO (Decompiled from varmain/offsetsub/cpjo.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(L1=LENGTH, TooltipShort="L1")
@param(H=LENGTH, TooltipShort="H")
@param(A=ANGLE, TooltipShort="A")
@param(R1=LENGTH, TooltipShort="R1")
@param(R2=LENGTH, TooltipShort="R2")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPJO(s, D1=114.3, D2=0.0, L=500.0, L1=100.0, H=230.0, A=0.0, R1=0.0, R2=0.0, OF=-1.0, ID='CPJO', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                _exc_stk.append(23)
                _pc = 3
            elif _pc == 3:
                m1 = float(kw['m1'])
                _pc = 46
            elif _pc == 23:
                _tmp = _stk.pop()
                _stk.append(_tmp)
                _pc = 45 if not (issubclass(_tmp, KeyError)) else 33
            elif _pc == 33:
                _stk.pop()
                _stk.pop()
                _stk.pop()
                m1 = 0.0
                _pc = 46
            elif _pc == 45:
                _pc = 46
            elif _pc == 46:
                _exc_stk.append(69)
                _pc = 49
            elif _pc == 49:
                m2 = float(kw['m2'])
                _pc = 92
            elif _pc == 69:
                _tmp = _stk.pop()
                _stk.append(_tmp)
                _pc = 91 if not (issubclass(_tmp, KeyError)) else 79
            elif _pc == 79:
                _stk.pop()
                _stk.pop()
                _stk.pop()
                m2 = 0.0
                _pc = 92
            elif _pc == 91:
                _pc = 92
            elif _pc == 92:
                _exc_stk.append(130)
                _pc = 95
            elif _pc == 95:
                POF = False
                _pc = 126 if not (kw['POF'] == 1) else 117
            elif _pc == 117:
                POF = True
                _pc = 126
            elif _pc == 126:
                _pc = 153
            elif _pc == 130:
                _tmp = _stk.pop()
                _stk.append(_tmp)
                _pc = 152 if not (issubclass(_tmp, KeyError)) else 140
            elif _pc == 140:
                _stk.pop()
                _stk.pop()
                _stk.pop()
                POF = False
                _pc = 153
            elif _pc == 152:
                _pc = 153
            elif _pc == 153:
                OF = getThickness(D=D1, OF=OF, Ever=POF)
                _pc = 201 if not ((D2 if D2 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 192
            elif _pc == 192:
                D2 = D1
                _pc = 201
            elif _pc == 201:
                _pc = 268 if not (POF) else 207
            elif _pc == 207:
                _pc = 236 if not ((m1 if m1 is not None else -1e30) < (0.0 if 0.0 is not None else -1e30)) else 219
            elif _pc == 219:
                D1 = D1 + (OF * 2.0)
                _pc = 236
            elif _pc == 236:
                _pc = 268 if not ((m2 if m2 is not None else -1e30) < (0.0 if 0.0 is not None else -1e30)) else 248
            elif _pc == 248:
                D2 = D2 + (OF * 2.0)
                _pc = 268
            elif _pc == 265:
                _pc = 268
            elif _pc == 268:
                _pc = 289 if not ((A if A is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 280
            elif _pc == 280:
                A = 45.0
                _pc = 289
            elif _pc == 289:
                _pc = 328 if not ((R1 if R1 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 301
            elif _pc == 301:
                R1 = D1 / 2.0
                R1 = R1 + (R1 * 0.0001)
                _pc = 371
            elif _pc == 328:
                _pc = 371 if not ((R1 if R1 is not None else -1e30) <= ((D1 / 2.0) if (D1 / 2.0) is not None else -1e30)) else 344
            elif _pc == 344:
                R1 = D1 / 2.0
                R1 = R1 + (R1 * 0.0001)
                _pc = 371
            elif _pc == 371:
                _pc = 392 if not (R2 == 0.0) else 383
            elif _pc == 383:
                R2 = R1
                _pc = 392
            elif _pc == 392:
                _pc = 420 if ((R2 if R2 is not None else -1e30) <= (-1 if -1 is not None else -1e30)) else 404
            elif _pc == 404:
                _pc = 447 if not ((R2 if R2 is not None else -1e30) <= ((D2 / 2.0) if (D2 / 2.0) is not None else -1e30)) else 420
            elif _pc == 420:
                R2 = D2 / 2.0
                R2 = R2 + (R2 * 0.0001)
                _pc = 447
            elif _pc == 447:
                o1 = CPJO_Sub(s, D1=D1, D2=D2, L=L, L1=L1, H=H, A=A, R1=R1, R2=R2, m1=m1, m2=m2).translate((m1, 0.0, 0.0))
                o0 = ((CYLINDER(s, R=(D1 - (D1 * 0.01)) / 2.0, H=D1 * 0.01)).rotateY(90.0)).translate((m1, 0.0, 0.0))
                o0.uniteWith(o1)
                o1.erase()
                _pc = 761 if (OF == 0.0) else 639
            elif _pc == 639:
                o2 = CPJO_Sub(s, D1=D1, D2=D2, L=L, L1=L1, H=H, A=A, R1=R1, R2=R2, OF=OF, m1=m1, m2=m2).translate((m1, 0.0, 0.0))
                o0.subtractFrom(o2)
                o2.erase()
                _pc = 761
            elif _pc == 761:
                s.setPoint((0.0, 0.0, 0.0), (-1, 0, 0))
                s.setPoint((L, H, 0.0), (1, 0, 0))
                return o0
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise


@activate(Group="Adapter", TooltipShort="Built-in CPJO", TooltipLong="Built-in CPJO (Decompiled from varmain/offsetsub/cpjo.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(L=LENGTH, TooltipShort="L")
@param(L1=LENGTH, TooltipShort="L1")
@param(H=LENGTH, TooltipShort="H")
@param(A=LENGTH, TooltipShort="A")
@param(R1=LENGTH, TooltipShort="R1")
@param(R2=LENGTH, TooltipShort="R2")
@param(OF=LENGTH, TooltipShort="OF")
@param(m1=LENGTH, TooltipShort="m1")
@param(m2=LENGTH, TooltipShort="m2")
@param(ID=STRING, TooltipShort="组件标识")
def CPJO_Sub(s, D1=114.3, D2=0.0, L=0.0, L1=0.0, H=0.0, A=0.0, R1=0.0, R2=0.0, OF=0.0, m1=0.0, m2=0.0, ID='CPJO_Sub', **kw):
    L = (L - m1) - m2
    L1 = L1 - m1
    oR1 = (D1 / 2.0) - OF
    oR2 = (D2 / 2.0) - OF
    aL = R1 * (tan(asRadiants(A / 2.0)))
    aH = R1 - (sqrt(pow(R1, 2.0) - (pow(R1 * (cos(asRadiants(90.0 - A))), 2.0))))
    bL = R2 * (tan(asRadiants(A / 2.0)))
    bH = R2 - (sqrt(pow(R2, 2.0) - (pow(R2 * (cos(asRadiants(90.0 - A))), 2.0))))
    hL = H / tan(asRadiants(A))
    sL = sqrt(pow(H, 2.0) + pow(hL, 2.0))
    mL = (sL - aL) - bL
    eL = L - (((L1 + hL) + aL) + bL)
    o0 = CYLINDER(s, R=oR1, H=L1).rotateY(90.0)
    o1 = ARC3D2_(s, D=oR1, D2=oR1, R=R1, A=A).rotateZ(A).translate((L1 + aL, 0.0, 0.0))
    if oR1 > oR2:
        o2 = CONE(s, R1=oR1, R2=oR2, H=mL, E=0.0).rotateY(90.0)
    else:
        if oR1 < oR2:
            o2 = CONE(s, R1=oR2, R2=oR1, H=mL, E=0.0).rotateY(90.0).rotateZ(180.0).translate((mL, 0.0, 0.0))
        else:
            o2 = CYLINDER(s, R=oR1, H=mL).rotateY(90.0)
    o2.translate((aL, 0.0, 0.0)).rotateZ(A).translate((L1 + aL, 0.0, 0.0))
    o3 = ARC3D2_(s, D=oR2, D2=oR2, R=R2, A=A).rotateZ(180.0).translate((sL, 0.0, 0.0)).rotateZ(A).translate((L1 + aL, 0.0, 0.0))
    o4 = CYLINDER(s, R=oR2, H=eL).rotateY(-90.0).translate((L, H, 0.0))
    o0.uniteWith(o1)
    o1.erase()
    o0.uniteWith(o2)
    o2.erase()
    o0.uniteWith(o3)
    o3.erase()
    o0.uniteWith(o4)
    o4.erase()
    return o0
