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
          TooltipShort=u"金属八角环垫 RTJ (ASME B16.20 R型)",
          TooltipLong=u"ASME B16.20 高压法兰金属八角形环垫(RTJ)，精准还原上下双倒角八角截面环体",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"金属八角环垫 RTJ 主要几何尺寸参数")
@param(P_PITCH=LENGTH, TooltipShort=u"节圆直径", TooltipLong=u"环垫中径/节圆直径 P (mm)")
@param(A_WIDTH=LENGTH, TooltipShort=u"环宽", TooltipLong=u"八角截面宽度 A (mm)")
@param(H_TOT=LENGTH, TooltipShort=u"环高", TooltipLong=u"八角截面总高度 H (mm)", Ask4Dist=True)
@param(C_CHAMFER=LENGTH, TooltipShort=u"倒角宽度", TooltipLong=u"双侧密封斜面轴向高度/径向倒角量 (mm)")
def GASKET_RTJ_OCTAGONAL(
    s,
    P_PITCH=149.23,
    A_WIDTH=11.13,
    H_TOT=15.88,
    C_CHAMFER=4.0,
    ID=u"GASKET_RTJ_OCTAGONAL",
    **kw
):
    u"""ASME B16.20 金属八角环垫 RTJ (双倒角八角截面环，Port 1 在 X=0, Port 2 在 X=H_TOT)。"""
    P_PITCH = max(40.0, float(P_PITCH))
    A_WIDTH = max(6.0, min(P_PITCH * 0.35, float(A_WIDTH)))
    H_TOT = float(H_TOT)
    if H_TOT < 1.0:
        H_TOT = 1.0
    C_CHAMFER = max(1.5, min(H_TOT * 0.38, A_WIDTH * 0.32, float(C_CHAMFER)))

    r_mid = P_PITCH * 0.5
    r_out = r_mid + A_WIDTH * 0.5
    r_in = max(5.0, r_mid - A_WIDTH * 0.5)
    r_ch = C_CHAMFER * 0.65
    h_mid = max(2.0, H_TOT - 2.0 * C_CHAMFER)

    # 1. 外轮廓（前端倒角圆台 + 中部直柱 + 后端倒角圆台，均微搭接 0.1mm 稳定融合）
    o_main = CONE(s, R1=r_out - r_ch, R2=r_out, H=C_CHAMFER + 0.1, E=0.0).rotateY(90.0)
    o_mid = CYLINDER(s, R=r_out, H=h_mid + 0.2, O=0.0).rotateY(90.0).translate((C_CHAMFER - 0.1, 0.0, 0.0))
    o_back = CONE(s, R1=r_out, R2=r_out - r_ch, H=C_CHAMFER + 0.1, E=0.0).rotateY(90.0).translate((C_CHAMFER + h_mid - 0.1, 0.0, 0.0))
    o_main.uniteWith(o_mid)
    o_mid.erase()
    o_main.uniteWith(o_back)
    o_back.erase()

    # 2. 分别减去贯穿主内孔及前/后双内倒角（逐个单原语差集确保 100% 贯通）
    o_bore = CYLINDER(s, R=r_in, H=H_TOT + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    o_cf = CONE(s, R1=r_in + r_ch + 0.5, R2=r_in - 0.1, H=C_CHAMFER + 0.6, E=0.0).rotateY(90.0).translate((-0.5, 0.0, 0.0))
    o_main.subtractFrom(o_cf)
    o_cf.erase()

    o_cb = CONE(s, R1=r_in - 0.1, R2=r_in + r_ch + 0.5, H=C_CHAMFER + 0.6, E=0.0).rotateY(90.0).translate((H_TOT - C_CHAMFER - 0.1, 0.0, 0.0))
    o_main.subtractFrom(o_cb)
    o_cb.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H_TOT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOT', (0.0, 0.0, 0.0), (H_TOT, 0.0, 0.0))
