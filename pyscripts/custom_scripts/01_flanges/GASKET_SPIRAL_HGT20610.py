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
          TooltipShort=u"金属缠绕垫片 (HG/T 20610 D型 PN16 RF)",
          TooltipLong=u"HG/T 20610-2009 带内外环金属缠绕垫片(D型)，内外金属定位环与凸出缠绕密封带三层清晰台阶",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"金属缠绕垫片主要几何尺寸参数")
@param(D1=LENGTH, TooltipShort=u"内环内径", TooltipLong=u"内加强环内径 D1 (mm)")
@param(D2=LENGTH, TooltipShort=u"缠绕带内径", TooltipLong=u"缠绕密封带内径 D2 (mm)")
@param(D3=LENGTH, TooltipShort=u"缠绕带外径", TooltipLong=u"缠绕密封带外径 D3 (mm)")
@param(D4=LENGTH, TooltipShort=u"外环外径", TooltipLong=u"外定位环外径 D4 (mm)")
@param(T_WIND=LENGTH, TooltipShort=u"缠绕带厚度", TooltipLong=u"缠绕密封带厚度 T (mm)", Ask4Dist=True)
@param(T_RING=LENGTH, TooltipShort=u"定位环厚度", TooltipLong=u"内外定位环厚度 Tr (mm)")
def GASKET_SPIRAL_HGT20610(
    s,
    D1=114.0,
    D2=127.0,
    D3=149.0,
    D4=162.0,
    T_WIND=4.5,
    T_RING=3.2,
    ID=u"GASKET_SPIRAL_HGT20610",
    **kw
):
    u"""HG/T 20610 D型金属缠绕垫片 (三层清晰台阶，Port 1 在 X=0, Port 2 在 X=T_WIND)。"""
    D1 = max(12.0, float(D1))
    D2 = max(D1 + 4.0, float(D2))
    D3 = max(D2 + 8.0, float(D3))
    D4 = max(D3 + 6.0, float(D4))
    T_WIND = float(T_WIND)
    if T_WIND < 1.0:
        T_WIND = 1.0
    T_RING = max(1.5, min(T_WIND - 0.6, float(T_RING)))

    x_ring = (T_WIND - T_RING) * 0.5
    # 1. 中间缠绕密封带 (凸出台阶)
    o_main = CYLINDER(s, R=D3 * 0.5, H=T_WIND, O=D2 * 0.5).rotateY(90.0)

    # 2. 内加强环
    o_in = CYLINDER(s, R=D2 * 0.5 + 0.25, H=T_RING, O=D1 * 0.5).rotateY(90.0).translate((x_ring, 0.0, 0.0))
    o_main.uniteWith(o_in)
    o_in.erase()

    # 3. 外定位环
    o_out = CYLINDER(s, R=D4 * 0.5, H=T_RING, O=D3 * 0.5 - 0.25).rotateY(90.0).translate((x_ring, 0.0, 0.0))
    o_main.uniteWith(o_out)
    o_out.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((T_WIND, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('T_WIND', (0.0, 0.0, 0.0), (T_WIND, 0.0, 0.0))
