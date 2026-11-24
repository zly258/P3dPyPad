# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cnut6_001 import *
from varmain.supportssub.csghsub.csgh007 import *


@activate(Group="Support", TooltipShort="CSGH009", TooltipLong="CSGH009", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(H=LENGTH, TooltipShort="H")
@param(BW=LENGTH, TooltipShort="BW")
@param(BH=LENGTH, TooltipShort="BH")
@param(BL=LENGTH, TooltipShort="BL")
@param(BT=LENGTH, TooltipShort="BT")
@param(RD=LENGTH, TooltipShort="RD")
@param(RL=LENGTH, TooltipShort="RL")
@param(RDI=LENGTH, TooltipShort="RDI")
@param(RLI=LENGTH, TooltipShort="RLI")
@param(RTYPE=INT, TooltipShort="RTYPE")
@param(DOUBROLL=INT, TooltipShort="DOUBROLL")
@param(HD3=LENGTH, TooltipShort="HD3")
@param(HS=LENGTH, TooltipShort="HS")
@param(HO=LENGTH, TooltipShort="HO")
@param(test=LENGTH, TooltipShort="test")
@param(ID=STRING, TooltipShort="组件标识")
def CSGH009(s, D=116.0, H=500.0, BW=0.0, BH=0.0, BL=50.0, BT=5.0, RD=80.0, RL=150.0, RDI=0.0, RLI=50.0, RTYPE=0, DOUBROLL=0, HD3=0.0, HS=10.0, HO=0.0, test=False, ID='CSGH009', **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                _seq = list(CSGR000_util(D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE))
                R1 = _seq[0]
                R2 = _seq[1]
                R3 = _seq[2]
                RC = _seq[3]
                RD = _seq[4]
                RDI = _seq[5]
                RLI = _seq[6]
                LM = _seq[7]
                _pc = 94 if not ((HD3 if HD3 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 81
            elif _pc == 81:
                HD3 = D / 10.0
                _pc = 94
            elif _pc == 94:
                nHT = (round(HD3 * 750)) / 1000
                _pc = 182 if not ((BH if BH is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 126
            elif _pc == 126:
                BH = ((RC + R1) + (nHT * 2.0)) + (BL / 2.0)
                _pc = 182 if not (DOUBROLL) else 158
            elif _pc == 158:
                BH = BH + ((R2 + R3) + R3)
                _pc = 182
            elif _pc == 179:
                _pc = 182
            elif _pc == 182:
                _pc = 203 if not ((BW if BW is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 194
            elif _pc == 194:
                BW = RL
                _pc = 203
            elif _pc == 203:
                _pc = 224 if not ((BW if BW is not None else -1e30) <= (D if D is not None else -1e30)) else 215
            elif _pc == 215:
                BW = D
                _pc = 224
            elif _pc == 224:
                tP = BH - RC
                o0 = ((CYLINDER(s, R=HD3 / 2.0, H=(H - BH) + RC, O=0.0)).rotateX(-90.0)).translate((0.0, tP, 0.0))
                o1 = ((CBOLT_001(s, D=HD3, L=nHT * 2.0)).rotateZ(90.0)).translate((0.0, (tP - BT) - (nHT * 1.5), 0.0))
                o2 = CNUT6_001(s, D=HD3, W=0.0, H=nHT).rotateZ(90.0).translate((0.0, tP, 0.0))
                o3 = CNUT6_001(s, D=HD3, W=0.0, H=nHT).rotateZ(-90.0).translate((0.0, tP - BT, 0.0))
                o4 = ((CBOLT_001(s, D=HD3, L=(nHT * 2.0) + HS)).rotateZ(90.0)).translate((0.0, H - (nHT * 0.5), 0.0))
                o5 = CNUT6_001(s, D=HD3, W=0.0, H=nHT).rotateZ(90.0).translate((0.0, H + HS, 0.0))
                o6 = CNUT6_001(s, D=HD3, W=0.0, H=nHT).rotateZ(-90.0).translate((0.0, H, 0.0))
                o0.uniteWith(o1)
                o1.erase()
                o0.uniteWith(o2)
                o2.erase()
                o0.uniteWith(o3)
                o3.erase()
                o0.uniteWith(o4)
                o4.erase()
                o0.uniteWith(o5)
                o5.erase()
                o0.uniteWith(o6)
                o6.erase()
                o0.rotateX(90.0).rotateZ(90.0)
                o7 = CSGH007sub(s, D=D, BW=BW, BH=BH, BL=BL, BT=BT, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE, DOUBROLL=DOUBROLL, HD3=HD3, test=test).translate((0.0, 0.0, tP))
                o0.uniteWith(o7)
                o7.erase()
                s.setPoint((0, 0, 0), (-1, 0, 0))
                s.setLinearDimension('H', (0, 0, 0), (0, 0, H))
                return None
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
