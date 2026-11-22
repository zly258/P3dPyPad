# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.crosssub.cpxxsub.cpxx_util import *


@activate(Group="Cross", TooltipShort="CP METRIC Cross", TooltipLong="CP METRIC Cross (Decompiled from varmain/crosssub/cpxxsub/cpxx.pyc)", LengthUnit="mm", Ports=4)
@group("MainDimensions")
@param(D1=LENGTH, TooltipShort="D1")
@param(D2=LENGTH, TooltipShort="D2")
@param(D3=LENGTH, TooltipShort="D3")
@param(D4=LENGTH, TooltipShort="D4")
@param(L1=LENGTH, TooltipShort="L1")
@param(L2=LENGTH, TooltipShort="L2")
@param(L3=LENGTH, TooltipShort="L3")
@param(L4=LENGTH, TooltipShort="L4")
@param(A=ANGLE, TooltipShort="A")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPXX(s, D1=1016.0, D2=1016.0, D3=1016.0, D4=1016.0, L1=749.0, L2=749.0, L3=749.0, L4=749.0, A=90.0, OF=-1.0, ID='CPXX', **kw):
    vC = CPXXCORRV(D1=D1, D2=D2, D3=D3, D4=D4, L1=L1, L2=L2, L3=L3, L4=L4, A=A, OF=OF, L11=0.0, I1=0.0, L12=0.0, I2=0.0, L13=0.0, I3=0.0, L14=0.0, I4=0.0, Ever=None, FN=None, CPSTYPE=None)
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
    if vC[2] == vC[3]:
        o2 = CYLINDER(s, R=R3, H=vC[16], O=vC[12]).rotateX(270).translate((0, -vC[7], 0)).rotateZ(vC[17])
        if vC[14]:
            o4 = CYLINDER(s, R=vC[12], H=vC[16], O=0.0).rotateX(270).translate((0, -vC[7], 0)).rotateZ(vC[17])
    else:
        o2 = CONE(s, R1=R3, R2=R4, H=vC[16], E=0.0).rotateX(-90).rotateZ(180).translate((0, vC[6], 0)).rotateZ(vC[17])
        if vC[14]:
            o4 = CONE(s, R1=vC[12], R2=vC[13], H=vC[16], E=0.0).rotateX(-90).rotateZ(180).translate((0, vC[6], 0)).rotateZ(vC[17])
    o1.uniteWith(o2)
    o2.erase()
    if vC[14]:
        o3.uniteWith(o4)
        o4.erase()
        o1.subtractFrom(o3)
        o3.erase()
    s.setPoint(vC[18], vC[22], vC[66])
    s.setPoint(vC[19], vC[23], vC[67])
    s.setPoint(vC[20], vC[24], vC[68])
    s.setPoint(vC[21], vC[25], vC[69])
