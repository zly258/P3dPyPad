# -*- coding: utf-8 -*-
# HG/T 21629-2021 A6 可调节的U形管夹（图 C.1-6）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="可调节的U形管夹", TooltipLong="HG/T 21629-2021 A6 可调节的U形管夹 图C.1-6", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="腿长", TooltipLong="U形螺栓直线段长度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="开档", TooltipLong="U形中心距/内宽")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="U形圆钢螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A6(s, D=114.3, H=120.7, B=130.3, d=12.0, ID=u"A6", **kw):
    D = float(D); H = float(H); B = float(B); d = float(d)
    if D < 15.0: D = 33.7
    if d < 6.0: d = 10.0
    if B < (D + d * 1.5): B = D + d * 2.0
    if H < (D * 0.85 + 40.0): H = D * 0.95 + 55.0
    R1 = D / 2.0
    t_bar = max(4.0, d * 0.45)
    w_bar = max(25.0, d * 2.6)
    R_out = R1 + t_bar
    gap_z = max(14.0, d * 1.5)
    ear_len = max(28.0, d * 3.0)
    # 1. 下半U形扁钢托箍（下半圆弧 + 两侧竖直段至 Z = -gap_z/2 + 腰部水平外折耳板）
    o1 = CYLINDER(s, R=R_out, H=w_bar, O=0.0).rotateY(90.0).translate((-(w_bar / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=w_bar + 4.0, O=0.0).rotateY(90.0).translate((-(w_bar / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_up_cut = BOX(s, L=R_out * 2.5, W=R_out * 1.5, H=w_bar + 8.0).translate((0.0, 0.0, R_out * 0.75))
    o1.subtractFrom(o_up_cut); o_up_cut.erase()
    # 2. 上半可调节折弯扁钢拱架（腰部水平耳板 Z = +gap_z/2 + 竖直段 + 斜肩段 + 顶部水平吊杆座）
    z_top = max(R_out + d * 3.5, H - R_out)
    top_w = max(d * 3.2, R_out * 0.7)
    o_top_seat = BOX(s, L=top_w, W=t_bar * 1.3, H=w_bar).translate((0.0, 0.0, z_top))
    o_top_hole = CYLINDER(s, R=d * 0.55, H=t_bar * 4.0, O=0.0).translate((0.0, 0.0, z_top - t_bar * 2.0))
    o_top_seat.subtractFrom(o_top_hole); o_top_hole.erase()
    o_top_rod = CYLINDER(s, R=d * 0.5, H=d * 4.0, O=0.0).translate((0.0, 0.0, z_top - d * 1.5))
    o_top_nut = CYLINDER(s, R=d * 0.9, H=d * 0.8, O=0.0).translate((0.0, 0.0, z_top - d * 0.8 - t_bar * 0.65))
    o1.uniteWith(o_top_seat); o_top_seat.erase()
    o1.uniteWith(o_top_rod); o_top_rod.erase()
    o1.uniteWith(o_top_nut); o_top_nut.erase()
    z_knee = R1 * 0.55
    for sy in (-1.0, 1.0):
        # 腰部上下耳板与调节螺栓（含上下双锁紧螺母）
        o_low_ear = BOX(s, L=ear_len, W=t_bar, H=w_bar).translate((0.0, sy * (R1 + ear_len / 2.0), -(gap_z / 2.0 + t_bar / 2.0)))
        o_up_ear = BOX(s, L=ear_len, W=t_bar, H=w_bar).translate((0.0, sy * (R1 + ear_len / 2.0), (gap_z / 2.0 + t_bar / 2.0)))
        o_up_leg = BOX(s, L=t_bar, W=max(10.0, z_knee - gap_z / 2.0), H=w_bar).translate((0.0, sy * (R1 + t_bar / 2.0), (gap_z / 2.0 + z_knee) / 2.0))
        dx_s = (R1 + t_bar / 2.0) - top_w * 0.42
        dz_s = z_top - z_knee
        sl_len = sqrt(dx_s * dx_s + dz_s * dz_s)
        sl_ang = degrees(atan2(dx_s, dz_s))
        o_slope = BOX(s, L=t_bar, W=sl_len + t_bar, H=w_bar).rotateX(sy * sl_ang).translate((0.0, sy * (top_w * 0.42 + dx_s / 2.0), z_knee + dz_s / 2.0))
        yb = sy * (R1 + ear_len * 0.58)
        bh = gap_z + t_bar * 5.0
        o_blt = CYLINDER(s, R=d * 0.42, H=bh, O=0.0).translate((0.0, yb, -(bh / 2.0)))
        o_n1 = CYLINDER(s, R=d * 0.78, H=d * 0.65, O=0.0).translate((0.0, yb, gap_z / 2.0 + t_bar))
        o_n2 = CYLINDER(s, R=d * 0.78, H=d * 0.65, O=0.0).translate((0.0, yb, -(gap_z / 2.0 + t_bar + d * 0.65)))
        for p in (o_low_ear, o_up_ear, o_up_leg, o_slope, o_blt, o_n1, o_n2):
            o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
