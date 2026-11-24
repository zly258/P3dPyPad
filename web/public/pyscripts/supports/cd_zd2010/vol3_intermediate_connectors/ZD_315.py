# -*- coding: utf-8 -*-
# CD-ZD2010 315 恒吊用三孔连接板（下部梯形双孔板 + 顶部水平过渡垫板 + U形双耳夹板与横向穿销，与314明显区分）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="315恒吊用三孔连接板", TooltipLong="CD-ZD2010 315 恒吊用三孔连接板（顶部U形双耳夹板+销轴）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L1=LENGTH, TooltipShort="纵孔距", TooltipLong="顶部双耳销孔至底部双孔中心线高 H", Ask4Dist=True)
@param(L2=LENGTH, TooltipShort="横孔距", TooltipLong="底部双孔水平中心距 C")
@param(W=LENGTH, TooltipShort="边距宽", TooltipLong="连接板边距/耳宽")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="连接板厚度")
@param(d=LENGTH, TooltipShort="孔径", TooltipLong="穿销孔直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_315(s, L1=230.0, L2=190.0, W=60.0, T=12.0, d=22.0, ID=u"ZD_315", **kw):
    L1 = float(L1); L2 = float(L2); W = float(W); T = float(T); d = float(d)
    if d < 8.0: d = 8.0
    if T < 6.0: T = 6.0
    if W <= d * 1.6: W = d * 2.2
    if L1 < W * 1.8: L1 = W * 2.5
    if L2 < W * 1.5: L2 = W * 2.2

    # 1. 下部梯形双底孔立板 (从 Z = -clevis_h 向下延伸至 Z = -(L1 + W*0.45))
    clevis_h = max(W * 0.85, L1 * 0.34)
    plate_h = (L1 + W * 0.45) - clevis_h
    tot_w = L2 + W
    top_neck_w = W * 1.25
    o1 = BOX(s, L=T, W=plate_h, H=tot_w).translate((0.0, 0.0, -(clevis_h + plate_h / 2.0)))
    cut_dx = (tot_w - top_neck_w) / 2.0
    if cut_dx > 4.0 and plate_h > 20.0:
        ang = degrees(atan2(cut_dx, plate_h * 0.82))
        for sx in (-1.0, 1.0):
            mid_x = sx * (top_neck_w / 2.0 + tot_w / 2.0) * 0.5
            mid_z = -(clevis_h + plate_h * 0.42)
            o_cut = BOX(s, L=T * 4.0, W=plate_h * 2.5, H=tot_w * 2.0).translate((sx * tot_w, 0.0, 0.0)).rotateY(-sx * ang).translate((mid_x, 0.0, mid_z))
            o1.subtractFrom(o_cut); o_cut.erase()

    # 底部双圆孔切除 (位于 X = ±L2/2, Z = -L1)
    for sx in (-1.0, 1.0):
        o_bh = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateX(90.0).translate((sx * (L2 / 2.0), T * 2.0, -L1))
        o1.subtractFrom(o_bh); o_bh.erase()

    # 2. 顶部水平承压分界焊板 (在 Z = -clevis_h 处，完全还原图集 315 标志性台阶焊板)
    cap_y = T * 3.8
    cap_t = T * 1.15
    o_cap = BOX(s, L=cap_y, W=cap_t, H=top_neck_w * 1.08).translate((0.0, 0.0, -(clevis_h - cap_t / 2.0)))
    o1.uniteWith(o_cap); o_cap.erase()

    # 3. 顶部 U 形双耳夹板 (前后两片平行圆头立耳位于 Y = ±ear_y) + 横向穿销轴 (Z = 0)
    ear_t = T * 0.9
    ear_y = T * 0.95 + ear_t / 2.0
    ear_r = W * 0.46
    for sy in (-1.0, 1.0):
        yc = sy * ear_y
        o_ear = BOX(s, L=ear_t, W=clevis_h, H=ear_r * 2.0).translate((0.0, yc, -(clevis_h / 2.0)))
        o_top_c = CYLINDER(s, R=ear_r, H=ear_t, O=0.0).rotateX(90.0).translate((0.0, yc + ear_t / 2.0, 0.0))
        o_ear.uniteWith(o_top_c); o_top_c.erase()
        o_eh = CYLINDER(s, R=d / 2.0, H=ear_t * 3.0, O=0.0).rotateX(90.0).translate((0.0, yc + ear_t * 1.5, 0.0))
        o_ear.subtractFrom(o_eh); o_eh.erase()
        o1.uniteWith(o_ear); o_ear.erase()

    # 横向销轴与挡圈穿过顶部双耳孔 (Z = 0，沿 Y 轴)
    pin_len = cap_y + d * 1.2
    o_pin = CYLINDER(s, R=(d / 2.0) * 0.9, H=pin_len, O=0.0).rotateX(90.0).translate((0.0, pin_len / 2.0, 0.0))
    o1.uniteWith(o_pin); o_pin.erase()
    for sy_c in (-1.0, 1.0):
        yc_col = sy_c * (ear_y + ear_t / 2.0) + (d * 0.35 if sy_c > 0 else 0.0)
        o_pcol = CYLINDER(s, R=d * 0.68, H=d * 0.35, O=0.0).rotateX(90.0).translate((0.0, yc_col, 0.0))
        o1.uniteWith(o_pcol); o_pcol.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('L1', (0.0, 0.0, 0.0), (0.0, 0.0, -L1))
