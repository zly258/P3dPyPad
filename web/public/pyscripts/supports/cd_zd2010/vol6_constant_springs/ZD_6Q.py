# -*- coding: utf-8 -*-
# CD-ZD2010 6Q 直立单吊板连接恒力弹簧组件（下部竖直立置圆柱形弹簧筒体 + 上部凸轮摇臂框架壳体 + 顶面焊接单耳吊板 + 侧面悬吊向下负载吊杆与花兰螺丝）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="6Q直立单吊板恒吊", TooltipLong="CD-ZD2010 6Q 直立单吊板连接恒力弹簧组件", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L_body=LENGTH, TooltipShort="框架宽L", TooltipLong="直立框架宽度 L")
@param(W_body=LENGTH, TooltipShort="筒外径D", TooltipLong="下部弹簧筒外径 D")
@param(H_body=LENGTH, TooltipShort="壳体总高A", TooltipLong="直立壳体高度 A", Ask4Dist=True)
@param(Pin_d=LENGTH, TooltipShort="销孔径K", TooltipLong="顶吊板销孔径 K")
@param(Travel_mm=LENGTH, TooltipShort="行程", TooltipLong="工作行程")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="荷载", TooltipLong="工作荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_6Q(s, L_body=320.0, W_body=219.0, H_body=556.0, Pin_d=22.0, Travel_mm=120.0, ID=u"ZD_6Q", Load_kN=18.42, Weight_kg=40.5, **kw):
    L_body = float(L_body); W_body = float(W_body); H_body = float(H_body); Pin_d = float(Pin_d); Travel_mm = float(Travel_mm)
    if L_body < 160.0: L_body = 160.0
    if W_body < 120.0: W_body = 120.0
    if H_body < 300.0: H_body = 300.0
    if Pin_d < 12.0: Pin_d = 12.0

    R_cyl = min(W_body, L_body) * 0.46
    H_frame = H_body * 0.54
    H_cyl = H_body - H_frame
    z_junc = -H_frame
    z_btm = -H_body
    thk = max(8.0, min(16.0, R_cyl * 0.12))

    # 1. 下部竖直立置空心圆柱弹簧筒体 + 中部法兰板
    o1 = CYLINDER(s, R=R_cyl, H=H_cyl + thk, O=0.0).translate((0.0, 0.0, z_btm))
    o_in = CYLINDER(s, R=R_cyl - thk, H=max(20.0, H_cyl - thk * 2.0), O=0.0).translate((0.0, 0.0, z_btm + thk))
    o1.subtractFrom(o_in); o_in.erase()
    o_mid_flange = BOX(s, L=R_cyl * 2.1, W=thk * 1.5, H=L_body * 0.88).translate((0.0, 0.0, z_junc))
    o1.uniteWith(o_mid_flange); o_mid_flange.erase()

    # 2. 上部双侧凸轮摇臂框架壳体 + 顶板 + 转轴销 + 弧形导向槽
    plate_t = max(10.0, L_body * 0.04)
    frame_y = max(100.0, R_cyl * 1.45)
    frame_x = L_body * 0.92
    for sy in (-1.0, 1.0):
        yc = sy * (frame_y / 2.0)
        o_side = BOX(s, L=plate_t, W=H_frame, H=frame_x).translate((frame_x * 0.08, yc, -H_frame / 2.0))
        lobe_w = frame_x * 0.55
        lobe_h = H_frame * 0.52
        o_lobe = BOX(s, L=plate_t, W=lobe_h, H=lobe_w).translate((frame_x * 0.35, yc, z_junc + lobe_h * 0.45))
        o_side.uniteWith(o_lobe); o_lobe.erase()
        slot_h = min(H_frame * 0.45, max(35.0, Travel_mm * 0.55))
        o_slot = BOX(s, L=plate_t * 3.0, W=slot_h, H=max(12.0, frame_x * 0.07)).rotateY(-28.0).translate((frame_x * 0.28, yc, z_junc + H_frame * 0.36))
        o_side.subtractFrom(o_slot); o_slot.erase()
        o1.uniteWith(o_side); o_side.erase()

    o_top = BOX(s, L=frame_y + plate_t * 2.0, W=plate_t, H=L_body).translate((0.0, 0.0, -plate_t / 2.0))
    o1.uniteWith(o_top); o_top.erase()

    pin_r = max(14.0, R_cyl * 0.16)
    o_pin = CYLINDER(s, R=pin_r, H=frame_y + plate_t * 3.5, O=0.0).rotateX(90.0).translate((frame_x * 0.22, (frame_y + plate_t * 3.5) / 2.0, z_junc + H_frame * 0.32))
    o_cam = CYLINDER(s, R=H_frame * 0.26, H=frame_y * 0.5, O=0.0).rotateX(90.0).translate((frame_x * 0.26, frame_y * 0.25, z_junc + H_frame * 0.28))
    o1.uniteWith(o_pin); o_pin.erase()
    o1.uniteWith(o_cam); o_cam.erase()

    # 3. 6Q 专属顶部连接结构：上部框架顶面焊接直立双孔/单耳吊板 (含左、右对称两销孔，孔距 C，板厚 I，对照图集 p.254 6Q)
    ear_h = max(45.0, min(Pin_d * 2.4, H_frame * 0.28))
    ear_t = max(12.0, min(30.0, Pin_d * 0.65))
    ear_w = L_body * 0.82
    hole_r = min(Pin_d / 2.0, ear_h * 0.32)
    o_ear = BOX(s, L=ear_t, W=ear_h + 8.0, H=ear_w).translate((0.0, 0.0, (ear_h - 8.0) / 2.0))
    for sx in (-1.0, 1.0):
        xh = sx * (ear_w * 0.34)
        o_eh = CYLINDER(s, R=hole_r, H=ear_t * 3.0, O=0.0).rotateX(90.0).translate((xh, ear_t * 1.5, ear_h * 0.58))
        o_ear.subtractFrom(o_eh); o_eh.erase()
    o1.uniteWith(o_ear); o_ear.erase()

    # 4. 从上部摇臂侧面悬吊向下的负载吊杆与花兰螺丝
    rod_r = max(8.0, min(22.0, L_body * 0.035))
    x_load = frame_x * 0.44
    load_h = H_cyl * 0.92
    z_load_btm = z_junc - load_h
    o_lrod = CYLINDER(s, R=rod_r, H=load_h + H_frame * 0.25, O=0.0).translate((x_load, 0.0, z_load_btm))
    o_turn = CYLINDER(s, R=rod_r * 1.85, H=load_h * 0.45, O=0.0).translate((x_load, 0.0, z_load_btm + load_h * 0.15))
    o_thole = BOX(s, L=rod_r * 4.5, W=load_h * 0.26, H=rod_r * 1.1).translate((x_load, 0.0, z_load_btm + load_h * 0.38))
    o_turn.subtractFrom(o_thole); o_thole.erase()
    o1.uniteWith(o_lrod); o_lrod.erase()
    o1.uniteWith(o_turn); o_turn.erase()

    s.setPoint((0.0, 0.0, ear_h * 0.58), (0.0, 0.0, 1.0))
    s.setLinearDimension('H_body', (0.0, 0.0, 0.0), (0.0, 0.0, -H_body))
