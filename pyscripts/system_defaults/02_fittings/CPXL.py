# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.crosssub.cpxlsub.cpxl_util import *


@activate(Group="Cross", TooltipShort="Built-in CPXL", TooltipLong="Built-in CPXL (Decompiled from varmain/crosssub/cpxlsub/cpxl.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(D4=LENGTH, TooltipShort="D4")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(L3=LENGTH, TooltipShort="L3")
@param(L4=LENGTH, TooltipShort="L4")
@param(A1=ANGLE, TooltipShort="A1")
@param(A2=ANGLE, TooltipShort="A2")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPXL(s, D1=114.3, D2=0.0, D3=0.0, D4=0.0, L1=350.0, L2=100.0, L3=250.0, L4=0.0, A1=0.0, A2=0.0, OF=-1.0, ID='CPXL', **kw):
    vC = CPXLCORRV(D1=D1, D2=D2, D3=D3, D4=D4, L1=L1, L2=L2, L3=L3, L4=L4, A1=A1, A2=A2, OF=OF, L11=0.0, I1=0.0, L12=0.0, I2=0.0, L13=0.0, I3=0.0, L14=0.0, I4=0.0, Ever=None, FN=None, CPSTYPE=None)
    R1 = vC[0] / 2.0
    R2 = vC[1] / 2.0
    R3 = vC[2] / 2.0
    R4 = vC[3] / 2.0
    if vC[0] == vC[1]:
        o1 = CYLINDER(s, R=R1, H=vC[15], O=0.0).rotateY(270).translate((vC[5], 0, 0))
        if vC[14]:
            o3 = CYLINDER(s, R=vC[10], H=vC[15], O=0.0).rotateY(270).translate((vC[5], 0, 0))
    else:
        o1 = CONE(s, R1=R1, R2=R2, H=vC[15], E=0.0).rotateY(90).translate((-vC[4], 0, 0))
        if vC[14]:
            o3 = CONE(s, R1=vC[10], R2=vC[11], H=vC[15], E=0.0).rotateY(90).translate((-vC[4], 0, 0))
    o2 = CYLINDER(s, R=R3, H=vC[6], O=vC[12]).rotateX(270).translate((0, -vC[6], 0)).rotateZ(vC[17])
    if vC[14]:
        o4 = CYLINDER(s, R=vC[12], H=vC[6], O=0.0).rotateX(270).translate((0, -vC[6], 0)).rotateZ(vC[17])
    o1.uniteWith(o2)
    o2.erase()
    o5 = CYLINDER(s, R=R4, H=vC[7], O=vC[13]).rotateX(270).translate((0, -vC[7], 0)).rotateZ(vC[71])
    if vC[14]:
        o6 = CYLINDER(s, R=vC[13], H=vC[7], O=0.0).rotateX(270).translate((0, -vC[7], 0)).rotateZ(vC[71])
    o1.uniteWith(o5)
    o5.erase()
    if vC[14]:
        o3.uniteWith(o4)
        o4.erase()
        o3.uniteWith(o6)
        o6.erase()
        o1.subtractFrom(o3)
        o3.erase()
    s.setPoint(vC[18], vC[22], vC[66])
    s.setPoint(vC[19], vC[23], vC[67])
    s.setPoint(vC[20], vC[24], vC[68])
    s.setPoint(vC[21], vC[25], vC[69])
