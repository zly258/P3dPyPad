# -*- coding: utf-8 -*-
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
from varmain.supportssub.csgdsub.csgd_util import *


@activate(Group="Support", TooltipShort="CSGD001", TooltipLong="CSGD001", LengthUnit="mm", Ports=1)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort="D")
@param(L=LENGTH, TooltipShort="L")
@param(OF=LENGTH, TooltipShort="OF")
@param(IL=LENGTH, TooltipShort="IL")
@param(ID=STRING, TooltipShort="组件标识")
def CSGD001(s, D=114.3, L=500.0, OF=-1.0, IL=0.0, ID='CSGD001', **kw):
    if L <= 0.0:
        L = defaultPipeLength
    OF = getThickness(D=D, OF=OF, Ever=None)
    DI = getInsideDiameter(D=D, OF=OF)
    oTH = ((CYLINDER(s, R=D / 2.0, H=L + IL, O=DI / 2.0)).rotateY(90.0)).translate((-IL, 0.0, 0.0))
    if OF > 0.0:
        oTE = ((CYLINDER(s, R=D / 2.0, H=OF, O=0.0)).rotateY(-90.0)).translate((L, 0.0, 0.0))
        oTH.uniteWith(oTE)
        oTE.erase()
    oTH.rotateY(90)
    CSGCutOut(s, oTH, D, kw)
    oTH.rotateY(-90)
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 0.0)
    s.setLinearDimension('L', (0, 0, 0), (L, 0, 0))
