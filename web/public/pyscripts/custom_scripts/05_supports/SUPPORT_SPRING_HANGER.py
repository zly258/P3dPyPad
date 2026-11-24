# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *
import math

def _hex_z(s, af, h):
    rc = float(af) / math.sqrt(3.0)
    b0 = BOX(s, L=af, W=h, H=rc).translate((0.0, 0.0, h * 0.5))
    b1 = BOX(s, L=af, W=h, H=rc).rotateZ(60.0).translate((0.0, 0.0, h * 0.5))
    b2 = BOX(s, L=af, W=h, H=rc).rotateZ(120.0).translate((0.0, 0.0, h * 0.5))
    b0.uniteWith(b1); b1.erase()
    b0.uniteWith(b2); b2.erase()
    return b0

@activate(Group="Support", Ports=1, TooltipShort=u"化工可变弹簧吊架 (HG/T 21629 C类 / VS)", TooltipLong=u"化工行业标准 HG/T 21629-2021 / NB/T 47039 串联可变弹簧支吊架 (Variable Spring Hanger)，含双耳管夹、下拉杆、可变弹簧钢筒(带载荷位移刻度牌)、花篮调节螺母与顶部生根吊耳", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"支吊架主要结构尺寸：管道口径、结构与型钢规格")
@param(D=LENGTH, TooltipShort=u"管道外径 OD", Ask4Dist=True, TooltipLong=u"管道外径 OD")
@param(H=LENGTH, TooltipShort=u"管中心至生根点总高 H", Ask4Dist=True, TooltipLong=u"管中心至生根点总高 H")
@param(D_CAN=LENGTH, TooltipShort=u"弹簧筒体外径", Ask4Dist=True, TooltipLong=u"弹簧筒体外径")
@param(H_CAN=LENGTH, TooltipShort=u"弹簧筒体高度", Ask4Dist=True, TooltipLong=u"弹簧筒体高度")
@param(ROD_D=LENGTH, TooltipShort=u"吊杆直径", TooltipLong=u"吊杆直径")
@param(ID=STRING, TooltipShort=u"弹簧吊架代号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def SUPPORT_SPRING_HANGER(s, D=114.3, H=680.0, D_CAN=168.0, H_CAN=260.0, ROD_D=20.0, ID="VS60F2-DN100", **kw):
    D = max(25.0, float(D))
    r_pipe = D / 2.0
    H_CAN = max(140.0, float(H_CAN))
    D_CAN = max(95.0, float(D_CAN))
    H = max(r_pipe + H_CAN + 180.0, float(H))
    ROD_D = max(12.0, float(ROD_D))

    r_rod = ROD_D / 2.0
    r_can = D_CAN / 2.0
    t_clamp = max(8.0, D * 0.08)
    w_clamp = max(40.0, D * 0.36)
    ear_h = max(42.0, D * 0.38)
    gap = ROD_D * 1.35

    # 1. 底部双耳管夹抱箍 (围绕原点 (0,0,0) 的管道，管轴沿 X)
    o_hanger = CYLINDER(s, R=r_pipe + t_clamp, H=w_clamp, O=0.0).rotateY(90.0).translate((-w_clamp * 0.5, 0.0, 0.0))
    for sy in (-1.0, 1.0):
        yc = sy * (gap * 0.5 + t_clamp * 0.5)
        e_top = BOX(s, L=t_clamp, W=ear_h, H=w_clamp).translate((0.0, yc, r_pipe + ear_h * 0.45))
        e_bot = BOX(s, L=t_clamp, W=ear_h * 0.65, H=w_clamp).translate((0.0, yc, -(r_pipe + ear_h * 0.25)))
        o_hanger.uniteWith(e_top); e_top.erase()
        o_hanger.uniteWith(e_bot); e_bot.erase()

    o_pipe_cut = CYLINDER(s, R=r_pipe, H=w_clamp + 10.0, O=0.0).rotateY(90.0).translate((-(w_clamp * 0.5 + 5.0), 0.0, 0.0))
    o_hanger.subtractFrom(o_pipe_cut); o_pipe_cut.erase()
    o_slot_cut = BOX(s, L=gap, W=2.0 * (r_pipe + ear_h + 20.0), H=w_clamp + 10.0)
    o_hanger.subtractFrom(o_slot_cut); o_slot_cut.erase()

    # 上下夹紧横销
    z_pin = r_pipe + ear_h * 0.52
    pin_l = gap + 2.0 * t_clamp + 28.0
    o_pin = CYLINDER(s, R=r_rod * 0.85, H=pin_l, O=0.0).rotateX(90.0).translate((0.0, pin_l * 0.5, z_pin))
    o_hanger.uniteWith(o_pin); o_pin.erase()

    # 2. 下吊杆 + 弹簧筒体 (Spring Canister at middle height)
    z_can_bot = r_pipe + ear_h + (H - (r_pipe + ear_h) - H_CAN) * 0.36
    z_can_top = z_can_bot + H_CAN

    o_rod_low = CYLINDER(s, R=r_rod, H=z_can_bot - z_pin + 15.0, O=0.0).translate((0.0, 0.0, z_pin))
    o_hanger.uniteWith(o_rod_low); o_rod_low.erase()
    n_low = _hex_z(s, ROD_D * 1.65, ROD_D * 0.85).translate((0.0, 0.0, z_can_bot - ROD_D * 0.85))
    o_hanger.uniteWith(n_low); n_low.erase()

    # 弹簧筒体 + 顶底加厚封板圆盘 + 侧向载荷位移指示标尺窗框
    fl_t = 14.0
    o_can = CYLINDER(s, R=r_can, H=H_CAN, O=0.0).translate((0.0, 0.0, z_can_bot))
    o_hanger.uniteWith(o_can); o_can.erase()
    for zf in (z_can_bot, z_can_top - fl_t):
        cap = CYLINDER(s, R=r_can * 1.12, H=fl_t, O=0.0).translate((0.0, 0.0, zf))
        o_hanger.uniteWith(cap); cap.erase()

    # 前侧 (-Y) 载荷刻度铭牌框与行程指针耳
    o_scale_plate = BOX(s, L=12.0, W=H_CAN * 0.65, H=r_can * 0.55).translate((0.0, -r_can - 4.0, z_can_bot + H_CAN * 0.5))
    o_hanger.uniteWith(o_scale_plate); o_scale_plate.erase()
    o_ptr_lug = BOX(s, L=22.0, W=10.0, H=r_can * 0.72).translate((0.0, -r_can - 6.0, z_can_bot + H_CAN * 0.5))
    o_hanger.uniteWith(o_ptr_lug); o_ptr_lug.erase()

    # 3. 上吊杆 + 六角花篮调节螺母 (Turnbuckle) + 顶部工字钢生根双耳夹座
    o_rod_up = CYLINDER(s, R=r_rod, H=H - z_can_top + 10.0, O=0.0).translate((0.0, 0.0, z_can_top - 5.0))
    o_hanger.uniteWith(o_rod_up); o_rod_up.erase()

    z_tb = z_can_top + (H - z_can_top) * 0.45
    h_tb = max(65.0, (H - z_can_top) * 0.36)
    o_tb = _hex_z(s, ROD_D * 2.1, h_tb).translate((0.0, 0.0, z_tb - h_tb * 0.5))
    o_hanger.uniteWith(o_tb); o_tb.erase()

    # 顶部生根底板 + 吊耳板
    o_top_pl = BOX(s, L=D_CAN * 0.85, W=14.0, H=D_CAN * 0.85).translate((0.0, 0.0, H - 7.0))
    o_hanger.uniteWith(o_top_pl); o_top_pl.erase()
    o_top_nut = _hex_z(s, ROD_D * 1.75, ROD_D * 0.9).translate((0.0, 0.0, H - 14.0 - ROD_D * 0.9))
    o_hanger.uniteWith(o_top_nut); o_top_nut.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))

    s.setLinearDimension("H", (0.0, -r_can, 0.0), (0.0, -r_can, H))
    s.setLinearDimension("H_CAN", (0.0, r_can, z_can_bot), (0.0, r_can, z_can_top))
    s.setLinearDimension("D_CAN", (-r_can, 0.0, z_can_top), (r_can, 0.0, z_can_top))
    s.setLinearDimension("D", (0.0, -r_pipe, -r_pipe), (0.0, -r_pipe, r_pipe))
