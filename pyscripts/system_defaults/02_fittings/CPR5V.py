# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.multisub.cpr5vsub.cpr5v_util import *


@activate(Group="MultiPort", TooltipShort="Built-in CPR5V", TooltipLong="Built-in CPR5V (Decompiled from varmain/multisub/cpr5vsub/cpr5v.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(D4=LENGTH, TooltipShort="D4")
@param(D5=LENGTH, TooltipShort="D5")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(L3=LENGTH, TooltipShort="L3")
@param(H3=LENGTH, TooltipShort="H3")
@param(R3=LENGTH, TooltipShort="R3")
@param(L4=LENGTH, TooltipShort="L4")
@param(H4=LENGTH, TooltipShort="H4")
@param(R4=LENGTH, TooltipShort="R4")
@param(L5=LENGTH, TooltipShort="L5")
@param(H5=LENGTH, TooltipShort="H5")
@param(TOP=INT, TooltipShort="TOP")
@param(A1=ANGLE, TooltipShort="A1")
@param(A2=ANGLE, TooltipShort="A2")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPR5V(s, D1=114.3, D2=0.0, D3=0.0, D4=0.0, D5=0.0, L1=350.0, L2=100.0, L3=250.0, H3=180.0, R3=0.0, L4=0.0, H4=0.0, R4=0.0, L5=100.0, H5=180.0, TOP=1, A1=0.0, A2=0.0, OF=-1.0, ID='CPR5V', **kw):
    vC = CPR5VCORRV(D1=D1, D2=D2, D3=D3, D4=D4, D5=D5, L1=L1, L2=L2, L3=L3, H3=H3, R3=R3, L4=L4, H4=H4, R4=R4, L5=L5, H5=H5, A1=A1, A2=A2, OF=OF, L11=0.0, I1=0.0, L12=0.0, I2=0.0, L13=0.0, I3=0.0, L14=0.0, I4=0.0, L15=0.0, I5=0.0, TOP=TOP, Ever=None, FN=None, CPSTYPE=None)
    R1 = vC[0] / 2.0
    R2 = vC[1] / 2.0
    R3 = vC[2] / 2.0
    R4 = vC[3] / 2.0
    R5 = vC[89] / 2.0
    if vC[0] == vC[1]:
        o1 = CYLINDER(s, R=R1, H=vC[15], O=0.0).rotateY(270).translate((vC[5], 0, 0))
        if vC[14]:
            o3 = CYLINDER(s, R=vC[10], H=vC[15], O=0.0).rotateY(270).translate((vC[5], 0, 0))
    else:
        o1 = CONE(s, R1=R1, R2=R2, H=vC[15], E=0.0).rotateY(90).translate((-vC[4], 0, 0))
        if vC[14]:
            o3 = CONE(s, R1=vC[10], R2=vC[11], H=vC[15], E=0.0).rotateY(90).translate((-vC[4], 0, 0))
    o2 = CYLINDER(s, R=R3, H=vC[77], O=vC[12]).rotateX(270).translate((0, -vC[77], 0)).rotateZ(vC[17])
    o2a = ((ARC3D2(s, D=R3, D2=R3, R=vC[75], A=90.0 - vC[9])).rotateZ(-vC[9])).translate(vC[79])
    o2b = CYLINDER(s, R=R3, H=vC[81], O=vC[12]).rotateX(270).translate(vC[83])
    if vC[14]:
        o4 = CYLINDER(s, R=vC[12], H=vC[77], O=0.0).rotateX(270).translate((0, -vC[77], 0)).rotateZ(vC[17])
        o4a = ((ARC3D2(s, D=vC[12], D2=vC[12], R=vC[75], A=90.0 - vC[9])).rotateZ(-vC[9])).translate(vC[79])
        o4b = CYLINDER(s, R=vC[12], H=vC[81], O=0.0).rotateX(270).translate(vC[83])
    o1.uniteWith(o2)
    o2.erase()
    o1.uniteWith(o2a)
    o2a.erase()
    o1.uniteWith(o2b)
    o2b.erase()
    o5 = CYLINDER(s, R=R4, H=vC[78], O=vC[13]).rotateX(270).translate((0, -vC[78], 0)).rotateZ(vC[71])
    o5a = ((ARC3D2(s, D=R4, D2=R4, R=vC[76], A=90.0 - vC[70])).rotateZ(-90.0)).translate(vC[80])
    o5b = CYLINDER(s, R=R4, H=vC[82], O=vC[13]).rotateX(90).translate(vC[84])
    if vC[14]:
        o6 = CYLINDER(s, R=vC[13], H=vC[78], O=0.0).rotateX(270).translate((0, -vC[78], 0)).rotateZ(vC[71])
        o6a = ((ARC3D2(s, D=vC[13], D2=vC[13], R=vC[76], A=90.0 - vC[70])).rotateZ(-90.0)).translate(vC[80])
        o6b = CYLINDER(s, R=vC[13], H=vC[82], O=0.0).rotateX(90).translate(vC[84])
    o1.uniteWith(o5)
    o5.erase()
    o1.uniteWith(o5a)
    o5a.erase()
    o1.uniteWith(o5b)
    o5b.erase()
    o7 = CYLINDER(s, R=R5, H=vC[97], O=0.0).rotateX(vC[87]).translate((vC[92], 0, 0)).rotateZ(vC[107])
    if vC[14]:
        xH = vC[97]
        if xH < R1:
            xH = R1
        o8 = CYLINDER(s, R=vC[95], H=xH, O=0.0).rotateX(vC[87]).translate((vC[92], 0, 0)).rotateZ(vC[107])
    o1.uniteWith(o7)
    o7.erase()
    if vC[14]:
        o3.uniteWith(o4)
        o4.erase()
        o3.uniteWith(o4a)
        o4a.erase()
        o3.uniteWith(o4b)
        o4b.erase()
        o3.uniteWith(o6)
        o6.erase()
        o3.uniteWith(o6a)
        o6a.erase()
        o3.uniteWith(o6b)
        o6b.erase()
        o3.uniteWith(o8)
        o8.erase()
        o1.subtractFrom(o3)
        o3.erase()
    s.setPoint(vC[18], vC[22], vC[66])
    s.setPoint(vC[19], vC[23], vC[67])
    s.setPoint(vC[20], vC[24], vC[68])
    s.setPoint(vC[21], vC[25], vC[69])
    s.setPoint(vC[93], vC[94], vC[105])
