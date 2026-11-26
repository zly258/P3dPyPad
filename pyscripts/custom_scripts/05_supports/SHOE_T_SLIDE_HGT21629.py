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
          TooltipShort=u"T型焊接滑动管托 (HG/T 21629 A1)",
          TooltipLong=u"HG/T 21629-2021 A1 T型焊接滑动管托，含弧口纵向立板、两侧三角加强筋与滑动底板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"T型焊接滑动管托主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支撑管道外径 D (mm)")
@param(H1=LENGTH, TooltipShort=u"管托高度", TooltipLong=u"管底至滑动底板下表面净高 H1 (mm)", Ask4Dist=True)
@param(L1=LENGTH, TooltipShort=u"管托长度", TooltipLong=u"管托沿管道轴向长度 L1 (mm)", Ask4Dist=True)
@param(B1=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"滑动底板宽度 B1 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"钢板厚度", TooltipLong=u"立板、加强筋及底板厚度 (mm)")
def SHOE_T_SLIDE_HGT21629(
    s,
    D=114.3,
    H1=100.0,
    L1=300.0,
    B1=120.0,
    T_PLT=10.0,
    ID=u"SHOE_T_SLIDE_HGT21629",
    **kw
):
    u"""T型焊接滑动管托 (原点在管道中心线, 管道沿 X 轴, 支座向 -Z 延伸)。"""
    D = max(25.0, float(D))
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
    T_PLT = max(6.0, float(T_PLT))

    z_bot = -(r_p + H1)
    z_base_top = z_bot + T_PLT

    # 1. 干净平板滑动底板
    o_main = CORNERBOX(s, L=L1, W=B1, H=T_PLT).translate((-L1 / 2.0, -B1 / 2.0, z_bot))

    # 2. 中央纵向立板（顶部按管外径弧面裁切，直达管底）
    web_h = H1 + r_p * 0.35
    o_web = CORNERBOX(s, L=L1, W=T_PLT, H=web_h).translate((-L1 / 2.0, -T_PLT / 2.0, z_base_top - 1.0))
    o_pcut = CYLINDER(s, R=r_p, H=L1 + 40.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 20.0), 0.0, 0.0))
    o_web.subtractFrom(o_pcut)
    o_pcut.erase()
    o_main.uniteWith(o_web)
    o_web.erase()

    # 3. 前后双横向加强筋（带管底弧口）
    rib_w = max(T_PLT * 3.0, min(B1 * 0.82, D * 0.78))
    rib_h = H1 + r_p * 0.45
    rib_x_off = max(T_PLT * 1.5, L1 / 2.0 - T_PLT * 2.5)
    for sx in (-1.0, 1.0):
        rx = sx * rib_x_off - T_PLT / 2.0
        o_rib = CORNERBOX(s, L=T_PLT, W=rib_w, H=rib_h).translate((rx, -rib_w / 2.0, z_base_top - 1.0))
        o_rcut = CYLINDER(s, R=r_p, H=L1 + 40.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 20.0), 0.0, 0.0))
        o_rib.subtractFrom(o_rcut)
        o_rcut.erase()
        o_main.uniteWith(o_rib)
        o_rib.erase()

    # 4. 中部两侧低矮侧向加劲肋
    gus_w = (B1 - T_PLT) * 0.42
    gus_h = min(H1 * 0.65, max(25.0, H1 - T_PLT - 10.0))
    for sy in (-1.0, 1.0):
        gy = (T_PLT / 2.0 - 1.0) if sy > 0 else -(T_PLT / 2.0 - 1.0 + gus_w)
        o_gus = CORNERBOX(s, L=T_PLT, W=gus_w, H=gus_h).translate((-T_PLT / 2.0, gy, z_base_top - 1.0))
        o_main.uniteWith(o_gus)
        o_gus.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H1', (0.0, 0.0, -r_p), (0.0, 0.0, z_bot))
    s.setLinearDimension('L1', (-L1 / 2.0, 0.0, z_bot), (L1 / 2.0, 0.0, z_bot))
    s.setLinearDimension('B1', (0.0, -B1 / 2.0, z_bot), (0.0, B1 / 2.0, z_bot))
