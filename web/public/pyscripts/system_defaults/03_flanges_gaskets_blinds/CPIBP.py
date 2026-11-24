# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.blindsub.cpib_util import *
from varmain.blindsub.cpibl import *


@activate(Group="BlindDisk", TooltipShort="CP METRIC Spectacle Blind", TooltipLong="CP METRIC Spectacle Blind (Decompiled from varmain/blindsub/cpibp.pyc)", LengthUnit="mm", Ports=2)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(W=LENGTH, TooltipShort="W")
@param(L=LENGTH, TooltipShort="L")
@param(H=LENGTH, TooltipShort="H")
@param(OF=LENGTH, TooltipShort="OF")
@param(BD=LENGTH, TooltipShort="BD")
@param(ID=STRING, TooltipShort="组件标识")
def CPIBP(s, D1=105.0, D2=26.9, W=0.0, L=0.0, H=18.0, OF=-1.0, BD=0.0, ID='CPIBP', **kw):
    if W <= 0.0:
        W = D1 / 4.0
    if L <= 0.0:
        L = D1 + W
    sF = getThickness(D=D1, OF=OF, Ever=1, mustCalc=True)
    if H <= 0.0:
        H = sF * 2.0
    else:
        if sF > H:
            sF = H
    if D2 <= 0.0:
        D2 = D1 * 0.66666
    sL = L / 2.0
    o0 = CPIBL(s, D1=D1, D2=D2, W=W, L=sL, L1=0.0, H=H, OF=sF, BD=0.0)
    o1 = CPIBL(s, D1=D1, D2=0.0, W=W, L=sL, L1=0.0, H=H, OF=sF, BD=0.0).rotateY(180.0).translate((H, 0.0, L))
    oT = CYLINDER(s, R=sF, H=sF, O=0.0).rotateY(90.0).translate(((H - sF) / 2.0, 0.0, sL))
    oH = None
    if BD > 0.0:
        oH = ((CYLINDER(s, R=BD / 2.0, H=H * 3.0, O=0.0)).rotateY(90)).translate((-H, 0.0, sL))
    oT.uniteWith(o0)
    o0.erase()
    oT.uniteWith(o1)
    o1.erase()
    if oH:
        oT.subtractFrom(oH)
        oH.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
    s.setPoint((H, 0.0, 0.0), (1.0, 0.0, 0.0), 0.0)
