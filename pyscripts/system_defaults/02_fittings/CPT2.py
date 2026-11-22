# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *


@activate(Group="Tee", TooltipShort="Built-in CPT2", TooltipLong="Built-in CPT2 (Decompiled from varmain/teesub/cpt2sub/cpt2.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(R=LENGTH, TooltipShort="R")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CPT2(s, D=114.3, R=105.0, OF=-1.0, ID='CPT2', **kw):
    R1 = D / 2.0
    if R < R1:
        R = R1
    o0 = ARC3D(s, D=R1, R=R, A=90.0)
    o1 = ARC3D(s, D=R1, R=R, A=90.0).rotateY(180.0)
    o0.uniteWith(o1)
    o1.erase()
    Drill = 1
    if OF > 0.0:
        hR1 = R1 - OF
    else:
        if OF == -1:
            hR1 = CON_OF_DIV(R1)
        else:
            Drill = None
    if Drill:
        o3 = ARC3D(s, D=hR1, R=R, A=90.0)
        o4 = ARC3D(s, D=hR1, R=R, A=90.0).rotateY(180.0)
        o3.uniteWith(o4)
        o4.erase()
        o0.subtractFrom(o3)
        o3.erase()
    s.setPoint((-R, 0, 0), (-1, 0, 0))
    s.setPoint((R, 0, 0), (1, 0, 0))
    s.setPoint((0, R, 0), (0, 1, 0))
