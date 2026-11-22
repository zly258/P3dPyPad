# -*- coding: utf-8 -*-
# CD-ZD2010 6S 直立底座连接恒力弹簧组件（倒置安装：上部为竖直立置圆柱形弹簧筒体 A1 + 下部为凸轮摇臂框架壳体 + 底部水平支承底座板 O + 侧面向下穿出的负载吊杆与花兰螺丝）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="6S直立底座恒吊", TooltipLong="CD-ZD2010 6S 直立底座连接恒力弹簧组件", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L_body=LENGTH, TooltipShort="框架宽", TooltipLong="框架横向宽")
@param(W_body=LENGTH, TooltipShort="筒外径D", TooltipLong="弹簧筒外径 D")
@param(H_body=LENGTH, TooltipShort="总高A", TooltipLong="壳体总高 A", Ask4Dist=True)
@param(Base_L=LENGTH, TooltipShort="底板长O", TooltipLong="生根底座总长 O")
@param(Travel_mm=LENGTH, TooltipShort="行程", TooltipLong="工作行程")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="荷载", TooltipLong="工作荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_6S(s, L_body=320.0, W_body=219.0, H_body=485.0, Base_L=420.0, Travel_mm=120.0, ID=u"ZD_6S", Load_kN=18.42, Weight_kg=40.5, **kw):
    L_body = float(L_body); W_body = float(W_body); H_body = float(H_body); Base_L = float(Base_L); Travel_mm = float(Travel_mm)
    if L_body < 160.0: L_body = 160.0
    if W_body < 120.0: W_body = 120.0
    if H_body < 300.0: H_body = 300.0
    if Base_L < L_body + 60.0: Base_L = L_body + 80.0

    # 对照图集 p.257 6S：上部为竖直立置圆柱形弹簧筒体 (Z in [-H_cyl, 0])，下部为凸轮摇臂框架壳体 (Z in [-H_body, -H_cyl])，框架下缘设水平支承底座板 O
    R_cyl = min(W_body, L_body) * 0.46
    H_cyl = H_body * 0.52
    H_frame = H_body - H_cyl
    z_junc = -H_cyl
    z_btm = -H_body
    thk = max(8.0, min(16.0, R_cyl * 0.12))
    base_t = max(14.0, H_body * 0.03)

    # 1. 上部竖直立置的空心圆柱弹簧筒体 + 顶封板 + 中部连接法兰 (Z in [z_junc, 0])
    o1 = CYLINDER(s, R=R_cyl, H=H_cyl, O=0.0).translate((0.0, 0.0, z_junc))
    o_in = CYLINDER(s, R=R_cyl - thk, H=max(20.0, H_cyl - thk * 2.0), O=0.0).translate((0.0, 0.0, z_junc + thk))
    o1.subtractFrom(o_in); o_in.erase()
    o_mid_flange = BOX(s, L=R_cyl * 2.1, W=thk * 1.5, H=L_body * 0.92).translate((0.0, 0.0, z_junc))
    o1.uniteWith(o_mid_flange); o_mid_flange.erase()

    # 2. 下部双侧凸轮摇臂框架壳体 + 转轴销 + 弧形导向槽 (Z in [z_btm + base_t, z_junc])
    plate_t = max(10.0, L_body * 0.04)
    frame_y = max(100.0, R_cyl * 1.45)
    frame_x = L_body * 0.92
    fh = H_frame - base_t
    for sy in (-1.0, 1.0):
        yc = sy * (frame_y / 2.0)
        o_side = BOX(s, L=plate_t, W=fh + thk, H=frame_x).translate((frame_x * 0.08, yc, z_btm + base_t + fh / 2.0))
        lobe_w = frame_x * 0.55
        lobe_h = fh * 0.65
        o_lobe = BOX(s, L=plate_t, W=lobe_h, H=lobe_w).translate((frame_x * 0.35, yc, z_btm + base_t + lobe_h * 0.55))
        o_side.uniteWith(o_lobe); o_lobe.erase()
        slot_h = min(fh * 0.48, max(35.0, Travel_mm * 0.55))
        o_slot = BOX(s, L=plate_t * 3.0, W=slot_h, H=max(12.0, frame_x * 0.07)).rotateY(28.0).translate((frame_x * 0.28, yc, z_btm + base_t + fh * 0.52))
        o_side.subtractFrom(o_slot); o_slot.erase()
        o1.uniteWith(o_side); o_side.erase()

    pin_r = max(14.0, R_cyl * 0.16)
    o_pin = CYLINDER(s, R=pin_r, H=frame_y + plate_t * 3.5, O=0.0).rotateX(90.0).translate((frame_x * 0.22, (frame_y + plate_t * 3.5) / 2.0, z_btm + base_t + fh * 0.55))
    o_cam = CYLINDER(s, R=fh * 0.32, H=frame_y * 0.5, O=0.0).rotateX(90.0).translate((frame_x * 0.26, frame_y * 0.25, z_btm + base_t + fh * 0.50))
    o1.uniteWith(o_pin); o_pin.erase()
    o1.uniteWith(o_cam); o_cam.erase()

    # 3. 6S 专属底部连接结构：框架下缘设加宽水平支承底座板 (长 Base_L，宽 P，带 4-ØK 安装孔与竖向肋板，搁置在双钢梁上，对照图集 p.257 6S)
    base_w = max(W_body * 1.35, frame_y + 80.0)
    o_base = BOX(s, L=base_w, W=base_t, H=Base_L).translate((frame_x * 0.12, 0.0, z_btm + base_t / 2.0))
    hole_r = max(7.0, W_body * 0.045)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            xb = frame_x * 0.12 + sx * (Base_L * 0.36)
            yb = sy * (base_w * 0.38)
            o_bh = CYLINDER(s, R=hole_r, H=base_t * 3.0, O=0.0).translate((xb, yb, z_btm - base_t))
            o_base.subtractFrom(o_bh); o_bh.erase()
    o1.uniteWith(o_base); o_base.erase()

    # 4. 从摇臂侧面穿过底座板向下悬垂的负载吊杆与花兰螺丝
    rod_r = max(8.0, min(22.0, L_body * 0.035))
    x_load = frame_x * 0.44
    load_h = max(120.0, H_body * 0.35)
    z_load_btm = z_btm - load_h
    o_lrod = CYLINDER(s, R=rod_r, H=load_h + fh * 0.5, O=0.0).translate((x_load, 0.0, z_load_btm))
    o_turn = CYLINDER(s, R=rod_r * 1.85, H=load_h * 0.52, O=0.0).translate((x_load, 0.0, z_load_btm + load_h * 0.18))
    o_thole = BOX(s, L=rod_r * 4.5, W=load_h * 0.28, H=rod_r * 1.1).translate((x_load, 0.0, z_load_btm + load_h * 0.44))
    o_turn.subtractFrom(o_thole); o_thole.erase()
    o1.uniteWith(o_lrod); o_lrod.erase()
    o1.uniteWith(o_turn); o_turn.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('H_body', (0.0, 0.0, 0.0), (0.0, 0.0, -H_body))
