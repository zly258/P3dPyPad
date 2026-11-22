# -*- coding: utf-8 -*-
# CD-ZD2010 131 管卡横担（水平管 U 形管卡穿过下部双槽钢横担梁并锁紧螺母，横担梁两端带吊杆）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="131管卡横担", TooltipLong="CD-ZD2010 131 管卡横担", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(L=LENGTH, TooltipShort="横担长", TooltipLong="双槽钢横担总长", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="横担高", TooltipLong="双槽钢横担截面高")
@param(W=LENGTH, TooltipShort="型钢宽", TooltipLong="双槽钢组合宽度")
@param(d=LENGTH, TooltipShort="吊杆径", TooltipLong="两端吊杆及U形卡杆径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_131(s, D=159.0, L=550.0, H=100.0, W=70.0, d=18.0, ID=u"ZD_131", **kw):
    D = float(D); L = float(L); H = float(H); W = float(W); d = float(d)
    if D < 15.0: D = 15.0
    if d < 10.0: d = 10.0
    if d > 36.0: d = 24.0
    if W < 40.0: W = 40.0
    R1 = D / 2.0
    ch_h = max(63.0, min(160.0, H if H < 180.0 else W * 1.4))
    ch_w = max(36.0, W * 0.55)
    ch_t = max(5.5, ch_h * 0.08)
    if L <= D + d * 6.0 + 80.0: L = D + d * 6.0 + 150.0

    # 1. 下部背靠背双槽钢横担梁 (紧贴管道底部 Z = -R1 至 -(R1 + ch_h))
    gap_x = d + 6.0
    z_top_beam = -R1
    z_bot_beam = -(R1 + ch_h)
    z_mid = (z_top_beam + z_bot_beam) / 2.0
    o1 = BOX(s, L=L, W=ch_h, H=ch_w).translate((-(gap_x / 2.0 + ch_w / 2.0), 0.0, z_mid))
    o_c1 = BOX(s, L=L + 4.0, W=ch_h - 2.0 * ch_t, H=ch_w - ch_t).translate((-(gap_x / 2.0 + ch_w / 2.0 + ch_t / 2.0), 0.0, z_mid))
    o1.subtractFrom(o_c1); o_c1.erase()

    o2 = BOX(s, L=L, W=ch_h, H=ch_w).translate(((gap_x / 2.0 + ch_w / 2.0), 0.0, z_mid))
    o_c2 = BOX(s, L=L + 4.0, W=ch_h - 2.0 * ch_t, H=ch_w - ch_t).translate(((gap_x / 2.0 + ch_w / 2.0 + ch_t / 2.0), 0.0, z_mid))
    o2.subtractFrom(o_c2); o_c2.erase()
    o1.uniteWith(o2); o2.erase()

    # 2. 中部 U 形圆钢管卡穿过双槽钢中间缝隙，并在横担梁底部锁紧螺母
    u_d = max(10.0, d * 0.75)
    R_u = R1 + u_d / 2.0
    o_u = TORUS(s, R1=R_u, R2=u_d / 2.0).rotateY(90.0)
    o_cut = BOX(s, L=(R_u + u_d) * 3.0, W=(R_u + u_d) * 2.0, H=(R_u + u_d) * 3.0).translate((0.0, 0.0, -(R_u + u_d)))
    o_u.subtractFrom(o_cut); o_cut.erase()
    o1.uniteWith(o_u); o_u.erase()

    leg_bot = z_bot_beam - u_d * 2.0
    for sy in (-1.0, 1.0):
        o_leg = CYLINDER(s, R=u_d / 2.0, H=-leg_bot, O=0.0).translate((0.0, sy * R_u, leg_bot))
        o_nut = CYLINDER(s, R=u_d * 0.9, H=u_d * 1.1, O=0.0).translate((0.0, sy * R_u, z_bot_beam - u_d * 1.1))
        o1.uniteWith(o_leg); o_leg.erase()
        o1.uniteWith(o_nut); o_nut.erase()

    # 3. 横担梁两端竖直吊杆 + 垫板与锁紧螺母
    y_rod = L / 2.0 - max(45.0, d * 2.2)
    rod_top = R1 + d * 3.2
    rod_bot = z_bot_beam - d * 1.8
    for sy in (-1.0, 1.0):
        o_pad = BOX(s, L=d * 2.8, W=ch_t * 1.5, H=gap_x + ch_w * 1.5).translate((0.0, sy * y_rod, z_bot_beam - ch_t * 0.75))
        o_rod = CYLINDER(s, R=d / 2.0, H=rod_top - rod_bot, O=0.0).translate((0.0, sy * y_rod, rod_bot))
        o1.uniteWith(o_pad); o_pad.erase()
        o1.uniteWith(o_rod); o_rod.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, -(L / 2.0), z_bot_beam), (0.0, (L / 2.0), z_bot_beam))
