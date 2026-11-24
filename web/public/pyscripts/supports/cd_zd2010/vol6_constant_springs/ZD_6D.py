# -*- coding: utf-8 -*-
# CD-ZD2010 6D 平卧顶面连接恒力弹簧组件（左侧水平卧置圆柱弹簧筒体 + 右侧凸轮摇臂框架壳体 + 框架顶部加宽水平安装顶板带螺栓孔 + 右侧下方负载吊杆与花兰螺丝）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="6D平卧顶面恒吊", TooltipLong="CD-ZD2010 6D 平卧顶面连接恒力弹簧组件", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L_body=LENGTH, TooltipShort="总长A", TooltipLong="箱体长度 A", Ask4Dist=True)
@param(W_body=LENGTH, TooltipShort="框架宽N", TooltipLong="框架宽度 N")
@param(H_body=LENGTH, TooltipShort="弹簧筒径D", TooltipLong="卧置弹簧筒外径 D")
@param(Travel_mm=LENGTH, TooltipShort="位移量", TooltipLong="工作行程")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="荷载", TooltipLong="工作荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_6D(s, L_body=669.0, W_body=180.0, H_body=219.0, Travel_mm=120.0, ID=u"ZD_6D", Load_kN=18.42, Weight_kg=39.6, **kw):
    L_body = float(L_body); W_body = float(W_body); H_body = float(H_body); Travel_mm = float(Travel_mm)
    if L_body < 300.0: L_body = 300.0
    if W_body < 100.0: W_body = 100.0
    if H_body < 120.0: H_body = 120.0

    R_cyl = H_body / 2.0
    L_cyl = L_body * 0.46
    L_frame = L_body - L_cyl
    x_left = -(L_body / 2.0)
    x_junc = x_left + L_cyl
    x_right = L_body / 2.0
    z_center = -(R_cyl + 12.0)
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

    pin_r = max(14.0, H_body * 0.08)
    o_pin1 = CYLINDER(s, R=pin_r, H=frame_w + plate_t * 3.0, O=0.0).rotateX(90.0).translate((x_junc + L_frame * 0.25, (frame_w + plate_t * 3.0) / 2.0, z_center + frame_h * 0.06))
    o_pin2 = CYLINDER(s, R=pin_r * 0.85, H=frame_w + plate_t * 2.5, O=0.0).rotateX(90.0).translate((x_junc + L_frame * 0.58, (frame_w + plate_t * 2.5) / 2.0, z_center - frame_h * 0.14))
    o_cam = CYLINDER(s, R=frame_h * 0.34, H=frame_w * 0.45, O=0.0).rotateX(90.0).translate((x_junc + L_frame * 0.42, frame_w * 0.225, z_center - frame_h * 0.04))
    o1.uniteWith(o_pin1); o_pin1.erase()
    o1.uniteWith(o_pin2); o_pin2.erase()
    o1.uniteWith(o_cam); o_cam.erase()

    # 3. 6D 专属顶部连接结构：框架顶部设加宽水平安装顶板（带 4-ØK 安装螺栓孔与翼缘加劲肋，直接贴装于钢梁底面 Z=0，对照图集 p.250 6D）
    top_plate_w = W_body * 1.45
    top_plate_t = max(12.0, plate_t * 1.2)
    o_top_plate = BOX(s, L=top_plate_w, W=top_plate_t, H=L_frame + thk).translate((x_junc + L_frame / 2.0 - thk * 0.5, 0.0, -(top_plate_t / 2.0)))
    hole_r = max(7.0, W_body * 0.045)
    for xb in (x_junc + L_frame * 0.22, x_junc + L_frame * 0.78):
        for sy in (-1.0, 1.0):
            yb = sy * (top_plate_w * 0.38)
            o_bh = CYLINDER(s, R=hole_r, H=top_plate_t * 3.0, O=0.0).translate((xb, yb, -top_plate_t * 1.5))
            o_top_plate.subtractFrom(o_bh); o_bh.erase()
            # 侧向三角支撑小肋板
            o_rib = BOX(s, L=(top_plate_w - frame_w) * 0.38, W=top_plate_t * 2.2, H=plate_t).translate((xb, sy * (frame_w / 2.0 + (top_plate_w - frame_w) * 0.2), -(top_plate_t * 1.6)))
            o_top_plate.uniteWith(o_rib); o_rib.erase()
    o1.uniteWith(o_top_plate); o_top_plate.erase()

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
