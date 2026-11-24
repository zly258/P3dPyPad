# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.miscellaneoussub.cpmdsub.cpmd_util import *


@activate(Group="Trap", TooltipShort="Built-in CPMDB", TooltipLong="Built-in CPMDB (Decompiled from varmain/miscellaneoussub/cpmdsub/cpmdbsub/cpmdb.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(H1=LENGTH, TooltipShort="H1")
@param(H2=LENGTH, TooltipShort="H2")
@param(R2=LENGTH, TooltipShort="R2")
@param(OF=LENGTH, TooltipShort="OF")
@param(SC=INT, TooltipShort="SC")
@param(ID=STRING, TooltipShort="组件标识")
def CPMDB(s, D=114.3, L=500.0, H1=300.0, H2=400.0, R2=150.0, OF=-1.0, SC=0, ID='CPMDB', **kw):
    if R2 <= 0.0:
        R2 = D * 1.5
    pL1 = L - (R2 / 2.0)
    pH1 = (H1 - R2) - (D / 2.0)
    pH2 = (H2 - (R2 / 2.0)) - (D / 2.0)
    pR = R2 / 2.0
    o0 = (CYLINDER(s, R=D / 2.0, H=pL1, O=0.0)).rotateY(90.0)
    o1 = (((ARC3D2(s, D=D / 2.0, D2=D / 2.0, R=pR, A=90.0)).rotateZ(180.0)).rotateX(90.0)).translate((pL1 + pR, 0.0, 0.0))
    o2 = (CYLINDER(s, R=D / 2.0, H=pH1, O=0.0)).translate((pL1 + pR, 0.0, -(pR + pH1)))
    if SC > 0:
        o3 = ((((ARC3D2(s, D=D / 2.0, D2=D / 2.0, R=pR, A=180.0)).rotateZ(90.0)).rotateX(90.0)).rotateZ(90.0)).translate((pL1 + pR, 0.0, -(R2 + pH1)))
        o4 = (CYLINDER(s, R=D / 2.0, H=pH2, O=0.0)).translate((L, -R2, -(pR + pH1)))
        cpY = -R2
    else:
        o3 = ((((ARC3D2(s, D=D / 2.0, D2=D / 2.0, R=pR, A=180.0)).rotateZ(90.0)).rotateX(90.0)).rotateZ(-90.0)).translate((pL1 + pR, 0.0, -(R2 + pH1)))
        o4 = (CYLINDER(s, R=D / 2.0, H=pH2, O=0.0)).translate((L, R2, -(pR + pH1)))
        cpY = R2
    o0.uniteWith(o1)
    o1.erase()
    o0.uniteWith(o2)
    o2.erase()
    o0.uniteWith(o3)
    o3.erase()
    o0.uniteWith(o4)
    o4.erase()
    OF = getThickness(D=D, OF=OF)
    if OF > 0.0:
        O1 = getInsideDiameter(D=D, OF=OF, Ever=1)
        s0 = (CYLINDER(s, R=O1 / 2.0, H=pL1, O=0.0)).rotateY(90.0)
        s1 = (((ARC3D2(s, D=O1 / 2.0, D2=O1 / 2.0, R=pR, A=90.0)).rotateZ(180.0)).rotateX(90.0)).translate((pL1 + pR, 0.0, 0.0))
        s2 = (CYLINDER(s, R=O1 / 2.0, H=pH1, O=0.0)).translate((pL1 + pR, 0.0, -(pR + pH1)))
        if SC > 0:
            s3 = ((((ARC3D2(s, D=O1 / 2.0, D2=O1 / 2.0, R=pR, A=180.0)).rotateZ(90.0)).rotateX(90.0)).rotateZ(90.0)).translate((pL1 + pR, 0.0, -(R2 + pH1)))
            s4 = (CYLINDER(s, R=O1 / 2.0, H=pH2, O=0.0)).translate((L, -R2, -(pR + pH1)))
        else:
            s3 = ((((ARC3D2(s, D=O1 / 2.0, D2=O1 / 2.0, R=pR, A=180.0)).rotateZ(90.0)).rotateX(90.0)).rotateZ(-90.0)).translate((pL1 + pR, 0.0, -(R2 + pH1)))
            s4 = (CYLINDER(s, R=O1 / 2.0, H=pH2, O=0.0)).translate((L, R2, -(pR + pH1)))
        s0.uniteWith(s1)
        s1.erase()
        s0.uniteWith(s2)
        s2.erase()
        s0.uniteWith(s3)
        s3.erase()
        s0.uniteWith(s4)
        s4.erase()
        o0.subtractFrom(s0)
        s0.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
    s.setPoint((L, cpY, H2 - H1), (0.0, 0.0, 1.0), 0.0)
