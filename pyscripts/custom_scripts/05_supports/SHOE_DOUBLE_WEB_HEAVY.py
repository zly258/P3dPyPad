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

@activate(Group="Support",
          TooltipShort=u"双立板重型焊接滑动管托 (HG/T 21629 A2)",
          TooltipLong=u"双立板重型焊接滑动管托，含双平行马鞍弧口立板、三道横向加强筋、外侧加劲肋与重型底板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"双立板重型焊接滑动管托主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支撑管道外径 D (mm)")
@param(H1=LENGTH, TooltipShort=u"管托高度", TooltipLong=u"管底至滑动底板下表面净高 H1 (mm)", Ask4Dist=True)
@param(L1=LENGTH, TooltipShort=u"管托长度", TooltipLong=u"管托沿管道轴向长度 L1 (mm)", Ask4Dist=True)
@param(B1=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"重型底板宽度 B1 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"钢板厚度", TooltipLong=u"立板、加强筋及底板厚度 (mm)")
def SHOE_DOUBLE_WEB_HEAVY(
    s,
    D=219.1,
    H1=150.0,
    L1=400.0,
    B1=220.0,
    T_PLT=12.0,
    ID=u"SHOE_DOUBLE_WEB_HEAVY",
    **kw
):
    u"""双立板重型焊接滑动管托 (原点在管道中心线, 管道沿 X 轴, 支座向 -Z 延伸)。"""
    D = max(80.0, float(D))
    r_p = D / 2.0
    H1 = float(H1)
    if H1 < 1.0:
        H1 = 1.0
    L1 = float(L1)
    if L1 < 1.0:
        L1 = 1.0
    B1 = float(B1)
    if B1 < 1.0:
        B1 = 1.0
    T_PLT = max(8.0, float(T_PLT))

    z_bot = -(r_p + H1)
    z_base_top = z_bot + T_PLT
    web_sp = max(T_PLT * 4.0, min(B1 * 0.54, D * 0.56))

    # 1. 重型底板
    o_main = CORNERBOX(s, L=L1, W=B1, H=T_PLT).translate((-L1 / 2.0, -B1 / 2.0, z_bot))

    # 2. 双平行纵向立板（顶部沿管道弧面裁切，呈现马鞍弧口）
    web_top_z = -math.sqrt(max(1.0, r_p * r_p - (web_sp / 2.0) ** 2)) + 16.0
    web_h = max(30.0, web_top_z - (z_base_top - 1.0))
    for sy in (-1.0, 1.0):
        wy = sy * (web_sp / 2.0) - T_PLT / 2.0
        o_web = CORNERBOX(s, L=L1, W=T_PLT, H=web_h).translate((-L1 / 2.0, wy, z_base_top - 1.0))
        o_pcut = CYLINDER(s, R=r_p, H=L1 + 40.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 20.0), 0.0, 0.0))
        o_web.subtractFrom(o_pcut)
        o_pcut.erase()
        o_main.uniteWith(o_web)
        o_web.erase()

    # 3. 三道横向加强筋（贯通双立板内外，顶面带管弧口）
    rib_w = min(B1 * 0.92, web_sp + T_PLT * 5.0)
    rib_h = max(30.0, (-r_p + r_p * 0.38) - (z_base_top - 1.0))
    rib_xs = (-L1 * 0.38, 0.0, L1 * 0.38)
    for rx_c in rib_xs:
        o_rib = CORNERBOX(s, L=T_PLT, W=rib_w, H=rib_h).translate((rx_c - T_PLT / 2.0, -rib_w / 2.0, z_base_top - 1.0))
        o_rcut = CYLINDER(s, R=r_p, H=L1 + 40.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 20.0), 0.0, 0.0))
        o_rib.subtractFrom(o_rcut)
        o_rcut.erase()
        o_main.uniteWith(o_rib)
        o_rib.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H1', (0.0, 0.0, -r_p), (0.0, 0.0, z_bot))
    s.setLinearDimension('L1', (-L1 / 2.0, 0.0, z_bot), (L1 / 2.0, 0.0, z_bot))
    s.setLinearDimension('B1', (0.0, -B1 / 2.0, z_bot), (0.0, B1 / 2.0, z_bot))
