# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.divsub.cnut6_001 import *
from varmain.divsub.cbolt_001 import *


@activate(Group="Support", TooltipShort="CSGT001", TooltipLong="CSGT001", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(L=LENGTH, TooltipShort="L")
@param(W=LENGTH, TooltipShort="W")
@param(K=LENGTH, TooltipShort="K")
@param(O=LENGTH, TooltipShort="O")
@param(H1=LENGTH, TooltipShort="H1")
@param(H2=LENGTH, TooltipShort="H2")
@param(HD3=LENGTH, TooltipShort="HD3")
@param(HT4=LENGTH, TooltipShort="HT4")
@param(HL4=LENGTH, TooltipShort="HL4")
@param(HW4=LENGTH, TooltipShort="HW4")
@param(HH4=LENGTH, TooltipShort="HH4")
@param(ID=STRING, TooltipShort="组件标识")
def CSGT001(s, L=300.0, W=50.0, K=25.0, O=0.0, H1=200.0, H2=0.0, HD3=0.0, HT4=0.0, HL4=0.0, HW4=0.0, HH4=0.0, ID='CSGT001', **kw):
    if K <= 0.0:
        K = W
    if O <= 0.0:
        O = W / 2.0
    if H2 <= 0.0:
        H2 = H1
    if HD3 <= 0.0:
        HD3 = W / 25.0
    if HT4 <= 0.0:
        HT4 = HD3 * 0.25
    if HL4 <= 0.0:
        HL4 = HD3 + (HT4 * 3.0)
    if HW4 <= 0.0:
        HW4 = HD3
    if HH4 <= 0.0:
        HH4 = HD3
    o0 = (BOX(s, L=K, W=W, H=L + (O * 2.0))).translate((0.0, -(K / 2.0), 0.0))
    for cnt in [1, 2]:
        if cnt == 1:
            H = H1
        else:
            H = H2
        o1 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(90.0).rotateX(90.0).translate((0.0, 0.0, 0.0))
        MH = abs(o1.pointAt(1).y() - o1.pointAt(0).y())
        o2 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(-90.0).rotateX(90.0).translate((0.0, (H - HD3) - HH4, 0.0))
        o5 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(-90.0).rotateX(90.0).translate((0.0, -K, 0.0))
        o6 = CNUT6_001(s, D=HD3, W=0.0, H=0.0).rotateY(-90.0).rotateX(90.0).rotateY(15.0).translate((0.0, -(K + MH), 0.0))
        hExt = (MH * 2.5) + K
        cL3 = H
        o3 = ((CBOLT_001(s, D=HD3, L=cL3 + hExt)).rotateZ(90.0)).translate((0.0, -hExt, 0.0))
        xL1 = HL4 + (HT4 * 2.0)
        xH1 = (H - ((HH4 - HT4) / 2.0)) - HT4
        o4a = BOX(s, L=HH4, W=HW4, H=HT4).translate(((HL4 / 2.0) - (HT4 / 2.0), H - (HH4 / 2.0), 0.0))
        o4b = BOX(s, L=HH4, W=HW4, H=HT4).translate((-((HL4 / 2.0) - (HT4 / 2.0)), H - (HH4 / 2.0), 0.0))
        o4c = BOX(s, L=HT4, W=HW4, H=HL4).translate((0.0, H - (HT4 / 2.0), 0.0))
        o4d = CYLINDER(s, R=HT4, H=xL1, O=0.0).rotateY(-90.0).translate((xL1 / 2.0, xH1, 0.0))
        o4d.uniteWith(o4c)
        o4c.erase()
        o4d.uniteWith(o4b)
        o4b.erase()
        o4d.uniteWith(o4a)
        o4a.erase()
        o4d.uniteWith(o3)
        o3.erase()
        o4d.uniteWith(o2)
        o2.erase()
        o4d.uniteWith(o1)
        o1.erase()
        o4d.uniteWith(o5)
        o5.erase()
        o4d.uniteWith(o6)
        o6.erase()
        if cnt == 1:
            xM = -(L / 2.0)
        else:
            xM = +(L / 2.0)
        o4d.translate((xM, 0.0, 0.0))
        o0.uniteWith(o4d)
        o4d.erase()
    o0.rotateZ(90.0).rotateY(90.0)
    s.setLinearDimension('H1', (0, 0, 0), (0, 0, H1))
