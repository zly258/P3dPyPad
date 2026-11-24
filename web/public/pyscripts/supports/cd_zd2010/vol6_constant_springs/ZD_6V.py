# -*- coding: utf-8 -*-
# CD-ZD2010 6V 下支式恒力弹簧组件（底部宽底座 + 梯形立式摇臂框架 + 竖置弹簧筒 + 斜向上伸出的摆臂连杆 + 顶部向上托举的圆形管道承重鞍座托盘）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="6V下支式恒力弹簧", TooltipLong="CD-ZD2010 6V 下支式恒力弹簧组件（顶撑式恒吊）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L_body=LENGTH, TooltipShort="底板长a", TooltipLong="底座板长度 a")
@param(W_body=LENGTH, TooltipShort="筒外径D", TooltipLong="弹簧筒外径 D")
@param(H_body=LENGTH, TooltipShort="框架高A", TooltipLong="主体框架高 A")
@param(Support_H=LENGTH, TooltipShort="总支高", TooltipLong="底座至顶撑托盘总高", Ask4Dist=True)
@param(Travel_mm=LENGTH, TooltipShort="位移量", TooltipLong="垂直恒力位移量")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="荷载", TooltipLong="工作荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_6V(s, L_body=330.0, W_body=325.0, H_body=648.0, Support_H=790.0, Travel_mm=120.0, ID=u"ZD_6V", Load_kN=26.1, Weight_kg=70.2, **kw):
    L_body = float(L_body); W_body = float(W_body); H_body = float(H_body); Support_H = float(Support_H); Travel_mm = float(Travel_mm)
    if L_body < 180.0: L_body = 180.0
    if W_body < 150.0: W_body = 150.0
    if H_body < 300.0: H_body = 300.0
    if Support_H <= H_body + 60.0: Support_H = H_body + 120.0

    # 对照图集 p.259 6V：底部宽底座 (带四角三角翼板与 4-ØK 孔，位于 Z = -Support_H) + 下部空心圆柱弹簧筒体 D + 中上部梯形双侧立式摇臂框架 + 斜向上的摆臂托杆 + 顶部圆形管道承重托盘 (Z = 0.0)
    R_cyl = min(W_body, L_body) * 0.46
    base_t = max(12.0, H_body * 0.025)
    H_cyl = H_body * 0.48
    H_frame = H_body - H_cyl
    z_btm = -Support_H
    z_cyl_top = z_btm + base_t + H_cyl
    z_frame_top = z_btm + H_body
    thk = max(8.0, min(16.0, R_cyl * 0.12))

    # 1. 底部宽底座板 + 前后斜向三角支承翼板 (对照 p.259 俯视图与主视图)
    base_l = max(L_body * 1.25, R_cyl * 2.6)
    base_w = max(W_body * 1.15, R_cyl * 2.3)
    o1 = BOX(s, L=base_w, W=base_t, H=base_l).translate((-base_l * 0.08, 0.0, z_btm + base_t / 2.0))
    hole_r = max(7.0, R_cyl * 0.08)
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            o_bh = CYLINDER(s, R=hole_r, H=base_t * 3.0, O=0.0).translate((sx * base_l * 0.32, sy * base_w * 0.38, z_btm - base_t))
            o1.subtractFrom(o_bh); o_bh.erase()

    # 2. 下部立式空心圆柱弹簧筒体与左侧斜向加劲肋板 (Z in [z_btm + base_t, z_cyl_top])
    o_cyl = CYLINDER(s, R=R_cyl, H=H_cyl + thk, O=0.0).translate((0.0, 0.0, z_btm + base_t))
    o_in = CYLINDER(s, R=R_cyl - thk, H=max(20.0, H_cyl - thk * 2.0), O=0.0).translate((0.0, 0.0, z_btm + base_t + thk))
    o_cyl.subtractFrom(o_in); o_in.erase()
    o_mid_plate = BOX(s, L=base_w * 0.9, W=thk * 1.4, H=R_cyl * 2.2).translate((0.0, 0.0, z_cyl_top))
    o1.uniteWith(o_cyl); o_cyl.erase()
    o1.uniteWith(o_mid_plate); o_mid_plate.erase()

    # 左侧斜向三角形加强腹板 (连接底座左缘与弹簧筒顶板)
    for sy in (-1.0, 1.0):
        o_gusset = BOX(s, L=thk, W=H_cyl * 0.85, H=R_cyl * 0.95).rotateY(22.0).translate((-(R_cyl * 0.95), sy * R_cyl * 0.55, z_btm + base_t + H_cyl * 0.42))
        o1.uniteWith(o_gusset); o_gusset.erase()

    # 3. 中上部梯形双侧立式凸轮摇臂框架 (Z in [z_cyl_top, z_frame_top]) + 转轴销 + 弧形导向槽
    frame_w = R_cyl * 1.15
    plate_t = max(10.0, thk)
    for sy in (-1.0, 1.0):
        yc = sy * (frame_w / 2.0)
        o_fside = BOX(s, L=plate_t, W=H_frame, H=R_cyl * 1.55).translate((R_cyl * 0.15, yc, z_cyl_top + H_frame / 2.0))
        slot_h = min(H_frame * 0.55, max(30.0, Travel_mm * 0.48))
        o_slot = BOX(s, L=plate_t * 3.0, W=slot_h, H=max(12.0, R_cyl * 0.14)).rotateY(-24.0).translate((R_cyl * 0.35, yc, z_cyl_top + H_frame * 0.48))
        o_fside.subtractFrom(o_slot); o_slot.erase()
        o1.uniteWith(o_fside); o_fside.erase()

    pin_r = max(12.0, R_cyl * 0.14)
    o_pin1 = CYLINDER(s, R=pin_r, H=frame_w + plate_t * 3.0, O=0.0).rotateX(90.0).translate((0.0, (frame_w + plate_t * 3.0) / 2.0, z_cyl_top + H_frame * 0.35))
    o_pin2 = CYLINDER(s, R=pin_r * 0.85, H=frame_w + plate_t * 2.5, O=0.0).rotateX(90.0).translate((R_cyl * 0.25, (frame_w + plate_t * 2.5) / 2.0, z_cyl_top + H_frame * 0.78))
    o1.uniteWith(o_pin1); o_pin1.erase()
    o1.uniteWith(o_pin2); o_pin2.erase()

    # 4. 斜向上伸出的恒力摆臂连杆 + 顶部竖直支承立柱与圆形管道承重托盘 (顶面位于 Z = 0.0，对照 p.259 主视图左上角)
    x_load = -(R_cyl * 0.85)
    z_hinge = -(Support_H - H_body) * 0.65
    dx_arm = -x_load
    dz_arm = z_hinge - (z_cyl_top + H_frame * 0.35)
    arm_len = sqrt(dx_arm * dx_arm + dz_arm * dz_arm)
    arm_ang = degrees(atan2(dz_arm, dx_arm))
    o_arm = BOX(s, L=frame_w * 0.55, W=max(28.0, R_cyl * 0.28), H=arm_len + 20.0).rotateY(arm_ang).translate((x_load / 2.0, 0.0, (z_hinge + z_cyl_top + H_frame * 0.35) / 2.0))
    o_jpin = CYLINDER(s, R=pin_r * 0.9, H=frame_w * 0.85, O=0.0).rotateX(90.0).translate((x_load, frame_w * 0.425, z_hinge))
    o1.uniteWith(o_arm); o_arm.erase()
    o1.uniteWith(o_jpin); o_jpin.erase()

    # 顶部竖直载荷柱与圆形承重鞍座托盘 (顶面位于 Z = 0.0)
    post_h = abs(z_hinge)
    o_post = CYLINDER(s, R=max(16.0, R_cyl * 0.18), H=post_h, O=0.0).translate((x_load, 0.0, z_hinge))
    pad_r = max(55.0, R_cyl * 0.55)
    pad_t = max(14.0, base_t)
    o_pad = CYLINDER(s, R=pad_r, H=pad_t, O=0.0).translate((x_load, 0.0, -pad_t))
    o1.uniteWith(o_post); o_post.erase()
    o1.uniteWith(o_pad); o_pad.erase()

    s.setPoint((x_load, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('Support_H', (x_load, 0.0, 0.0), (x_load, 0.0, -Support_H))
