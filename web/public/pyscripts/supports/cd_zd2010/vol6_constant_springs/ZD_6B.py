# -*- coding: utf-8 -*-
# CD-ZD2010 6B 平卧单吊板连接恒力弹簧组件（左侧水平卧置圆柱弹簧筒体 + 右侧凸轮摇臂框架壳体 + 框架顶部左、右两端各 1 块竖直单孔吊板 + 右侧下方负载吊杆与花兰螺丝）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="6B平卧单吊板恒吊", TooltipLong="CD-ZD2010 6B 平卧单吊板连接恒力弹簧组件", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L_body=LENGTH, TooltipShort="总长A", TooltipLong="箱体总长 A", Ask4Dist=True)
@param(W_body=LENGTH, TooltipShort="框架宽N", TooltipLong="摇臂框架宽度 N")
@param(H_body=LENGTH, TooltipShort="弹簧筒径D", TooltipLong="卧置弹簧筒外径 D")
@param(Pin_d=LENGTH, TooltipShort="销孔径K", TooltipLong="顶部单吊板销孔径 K")
@param(Travel_mm=LENGTH, TooltipShort="行程", TooltipLong="额定工作行程")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="荷载", TooltipLong="工作荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_6B(s, L_body=669.0, W_body=180.0, H_body=219.0, Pin_d=22.0, Travel_mm=120.0, ID=u"ZD_6B", Load_kN=18.42, Weight_kg=39.6, **kw):
    L_body = float(L_body); W_body = float(W_body); H_body = float(H_body); Pin_d = float(Pin_d); Travel_mm = float(Travel_mm)
    if L_body < 300.0: L_body = 300.0
    if W_body < 100.0: W_body = 100.0
    if H_body < 120.0: H_body = 120.0
    if Pin_d < 12.0: Pin_d = 12.0

    R_cyl = H_body / 2.0
    L_cyl = L_body * 0.46
    L_frame = L_body - L_cyl
    x_left = -(L_body / 2.0)
    x_junc = x_left + L_cyl
    x_right = L_body / 2.0
    z_center = -(R_cyl + 16.0)
    thk = max(8.0, min(16.0, R_cyl * 0.12))

    # 1. 左侧水平卧置空心圆柱弹簧筒体 + 中部连接方法兰面板
    o1 = CYLINDER(s, R=R_cyl, H=L_cyl, O=0.0).rotateY(90.0).translate((x_left, 0.0, z_center))
    o_in = CYLINDER(s, R=R_cyl - thk, H=max(20.0, L_cyl - thk * 2.0), O=0.0).rotateY(90.0).translate((x_left + thk, 0.0, z_center))
    o1.subtractFrom(o_in); o_in.erase()
    flange_w = max(W_body * 1.05, H_body * 1.04)
    o_flange = BOX(s, L=flange_w, W=H_body * 1.04, H=thk * 1.4).translate((x_junc - thk * 0.5, 0.0, z_center))
    o1.uniteWith(o_flange); o_flange.erase()

    # 2. 右侧双侧扇形/梯形凸轮摇臂框架壳体 + 转轴销 + 弧形导向槽
    plate_t = max(10.0, W_body * 0.08)
    frame_w = W_body * 0.72
    frame_h = H_body * 0.96
    for sy in (-1.0, 1.0):
        yc = sy * (frame_w / 2.0)
        o_side = BOX(s, L=plate_t, W=frame_h, H=L_frame + thk).translate((x_junc + L_frame / 2.0 - thk * 0.5, yc, z_center))
        cut_l = L_frame * 0.65
        o_cut = BOX(s, L=plate_t * 3.0, W=frame_h * 0.7, H=cut_l).rotateY(-28.0).translate((x_right - cut_l * 0.15, yc, z_center - frame_h * 0.48))
        o_side.subtractFrom(o_cut); o_cut.erase()
        slot_len = min(L_frame * 0.48, max(35.0, Travel_mm * 0.55))
        o_slot = BOX(s, L=plate_t * 3.0, W=max(12.0, frame_h * 0.09), H=slot_len).rotateY(32.0).translate((x_junc + L_frame * 0.52, yc, z_center - frame_h * 0.05))
        o_side.subtractFrom(o_slot); o_slot.erase()
        o1.uniteWith(o_side); o_side.erase()

    top_bar_z = z_center + frame_h / 2.0 - plate_t / 2.0
    o_top_bar = BOX(s, L=frame_w + plate_t, W=plate_t, H=L_frame).translate((x_junc + L_frame / 2.0, 0.0, top_bar_z))
    o1.uniteWith(o_top_bar); o_top_bar.erase()

    pin_r = max(14.0, H_body * 0.08)
    o_pin1 = CYLINDER(s, R=pin_r, H=frame_w + plate_t * 3.0, O=0.0).rotateX(90.0).translate((x_junc + L_frame * 0.25, (frame_w + plate_t * 3.0) / 2.0, z_center + frame_h * 0.06))
    o_pin2 = CYLINDER(s, R=pin_r * 0.85, H=frame_w + plate_t * 2.5, O=0.0).rotateX(90.0).translate((x_junc + L_frame * 0.58, (frame_w + plate_t * 2.5) / 2.0, z_center - frame_h * 0.14))
    o_cam = CYLINDER(s, R=frame_h * 0.34, H=frame_w * 0.45, O=0.0).rotateX(90.0).translate((x_junc + L_frame * 0.42, frame_w * 0.225, z_center - frame_h * 0.04))
    o1.uniteWith(o_pin1); o_pin1.erase()
    o1.uniteWith(o_pin2); o_pin2.erase()
    o1.uniteWith(o_cam); o_cam.erase()

    # 3. 6B 专属顶部连接结构：框架顶部左端 1 块 + 右端 1 块竖直圆头单孔吊板 (对照图集 p.248 6B)
    ear_r = max(24.0, min(Pin_d * 1.4, L_frame * 0.16))
    ear_h = max(38.0, ear_r * 1.5)
    ear_t = max(10.0, min(25.0, Pin_d * 0.55))
    hole_r = min(Pin_d / 2.0, ear_r * 0.55)
    x_lug1 = x_junc + L_frame * 0.20
    x_lug2 = x_junc + L_frame * 0.76
    for xl in (x_lug1, x_lug2):
        o_eb = BOX(s, L=ear_t, W=ear_h, H=ear_r * 2.0).translate((xl, 0.0, top_bar_z + ear_h / 2.0))
        o_et = CYLINDER(s, R=ear_r, H=ear_t, O=0.0).rotateX(90.0).translate((xl, ear_t / 2.0, top_bar_z + ear_h))
        o_eb.uniteWith(o_et); o_et.erase()
        o_eh = CYLINDER(s, R=hole_r, H=ear_t * 3.0, O=0.0).rotateX(90.0).translate((xl, ear_t * 1.5, top_bar_z + ear_h))
        o_eb.subtractFrom(o_eh); o_eh.erase()
        o1.uniteWith(o_eb); o_eb.erase()

    # 4. 右侧下方垂下的负载吊杆与花兰螺丝
    rod_r = max(8.0, min(22.0, W_body * 0.06))
    x_load = x_junc + L_frame * 0.65
    load_h = max(110.0, H_body * 0.55)
    z_load_btm = z_center - frame_h * 0.35 - load_h
    o_lrod = CYLINDER(s, R=rod_r, H=load_h + frame_h * 0.35, O=0.0).translate((x_load, 0.0, z_load_btm))
    o_turn = CYLINDER(s, R=rod_r * 1.85, H=load_h * 0.48, O=0.0).translate((x_load, 0.0, z_load_btm + load_h * 0.18))
    o_thole = BOX(s, L=rod_r * 4.5, W=load_h * 0.28, H=rod_r * 1.1).translate((x_load, 0.0, z_load_btm + load_h * 0.42))
    o_turn.subtractFrom(o_thole); o_thole.erase()
    o1.uniteWith(o_lrod); o_lrod.erase()
    o1.uniteWith(o_turn); o_turn.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('L_body', (-(L_body / 2.0), 0.0, 0.0), ((L_body / 2.0), 0.0, 0.0))
