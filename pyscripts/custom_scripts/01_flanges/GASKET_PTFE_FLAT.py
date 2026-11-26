# -*- coding: utf-8 -*-
import math
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except (NameError, AttributeError):
    pass

from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *

@activate(Group="Flange",
          TooltipShort=u"非金属聚四氟乙烯平垫片 (HG/T 20606 PTFE RF/FF)",
          TooltipLong=u"HG/T 20606-2009 非金属 PTFE/非石棉突面(RF)与全平面(FF)平垫片，结构平整清晰，适配各类中低压法兰",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"非金属平垫片主要几何尺寸参数")
@param(D_IN=LENGTH, TooltipShort=u"垫片内径", TooltipLong=u"平垫片内孔直径 d1 (mm)")
@param(D_OUT=LENGTH, TooltipShort=u"垫片外径", TooltipLong=u"平垫片外径 D (mm)")
@param(T_GSK=LENGTH, TooltipShort=u"垫片厚度", TooltipLong=u"平垫片厚度 δ (mm)", Ask4Dist=True)
def GASKET_PTFE_FLAT(
    s,
    D_IN=115.0,
    D_OUT=162.0,
    T_GSK=3.0,
    ID=u"GASKET_PTFE_FLAT",
    **kw
):
    u"""HG/T 20606 非金属平垫片 (Port 1 在 X=0, Port 2 在 X=T_GSK)。"""
    D_IN = max(10.0, float(D_IN))
    D_OUT = max(D_IN + 12.0, float(D_OUT))
    T_GSK = float(T_GSK)
    if T_GSK < 1.0:
        T_GSK = 1.0

    o_main = CYLINDER(s, R=D_OUT * 0.5, H=T_GSK, O=D_IN * 0.5).rotateY(90.0)

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((T_GSK, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('T_GSK', (0.0, 0.0, 0.0), (T_GSK, 0.0, 0.0))
