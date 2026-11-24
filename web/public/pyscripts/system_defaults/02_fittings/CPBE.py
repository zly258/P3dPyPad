# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.arcsub.cpb_util import *


@activate(Group="Elbow", TooltipShort="Built-in CPBE", TooltipLong="Built-in CPBE (Decompiled from varmain/arcsub/cpbesub/cpbe.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(D2=LENGTH, TooltipShort="D2")
@param(L1=LENGTH, TooltipShort="L1")
@param(L11=LENGTH, TooltipShort="L11")
@param(L2=LENGTH, TooltipShort="L2")
@param(L12=LENGTH, TooltipShort="L12")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPBE(s, D=114.3, D2=0.0, L1=180.0, L11=0.0, L2=0.0, L12=0.0, OF=-1.0, ID='CPBE', **kw):
    vC = CPBE_calc(s, D=D, D2=D2, L1=L1, L11=L11, L2=L2, L12=L12, OF=OF)
    o1 = CPBE_sub(s, D=vC[0], D2=vC[1], L1=vC[2], L11=vC[3], L2=vC[4], L12=vC[5])
    cR = (vC[0] / 2.0) + vC[13]
    cH = vC[0] + (vC[13] * 2.0)
    oC1 = CYLINDER(s, R=cR, H=cH, O=0.0).translate((0.0, 0.0, -(cH / 2.0)))
    oC2 = (CORNERBOX(s, L=vC[7], W=(vC[8] + vC[13]) + (vC[0] / 2.0), H=cH)).translate((0.0, (-(vC[0] / 2.0)) - vC[13], -cH / 2.0))
    oC3 = (CORNERBOX(s, L=(vC[7] + vC[13]) + (vC[0] / 2.0), W=vC[8], H=cH)).translate(((-(vC[0] / 2.0)) - vC[13], 0.0, -cH / 2.0))
    if areEqual(vC[7], vC[8]):
        sR = (vC[7] - (vC[0] / 2.0)) - vC[13]
        oC4 = CYLINDER(s, R=sR, H=cH, O=0.0).translate((vC[7], vC[8], -(cH / 2.0)))
    else:
        if vC[7] > vC[8]:
            sR = (vC[8] - (vC[0] / 2.0)) - vC[13]
            oC4 = CYLINDER(s, R=sR, H=cH, O=0.0).translate((vC[8], vC[8], -(cH / 2.0)))
            oC5 = (CORNERBOX(s, L=(vC[7] - (vC[0] / 2.0)) - sR, W=sR, H=cH)).translate((vC[8], vC[8] - sR, -cH / 2.0))
        else:
            sR = (vC[7] - (vC[0] / 2.0)) - vC[13]
            oC4 = CYLINDER(s, R=sR, H=cH, O=0.0).translate((vC[7], vC[7], -(cH / 2.0)))
            oC5 = (CORNERBOX(s, L=sR, W=(vC[8] - (vC[0] / 2.0)) - sR, H=cH)).translate((vC[7] - sR, vC[7], -cH / 2.0))
        oC4.uniteWith(oC5)
        oC5.erase()
    oC1.uniteWith(oC2)
    oC2.erase()
    oC1.uniteWith(oC3)
    oC3.erase()
    oC1.subtractFrom(oC4)
    oC4.erase()
    o1.uniteWith(oC1)
    oC1.erase()
    if vC[12] > 0.0:
        s1 = CPBE_sub(s, D=vC[14], D2=vC[15], L1=vC[2], L11=vC[3], L2=vC[4], L12=vC[5])
        o1.subtractFrom(s1)
        s1.erase()
    s.setPoint(vC[34], vC[35], vC[23])
    s.setPoint(vC[36], vC[37], vC[32])


def CPBE_sub(s, D=114.3, D2=0.0, L1=180.0, L11=0.0, L2=0.0, L12=0.0, **kw):
    vC = CPBE_calc(s, D=D, D2=D2, L1=L1, L11=L11, L2=L2, L12=L12)
    if areEqual(vC[0], vC[1]):
        oL1 = (CYLINDER(s, R=vC[0] / 2.0, H=vC[2], O=0.0)).rotateY(90.0)
        oL2 = ((CYLINDER(s, R=vC[1] / 2.0, H=vC[4], O=0.0)).rotateY(90.0)).rotateZ(vC[6])
    else:
        oL1 = ((CYLINDER(s, R=vC[0] / 2.0, H=vC[3], O=0.0)).rotateY(90.0)).translate((vC[7], 0.0, 0.0))
        oL2 = (((CYLINDER(s, R=vC[1] / 2.0, H=vC[5], O=0.0)).rotateY(90.0)).rotateZ(vC[6])).translate((0.0, vC[8], 0.0))
        oL3 = ((CONE(s, R1=vC[0] / 2.0, R2=vC[11], H=vC[7], O=0.0)).rotateY(-90.0)).translate((vC[7], 0.0, 0.0))
        oL1.uniteWith(oL3)
        oL3.erase()
        oL4 = ((CONE(s, R1=vC[11], R2=vC[1] / 2.0, H=vC[8], O=0.0)).rotateY(90.0)).rotateZ(vC[6])
        oL2.uniteWith(oL4)
        oL4.erase()
    oL5 = SPHERE(s, R=vC[11])
    oL1.uniteWith(oL5)
    oL5.erase()
    oL1.uniteWith(oL2)
    oL2.erase()
    return oL1


def CPBE_calc(s, D=114.3, D2=0.0, L1=180.0, L11=0.0, L2=0.0, L12=0.0, OF=0.0, L31=None, B31=None, D31=None, D41=None, W1=None, O31=None, L32=None, B32=None, D32=None, D42=None, W2=None, O32=None, L21=None, I1=None, L22=None, I2=None, **kw):
    _pc = 0
    _stk = []
    _exc_stk = []
    while _pc >= 0:
        try:
            if _pc == 0:
                retVal = []
                A = 90.0
                _pc = 33 if not ((D2 if D2 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 24
            elif _pc == 24:
                D2 = D
                _pc = 33
            elif _pc == 33:
                _pc = 58 if not ((L11 if L11 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 45
            elif _pc == 45:
                L11 = L1 - D
                _pc = 58
            elif _pc == 58:
                _pc = 79 if not ((L2 if L2 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 70
            elif _pc == 70:
                L2 = L1
                _pc = 79
            elif _pc == 79:
                _pc = 100 if not ((L12 if L12 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 91
            elif _pc == 91:
                L12 = L11
                _pc = 100
            elif _pc == 100:
                sL1 = L1 - L11
                sL2 = L2 - L12
                _pc = 148 if not (areEqual(D, D2)) else 135
            elif _pc == 135:
                cR = D / 2.0
                _pc = 162
            elif _pc == 148:
                cR = (D + D2) / 4.0
                _pc = 162
            elif _pc == 162:
                OF = getThickness(D=D, OF=OF)
                sF = getThickness(D=D, OF=OF, Ever=1, mustCalc=True)
                oD = D - (OF * 2.0)
                oD2 = D2 - (OF * 2.0)
                wA1 = 0.0
                xL31 = 0.0
                yL31 = 0.0
                noLeft = False
                _pc = 480 if not (L31 != None) else 280
            elif _pc == 280:
                _pc = 480 if not (B31 != None) else 292
            elif _pc == 292:
                _pc = 480 if not (D31 != None) else 304
            elif _pc == 304:
                _pc = 480 if not (D41 != None) else 316
            elif _pc == 316:
                _pc = 480 if not (W1 != None) else 328
            elif _pc == 328:
                _pc = 480 if not (O31 != None) else 340
            elif _pc == 340:
                _pc = 364 if (L31 == -2) else 352
            elif _pc == 352:
                _pc = 379 if not (B31 == -2) else 364
            elif _pc == 364:
                noLeft = True
                L31 = 0.0
                _pc = 379
            elif _pc == 379:
                _pc = 408 if not (W1 == -1) else 391
            elif _pc == 391:
                W1 = D + (OF * 2.0)
                _pc = 429
            elif _pc == 408:
                _pc = 429 if not ((W1 if W1 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 420
            elif _pc == 420:
                W1 = D31
                _pc = 429
            elif _pc == 429:
                _pc = 456 if not (L31) else 435
            elif _pc == 435:
                _pc = 456 if not (O31 == 0) else 447
            elif _pc == 447:
                xL31 = L31
                _pc = 456
            elif _pc == 456:
                _pc = 842 if not ((W1 if W1 is not None else -1e30) < (D31 if D31 is not None else -1e30)) else 468
            elif _pc == 468:
                wA1 = 90.0
                _pc = 842
            elif _pc == 477:
                _pc = 842
            elif _pc == 480:
                _pc = 635 if not (L31 != None) else 492
            elif _pc == 492:
                _pc = 635 if not (D31 != None) else 504
            elif _pc == 504:
                _pc = 635 if not (O31 != None) else 516
            elif _pc == 516:
                _pc = 540 if (L31 == 0.0) else 528
            elif _pc == 528:
                _pc = 549 if not (L31 == -1) else 540
            elif _pc == 540:
                L31 = sF
                _pc = 549
            elif _pc == 549:
                _pc = 576 if not (L31 == -2) else 561
            elif _pc == 561:
                noLeft = True
                L31 = None
                _pc = 576
            elif _pc == 576:
                _pc = 605 if not ((D31 if D31 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 588
            elif _pc == 588:
                D31 = D + (sF * 2.0)
                _pc = 605
            elif _pc == 605:
                _pc = 842 if not (L31) else 611
            elif _pc == 611:
                _pc = 842 if not (O31 == 0) else 623
            elif _pc == 623:
                xL31 = L31
                _pc = 842
            elif _pc == 632:
                _pc = 842
            elif _pc == 635:
                _pc = 712 if not (L21 != None) else 647
            elif _pc == 647:
                _pc = 712 if not (I1 != None) else 659
            elif _pc == 659:
                _pc = 692 if not (L21 == -2) else 671
            elif _pc == 671:
                noLeft = True
                L21 = None
                I1 = 0.0
                _pc = 842
            elif _pc == 692:
                xL31 = -L21
                yL31 = L21 - I1
                _pc = 842
            elif _pc == 712:
                _pc = 767 if not (L21 != None) else 724
            elif _pc == 724:
                _pc = 751 if not (L21 == -2) else 736
            elif _pc == 736:
                noLeft = True
                L21 = None
                _pc = 842
            elif _pc == 751:
                xL31 = -L21
                yL31 = L21
                _pc = 842
            elif _pc == 767:
                _pc = 842 if not (I1 != None) else 779
            elif _pc == 779:
                _pc = 806 if not (I1 == -2) else 791
            elif _pc == 791:
                noLeft = True
                I1 = None
                _pc = 842
            elif _pc == 806:
                xL31 = 0.0
                yL31 = -I1
                oD = D
                D = D + (OF * 2.0)
                _pc = 842
            elif _pc == 842:
                wA2 = 0.0
                xL32 = 0.0
                yL32 = 0.0
                noRight = False
                _pc = 1238 if not (L32 != None) else 878
            elif _pc == 878:
                _pc = 1238 if not (B32 != None) else 890
            elif _pc == 890:
                _pc = 1238 if not (D32 != None) else 902
            elif _pc == 902:
                _pc = 1238 if not (D42 != None) else 914
            elif _pc == 914:
                _pc = 1238 if not (W2 != None) else 926
            elif _pc == 926:
                _pc = 1238 if not (O32 != None) else 938
            elif _pc == 938:
                _pc = 971 if not (L32 == 0.0) else 950
            elif _pc == 950:
                _pc = 971 if not (L31 != None) else 962
            elif _pc == 962:
                L32 = L31
                _pc = 971
            elif _pc == 971:
                _pc = 1020 if not ((B32 if B32 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 983
            elif _pc == 983:
                _pc = 1020 if not (not areEqual(B32, -2.0)) else 999
            elif _pc == 999:
                _pc = 1020 if not (B31 != None) else 1011
            elif _pc == 1011:
                B32 = B31
                _pc = 1020
            elif _pc == 1020:
                _pc = 1038 if not (L32) else 1026
            elif _pc == 1026:
                _pc = 1056 if (L32 == -2) else 1038
            elif _pc == 1038:
                _pc = 1071 if not (B32) else 1044
            elif _pc == 1044:
                _pc = 1071 if not (B32 == -2) else 1056
            elif _pc == 1056:
                noRight = True
                L32 = 0.0
                _pc = 1071
            elif _pc == 1071:
                _pc = 1104 if not ((D32 if D32 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 1083
            elif _pc == 1083:
                _pc = 1104 if not (D31 != None) else 1095
            elif _pc == 1095:
                D32 = D31
                _pc = 1104
            elif _pc == 1104:
                _pc = 1137 if not ((D42 if D42 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 1116
            elif _pc == 1116:
                _pc = 1137 if not (D41 != None) else 1128
            elif _pc == 1128:
                D42 = D41
                _pc = 1137
            elif _pc == 1137:
                _pc = 1166 if not (W2 == -1) else 1149
            elif _pc == 1149:
                W2 = D2 + (OF * 2.0)
                _pc = 1187
            elif _pc == 1166:
                _pc = 1187 if not ((W2 if W2 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 1178
            elif _pc == 1178:
                W2 = D32
                _pc = 1187
            elif _pc == 1187:
                _pc = 1214 if not (L32) else 1193
            elif _pc == 1193:
                _pc = 1214 if not (O32 == 0) else 1205
            elif _pc == 1205:
                xL32 = L32
                _pc = 1214
            elif _pc == 1214:
                _pc = 1702 if not ((W2 if W2 is not None else -1e30) < (D32 if D32 is not None else -1e30)) else 1226
            elif _pc == 1226:
                wA2 = 90.0
                _pc = 1702
            elif _pc == 1235:
                _pc = 1702
            elif _pc == 1238:
                _pc = 1393 if not (L32 != None) else 1250
            elif _pc == 1250:
                _pc = 1393 if not (D32 != None) else 1262
            elif _pc == 1262:
                _pc = 1393 if not (O32 != None) else 1274
            elif _pc == 1274:
                _pc = 1298 if (L32 == 0.0) else 1286
            elif _pc == 1286:
                _pc = 1307 if not (L32 == -1) else 1298
            elif _pc == 1298:
                L32 = sF
                _pc = 1307
            elif _pc == 1307:
                _pc = 1334 if not (L32 == -2) else 1319
            elif _pc == 1319:
                noRight = True
                L32 = None
                _pc = 1334
            elif _pc == 1334:
                _pc = 1363 if not ((D32 if D32 is not None else -1e30) <= (0.0 if 0.0 is not None else -1e30)) else 1346
            elif _pc == 1346:
                D32 = D2 + (sF * 2.0)
                _pc = 1363
            elif _pc == 1363:
                _pc = 1702 if not (L32) else 1369
            elif _pc == 1369:
                _pc = 1702 if not (O32 == 0) else 1381
            elif _pc == 1381:
                xL32 = L32
                _pc = 1702
            elif _pc == 1390:
                _pc = 1702
            elif _pc == 1393:
                _pc = 1500 if not (L22 != None) else 1405
            elif _pc == 1405:
                _pc = 1500 if not (I2 != None) else 1417
            elif _pc == 1417:
                _pc = 1438 if not (L22 == 0.0) else 1429
            elif _pc == 1429:
                L22 = L21
                _pc = 1438
            elif _pc == 1438:
                _pc = 1471 if not (L22) else 1444
            elif _pc == 1444:
                _pc = 1471 if not (L22 == -2) else 1456
            elif _pc == 1456:
                noRight = True
                L22 = None
                _pc = 1471
            elif _pc == 1471:
                _pc = 1702 if not (L22) else 1477
            elif _pc == 1477:
                xL32 = -L22
                yL32 = L22 - I2
                _pc = 1702
            elif _pc == 1497:
                _pc = 1702
            elif _pc == 1500:
                _pc = 1591 if not (L22 != None) else 1512
            elif _pc == 1512:
                _pc = 1533 if not (L22 == 0.0) else 1524
            elif _pc == 1524:
                L22 = L21
                _pc = 1533
            elif _pc == 1533:
                _pc = 1566 if not (L22) else 1539
            elif _pc == 1539:
                _pc = 1566 if not (L22 == -2) else 1551
            elif _pc == 1551:
                noRight = True
                L22 = None
                _pc = 1566
            elif _pc == 1566:
                _pc = 1702 if not (L22) else 1572
            elif _pc == 1572:
                xL32 = -L22
                yL32 = L22
                _pc = 1702
            elif _pc == 1588:
                _pc = 1702
            elif _pc == 1591:
                _pc = 1702 if not (I2 != None) else 1603
            elif _pc == 1603:
                _pc = 1624 if not (I2 == 0.0) else 1615
            elif _pc == 1615:
                I2 = L21
                _pc = 1624
            elif _pc == 1624:
                _pc = 1657 if not (I2) else 1630
            elif _pc == 1630:
                _pc = 1657 if not (I2 == -2) else 1642
            elif _pc == 1642:
                noRight = True
                I2 = None
                _pc = 1657
            elif _pc == 1657:
                _pc = 1702 if not (I2) else 1663
            elif _pc == 1663:
                xL32 = 0.0
                yL32 = -I2
                oD2 = D2
                D2 = D2 + (OF * 2.0)
                _pc = 1702
            elif _pc == 1699:
                _pc = 1702
            elif _pc == 1702:
                pP1 = mPoint((L1 + xL31) + yL31, 0.0, 0.0)
                pP2 = mPoint(0.0, (L2 + xL32) + yL32, 0.0)
                pD1 = mVector(1.0, 0.0, 0.0)
                pD2 = mVector(0.0, 1.0, 0.0)
                retVal.append(D)
                retVal.append(D2)
                retVal.append(L1)
                retVal.append(L11)
                retVal.append(L2)
                retVal.append(L12)
                retVal.append(A)
                retVal.append(sL1)
                retVal.append(sL2)
                retVal.append(D / 2.0)
                retVal.append(D2 / 2.0)
                retVal.append(cR)
                retVal.append(OF)
                retVal.append(sF)
                retVal.append(oD)
                retVal.append(oD2)
                retVal.append(noLeft)
                retVal.append(L31)
                retVal.append(B31)
                retVal.append(D31)
                retVal.append(D41)
                retVal.append(W1)
                retVal.append(O31)
                retVal.append(wA1)
                retVal.append(xL31)
                retVal.append(noRight)
                retVal.append(L32)
                retVal.append(B32)
                retVal.append(D32)
                retVal.append(D42)
                retVal.append(W2)
                retVal.append(O32)
                retVal.append(wA2)
                retVal.append(xL32)
                retVal.append(pP1)
                retVal.append(pD1)
                retVal.append(pP2)
                retVal.append(pD2)
                retVal.append(L21)
                retVal.append(I1)
                retVal.append(L22)
                retVal.append(I2)
                return retVal
            else:
                break
        except Exception as _e:
            if _exc_stk:
                _stk.extend([None, _e, type(_e)])
                _pc = _exc_stk.pop()
            else:
                raise
