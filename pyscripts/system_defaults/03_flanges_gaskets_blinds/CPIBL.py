# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.blindsub.cpib_util import *


@activate(Group="BlindDisk", TooltipShort="Built-in CPIBL", TooltipLong="Built-in CPIBL (Decompiled from varmain/blindsub/cpibl.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(W=LENGTH, TooltipShort="W")
@param(L=LENGTH, TooltipShort="L")
@param(L1=LENGTH, TooltipShort="L1")
@param(H=LENGTH, TooltipShort="H")
@param(OF=LENGTH, TooltipShort="OF")
@param(BD=LENGTH, TooltipShort="BD")
@param(ID=STRING, TooltipShort="组件标识")
def CPIBL(s, D1=114.3, D2=0.0, W=0.0, L=0.0, L1=0.0, H=0.0, OF=-1.0, BD=0.0, ID='CPIBL', **kw):
    if W <= 0.0:
        W = D1 / 4.0
    if L <= 0.0:
        L = (D1 + W) / 2.0
    if L1 <= 0.0:
        BD = 0.0
        L1 = 0.0
    sF = getThickness(D=D1, OF=OF, Ever=1, mustCalc=True)
    if H <= 0.0:
        H = sF * 2.0
    else:
        if sF > H:
            sF = H
    R1 = D1 / 2.0
    sL = L + L1
    o0 = CYLINDER(s, R=R1, H=H, O=0.0).rotateY(90)
    oS = None
    if D2:
        oS = (CYLINDER(s, R=D2 / 2.0, H=H * 2.0, O=0.0)).rotateY(90.0)
    o1 = BOX(s, L=W, W=sL, H=sF).translate((H / 2.0, 0.0, sL / 2.0))
    oH = None
    if BD > 0.0:
        oH = ((CYLINDER(s, R=BD / 2.0, H=H * 3.0, O=0.0)).rotateY(90.0)).translate((-H, 0.0, L))
    o0.uniteWith(o1)
    o1.erase()
    if oS:
        o0.subtractFrom(oS)
        oS.erase()
    if oH:
        o0.subtractFrom(oH)
        oH.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
    s.setPoint((H, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0)
