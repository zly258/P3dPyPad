# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cnut6_001 import *
from varmain.divsub.cbolt_001 import *


@activate(Group="Support", TooltipShort="CSGT002", TooltipLong="CSGT002", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(O=LENGTH, TooltipShort="O")
@param(H1=LENGTH, TooltipShort="H1")
@param(H2=LENGTH, TooltipShort="H2")
@param(HD3=LENGTH, TooltipShort="HD3")
@param(HS=LENGTH, TooltipShort="HS")
@param(HO=LENGTH, TooltipShort="HO")
@param(ID=STRING, TooltipShort="组件标识")
def CSGT002(s, L=300.0, W=50.0, K=25.0, O=0.0, H1=200.0, H2=0.0, HD3=0.0, HS=10.0, HO=0.0, ID='CSGT002', **kw):
    if K <= 0.0:
        K = W
    if O <= 0.0:
        O = W / 2.0
    if H2 <= 0.0:
        H2 = H1
    if HD3 <= 0.0:
        HD3 = W / 25.0
    o0 = (BOX(s, L=K, W=W, H=L + (O * 2.0))).translate((0.0, -(K / 2.0), 0.0))
    for cnt in [1, 2]:
        if cnt == 1:
            H = H1
        else:
            H = H2
        o3 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateZ(90.0).rotateY(90.0).translate((0.0, 0.0, 0.0))
        o4 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateZ(90.0).rotateY(90.0).translate((0.0, H + HS, 0.0))
        MH = abs(o4.pointAt(1).y() - o4.pointAt(0).y())
        o6 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(-90.0).rotateX(90.0).translate((0.0, -K, 0.0))
        o7 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(-90.0).rotateX(90.0).rotateY(15.0).translate((0.0, -(K + MH), 0.0))
        if HO <= 0.0:
            HO = MH * 3.0
        if (MH * 3.0) > HO:
            o5 = None
        else:
            o5 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateZ(90.0).translate(o4.pointAt(1))
        hExt = (MH * 2.5) + K
        cL3 = (H + HS) + HO
        o2 = ((CBOLT_001(s, D=HD3, L=cL3 + hExt)).rotateZ(90.0)).translate((0.0, -hExt, 0.0))
        oX = (CYLINDER(s, R=HD3 * 0.01, H=HD3 * 0.01, O=0.0)).rotateX(-90.0)
        oX.uniteWith(o2)
        o2.erase()
        oX.uniteWith(o4)
        o4.erase()
        oX.uniteWith(o3)
        o3.erase()
        oX.uniteWith(o6)
        o6.erase()
        oX.uniteWith(o7)
        o7.erase()
        if o5:
            oX.uniteWith(o5)
            o5.erase()
        if cnt == 1:
            xM = -(L / 2.0)
        else:
            xM = +(L / 2.0)
        oX.translate((xM, 0.0, 0.0))
        o0.uniteWith(oX)
        oX.erase()
    o0.rotateZ(90.0).rotateY(90.0)
    s.setLinearDimension('H1', (0, 0, 0), (0, 0, H1))
