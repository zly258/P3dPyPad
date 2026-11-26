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
          TooltipShort=u"大管径弧形鞍式管托 (120° 护板)",
          TooltipLong=u"大管径弧形鞍式管托，含120°弧形贴管护板、双横向鞍形肋板、中央纵肋与重型底板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"大管径弧形鞍式管托主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支撑大口径管道外径 D (mm)")
@param(H1=LENGTH, TooltipShort=u"管托高度", TooltipLong=u"管底至底板下表面净高 H1 (mm)", Ask4Dist=True)
@param(L1=LENGTH, TooltipShort=u"管托长度", TooltipLong=u"鞍式管托轴向长度 L1 (mm)", Ask4Dist=True)
@param(B1=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"重型底板宽度 B1 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"肋板底板厚", TooltipLong=u"横向肋板与底板厚度 (mm)")
@param(T_SAD=LENGTH, TooltipShort=u"弧形护板厚", TooltipLong=u"120°弧形护板厚度 (mm)")
def SHOE_SADDLE_LARGE(
    s,
    D=406.4,
    H1=150.0,
    L1=450.0,
    B1=380.0,
    T_PLT=14.0,
    T_SAD=10.0,
    ID=u"SHOE_SADDLE_LARGE",
    **kw
):
    u"""大管径弧形鞍式管托 (原点在管道中心线, 管道沿 X 轴, 支座向 -Z 延伸)。"""
    D = max(150.0, float(D))
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
    T_PLT = max(10.0, float(T_PLT))
    T_SAD = max(6.0, float(T_SAD))

    z_bot = -(r_p + H1)
    z_base_top = z_bot + T_PLT
    r_sad_out = r_p + T_SAD
    # 120° 弧形护板：关于 -Z 对称，半张角 60°，上沿 z = -r_p * cos(60°) = -0.5 * r_p
    z_cut_120 = -r_p * 0.50
    sad_half_w = r_sad_out * math.sin(math.radians(60.0))

    # 1. 重型滑动底板
    o_main = CORNERBOX(s, L=L1, W=B1, H=T_PLT).translate((-L1 / 2.0, -B1 / 2.0, z_bot))

    # 2. 120° 弧形贴管护板（轴向略长于两肋板，完整贴合管底）
    o_sad = CYLINDER(s, R=r_sad_out, H=L1, O=r_p).rotateY(90.0).translate((-L1 / 2.0, 0.0, 0.0))
    o_top_cut = CORNERBOX(s, L=L1 + 40.0, W=D * 2.0, H=D * 1.5).translate((-(L1 / 2.0 + 20.0), -D, z_cut_120))
    o_sad.subtractFrom(o_top_cut)
    o_top_cut.erase()

    # 3. 双横向大鞍形肋板（两端偏内布置，顶面承托120°护板）
    rib_w = min(B1 * 0.96, sad_half_w * 2.0 + 10.0)
    rib_h = max(40.0, (z_cut_120 + 2.0) - (z_base_top - 1.0))
    rib_x_off = max(T_PLT * 2.0, L1 * 0.36)
    for sx in (-1.0, 1.0):
        rx = sx * rib_x_off - T_PLT / 2.0
        o_rib = CORNERBOX(s, L=T_PLT, W=rib_w, H=rib_h).translate((rx, -rib_w / 2.0, z_base_top - 1.0))
        o_pcut = CYLINDER(s, R=r_p + 1.0, H=L1 + 40.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 20.0), 0.0, 0.0))
        o_rib.subtractFrom(o_pcut)
        o_pcut.erase()
        o_main.uniteWith(o_rib)
        o_rib.erase()

    # 4. 三道纵向加劲腹板（中央1道 + 两侧各1道），将弧形护板、双横肋与底板连为刚性整体
    for sy in (-1.0, 0.0, 1.0):
        wy = sy * (rib_w * 0.30)
        z_top_local = -math.sqrt(max(1.0, r_sad_out * r_sad_out - wy * wy)) + 6.0
        wh = max(25.0, z_top_local - (z_base_top - 1.0))
        o_web = CORNERBOX(s, L=L1 * 0.86, W=T_PLT, H=wh).translate((-L1 * 0.43, wy - T_PLT / 2.0, z_base_top - 1.0))
        o_pcut2 = CYLINDER(s, R=r_p + 1.0, H=L1 + 40.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 20.0), 0.0, 0.0))
        o_web.subtractFrom(o_pcut2)
        o_pcut2.erase()
        o_main.uniteWith(o_web)
        o_web.erase()

    o_main.uniteWith(o_sad)
    o_sad.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H1', (0.0, 0.0, -r_p), (0.0, 0.0, z_bot))
    s.setLinearDimension('L1', (-L1 / 2.0, 0.0, z_bot), (L1 / 2.0, 0.0, z_bot))
    s.setLinearDimension('B1', (0.0, -B1 / 2.0, z_bot), (0.0, B1 / 2.0, z_bot))
