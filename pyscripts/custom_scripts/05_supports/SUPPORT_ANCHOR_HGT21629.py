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
          TooltipShort=u"四向固定管架 (HG/T 21629 D1)",
          TooltipLong=u"HG/T 21629-2021 D1 四向固定管架，含重型双抱箍、双立板焊鞍、扩展锚固底板与四向止推挡块",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"四向固定管架主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被固定管道外径 D (mm)")
@param(H1=LENGTH, TooltipShort=u"管架高度", TooltipLong=u"管底至锚固底板底面高度 H1 (mm)", Ask4Dist=True)
@param(L1=LENGTH, TooltipShort=u"底板长度", TooltipLong=u"锚固底板沿管道轴向长度 L1 (mm)", Ask4Dist=True)
@param(B1=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"锚固底板宽度 B1 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"钢板厚度", TooltipLong=u"底板、立板及止推挡块厚度 (mm)")
@param(CLAMP_W=LENGTH, TooltipShort=u"管夹宽度", TooltipLong=u"固定抱箍扁钢宽度 (mm)")
def SUPPORT_ANCHOR_HGT21629(
    s,
    D=168.3,
    H1=120.0,
    L1=340.0,
    B1=220.0,
    T_PLT=12.0,
    CLAMP_W=45.0,
    ID=u"SUPPORT_ANCHOR_HGT21629",
    **kw
):
    u"""四向固定管架 (原点在管道中心线, 管道沿 X 轴, 四向止推锁定)。"""
    D = max(32.0, float(D))
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
    CLAMP_W = max(25.0, float(CLAMP_W))
    clamp_t = max(6.0, T_PLT * 0.75)
    bolt_d = max(12.0, min(20.0, CLAMP_W * 0.35))

    z_bot = -(r_p + H1)
    z_base_top = z_bot + T_PLT
    r_out = r_p + clamp_t
    shoe_l = L1 * 0.72
    web_sp = max(T_PLT * 3.0, min(B1 * 0.48, D * 0.55))

    # 1. 重型扩展锚固底板
    o_main = CORNERBOX(s, L=L1, W=B1, H=T_PLT).translate((-L1 / 2.0, -B1 / 2.0, z_bot))

    # 2. 双纵向承重立板
    web_top_z = -math.sqrt(max(1.0, r_p * r_p - (web_sp / 2.0) ** 2)) + clamp_t
    web_h = max(30.0, (web_top_z + 16.0) - (z_base_top - 1.0))
    for sy in (-1.0, 1.0):
        wy = sy * (web_sp / 2.0) - T_PLT / 2.0
        o_web = CORNERBOX(s, L=shoe_l, W=T_PLT, H=web_h).translate((-shoe_l / 2.0, wy, z_base_top - 1.0))
        o_pcut = CYLINDER(s, R=r_p, H=L1 + 40.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 20.0), 0.0, 0.0))
        o_web.subtractFrom(o_pcut)
        o_pcut.erase()
        o_main.uniteWith(o_web)
        o_web.erase()

    # 3. 四向止推挡块（±X 轴向重型端挡板 + ±Y 侧向止推支撑筋）
    stop_h = max(36.0, min(H1 * 0.68, H1 - T_PLT - 12.0))
    # ±X 轴向止推挡块（紧顶双立板两端并带斜撑肋）
    x_stop_w = web_sp + T_PLT * 3.0
    for sx in (-1.0, 1.0):
        xs = sx * (shoe_l / 2.0) if sx > 0 else -(shoe_l / 2.0 + T_PLT)
        o_xstop = CORNERBOX(s, L=T_PLT, W=x_stop_w, H=stop_h).translate((xs, -x_stop_w / 2.0, z_base_top - 1.0))
        o_main.uniteWith(o_xstop)
        o_xstop.erase()
        # 轴向挡块外侧加强筋
        gus_l = (L1 - shoe_l) / 2.0 - T_PLT
        if gus_l > 8.0:
            gx = (shoe_l / 2.0 + T_PLT - 1.0) if sx > 0 else -(L1 / 2.0)
            for sy in (-1.0, 1.0):
                gy = sy * (web_sp * 0.35) - T_PLT / 2.0
                o_xg = CORNERBOX(s, L=gus_l + 1.0, W=T_PLT, H=stop_h * 0.78).translate((gx, gy, z_base_top - 1.0))
                o_main.uniteWith(o_xg)
                o_xg.erase()

    # ±Y 侧向止推挡块（紧抵立板外侧延伸至底板边沿）
    y_gus_w = (B1 - web_sp - T_PLT) / 2.0
    for sy in (-1.0, 1.0):
        gy = (web_sp / 2.0 + T_PLT / 2.0 - 1.0) if sy > 0 else -(B1 / 2.0)
        for sx in (-1.0, 0.0, 1.0):
            gx = sx * (shoe_l * 0.34) - T_PLT / 2.0
            o_yg = CORNERBOX(s, L=T_PLT, W=y_gus_w + 1.0, H=stop_h * 0.85).translate((gx, gy, z_base_top - 1.0))
            o_main.uniteWith(o_yg)
            o_yg.erase()

    # 4. 双重型抱箍管夹（紧固锁定管道）
    clamp_sp = shoe_l * 0.62
    ear_len = max(34.0, bolt_d * 2.2)
    ear_gap = max(6.0, clamp_t * 0.8)
    for sx in (-1.0, 1.0):
        cx = sx * (clamp_sp / 2.0)
        o_ring = CYLINDER(s, R=r_out, H=CLAMP_W, O=r_p).rotateY(90.0).translate((cx - CLAMP_W / 2.0, 0.0, 0.0))
        o_slot = CORNERBOX(s, L=CLAMP_W + 6.0, W=r_out * 2.4, H=ear_gap).translate(
            (cx - CLAMP_W / 2.0 - 3.0, -r_out * 1.2, -ear_gap / 2.0))
        o_ring.subtractFrom(o_slot)
        o_slot.erase()
        o_main.uniteWith(o_ring)
        o_ring.erase()
        for sy in (-1.0, 1.0):
            ey = (r_p + clamp_t * 0.3) if sy > 0 else -(r_p + clamp_t * 0.3 + ear_len)
            for sz in (-1.0, 1.0):
                ez = (ear_gap / 2.0) if sz > 0 else -(ear_gap / 2.0 + clamp_t)
                o_ear = CORNERBOX(s, L=CLAMP_W, W=ear_len, H=clamp_t).translate((cx - CLAMP_W / 2.0, ey, ez))
                o_main.uniteWith(o_ear)
                o_ear.erase()
            by = sy * (r_out + ear_len * 0.52)
            bh = ear_gap + clamp_t * 2.0 + bolt_d * 1.6
            o_bolt = CYLINDER(s, R=bolt_d * 0.5, H=bh, O=0.0).translate((cx, by, -bh / 2.0))
            o_main.uniteWith(o_bolt)
            o_bolt.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H1', (0.0, 0.0, -r_p), (0.0, 0.0, z_bot))
    s.setLinearDimension('L1', (-L1 / 2.0, 0.0, z_bot), (L1 / 2.0, 0.0, z_bot))
    s.setLinearDimension('B1', (0.0, -B1 / 2.0, z_bot), (0.0, B1 / 2.0, z_bot))
