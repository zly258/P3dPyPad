# -*- coding: utf-8 -*-
# CD-ZD2010 118 管卡（合并 118/119：U形圆钢半圆弯头 + 双直腿 + 下部双六角螺母与平垫圈）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="118管卡", TooltipLong="CD-ZD2010 118/119 U形圆钢螺栓管卡（配双螺母与垫圈）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(d=LENGTH, TooltipShort="圆钢径", TooltipLong="U形螺栓圆钢直径")
@param(H=LENGTH, TooltipShort="下伸高", TooltipLong="管心至螺杆下端长度", Ask4Dist=True)
@param(L=LENGTH, TooltipShort="螺纹长", TooltipLong="下端丝扣螺纹长度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_118(s, D=108.0, d=12.0, H=90.0, L=65.0, ID=u"ZD_118", **kw):
    D = float(D); d = float(d); H = float(H); L = float(L)
    if D < 12.0: D = 12.0
    if d < 6.0: d = 6.0
    R = D / 2.0 + d / 2.0
    if H < D / 2.0 + d * 3.0: H = D / 2.0 + d * 3.5

    # 1. 上半圆 U 形圆钢弯头 (位于 YZ 平面，Z >= 0)
    o1 = TORUS(s, R1=R, R2=d / 2.0).rotateY(90.0)
    o_cut = BOX(s, L=(R + d) * 4.0, W=(R + d) * 2.0, H=(R + d) * 4.0).translate((0.0, 0.0, -(R + d)))
    o1.subtractFrom(o_cut); o_cut.erase()

    # 2. 两侧垂直直腿 (上段光杆 + 下段螺纹小径台阶) + 上下两组六角螺母与平垫圈
    th_l = min(max(d * 2.5, L), H * 0.78)
    shank_h = H - th_l
    hex_s = d * 1.6
    nut_h = d * 0.8
    wash_r = d * 1.05
    wash_t = max(2.0, d * 0.2)

    for sy in (-1.0, 1.0):
        yc = sy * R
        o_leg = CYLINDER(s, R=d / 2.0, H=shank_h + 1.0, O=0.0).translate((0.0, yc, -shank_h))
        o_th = CYLINDER(s, R=(d / 2.0) * 0.84, H=H + 1.0, O=0.0).translate((0.0, yc, -H))
        o1.uniteWith(o_leg); o_leg.erase()
        o1.uniteWith(o_th); o_th.erase()

        # 垫圈与双六角螺母 (还原图集 118 螺杆上的锁紧螺母组)
        z_base = -(H - th_l * 0.45)
        o_w = CYLINDER(s, R=wash_r, H=wash_t, O=0.0).translate((0.0, yc, z_base))
        o1.uniteWith(o_w); o_w.erase()
        for n_idx in (-1, 1):
            zn = z_base + n_idx * (nut_h * 0.95)
            o_n1 = BOX(s, L=hex_s, W=nut_h, H=hex_s * 2.0).translate((0.0, yc, zn))
            o_n2 = BOX(s, L=hex_s, W=nut_h, H=hex_s * 2.0).rotateZ(60.0).translate((0.0, yc, zn))
            o_n3 = BOX(s, L=hex_s, W=nut_h, H=hex_s * 2.0).rotateZ(120.0).translate((0.0, yc, zn))
            o_n1.intersectWith(o_n2); o_n2.erase()
            o_n1.intersectWith(o_n3); o_n3.erase()
            o1.uniteWith(o_n1); o_n1.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, -H))
