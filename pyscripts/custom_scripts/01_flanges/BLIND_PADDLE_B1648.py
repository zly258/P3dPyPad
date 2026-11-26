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

@activate(Group="Blind",
          TooltipShort=u"插板盲板 (ASME B16.48 Paddle Blind)",
          TooltipLong=u"ASME B16.48 插板盲板(Paddle Blind)，由实心盲板盘、长操作手柄与端部圆头挂孔特征组成",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"插板盲板主要几何尺寸参数")
@param(D_OUT=LENGTH, TooltipShort=u"盲板外径", TooltipLong=u"实心盲板盘外径 O (mm)")
@param(T_DISC=LENGTH, TooltipShort=u"盲板厚度", TooltipLong=u"盲板盘厚度 T (mm)", Ask4Dist=True)
@param(L_HANDLE=LENGTH, TooltipShort=u"手柄总伸长", TooltipLong=u"从盘中心至手柄端部圆心长度 L (mm)")
@param(W_HANDLE=LENGTH, TooltipShort=u"手柄宽度", TooltipLong=u"操作手柄宽度 W (mm)")
@param(D_HOLE=LENGTH, TooltipShort=u"端部挂孔径", TooltipLong=u"手柄端部标识/挂孔直径 (mm)")
def BLIND_PADDLE_B1648(
    s,
    D_OUT=174.6,
    T_DISC=12.7,
    L_HANDLE=245.0,
    W_HANDLE=38.0,
    D_HOLE=16.0,
    ID=u"BLIND_PADDLE_B1648",
    **kw
):
    u"""ASME B16.48 插板盲板 (Port 1 在 X=0, Port 2 在 X=T_DISC, 手柄沿 +Z 延伸)。"""
    D_OUT = max(50.0, float(D_OUT))
    T_DISC = float(T_DISC)
    if T_DISC < 1.0:
        T_DISC = 1.0
    W_HANDLE = max(16.0, min(D_OUT * 0.45, float(W_HANDLE)))
    L_HANDLE = max(D_OUT * 0.75 + 40.0, float(L_HANDLE))
    D_HOLE = max(6.0, min(W_HANDLE * 0.55, float(D_HOLE)))

    # 1. 实心盲板盘 (X: 0 -> T_DISC)
    o_main = CYLINDER(s, R=D_OUT / 2.0, H=T_DISC, O=0.0).rotateY(90.0)

    # 2. 长手柄直段 (从 Z = D_OUT/2 - 12 延伸至 L_HANDLE)
    z_start = D_OUT * 0.5 - 12.0
    h_len = max(20.0, L_HANDLE - z_start)
    o_bar = BOX(s, L=W_HANDLE, W=h_len, H=T_DISC).translate((T_DISC * 0.5, 0.0, z_start + h_len * 0.5))
    o_main.uniteWith(o_bar)
    o_bar.erase()

    # 3. 端部圆头与挂孔特征
    o_tip = CYLINDER(s, R=W_HANDLE * 0.5, H=T_DISC, O=0.0).rotateY(90.0).translate((0.0, 0.0, L_HANDLE))
    o_main.uniteWith(o_tip)
    o_tip.erase()

    o_hole = CYLINDER(s, R=D_HOLE * 0.5, H=T_DISC + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, L_HANDLE))
    o_main.subtractFrom(o_hole)
    o_hole.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((T_DISC, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('T_DISC', (0.0, 0.0, 0.0), (T_DISC, 0.0, 0.0))
