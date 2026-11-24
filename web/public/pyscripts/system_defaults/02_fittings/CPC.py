# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Endcap", TooltipShort="CP METRIC Cap", TooltipLong="CP METRIC Cap (Decompiled from varmain/capsub/cpc.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(DISP=INT, TooltipShort="DISP")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPC(s, D=1016.0, L=749.0, DISP=0, OF=-1.0, ID='CPC', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                OF = getThickness(D=D, OF=OF, Ever=1)
                _tmp = getThickness(D=D, OF=OF, Ever=1, mustCalc=True)
                vTH = _tmp
                sF = _tmp
                _pc = 88 if (DISP == 0) else 76
            elif _pc == 76:
                _pc = 248 if not (DISP == 3) else 88
            elif _pc == 88:
                o2 = (TORISPHERICHEAD(s, R=D / 2.0)).rotateY(90.0)
                vT = o2.parameters()
                vTH = float(vT['H'])
                _pc = 219 if not (((L - vTH) if (L - vTH) is not None else -1e30) < (0.0 if 0.0 is not None else -1e30)) else 163
            elif _pc == 163:
                o2.erase()
                o2 = (TORISPHERICHEADH(s, R=D / 2.0, H=L)).rotateY(90.0)
                vTH = L
                _pc = 219
            elif _pc == 219:
                o2.translate((L - vTH, 0.0, 0.0))
                _pc = 407
            elif _pc == 248:
                _pc = 342 if not (DISP == 1) else 260
            elif _pc == 260:
                vTH = vTH + vTH
                o2 = ((CYLINDER(s, R=(D + vTH) / 2.0, H=vTH, O=0.0)).rotateY(90)).translate((L - vTH, 0.0, 0.0))
                _pc = 407
            elif _pc == 342:
                o2 = ((CYLINDER(s, R=D / 2.0, H=vTH, O=0.0)).rotateY(90)).translate((L - vTH, 0.0, 0.0))
                _pc = 407
            elif _pc == 407:
                _pc = 765 if not (DISP == 3) else 419
            elif _pc == 419:
                sFx = sF / 4.0
                x1 = (BOX(s, L=vTH, W=D / 2.0, H=L)).translate((L / 2.0, 0.0, D / 4.0))
                x2 = ((BOX(s, L=vTH, W=D / 2.0, H=L)).translate((L / 2.0, 0.0, D / 4.0))).rotateX(120.0)
                x1.uniteWith(x2)
                x2.erase()
                x3 = ((BOX(s, L=vTH, W=D / 2.0, H=L)).translate((L / 2.0, 0.0, D / 4.0))).rotateX(-120.0)
                x1.uniteWith(x3)
                x3.erase()
                x4 = (CYLINDER(s, R=D / 2.0, H=L, O=0.0)).rotateY(90.0)
                x1.intersectWith(x4)
                x4.erase()
                o2.uniteWith(x1)
                x1.erase()
                _pc = 765
            elif _pc == 765:
                _pc = 854 if not (((L - vTH) if (L - vTH) is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 781
            elif _pc == 781:
                o1 = (CYLINDER(s, R=D / 2.0, H=L - vTH, O=0.0)).rotateY(90.0)
                o1.uniteWith(o2)
                o2.erase()
                _pc = 860
            elif _pc == 854:
                o1 = o2
                _pc = 860
            elif _pc == 860:
                _pc = 1145 if (OF == 0.0) else 872
            elif _pc == 872:
                _pc = 899 if not (OF == -1) else 884
            elif _pc == 884:
                O = CON_OF_DIV(D)
                _pc = 913
            elif _pc == 899:
                O = D - (OF * 2.0)
                _pc = 913
            elif _pc == 913:
                L2 = (L - (D - O)) + OF
                _pc = 955 if (DISP == 0) else 943
            elif _pc == 943:
                _pc = 1015 if not (DISP == 3) else 955
            elif _pc == 955:
                o4 = (TORISPHERICHEAD(s, R=O / 2.0)).rotateY(90.0)
                o4.translate((L - vTH, 0.0, 0.0))
                _pc = 1021
            elif _pc == 1015:
                o4 = None
                _pc = 1021
            elif _pc == 1021:
                _pc = 1145 if not (((L - vTH) if (L - vTH) is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 1037
            elif _pc == 1037:
                o3 = (CYLINDER(s, R=O / 2.0, H=L - vTH, O=0.0)).rotateY(90.0)
                _pc = 1116 if not (o4) else 1090
            elif _pc == 1090:
                o3.uniteWith(o4)
                o4.erase()
                _pc = 1116
            elif _pc == 1116:
                o1.subtractFrom(o3)
                o3.erase()
                _pc = 1145
            elif _pc == 1142:
                _pc = 1145
            elif _pc == 1145:
                s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
                return None
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
