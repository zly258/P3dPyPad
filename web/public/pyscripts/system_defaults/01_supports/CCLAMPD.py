# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cnut6_001 import *
from varmain.divsub.cbolt6_001 import *


@activate(Group="Support", TooltipShort="CCLAMPD", TooltipLong="CCLAMPD", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(H=LENGTH, TooltipShort="H")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(ID=STRING, TooltipShort="组件标识")
def CCLAMPD(s, D=116.0, L=0.0, H=0.0, W=0.0, K=0.0, ID='CCLAMPD', **kw):
    W = getThickness(D, OF=W, Ever=True, mustCalc=True)
    if L <= 0.0:
        L = D * 0.5
    xL = L / 2.0
    if L <= 0.0:
        L = D * 0.5
    if H <= 0.0:
        H = xL / 2.0
    R1 = D / 2.0
    R2 = R1 + W
    if K <= 0.0:
        K = (D + (H * 2.0)) + L
    H *= 2.0
    R3 = H / 2.0
    R1e = 0.0
    if (R3 * 2.0) > L:
        R3 = xL / 1.5
    R1e = (H / 2.0) - R3
    sM = L - R3
    o01 = (TORUS(s, R1=R1 + R1e, R2=R3)).translate((0.0, 0.0, (-(L / 2.0)) + sM))
    o02 = (CYLINDER(s, R=R1 + (H / 2.0), H=L - (R3 * 2.0), O=0.0)).translate((0.0, 0.0, -((L - (R3 * 2.0)) / 2.0)))
    o03 = (TORUS(s, R1=R1 + R1e, R2=R3)).translate((0.0, 0.0, (L / 2.0) - sM))
    o04 = None
    if R1e > 0.0:
        o04 = (CYLINDER(s, R=R1 + R1e, H=L, O=0.0)).translate((0.0, 0.0, -L / 2.0))
    o05 = BOX(s, L=K, W=L, H=W * 3.0)
    o06 = CYLINDER(s, R=R1, H=L, O=0.0).translate((0, 0, -(L / 2.0)))
    o07 = BOX(s, L=K, W=L, H=W)
    o01.uniteWith(o02)
    o02.erase()
    o01.uniteWith(o03)
    o03.erase()
    if o04 != None:
        o01.uniteWith(o04)
        o04.erase()
    o01.uniteWith(o05)
    o05.erase()
    o06.uniteWith(o07)
    o07.erase()
    o01.subtractFrom(o06)
    o06.erase()
    o01.rotateY(90)
    blTmp = W * 3.0
    bd = L / 4.0
    bH = (round(750 * bd)) / 1000
    bW = (round(bd * 1500)) / 1000
    wH = bH / 5.0
    wTmp = sqrt((pow(bW * tan(asRadiants(30.0)), 2)) + pow(bW, 2))
    wD = wTmp + (((L / 2.0) - wTmp) / 2.0)
    bl = (blTmp + (wH * 2.0)) + (bH * 1.5)
    xBPos = L / 4.0
    yBPos = (K / 2.0) - (((K - D) - H) / 4.0)
    zRot = 10.0
    for xMove in [xBPos, -xBPos]:
        for yMove in [yBPos, -yBPos]:
            o08 = CBOLT6_001(s, D=bd, L=bl, W=0.0, H=0.0).rotateY(90.0).rotateZ(-zRot).translate((xMove, yMove, (blTmp / 2.0) + wH))
            o09 = (CYLINDER(s, R=wD / 2.0, H=wH, O=0.0)).translate((xMove, yMove, blTmp / 2.0))
            o10 = (CYLINDER(s, R=wD / 2.0, H=wH, O=0.0)).translate((xMove, yMove, (-(blTmp / 2.0)) - wH))
            o11 = CNUT6_001(s, D=bd, W=0.0, H=0.0).rotateY(90.0).rotateZ(zRot).translate((xMove, yMove, (-(blTmp / 2.0)) - wH))
            for obj in [o08, o09, o10, o11]:
                o01.uniteWith(obj)
                obj.erase()
            zRot += 10.0
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setPoint((0, 0, 0), (1, 0, 0))
