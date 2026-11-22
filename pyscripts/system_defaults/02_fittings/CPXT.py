# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.crosssub.cpxtsub.cpxt_util import *


@activate(Group="Cross", TooltipShort="CP METRIC Tee Side Outlet", TooltipLong="CP METRIC Tee Side Outlet (Decompiled from varmain/crosssub/cpxtsub/cpxt.pyc)", LengthUnit="mm", Ports=4)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(D4=LENGTH, TooltipShort="D4")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(L3=LENGTH, TooltipShort="L3")
@param(L4=LENGTH, TooltipShort="L4")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPXT(s, D1=1016.0, D2=1016.0, D3=1016.0, D4=1016.0, L1=749.0, L2=749.0, L3=749.0, L4=749.0, OF=-1.0, ID='CPXT', **kw):
    vC = CPXTCORRV(D1=D1, D2=D2, D3=D3, D4=D4, L1=L1, L2=L2, L3=L3, L4=L4, OF=OF, L11=0.0, I1=0.0, L12=0.0, I2=0.0, L13=0.0, I3=0.0, L14=0.0, I4=0.0, Ever=None, FN=None, CPSTYPE=None)
    R1 = vC[0] / 2.0
    R2 = vC[1] / 2.0
    R3 = vC[2] / 2.0
    R4 = vC[3] / 2.0
    if R1 == vC[54]:
        oo0 = CYLINDER(s, R=R1, H=vC[4], O=0.0).rotateY(270.0)
        if vC[14]:
            oi0 = CYLINDER(s, R=vC[10], H=vC[4], O=0.0).rotateY(270.0)
    else:
        oo0 = CONE(s, R1=vC[54], R2=R1, H=vC[4], E=0.0).rotateY(270.0)
        if vC[14]:
            oi0 = CONE(s, R1=vC[55], R2=vC[10], H=vC[4], E=0.0).rotateY(270.0)
    if R2 == vC[54]:
        oo1 = CYLINDER(s, R=R2, H=vC[5], O=0.0).rotateY(90.0)
        if vC[14]:
            oi1 = CYLINDER(s, R=vC[55], H=vC[5], O=0.0).rotateY(90.0)
    else:
        oo1 = CONE(s, R1=vC[54], R2=R2, H=vC[5], E=0.0).rotateY(90.0)
        if vC[14]:
            oi1 = CONE(s, R1=vC[55], R2=vC[11], H=vC[5], E=0.0).rotateY(90.0)
    if R3 == vC[54]:
        oo2 = (CYLINDER(s, R=R3, H=vC[6], O=0.0).rotateY(90.0).rotateZ(vC[9] / 2.0)).rotateY(180.0 + vC[9])
        if vC[14]:
            oi2 = (CYLINDER(s, R=vC[12], H=vC[6], O=0.0).rotateY(90.0).rotateZ(vC[9] / 2.0)).rotateY(180.0 + vC[9])
    else:
        oo2 = (CONE(s, R1=vC[54], R2=R3, H=vC[6], E=0.0).rotateY(90.0).rotateZ(vC[9] / 2.0)).rotateY(180.0 + vC[9])
        if vC[14]:
            oi2 = (CONE(s, R1=vC[55], R2=vC[12], H=vC[6], E=0.0).rotateY(90.0).rotateZ(vC[9] / 2.0)).rotateY(180.0 + vC[9])
    if R4 == vC[54]:
        oo3 = (CYLINDER(s, R=R4, H=vC[7], O=0.0).rotateY(90.0).rotateZ(0.0 - (vC[9] / 2.0))).rotateY(180.0 + vC[9])
        if vC[14]:
            oi3 = (CYLINDER(s, R=vC[55], H=vC[7], O=0.0).rotateY(90.0).rotateZ(0.0 - (vC[9] / 2.0))).rotateY(180.0 + vC[9])
    else:
        oo3 = (CONE(s, R1=vC[54], R2=R4, H=vC[7], E=0.0).rotateY(90.0).rotateZ(0.0 - (vC[9] / 2.0))).rotateY(180.0 + vC[9])
        if vC[14]:
            oi3 = (CONE(s, R1=vC[55], R2=vC[13], H=vC[7], E=0.0).rotateY(90.0).rotateZ(0.0 - (vC[9] / 2.0))).rotateY(180.0 + vC[9])
    oo4 = SPHERE(s, R=vC[54])
    if vC[14]:
        oi4 = SPHERE(s, R=vC[55])
    oo0.uniteWith(oo1)
    oo1.erase()
    oo0.uniteWith(oo2)
    oo2.erase()
    oo0.uniteWith(oo3)
    oo3.erase()
    oo0.uniteWith(oo4)
    oo4.erase()
    if vC[14]:
        oi0.uniteWith(oi1)
        oi1.erase()
        oi0.uniteWith(oi2)
        oi2.erase()
        oi0.uniteWith(oi3)
        oi3.erase()
        oi0.uniteWith(oi4)
        oi4.erase()
        oo0.subtractFrom(oi0)
        oi0.erase()
    s.setPoint(vC[18], vC[22], vC[68])
    s.setPoint(vC[19], vC[23], vC[69])
    s.setPoint(vC[20], vC[24], vC[70])
    s.setPoint(vC[21], vC[25], vC[71])
