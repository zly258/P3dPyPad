# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.weldentsub.cpnssub.cpns_util import *


@activate(Group="Olet", TooltipShort="CP METRIC Olet", TooltipLong="CP METRIC Olet (Decompiled from varmain/weldentsub/cpnssub/cpns.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(A=ANGLE, TooltipShort="A")
@param(D2=LENGTH, TooltipShort="D2")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPNS(s, D=10.2, L=10.2, W=164.0, A=90.0, D2=1016.0, OF=-1.0, ID='CPNS', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                vC = CPNS_util(D=D, D2=D2, W=W, A=A, OF=OF, L=L)
                R = vC[0] / 2.0
                R2 = vC[1] / 2.0
                o1 = CYLINDER(s, R=R, H=vC[13], O=0.0).rotateY(90).rotateZ(vC[2])
                o6 = CYLINDER(s, R=R, H=vC[6], O=0.0).rotateY(90).rotateZ(vC[2] + 180.0)
                o1.uniteWith(o6)
                o6.erase()
                sMove = 0.0
                _pc = 1379 if not (vC[19]) else 228
            elif _pc == 228:
                _pc = 582 if not (vC[2] == 90.0) else 244
            elif _pc == 244:
                o2 = CYLINDER(s, R1=R, R2=vC[22], H=vC[23], O=0.0).rotateY(90).rotateZ(90).translate((0.0, -vC[8], 0.0))
                o8 = (((CYLINDER(s, R1=R, R2=vC[20] / 2.0, H=R2 + vC[4], O=0.0)).rotateY(90)).rotateZ(90)).translate((0.0, -vC[8], 0.0))
                o2.uniteWith(o8)
                o8.erase()
                o1.uniteWith(o2)
                o2.erase()
                o4 = (((TORUS(s, R1=vC[22] - vC[4], R2=vC[21] - vC[4])).translate((0.0, 0, vC[21]))).rotateY(90)).rotateZ(90)
                o1.subtractFrom(o4)
                o4.erase()
                _pc = 1379
            elif _pc == 582:
                sMove = (vC[20] / 2.0) - vC[7]
                _pc = 733 if not ((sMove if sMove is not None else -1e30) < (0.0 if 0.0 is not None else -1e30)) else 616
            elif _pc == 616:
                sMove = abs(sMove)
                o2 = (((CYLINDER(s, R1=R, R2=vC[20] / 2.0, H=vC[23], O=0.0)).rotateY(90)).rotateZ(90)).translate((0.0, -vC[8], 0.0))
                o2.translate((0.0, 0.0, 0.0))
                _pc = 1246
            elif _pc == 733:
                sMove = 0.0
                o2 = (((CYLINDER(s, R1=R, R2=(vC[20] / 2.0) - vC[7], H=vC[23], O=0.0)).rotateY(90)).rotateZ(90)).translate((0.0, -vC[8], 0.0))
                o10 = (BOX(s, L=vC[23], W=vC[0], H=(vC[20] / 2.0) - vC[7])).translate((((vC[20] / 2.0) - vC[7]) / 2.0, (vC[23] / 2.0) - vC[8], 0.0))
                o2.subtractFrom(o10)
                o10.erase()
                o11 = (((CYLINDER(s, R1=R, R2=(vC[20] / 2.0) + vC[7], H=vC[23], O=0.0)).rotateY(90)).rotateZ(90)).translate((0.0, -vC[8], 0.0))
                o12 = (BOX(s, L=vC[23], W=vC[0], H=(vC[20] / 2.0) + vC[7])).translate(((-((vC[20] / 2.0) + vC[7])) / 2.0, (vC[23] / 2.0) - vC[8], 0.0))
                o11.subtractFrom(o12)
                o12.erase()
                o2.uniteWith(o11)
                o11.erase()
                o2.translate((-vC[7], 0.0, 0.0))
                _pc = 1246
            elif _pc == 1246:
                o4 = CYLINDER(s, R1=R2, R2=vC[23], H=vC[20], O=0.0).rotateY(270).translate((vC[20] / 2.0, -vC[8], 0.0))
                o2.intersectWith(o4)
                o4.erase()
                o1.uniteWith(o2)
                o2.erase()
                _pc = 1379
            elif _pc == 1379:
                _pc = 1562 if not (vC[5]) else 1389
            elif _pc == 1389:
                o4 = CYLINDER(s, R=vC[11], H=vC[13], O=0.0).rotateY(90).rotateZ(vC[2])
                o7 = CYLINDER(s, R=vC[11], H=vC[6], O=0.0).rotateY(90).rotateZ(vC[2] + 180.0)
                o4.uniteWith(o7)
                o7.erase()
                o1.subtractFrom(o4)
                o4.erase()
                _pc = 1562
            elif _pc == 1562:
                o5 = ((CYLINDER(s, R=R2, H=vC[20] + (sMove * 2.0), O=0.0)).rotateY(270)).translate((vC[20] / 2.0, -vC[8], 0))
                o9 = (BOX(s, L=R2, W=vC[1], H=vC[20] + (sMove * 2.0))).translate((-sMove, -(R2 + (R2 / 2.0)), 0))
                o5.uniteWith(o9)
                o9.erase()
                o1.subtractFrom(o5)
                o5.erase()
                o1.translate((vC[7], vC[8], 0.0))
                s.setPoint((0, 0, 0), (0, -1, 0))
                s.setPoint(vC[9], vC[12])
                return None
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
