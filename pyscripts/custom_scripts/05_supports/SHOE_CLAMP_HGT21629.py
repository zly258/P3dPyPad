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
          TooltipShort=u"管夹式滑动管托 (HG/T 21629 A4)",
          TooltipLong=u"HG/T 21629-2021 A4 管夹式滑动管托，含双抱箍管夹、紧固双耳螺栓、双纵向立板与滑动底板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"管夹式滑动管托主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支撑管道外径 D (mm)")
@param(H1=LENGTH, TooltipShort=u"管托高度", TooltipLong=u"管底至滑动底板下表面净高 H1 (mm)", Ask4Dist=True)
@param(L1=LENGTH, TooltipShort=u"管托长度", TooltipLong=u"管托沿管道轴向长度 L1 (mm)", Ask4Dist=True)
@param(B1=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"滑动底板宽度 B1 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"钢板厚度", TooltipLong=u"立板与底板钢板厚度 (mm)")
@param(CLAMP_W=LENGTH, TooltipShort=u"管夹宽度", TooltipLong=u"抱箍扁钢宽度 (mm)")
@param(CLAMP_T=LENGTH, TooltipShort=u"管夹厚度", TooltipLong=u"抱箍扁钢厚度 (mm)")
def SHOE_CLAMP_HGT21629(
    s,
    D=168.3,
    H1=100.0,
    L1=300.0,
    B1=140.0,
    T_PLT=10.0,
    CLAMP_W=40.0,
    CLAMP_T=8.0,
    ID=u"SHOE_CLAMP_HGT21629",
    **kw
):
    u"""管夹式滑动管托 (原点在管道中心线, 管道沿 X 轴, 支座向 -Z 延伸)。"""
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
    CLAMP_W = max(22.0, float(CLAMP_W))
    CLAMP_T = max(5.0, float(CLAMP_T))
    bolt_d = max(10.0, min(20.0, CLAMP_W * 0.36))

    r_out = r_p + CLAMP_T
    z_bot = -(r_p + H1)
    z_base_top = z_bot + T_PLT
    clamp_sp = max(CLAMP_W + 25.0, L1 - CLAMP_W - 40.0)
    web_sp = max(T_PLT * 2.8, min(B1 * 0.56, D * 0.55))

    # 1. 滑动底板
    o_main = CORNERBOX(s, L=L1, W=B1, H=T_PLT).translate((-L1 / 2.0, -B1 / 2.0, z_bot))

    # 2. 双纵向立板
    web_top_z = -math.sqrt(max(1.0, r_p * r_p - (web_sp / 2.0) ** 2)) + CLAMP_T * 0.7
    web_h = max(25.0, (web_top_z + 18.0) - (z_base_top - 1.0))
    for sy in (-1.0, 1.0):
        wy = sy * (web_sp / 2.0) - T_PLT / 2.0
        o_web = CORNERBOX(s, L=L1, W=T_PLT, H=web_h).translate((-L1 / 2.0, wy, z_base_top - 1.0))
        o_pcut = CYLINDER(s, R=r_p, H=L1 + 40.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 20.0), 0.0, 0.0))
        o_web.subtractFrom(o_pcut)
        o_pcut.erase()
        o_main.uniteWith(o_web)
        o_web.erase()

    # 3. 两端横向加强筋
    rib_w = max(12.0, web_sp - T_PLT + 2.0)
    rib_h = max(25.0, (-r_p + 12.0) - (z_base_top - 1.0))
    for sx in (-1.0, 1.0):
        rx = sx * (clamp_sp / 2.0) - T_PLT / 2.0
        o_rib = CORNERBOX(s, L=T_PLT, W=rib_w, H=rib_h).translate((rx, -rib_w / 2.0, z_base_top - 1.0))
        o_rcut = CYLINDER(s, R=r_p, H=L1 + 40.0, O=0.0).rotateY(90.0).translate((-(L1 / 2.0 + 20.0), 0.0, 0.0))
        o_rib.subtractFrom(o_rcut)
        o_rcut.erase()
        o_main.uniteWith(o_rib)
        o_rib.erase()

    # 4. 双抱箍管夹 + 两侧双耳紧固耳板与螺栓
    ear_len = max(32.0, bolt_d * 2.3)
    ear_gap = max(6.0, CLAMP_T * 0.8)
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
            ey = (r_p + CLAMP_T * 0.3) if sy > 0 else -(r_p + CLAMP_T * 0.3 + ear_len)
            for sz in (-1.0, 1.0):
                ez = (ear_gap / 2.0) if sz > 0 else -(ear_gap / 2.0 + CLAMP_T)
                o_ear = CORNERBOX(s, L=CLAMP_W, W=ear_len, H=CLAMP_T).translate((cx - CLAMP_W / 2.0, ey, ez))
                o_main.uniteWith(o_ear)
                o_ear.erase()
            by = sy * (r_out + ear_len * 0.52)
            bh = ear_gap + CLAMP_T * 2.0 + bolt_d * 1.6
            o_bolt = CYLINDER(s, R=bolt_d * 0.5, H=bh, O=0.0).translate((cx, by, -bh / 2.0))
            o_main.uniteWith(o_bolt)
            o_bolt.erase()
            for sz in (-1.0, 1.0):
                nz = (ear_gap / 2.0 + CLAMP_T - 0.5) if sz > 0 else -(ear_gap / 2.0 + CLAMP_T + bolt_d * 0.75 - 0.5)
                o_nut = CYLINDER(s, R=bolt_d * 0.88, H=bolt_d * 0.75, O=0.0).translate((cx, by, nz))
                o_main.uniteWith(o_nut)
                o_nut.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H1', (0.0, 0.0, -r_p), (0.0, 0.0, z_bot))
    s.setLinearDimension('L1', (-L1 / 2.0, 0.0, z_bot), (L1 / 2.0, 0.0, z_bot))
    s.setLinearDimension('B1', (0.0, -B1 / 2.0, z_bot), (0.0, B1 / 2.0, z_bot))
