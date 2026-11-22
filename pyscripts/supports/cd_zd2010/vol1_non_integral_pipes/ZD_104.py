# -*- coding: utf-8 -*-
# CD-ZD2010 104 C形钢带管夹（上下全圆钢带包箍 + 顶部焊接吊耳 + 两侧水平夹紧法兰耳与螺栓）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="104C形钢带管夹", TooltipLong="CD-ZD2010 104 C形钢带管夹", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(H=LENGTH, TooltipShort="耳孔高", TooltipLong="管心至顶部吊孔高度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="钢带宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="钢带厚度")
@param(d=LENGTH, TooltipShort="吊孔径", TooltipLong="顶部吊孔直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_104(s, D=508.0, H=420.0, B=140.0, T=14.0, d=48.0, ID=u"ZD_104", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 50.0: D = 50.0
    if T < 5.0: T = 5.0
    if B < 40.0: B = 40.0
    if d < 14.0: d = 14.0
    if d > D * 0.6: d = D * 0.3
    R1 = D / 2.0
    R2 = R1 + T
    if H <= R2 + d * 1.4: H = R2 + d * 2.0 + 30.0
    if H > R1 * 3.5 + 200.0: H = R1 * 1.65 + d * 1.8

    # 1. 上下全圆钢带包箍 (在 Z = 0 处留水平夹紧缝 gap)
    gap = max(10.0, T * 1.2)
    o1 = CYLINDER(s, R=R2, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=B + 4.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_seam = BOX(s, L=R2 * 3.0, W=gap, H=B + 6.0)
    o1.subtractFrom(o_seam); o_seam.erase()

    # 2. 顶部直立圆头吊耳板 + 两侧加劲鞍肋
    lug_w = max(d * 2.2, B * 0.75)
    lug_h = H - R1
    o_lug = BOX(s, L=T * 1.5, W=lug_h, H=lug_w).translate((0.0, 0.0, R1 + lug_h / 2.0))
    o_top_c = CYLINDER(s, R=lug_w / 2.0, H=T * 1.5, O=0.0).rotateX(90.0).translate((0.0, T * 0.75, H))
    o_lug.uniteWith(o_top_c); o_top_c.erase()
    o_hole = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateX(90.0).translate((0.0, T * 2.0, H))
    o_lug.subtractFrom(o_hole); o_hole.erase()
    o1.uniteWith(o_lug); o_lug.erase()

    # 3. 左右两侧上下水平夹紧法兰耳板 + 竖向穿孔紧固螺栓与双螺母
    bolt_d = max(14.0, min(30.0, d * 0.6))
    ear_len = bolt_d * 2.8 + T
    y_bolt = R2 + bolt_d * 1.3
    flange_t = T * 1.35
    for sy in (-1.0, 1.0):
        yc = sy * (R1 + ear_len / 2.0)
        # 上法兰耳与斜肋
        o_fu = BOX(s, L=ear_len, W=flange_t, H=B).translate((0.0, yc, gap / 2.0 + flange_t / 2.0))
        o1.uniteWith(o_fu); o_fu.erase()
        # 下法兰耳
        o_fd = BOX(s, L=ear_len, W=flange_t, H=B).translate((0.0, yc, -(gap / 2.0 + flange_t / 2.0)))
        o1.uniteWith(o_fd); o_fd.erase()
        # 顶部斜向连接肋板 (从上法兰耳连至吊耳)
        for sx in (-1.0, 1.0):
            o_rib = BOX(s, L=y_bolt, W=H * 0.55, H=T).translate((sx * (B * 0.36), sy * (y_bolt / 2.0), gap / 2.0 + H * 0.275))
            o1.uniteWith(o_rib); o_rib.erase()
        # 竖向夹紧螺栓与上下螺母
        tot_b = gap + flange_t * 2.0 + bolt_d * 2.6
        o_b = CYLINDER(s, R=bolt_d / 2.0, H=tot_b, O=0.0).translate((0.0, sy * y_bolt, -(tot_b / 2.0)))
        o1.uniteWith(o_b); o_b.erase()
        hex_s = bolt_d * 1.55
        nut_h = bolt_d * 0.75
        for sz in (-1.0, 1.0):
            zn = sz * (gap / 2.0 + flange_t + nut_h * 0.6)
            o_n1 = BOX(s, L=hex_s, W=nut_h, H=hex_s * 2.0).translate((0.0, sy * y_bolt, zn))
            o_n2 = BOX(s, L=hex_s, W=nut_h, H=hex_s * 2.0).rotateZ(60.0).translate((0.0, sy * y_bolt, zn))
            o_n3 = BOX(s, L=hex_s, W=nut_h, H=hex_s * 2.0).rotateZ(120.0).translate((0.0, sy * y_bolt, zn))
            o_n1.intersectWith(o_n2); o_n2.erase()
            o_n1.intersectWith(o_n3); o_n3.erase()
            o1.uniteWith(o_n1); o_n1.erase()

    o_clean = CYLINDER(s, R=R1, H=B + 10.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 5.0), 0.0, 0.0))
    o1.subtractFrom(o_clean); o_clean.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
