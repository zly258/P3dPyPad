# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.flangesub.cpf_util import *


@activate(Group="ManHandWay", TooltipShort="Nozzle, handway", TooltipLong="Nozzle, handway (Decompiled from varmain/flangesub/manhole.pyc)", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(DO=LENGTH, TooltipShort="DO")
@param(L=LENGTH, TooltipShort="L")
@param(B=LENGTH, TooltipShort="B")
@param(W=LENGTH, TooltipShort="W")
@param(A=ANGLE, TooltipShort="A")
@param(OF=LENGTH, TooltipShort="OF")
@param(ID=STRING, TooltipShort="组件标识")
def CMANHOLE(s, D=0.54, DO=2.5, L=100.0, B=0.28, W=0.0, A=90.0, OF=-1.0, ID='CMANHOLE', **kw):
    if (L <= 0.0) or (L <= B):
        L = (B * 3.0) + 0.0001
    OF = getThickness(D=D, OF=OF)
    B2 = B * 0.05
    o1 = CMANHOLEsub(s, D=D, DO=DO, L=L, B=B, B2=B2, OF=OF)
    if W > 0.0:
        o1.translate((0.0, W / 2, 0.0))
        o2 = CMANHOLEsub(s, D=D, DO=DO, L=L, B=B, B2=B2, OF=OF).translate((0.0, -(W / 2), 0.0))
        o3 = (CORNERBOX(s, L=L - B, W=W, H=D)).translate((0.0, -(W / 2.0), -(D / 2.0)))
        o4 = CORNERBOX(s, L=B, W=W, H=DO).translate((L - B, -(W / 2.0), -(DO / 2.0)))
        o5 = (CORNERBOX(s, L=B2, W=W, H=DO - (B2 * 2))).translate(((L - B) - B2, -(W / 2.0), (-(DO / 2.0)) - B2))
        o6 = CORNERBOX(s, L=B, W=W, H=DO).translate((((L - B) - B2) - B, -(W / 2.0), -(DO / 2.0)))
        o1.uniteWith(o2)
        o2.erase()
        o1.uniteWith(o3)
        o3.erase()
        o1.uniteWith(o4)
        o4.erase()
        o1.uniteWith(o5)
        o5.erase()
        o1.uniteWith(o6)
        o6.erase()
        if OF > 0.0:
            oC1 = ((CYLINDER(s, R=(D / 2.0) - OF, H=L - B, O=0)).rotateY(90)).translate((0.0, W / 2, 0.0))
            oC2 = (CORNERBOX(s, L=L - B, W=W, H=D - (OF * 2.0))).translate((0.0, -(W / 2.0), -((D / 2.0) - OF)))
            oC3 = ((CYLINDER(s, R=(D / 2.0) - OF, H=L - B, O=0)).rotateY(90)).translate((0.0, -(W / 2), 0.0))
            oC1.uniteWith(oC2)
            oC2.erase()
            oC1.uniteWith(oC3)
            oC3.erase()
            o1.subtractFrom(oC1)
            oC1.erase()
        o1.rotateX(A)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)


def CMANHOLEsub(s, D=114.3, DO=220.0, L=100.0, B=22.0, B2=2.0, OF=0, ID='CMANHOLEsub', **kw):
    o1 = (CYLINDER(s, R=D / 2.0, H=L - B, O=0)).rotateY(90)
    o2 = ((CYLINDER(s, R=DO / 2.0, H=B, O=0)).rotateY(-90)).translate((L, 0, 0))
    o3 = ((CYLINDER(s, R=(DO / 2.0) - B2, H=B2, O=0)).rotateY(-90)).translate((L - B2, 0, 0))
    o4 = ((CYLINDER(s, R=DO / 2.0, H=B, O=0)).rotateY(-90)).translate(((L - B) - B2, 0, 0))
    o1.uniteWith(o2)
    o2.erase()
    o1.uniteWith(o3)
    o3.erase()
    o1.uniteWith(o4)
    o4.erase()
    if OF > 0.0:
        oC = (CYLINDER(s, R=(D / 2.0) - OF, H=L - B, O=0)).rotateY(90)
        o1.subtractFrom(oC)
        oC.erase()
    return o1
