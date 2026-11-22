# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cnut6_001 import *
from varmain.supportssub.csghsub.csgh007 import *


@activate(Group="Support", TooltipShort="CSGH008", TooltipLong="CSGH008", LengthUnit="mm", Ports=1)
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
@param(HL1=LENGTH, TooltipShort="HL1")
@param(HL2=LENGTH, TooltipShort="HL2")
@param(HL21=LENGTH, TooltipShort="HL21")
@param(HL22=LENGTH, TooltipShort="HL22")
@param(HD21=LENGTH, TooltipShort="HD21")
@param(HD22=LENGTH, TooltipShort="HD22")
@param(HD3=LENGTH, TooltipShort="HD3")
@param(HT4=LENGTH, TooltipShort="HT4")
@param(HL4=LENGTH, TooltipShort="HL4")
@param(HW4=LENGTH, TooltipShort="HW4")
@param(HH4=LENGTH, TooltipShort="HH4")
@param(test=LENGTH, TooltipShort="test")
@param(ID=STRING, TooltipShort="组件标识")
def CSGH008(s, D=116.0, H=500.0, BW=0.0, BH=0.0, BL=50.0, BT=5.0, RD=80.0, RL=150.0, RDI=0.0, RLI=50.0, RTYPE=0, DOUBROLL=0, HL1=0.0, HL2=0.0, HL21=0.0, HL22=0.0, HD21=0.0, HD22=0.0, HD3=0.0, HT4=0.0, HL4=0.0, HW4=0.0, HH4=0.0, test=False, ID='CSGH008', **kw):
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
                _pc = 98 if not ((HL1 if HL1 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 81
            elif _pc == 81:
                HL1 = (H - R1) / 5.0
                _pc = 98
            elif _pc == 98:
                _pc = 127 if not ((HL2 if HL2 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 110
            elif _pc == 110:
                HL2 = (H - R1) / 3.0
                _pc = 127
            elif _pc == 127:
                _pc = 148 if not ((HD21 if HD21 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 139
            elif _pc == 139:
                HD21 = D
                _pc = 148
            elif _pc == 148:
                _pc = 173 if not ((HD3 if HD3 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 160
            elif _pc == 160:
                HD3 = D / 10.0
                _pc = 173
            elif _pc == 173:
                nHT = (round(HD3 * 750)) / 1000
                _pc = 261 if not ((BH if BH is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 205
            elif _pc == 205:
                BH = ((RC + R1) + (nHT * 2.0)) + (BL / 2.0)
                _pc = 261 if not (DOUBROLL) else 237
            elif _pc == 237:
                BH = BH + ((R2 + R3) + R3)
                _pc = 261
            elif _pc == 258:
                _pc = 261
            elif _pc == 261:
                _pc = 282 if not ((BW if BW is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 273
            elif _pc == 273:
                BW = RL
                _pc = 282
            elif _pc == 282:
                _pc = 303 if not ((BW if BW is not None else -1e30) <= (D if D is not None else -1e30)) else 294
            elif _pc == 294:
                BW = D
                _pc = 303
            elif _pc == 303:
                _pc = 324 if not ((HT4 if HT4 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 315
            elif _pc == 315:
                HT4 = BT
                _pc = 324
            elif _pc == 324:
                _pc = 353 if not ((HL4 if HL4 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 336
            elif _pc == 336:
                HL4 = HD3 + (HT4 * 3.0)
                _pc = 353
            elif _pc == 353:
                _pc = 374 if not ((HW4 if HW4 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 365
            elif _pc == 365:
                HW4 = HD3
                _pc = 374
            elif _pc == 374:
                _pc = 395 if not ((HH4 if HH4 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 386
            elif _pc == 386:
                HH4 = HD3
                _pc = 395
            elif _pc == 395:
                _pc = 428 if not ((HL21 if HL21 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 407
            elif _pc == 407:
                HL21 = (HD21 / 2.0) - (HD3 * 2.0)
                _pc = 428
            elif _pc == 428:
                _pc = 453 if not ((HL22 if HL22 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 440
            elif _pc == 440:
                HL22 = HL2 / 10.0
                _pc = 453
            elif _pc == 453:
                _pc = 478 if not ((HD22 if HD22 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 465
            elif _pc == 465:
                HD22 = HD21 * 1.2
                _pc = 478
            elif _pc == 478:
                tP = BH - RC
                cR2 = HD21 / 2.0
                cR3 = HD22 / 2.0
                o0 = ((CONE(s, R1=HD3 * 2.0, R2=cR2, H=HL21, E=0.0)).rotateX(-90.0)).translate((0.0, tP + HL1, 0.0))
                o1 = ((CYLINDER(s, R=cR2, H=(HL2 - HL21) - HL22, O=0.0)).rotateX(-90.0)).translate((0.0, (tP + HL1) + HL21, 0.0))
                o2 = CYLINDER(s, R=cR3, H=HL22, O=0.0).rotateX(90.0).translate((0.0, (tP + HL1) + HL2, 0.0))
                o0.uniteWith(o1)
                o1.erase()
                o0.uniteWith(o2)
                o2.erase()
                o0.rotateX(90.0).rotateZ(90.0)
                o3 = CSGH007(s, D=D, H=H, BW=BW, BH=BH, BL=BL, BT=BT, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE, DOUBROLL=DOUBROLL, HD3=HD3, HT4=HT4, HL4=HL4, HW4=HW4, HH4=HH4, test=test)
                o0.uniteWith(o3)
                o3.erase()
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
