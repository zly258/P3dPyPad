# -*- coding: utf-8 -*-
# CD-ZD2010 103 C形螺杆管夹（上半圆钢带顶焊吊板与横担耳 + 下半圆U形螺杆穿入水平横担板并配双螺母）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="103C形螺杆管夹", TooltipLong="CD-ZD2010 103 C形螺杆管夹", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(H=LENGTH, TooltipShort="吊心高", TooltipLong="管心至顶部吊孔中心高度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="带宽", TooltipLong="上半圆钢带宽度")
@param(T=LENGTH, TooltipShort="带厚", TooltipLong="钢带及耳板厚度")
@param(d=LENGTH, TooltipShort="吊孔径", TooltipLong="顶部吊孔直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_103(s, D=299.0, H=280.0, B=80.0, T=12.0, d=36.0, ID=u"ZD_103", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 50.0: D = 50.0
    if T < 6.0: T = 6.0
    if B < 40.0: B = 40.0
    if d < 14.0: d = 14.0
    R1 = D / 2.0
    R2 = R1 + T
    if H <= R2 + d * 1.5: H = R2 + d * 2.2 + 30.0

    # 1. 上半圆 C 形钢带鞍座 (Z >= 0)
    o1 = CYLINDER(s, R=R2, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=B + 4.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_cut_bot = BOX(s, L=R2 * 3.0, W=R2 * 2.0, H=B + 10.0).translate((0.0, 0.0, -R2))
    o1.subtractFrom(o_cut_bot); o_cut_bot.erase()

    # 2. 顶部圆头吊耳板 (沿 XZ 平面，带吊孔 d) + 前后梯形加劲肋板
    lug_w = max(d * 2.2, B * 0.85)
    lug_h = H - R1
    o_lug = BOX(s, L=T * 1.4, W=lug_h, H=lug_w).translate((0.0, 0.0, R1 + lug_h / 2.0))
    o_top_cyl = CYLINDER(s, R=lug_w / 2.0, H=T * 1.4, O=0.0).rotateX(90.0).translate((0.0, T * 0.7, H))
    o_lug.uniteWith(o_top_cyl); o_top_cyl.erase()
    o_hole = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateX(90.0).translate((0.0, T * 2.0, H))
    o_lug.subtractFrom(o_hole); o_hole.erase()
    o1.uniteWith(o_lug); o_lug.erase()

    # 3. 两侧水平横担承压耳板 (位于 Y = ±(R1 + ear_ext/2), Z = R1 * 0.25) 与立筋
    rod_d = max(14.0, min(32.0, d * 0.65))
    ear_ext = rod_d * 2.8 + T
    y_rod = R1 + rod_d * 1.35
    z_bar = R1 * 0.22
    bar_t = T * 1.5
    for sy in (-1.0, 1.0):
        o_bar = BOX(s, L=ear_ext + T, W=bar_t, H=B).translate((0.0, sy * (R1 + (ear_ext - T) / 2.0), z_bar))
        o1.uniteWith(o_bar); o_bar.erase()
        for sx in (-1.0, 1.0):
            o_rib = BOX(s, L=y_rod, W=H * 0.55, H=T * 0.85).translate((sx * (B * 0.35), sy * (y_rod / 2.0), z_bar + H * 0.275))
            o1.uniteWith(o_rib); o_rib.erase()

    o_clean = CYLINDER(s, R=R1, H=B + 10.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 5.0), 0.0, 0.0))
    o1.subtractFrom(o_clean); o_clean.erase()

    # 4. 下半圆 U 形圆钢螺杆 (绕管道下半部，直腿向上穿入两侧水平横担板并锁双螺母)
    o_ubend = TORUS(s, R1=y_rod, R2=rod_d / 2.0).rotateY(90.0)
    o_ucut = BOX(s, L=(y_rod + rod_d) * 3.0, W=(y_rod + rod_d) * 2.0, H=B * 2.0).translate((0.0, 0.0, (y_rod + rod_d)))
    o_ubend.subtractFrom(o_ucut); o_ucut.erase()
    o1.uniteWith(o_ubend); o_ubend.erase()

    leg_top = z_bar + bar_t / 2.0 + rod_d * 2.2
    hex_s = rod_d * 1.55
    nut_h = rod_d * 0.75
    for sy in (-1.0, 1.0):
        o_leg = CYLINDER(s, R=rod_d / 2.0, H=leg_top, O=0.0).translate((0.0, sy * y_rod, 0.0))
        o1.uniteWith(o_leg); o_leg.erase()
        # 横担板上方的双六角螺母
        for n_idx in (0, 1):
            zn = z_bar + bar_t / 2.0 + nut_h * (0.5 + n_idx * 1.05)
            o_n1 = BOX(s, L=hex_s, W=nut_h, H=hex_s * 2.0).translate((0.0, sy * y_rod, zn))
            o_n2 = BOX(s, L=hex_s, W=nut_h, H=hex_s * 2.0).rotateZ(60.0).translate((0.0, sy * y_rod, zn))
            o_n3 = BOX(s, L=hex_s, W=nut_h, H=hex_s * 2.0).rotateZ(120.0).translate((0.0, sy * y_rod, zn))
            o_n1.intersectWith(o_n2); o_n2.erase()
            o_n1.intersectWith(o_n3); o_n3.erase()
            o1.uniteWith(o_n1); o_n1.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
