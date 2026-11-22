# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cste_l import *
from varmain.flangesub.cpfwr import *
from varmain.pumpsub.cap_util import *


@activate(Group="Equipment", TooltipShort="Built-in CAPD1a", TooltipLong="Built-in CAPD1a (Decompiled from varmain/pumpsub/capd1a.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(DC=LENGTH, TooltipShort="DC")
@param(LC=LENGTH, TooltipShort="LC")
@param(CC=LENGTH, TooltipShort="CC")
@param(HC=LENGTH, TooltipShort="HC")
@param(D1FC=LENGTH, TooltipShort="D1FC")
@param(D2FC=LENGTH, TooltipShort="D2FC")
@param(LFC=LENGTH, TooltipShort="LFC")
@param(BFC=LENGTH, TooltipShort="BFC")
@param(MD=LENGTH, TooltipShort="MD")
@param(ML=LENGTH, TooltipShort="ML")
@param(DISP=INT, TooltipShort="DISP")
@param(ID=STRING, TooltipShort="组件标识")
def CAPD1a(s, DC=500.0, LC=250.0, CC=200.0, HC=450.0, D1FC=220.0, D2FC=114.3, LFC=50.0, BFC=22.0, MD=450.0, ML=600.0, DISP=0, ID='CAPD1a', **kw):
    R1 = DC / 2.0
    R2 = D2FC / 2.0
    R1 -= R2
    if (LFC <= 0.0) or (LFC <= BFC):
        LFC = BFC + 0.0001
    xH = CC - LFC
    oT0 = TORUS(s, R1=R1, R2=R2)
    oT1 = CYLINDER(s, R=R1, H=D2FC, O=0.0).translate((0.0, 0.0, -R2))
    oT2 = CPFWR(s, L=LFC, B=BFC, D1=D1FC, D2=D2FC, D3=0.0).rotateZ(-90.0)
    oT4 = None
    if DISP == 1:
        oT2.translate((-R1, HC, 0.0))
        oT3 = ((CYLINDER(s, R=R2, H=HC - LFC, O=0.0)).rotateX(-90.0)).translate((-R1, 0.0, 0.0))
    else:
        oT2.rotateX(90.0).translate((-((DC - D1FC) / 2.0), HC - (D1FC / 2.0), LFC))
        pt1 = oT2.pointAt(1)
        sA = (D1FC - D2FC) / 2.0
        sB = pt1.y()
        sL = sqrt(pow(sA, 2.0) + pow(sB, 2.0))
        sR = 90.0 - (asDegrees(acos(sA / sB)))
        oT3 = CYLINDER(s, R=R2, H=sL, O=0.0).rotateX(-90.0).rotateZ(-sR).translate((-R1, 0.0, 0.0))
        oT4 = HALFSPHERE(s, R=R2).rotateX(-180.0).translate((0.0, sL, 0.0)).rotateZ(-sR).translate((-R1, 0.0, 0.0))
    oT5 = None
    if DISP == 0:
        oT5 = (((BOX(s, L=DC, W=HC + (DC / 2.0), H=D1FC)).rotateX(-90)).rotateY(-90)).translate((0.0, ((HC + (DC / 2.0)) / 2.0) - (DC / 2.0), D1FC / 2.0))
    sH = LC - (D2FC / 2.0)
    oT7 = CYLINDER(s, R=DC / 2.0, H=sH, O=0.0)
    l1 = ML * 0.666666666
    l2 = (ML - l1) * 0.5
    d2 = MD * 0.666666666
    d3 = d2 * 0.5
    oT8 = (CYLINDER(s, R=MD / 2.0, H=l1, O=0.0)).translate((0.0, 0.0, sH))
    sH += l1
    cH = sH
    oT9 = (CYLINDER(s, R=d2 / 2.0, H=l2, O=0.0)).translate((0.0, 0.0, sH))
    sH += l2
    oTA = (CYLINDER(s, R=d3 / 2.0, H=l2, O=0.0)).translate((0.0, 0.0, sH))
    oTB = ((CONE(s, R1=D1FC / 2.0, R2=D2FC / 2.0, H=BFC, E=0.0)).rotateY(180.0)).translate((0.0, 0.0, -(D2FC / 2.0)))
    oTC = ((CYLINDER(s, R=D2FC / 2.0, H=BFC, O=0.0)).rotateY(180.0)).translate((0.0, 0.0, -(D2FC / 2.0)))
    xR = (d2 - d3) / 6.0
    bR = xR * 2.5
    cH += bR
    oC0 = (((ARC3D(s, D=xR / 2.0, R=bR, A=90.0)).rotateX(-90.0)).rotateZ(180.0)).translate(((MD - xR) / 2.0, 0.0, cH))
    oC1 = ((((ARC3D(s, D=xR / 2.0, R=bR, A=90.0)).rotateX(-90.0)).rotateZ(180.0)).translate(((MD - xR) / 2.0, 0.0, cH))).rotateZ(90.0)
    oC2 = ((((ARC3D(s, D=xR / 2.0, R=bR, A=90.0)).rotateX(-90.0)).rotateZ(180.0)).translate(((MD - xR) / 2.0, 0.0, cH))).rotateZ(180.0)
    oC3 = ((((ARC3D(s, D=xR / 2.0, R=bR, A=90.0)).rotateX(-90.0)).rotateZ(180.0)).translate(((MD - xR) / 2.0, 0.0, cH))).rotateZ(270.0)
    xxL1 = (MD - (bR * 2.0)) - xR
    oC4 = ((CYLINDER(s, R=xR / 2.0, H=xxL1, O=0.0)).rotateY(-90.0)).translate((xxL1 / 2.0, 0.0, cH))
    oC5 = ((CYLINDER(s, R=xR / 2.0, H=xxL1, O=0.0)).rotateX(90.0)).translate((0.0, xxL1 / 2.0, cH))
    xL = DC / 15.0
    xT = xL / 10.0
    xD = (sqrt(pow(xL, 2.0) + pow(xL, 2.0))) / 2.0
    oF0 = CSTE_L(s, W=xL, H=xL, T=xT, L=xH).rotateZ(135.0).translate(((DC / 2.0) - xD, 0.0, -xH))
    oF1 = (CSTE_L(s, W=xL, H=xL, T=xT, L=xH).rotateZ(135.0).translate(((DC / 2.0) - xD, 0.0, -xH))).rotateZ(90.0)
    oF2 = (CSTE_L(s, W=xL, H=xL, T=xT, L=xH).rotateZ(135.0).translate(((DC / 2.0) - xD, 0.0, -xH))).rotateZ(180.0)
    oF3 = (CSTE_L(s, W=xL, H=xL, T=xT, L=xH).rotateZ(135.0).translate(((DC / 2.0) - xD, 0.0, -xH))).rotateZ(270.0)
    for xPart in [oT1, oT3]:
        oT0.uniteWith(xPart)
        xPart.erase()
    if oT4:
        oT0.uniteWith(oT4)
        oT4.erase()
    if oT5:
        oT0.subtractFrom(oT5)
        oT5.erase()
    for xPart in [oT7, oT8, oT9, oTA, oTB, oF0, oF1, oF2, oF3, oC0, oC1, oC2, oC3, oC4, oC5]:
        oT0.uniteWith(xPart)
        xPart.erase()
    oT0.subtractFrom(oTC)
    oTC.erase()
    oT0.translate((0.0, 0.0, xH))
    oT2.translate((0.0, 0.0, xH))
    s.setPoint(oT2.pointAt(0), oT2.directionAt(0))
    oT0.uniteWith(oT2)
    oT2.erase()
