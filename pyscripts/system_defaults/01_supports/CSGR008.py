# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgrsub.csgr000 import *
from varmain.divsub.cnut6_001 import *
from varmain.divsub.cbolt_001 import *


@activate(Group="Support", TooltipShort="CSGR008", TooltipLong="CSGR008", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(SL=LENGTH, TooltipShort="SL")
@param(SW=LENGTH, TooltipShort="SW")
@param(SO=LENGTH, TooltipShort="SO")
@param(ST=LENGTH, TooltipShort="ST")
@param(RD=LENGTH, TooltipShort="RD")
@param(RW=LENGTH, TooltipShort="RW")
@param(RN=INT, TooltipShort="RN")
@param(H=LENGTH, TooltipShort="H")
@param(test=LENGTH, TooltipShort="test")
@param(ID=STRING, TooltipShort="组件标识")
def CSGR008(s, D=116.0, SL=40.0, SW=0.0, SO=400.0, ST=3.0, RD=60.0, RW=30.0, RN=2, H=110.0, test=False, ID='CSGR008', **kw):
    if RN == 0:
        RN = 2
    R1 = D / 2.0
    cH = H - ST
    R2 = RD / 2.0
    oD = SL / 2.0
    if oD > (RD / 2.0):
        oD = RD / 4.0
    sD = oD * 0.5
    nH = (round(sD * 750)) / 1000
    bL = (RW + (nH * 3.0)) + (ST * 2.0)
    sX = SO - (SW * 2.0)
    sX2 = sX / 2.0
    x1 = sqrt(pow(cH, 2.0) + pow(sX2, 2.0))
    rAng = asDegrees((atan(cH / sX2)) + (asin(((RW / 2.0) + ST) / x1)))
    oAng = (90.0 - rAng) - (rAng - 90.0)
    if RN > 1:
        sAng = [rAng - 90.0]
        if (RN - 2) > 0.0:
            aXL = oAng / (RN - 1)
            for rCnt in range(RN - 2):
                sAng.append(sAng[-1] + aXL)
        sAng.append(90.0 - rAng)
    else:
        sAng = [0.0]
    xCnt = 2
    o0 = None
    for rAng in sAng:
        rollMirr = False
        if rAng < 0.0:
            rAng = abs(rAng)
            rollMirr = True
        o1 = CYLINDER(s, R=R2, H=RW, O=0.0).rotateX(-90.0).translate((0.0, -(RW / 2.0), -R1 - R2))
        o2 = CBOLT_001(s, D=sD, L=bL).rotateZ(90.0).translate((0.0, -(bL / 2.0), -R1 - R2))
        o3 = CNUT6_001(s, D=sD, W=0.0, H=nH).rotateZ(-90.0).translate((0.0, (-(RW / 2.0)) - ST, -R1 - R2))
        o4 = CNUT6_001(s, D=sD, W=0.0, H=nH).rotateZ(90.0).translate((0.0, (RW / 2.0) + ST, -R1 - R2))
        o1.uniteWith(o2)
        o2.erase()
        o1.uniteWith(o3)
        o3.erase()
        o1.uniteWith(o4)
        o4.erase()
        ab = asRadiants(rAng)
        aa = (mcPi / 2.0) - ab
        xL = cH / cos(ab)
        xx = (xL - R1) - R2
        x1 = sqrt(pow(xx, 2.0) + (pow(RW / 2.0, 2.0)))
        yy = sqrt(pow(xL, 2.0) - pow(cH, 2.0))
        y2 = (RW / 2.0) / cos(ab)
        y1 = (RW / cos(ab)) - y2
        a1 = (mcPi / 2.0) - aa
        zz = ST / cos(a1)
        y3 = y1 + zz
        ac = atan((RW / 2.0) / xx)
        lL = sqrt((pow(x1, 2.0) + pow(y2, 2.0)) - (((2.0 * x1) * y2) * (cos(aa - ac))))
        rL = sqrt((pow(x1, 2.0) + pow(y3, 2.0)) - (((2.0 * x1) * y3) * (cos((mcPi - aa) - ac))))
        o2 = BOX(s, L=ST, W=rL, H=SL).translate((0.0, (ST / 2.0) + (RW / 2.0), ((-(rL / 2.0)) - R1) - R2))
        o3 = BOX(s, L=ST, W=lL, H=SL).translate((0.0, (-(ST / 2.0)) - (RW / 2.0), ((-(lL / 2.0)) - R1) - R2))
        o4 = BOX(s, L=ST, W=oD, H=SL).translate((0.0, (ST / 2.0) + (RW / 2.0), ((oD / 2.0) - R1) - R2))
        o5 = BOX(s, L=ST, W=oD, H=SL).translate((0.0, (-(ST / 2.0)) - (RW / 2.0), ((oD / 2.0) - R1) - R2))
        o1.uniteWith(o2)
        o2.erase()
        o1.uniteWith(o3)
        o3.erase()
        o1.uniteWith(o4)
        o4.erase()
        o1.uniteWith(o5)
        o5.erase()
        o1.rotateX(rAng)
        if SW > 0.0:
            sW = SW + zz
            o6 = BOX(s, L=sW, W=ST, H=SL).translate((0.0, ((+(sW / 2.0)) + yy) + y1, -(H - (ST / 2.0))))
            if rAng == 0.0:
                o7 = BOX(s, L=sW, W=ST, H=SL).translate((0.0, ((-(sW / 2.0)) + yy) - y2, -(H - (ST / 2.0))))
            else:
                sx = (ST + y2) + y1
                o7 = BOX(s, L=sx, W=ST, H=SL).translate((0.0, ((-(sx / 2.0)) + yy) + y1, -(H - (ST / 2.0))))
            o1.uniteWith(o6)
            o6.erase()
            o1.uniteWith(o7)
            o7.erase()
        if rollMirr:
            o1.rotateZ(180.0)
        if not (o0):
            if SW > 0.0:
                o0 = o1
            else:
                o0 = BOX(s, L=SO, W=ST, H=SL).translate((0.0, 0.0, -(H - (ST / 2.0))))
                o0.uniteWith(o1)
                o1.erase()
        else:
            o0.uniteWith(o1)
            o1.erase()
        xCnt += 1
    if test:
        oX = CYLINDER(s, R=R1, H=R1, O=0.0).rotateY(90.0).translate((-(R1 / 2.0), 0.0, 0.0))
    s.setPoint((0, 0, 0), (-1, 0, 0))
    s.setLinearDimension('H', (0, 0, 0), (0, 0, -H))
