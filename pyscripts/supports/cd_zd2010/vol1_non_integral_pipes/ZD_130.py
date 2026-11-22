# -*- coding: utf-8 -*-
# CD-ZD2010 130 管夹横担（水平管扁钢抱箍固定在下部背靠背双槽钢横担梁中心，横担梁两端带竖直吊杆）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="130管夹横担", TooltipLong="CD-ZD2010 130 管夹横担", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(L=LENGTH, TooltipShort="横担长", TooltipLong="背靠背双槽钢横担总长", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="下垂高", TooltipLong="管心至横担梁底面高度")
@param(W=LENGTH, TooltipShort="型钢宽", TooltipLong="双槽钢横担组合宽度")
@param(d=LENGTH, TooltipShort="吊杆径", TooltipLong="两端吊杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_130(s, D=159.0, L=550.0, H=180.0, W=80.0, d=20.0, ID=u"ZD_130", **kw):
    D = float(D); L = float(L); H = float(H); W = float(W); d = float(d)
    if D < 15.0: D = 15.0
    if d < 10.0: d = 10.0
    if W < 40.0: W = 40.0
    R1 = D / 2.0
    ch_h = max(63.0, W * 1.1)
    ch_w = max(36.0, W * 0.55)
    ch_t = max(5.5, ch_h * 0.08)
    if H <= R1 + ch_h + 15.0: H = R1 + ch_h + 35.0
    if L <= D + d * 6.0 + 80.0: L = D + d * 6.0 + 140.0

    # 1. 下部背靠背双槽钢横担梁 (沿 Y 轴跨长 L，两槽钢位于 X = ±(gap_x/2 + ch_w/2))
    gap_x = d + 6.0
    z_beam_mid = -(H - ch_h / 2.0)
    o1 = BOX(s, L=L, W=ch_h, H=ch_w).translate((-(gap_x / 2.0 + ch_w / 2.0), 0.0, z_beam_mid))
    o_c1 = BOX(s, L=L + 4.0, W=ch_h - 2.0 * ch_t, H=ch_w - ch_t).translate((-(gap_x / 2.0 + ch_w / 2.0 + ch_t / 2.0), 0.0, z_beam_mid))
    o1.subtractFrom(o_c1); o_c1.erase()

    o2 = BOX(s, L=L, W=ch_h, H=ch_w).translate(((gap_x / 2.0 + ch_w / 2.0), 0.0, z_beam_mid))
    o_c2 = BOX(s, L=L + 4.0, W=ch_h - 2.0 * ch_t, H=ch_w - ch_t).translate(((gap_x / 2.0 + ch_w / 2.0 + ch_t / 2.0), 0.0, z_beam_mid))
    o2.subtractFrom(o_c2); o_c2.erase()
    o1.uniteWith(o2); o2.erase()

    # 2. 中部管座立板 + 水平管双耳扁钢抱箍
    clamp_b = min(100.0, ch_w * 1.6)
    t_cl = max(6.0, d * 0.4)
    o_web = BOX(s, L=D * 0.85, W=H - ch_h, H=gap_x + ch_w * 1.4).translate((0.0, 0.0, -((H - ch_h) / 2.0)))
    o1.uniteWith(o_web); o_web.erase()

    o_clamp = CYLINDER(s, R=R1 + t_cl, H=clamp_b, O=0.0).rotateY(90.0).translate((-(clamp_b / 2.0), 0.0, 0.0))
    ear_l = t_cl * 3.5
    for sy in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            o_ear = BOX(s, L=ear_l, W=t_cl, H=clamp_b).translate((0.0, sy * (R1 + ear_l / 2.0), sz * t_cl * 0.9))
            o_clamp.uniteWith(o_ear); o_ear.erase()
    o1.uniteWith(o_clamp); o_clamp.erase()

    o_pipe = CYLINDER(s, R=R1, H=clamp_b * 3.0, O=0.0).rotateY(90.0).translate((-(clamp_b * 1.5), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    # 3. 横担梁两端竖直穿入吊杆短段 + 垫板与上下螺母 (还原图集 130 两端立杆特征)
    y_rod = L / 2.0 - max(45.0, d * 2.2)
    rod_top = R1 + d * 3.0
    rod_bot = -(H + d * 1.8)
    rod_h = rod_top - rod_bot
    for sy in (-1.0, 1.0):
        o_pad = BOX(s, L=d * 3.0, W=ch_t * 1.5, H=gap_x + ch_w * 1.6).translate((0.0, sy * y_rod, -(H - ch_h - ch_t * 0.75)))
        o_pad_b = BOX(s, L=d * 3.0, W=ch_t * 1.5, H=gap_x + ch_w * 1.6).translate((0.0, sy * y_rod, -(H + ch_t * 0.75)))
        o_rod = CYLINDER(s, R=d / 2.0, H=rod_h, O=0.0).translate((0.0, sy * y_rod, rod_bot))
        o1.uniteWith(o_pad); o_pad.erase()
        o1.uniteWith(o_pad_b); o_pad_b.erase()
        o1.uniteWith(o_rod); o_rod.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, -(L / 2.0), -H), (0.0, (L / 2.0), -H))
