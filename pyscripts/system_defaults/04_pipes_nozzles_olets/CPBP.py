# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.arcsub.cpb_util import *


@activate(Group="Elbow", TooltipShort="Nozzle, vent, ASME B16.9", TooltipLong="Nozzle, vent, ASME B16.9 (Decompiled from varmain/arcsub/cpbpsub/cpbp.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(D2=LENGTH, TooltipShort="D2")
@param(R=LENGTH, TooltipShort="R")
@param(A=ANGLE, TooltipShort="A")
@param(OF=LENGTH, TooltipShort="OF")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(ID=STRING, TooltipShort="组件标识")
def CPBP(s, D=0.84, D2=0.0, R=1.5, A=180.0, OF=-1.0, L1=200.0, L2=300.0, ID='CPBP', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                noLeft = 0
                noRight = 0
                _pc = 33 if not ((D2 if D2 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 24
            elif _pc == 24:
                D2 = D
                _pc = 33
            elif _pc == 33:
                _pc = 54 if not (L2 == 0.0) else 45
            elif _pc == 45:
                L2 = L1
                _pc = 54
            elif _pc == 54:
                _pc = 81 if (L1 == -2) else 66
            elif _pc == 66:
                _pc = 96 if not (areEqual(R, L1)) else 81
            elif _pc == 81:
                noLeft = 1
                L1 = None
                _pc = 96
            elif _pc == 96:
                _pc = 114 if not (L2) else 102
            elif _pc == 102:
                _pc = 129 if (L2 == -2) else 114
            elif _pc == 114:
                _pc = 144 if not (areEqual(R, L2)) else 129
            elif _pc == 129:
                noRight = 1
                L2 = None
                _pc = 144
            elif _pc == 144:
                _pc = 235 if not ((A if A is not None else -1e30) < (180.0 if 180.0 is not None else -1e30)) else 156
            elif _pc == 156:
                sLen = ((R * (sqrt(2.0 * (1 - cos(asRadiants(A)))))) * (sin(asRadiants(A / 2.0)))) / (sin(asRadiants(180.0 - A)))
                _pc = 241
            elif _pc == 235:
                sLen = R
                _pc = 241
            elif _pc == 241:
                _pc = 280 if not (L1) else 247
            elif _pc == 247:
                _pc = 280 if not ((L1 if L1 is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 259
            elif _pc == 259:
                _pc = 280 if not ((sLen if sLen is not None else -1e30) > (L1 if L1 is not None else -1e30)) else 271
            elif _pc == 271:
                R = L1
                _pc = 280
            elif _pc == 280:
                _pc = 319 if not (L2) else 286
            elif _pc == 286:
                _pc = 319 if not ((L2 if L2 is not None else -1e30) > (0.0 if 0.0 is not None else -1e30)) else 298
            elif _pc == 298:
                _pc = 319 if not ((sLen if sLen is not None else -1e30) > (L2 if L2 is not None else -1e30)) else 310
            elif _pc == 310:
                R = L2
                _pc = 319
            elif _pc == 319:
                _pc = 352 if not ((R if R is not None else -1e30) <= ((D / 2.0) if (D / 2.0) is not None else -1e30)) else 335
            elif _pc == 335:
                R = (D / 2.0) + 0.0001
                _pc = 352
            elif _pc == 352:
                o0 = ARC3D2(s, D=D / 2.0, D2=D2 / 2.0, R=R, A=A)
                Pts = CPB_CalcPts(o0, A, L1, L2, 0.0, 0.0)
                OF = getThickness(D=D, OF=OF)
                arc3d2TMP = ((CYLINDER(s, R=(D * 0.01) / 2.0, H=R * 0.01)).rotateY(-90)).translate(Pts[8])
                arc3d2TMP.uniteWith(o0)
                o0.erase()
                o0 = arc3d2TMP
                _pc = 655 if (OF == 0.0) else 543
            elif _pc == 543:
                O1 = getInsideDiameter(D=D, OF=OF) / 2.0
                O2 = getInsideDiameter(D=D2, OF=OF) / 2.0
                o1 = ARC3D2(s, D=O1, D2=O2, R=R, A=A)
                o0.subtractFrom(o1)
                o1.erase()
                _pc = 667
            elif _pc == 655:
                O1 = 0.0
                O2 = 0.0
                _pc = 667
            elif _pc == 667:
                _pc = 804 if not (noLeft == 0) else 679
            elif _pc == 679:
                _pc = 804 if not (not areEqual(0.0, Pts[0])) else 699
            elif _pc == 699:
                oL1 = (((CYLINDER(s, R=D / 2.0, H=Pts[0], O=O1)).rotateY(90.0)).rotateZ(asDegrees(Pts[2]))).translate(Pts[8])
                o0.uniteWith(oL1)
                oL1.erase()
                _pc = 804
            elif _pc == 804:
                _pc = 941 if not (noRight == 0) else 816
            elif _pc == 816:
                _pc = 941 if not (not areEqual(0.0, Pts[1])) else 836
            elif _pc == 836:
                oL2 = (((CYLINDER(s, R=D2 / 2.0, H=Pts[1], O=O2)).rotateY(90.0)).rotateZ(asDegrees(Pts[3]))).translate(Pts[9])
                o0.uniteWith(oL2)
                oL2.erase()
                _pc = 941
            elif _pc == 941:
                s.setPoint(Pts[4], Pts[6], 0.0)
                s.setPoint(Pts[5], Pts[7], 0.0)
                return None
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
