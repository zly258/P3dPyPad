# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cbolt_001 import *
from varmain.divsub.cnut6_001 import *
from varmain.supportssub.csgrsub.csgr000 import *


@activate(Group="Support", TooltipShort="CSGH007", TooltipLong="CSGH007", LengthUnit="mm", Ports=1)
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
@param(HT4=LENGTH, TooltipShort="HT4")
@param(HL4=LENGTH, TooltipShort="HL4")
@param(HW4=LENGTH, TooltipShort="HW4")
@param(HH4=LENGTH, TooltipShort="HH4")
@param(test=LENGTH, TooltipShort="test")
@param(ID=STRING, TooltipShort="组件标识")
def CSGH007(s, D=116.0, H=500.0, BW=0.0, BH=0.0, BL=50.0, BT=5.0, RD=80.0, RL=150.0, RDI=0.0, RLI=50.0, RTYPE=0, DOUBROLL=0, HD3=0.0, HT4=0.0, HL4=0.0, HW4=0.0, HH4=0.0, test=False, ID='CSGH007', **kw):
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
                _pc = 245 if not ((HT4 if HT4 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 236
            elif _pc == 236:
                HT4 = BT
                _pc = 245
            elif _pc == 245:
                _pc = 274 if not ((HL4 if HL4 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 257
            elif _pc == 257:
                HL4 = HD3 + (HT4 * 3.0)
                _pc = 274
            elif _pc == 274:
                _pc = 295 if not ((HW4 if HW4 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 286
            elif _pc == 286:
                HW4 = HD3
                _pc = 295
            elif _pc == 295:
                _pc = 316 if not ((HH4 if HH4 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 307
            elif _pc == 307:
                HH4 = HD3
                _pc = 316
            elif _pc == 316:
                tP = BH - RC
                o0 = ((CYLINDER(s, R=HD3 / 2.0, H=(H - BH) + RC, O=0.0)).rotateX(-90.0)).translate((0.0, tP, 0.0))
                o1 = ((CBOLT_001(s, D=HD3, L=nHT * 2.0)).rotateZ(90.0)).translate((0.0, (tP - BT) - (nHT * 1.5), 0.0))
                o2 = CNUT6_001(s, D=HD3, W=0.0, H=nHT).rotateZ(90.0).translate((0.0, tP, 0.0))
                o3 = CNUT6_001(s, D=HD3, W=0.0, H=nHT).rotateZ(-90.0).translate((0.0, tP - BT, 0.0))
                o0.uniteWith(o1)
                o1.erase()
                o0.uniteWith(o2)
                o2.erase()
                o0.uniteWith(o3)
                o3.erase()
                xL1 = HL4 + (HT4 * 2.0)
                xH1 = (H - ((HH4 - HT4) / 2.0)) - HT4
                o4 = CYLINDER(s, R=HT4, H=xL1, O=0.0).rotateY(-90.0).translate((xL1 / 2.0, xH1, 0.0))
                o5 = BOX(s, L=HH4, W=HW4, H=HT4).translate(((HL4 / 2.0) - (HT4 / 2.0), H - (HH4 / 2.0), 0.0))
                o6 = BOX(s, L=HH4, W=HW4, H=HT4).translate((-((HL4 / 2.0) - (HT4 / 2.0)), H - (HH4 / 2.0), 0.0))
                o7 = BOX(s, L=HT4, W=HW4, H=HL4).translate((0.0, H - (HT4 / 2.0), 0.0))
                o0.uniteWith(o4)
                o4.erase()
                o0.uniteWith(o5)
                o5.erase()
                o0.uniteWith(o6)
                o6.erase()
                o0.uniteWith(o7)
                o7.erase()
                o0.rotateX(90.0).rotateZ(90.0)
                o8 = CSGH007sub(s, D=D, BW=BW, BH=BH, BL=BL, BT=BT, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RTYPE=RTYPE, DOUBROLL=DOUBROLL, HD3=HD3, test=test).translate((0.0, 0.0, tP))
                o0.uniteWith(o8)
                o8.erase()
                s.setPoint((0, 0, 0), (-1, 0, 0))
                s.setLinearDimension('H', (0, 0, 0), (0, 0, H))
                return o0
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise


@activate(Group="Support", TooltipShort="CSGH007", TooltipLong="CSGH007", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
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
@param(test=LENGTH, TooltipShort="test")
@param(ID=STRING, TooltipShort="组件标识")
def CSGH007sub(s, D=116.0, BW=0.0, BH=0.0, BL=50.0, BT=5.0, RD=80.0, RL=150.0, RDI=0.0, RLI=50.0, RTYPE=0, DOUBROLL=0, HD3=10.0, test=False, ID='CSGH007sub', **kw):
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
                nHT = round(HD3 * 0.75)
                _pc = 153 if not ((BH if BH is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 97
            elif _pc == 97:
                BH = ((RC + R1) + (nHT * 2.0)) + (BL / 2.0)
                _pc = 153 if not (DOUBROLL) else 129
            elif _pc == 129:
                BH = BH + ((R2 + R3) + R3)
                _pc = 153
            elif _pc == 150:
                _pc = 153
            elif _pc == 153:
                _pc = 174 if not ((BW if BW is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 165
            elif _pc == 165:
                BW = RL
                _pc = 174
            elif _pc == 174:
                _pc = 195 if not ((BW if BW is not None else -1e30) <= (D if D is not None else -1e30)) else 186
            elif _pc == 186:
                BW = D
                _pc = 195
            elif _pc == 195:
                w1 = round((HD3 * 2.0) + 0.5)
                _pc = 236 if not ((w1 if w1 is not None else -1e30) < (BL if BL is not None else -1e30)) else 227
            elif _pc == 227:
                w1 = BL
                _pc = 236
            elif _pc == 236:
                o0 = BOX(s, L=w1, W=BT, H=BL).translate((0.0, 0.0, -(BT / 2.0)))
                w2 = (BW - w1) / 2.0
                w23 = w2 + BT
                w22 = w23 * tan(asRadiants(22.5))
                wExt = BT * (tan((mcPi - asRadiants(112.5)) / 2.0))
                w3 = sqrt(pow(w23, 2.0) + pow(w22, 2.0))
                o1 = ((BOX(s, L=w3, W=BT, H=BL).translate((0.0, w3 / 2.0, -(BT / 2.0)))).rotateX(-22.5)).translate((0.0, w1 / 2.0, 0.0))
                o2 = ((BOX(s, L=w3, W=BT, H=BL).translate((0.0, -(w3 / 2.0), -(BT / 2.0)))).rotateX(22.5)).translate((0.0, -(w1 / 2.0), 0.0))
                w4 = (BH - w22) + (BL / 2.0)
                o3 = BOX(s, L=BT, W=w4, H=BL).translate((0.0, (BT / 2.0) + (BW / 2.0), (-(w4 / 2.0)) - w22))
                o4 = BOX(s, L=BT, W=w4, H=BL).translate((0.0, (-(BT / 2.0)) - (BW / 2.0), (-(w4 / 2.0)) - w22))
                o0.uniteWith(o1)
                o1.erase()
                o0.uniteWith(o2)
                o2.erase()
                o0.uniteWith(o3)
                o3.erase()
                o0.uniteWith(o4)
                o4.erase()
                rD = RDI * 0.5
                nH = round(rD * 0.75)
                rW = round((rD * 1.5) + 0.5)
                bPZ = [RC - BH]
                _pc = 919 if not (DOUBROLL) else 891
            elif _pc == 891:
                bPZ.append((RC - BH) + (RC * 2.0))
                _pc = 919
            elif _pc == 919:
                _pc = 922
            elif _pc == 922:
                _stk.append(iter(bPZ))
                _pc = 926
            elif _pc == 926:
                _it = _stk.pop()
                try:
                    _nxt = next(_it)
                    _stk.append(_it)
                    _stk.append(_nxt)
                    _pc = 929
                except StopIteration:
                    _pc = 1367
            elif _pc == 929:
                pZ = _stk.pop()
                _pc = 957 if not (pZ == bPZ[0]) else 948
            elif _pc == 948:
                xtest = test
                _pc = 963
            elif _pc == 957:
                xtest = False
                _pc = 963
            elif _pc == 963:
                o1 = CSGR000(s, D=D, RD=RD, RL=RL, RDI=RDI, RLI=RLI, RLIU=1, RTYPE=RTYPE, W=0.0, WD=0.0, test=xtest).translate((0.0, 0.0, pZ))
                bL = (BW + (BT * 2.0)) + (nH * 3.0)
                o2 = CBOLT_001(s, D=rD, L=bL).rotateZ(90.0).translate((0.0, -bL / 2.0, pZ - RC))
                nL = (BW / 2.0) + BT
                o3 = CNUT6_001(s, D=rD, W=rW, H=nH).rotateZ(90.0).translate((0.0, nL, pZ - RC))
                o4 = CNUT6_001(s, D=rD, W=rW, H=nH).rotateZ(-90.0).translate((0.0, -nL, pZ - RC))
                o0.uniteWith(o1)
                o1.erase()
                o0.uniteWith(o2)
                o2.erase()
                o0.uniteWith(o3)
                o3.erase()
                o0.uniteWith(o4)
                o4.erase()
                _pc = 926
            elif _pc == 1367:
                _pc = 1368
            elif _pc == 1368:
                s.setPoint((0, 0, 0), (-1, 0, 0))
                s.setPoint((0, 0, 0), (1, 0, 0))
                return o0
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
