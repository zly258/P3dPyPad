# -*- coding: utf-8 -*-
# CD-ZD2010 6T 直立并联连接恒力弹簧组件（左右两台对称直立式恒力弹簧筒体 + 水平双槽钢横担梁并联跨接 + 两端上部拉杆与花兰螺丝 + 中心下部悬挂组件）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="6T直立并联恒吊", TooltipLong="CD-ZD2010 6T 直立并联连接恒力弹簧组件", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L_body=LENGTH, TooltipShort="单箱前后宽", TooltipLong="单台恒吊前后宽度")
@param(W_body=LENGTH, TooltipShort="并联总跨宽", TooltipLong="并联双箱总跨宽", Ask4Dist=True)
@param(H_body=LENGTH, TooltipShort="总高A", TooltipLong="直立总高 A")
@param(Travel_mm=LENGTH, TooltipShort="行程", TooltipLong="工作行程")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="荷载", TooltipLong="工作荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_6T(s, L_body=320.0, W_body=720.0, H_body=640.0, Travel_mm=120.0, ID=u"ZD_6T", Load_kN=36.84, Weight_kg=87.1, **kw):
    L_body = float(L_body); W_body = float(W_body); H_body = float(H_body); Travel_mm = float(Travel_mm)
    if L_body < 160.0: L_body = 160.0
    if H_body < 320.0: H_body = 320.0
    if W_body < L_body * 1.6: W_body = L_body * 2.0

    # 对照图集 p.258 6T：左右两台对称直立式恒力弹簧（下部竖直圆柱弹簧筒 D + 上部凸轮摇臂框架），中部由一根水平双槽钢横担梁 (高 W) 并联跨接！
    R_cyl = L_body * 0.34
    H_cyl = H_body * 0.46
    H_frame = H_body - H_cyl
    z_junc = -H_frame
    z_btm = -H_body
    thk = max(8.0, min(15.0, R_cyl * 0.12))
    y_unit = (W_body / 2.0) - R_cyl * 1.15

    # 1. 中部水平双槽钢并联横担大梁 (沿 Y 轴跨接左右两台恒吊，截面高 beam_h，背靠背间隙 S)
    beam_h = max(100.0, H_frame * 0.38)
    beam_w = max(48.0, L_body * 0.18)
    beam_gap = max(24.0, L_body * 0.10)
    z_beam = z_junc + beam_h / 2.0 + thk
    o1 = BOX(s, L=W_body + R_cyl * 0.8, W=beam_h, H=beam_w).translate((-(beam_gap / 2.0 + beam_w / 2.0), 0.0, z_beam))
    o_b2 = BOX(s, L=W_body + R_cyl * 0.8, W=beam_h, H=beam_w).translate(((beam_gap / 2.0 + beam_w / 2.0), 0.0, z_beam))
    o1.uniteWith(o_b2); o_b2.erase()

    # 2. 左右两台完全对称的直立式恒力弹簧组件 (sy = -1 左台, sy = +1 右台)
    plate_t = max(10.0, L_body * 0.04)
    frame_w = R_cyl * 1.4
    rod_r = max(10.0, R_cyl * 0.12)
    for sy in (-1.0, 1.0):
        yc = sy * y_unit
        # (a) 下部竖直立置空心圆柱弹簧筒体 (Z in [z_btm, z_junc])
        o_cyl = CYLINDER(s, R=R_cyl, H=H_cyl + thk, O=0.0).translate((0.0, yc, z_btm))
        o_cin = CYLINDER(s, R=R_cyl - thk, H=max(20.0, H_cyl - thk * 2.0), O=0.0).translate((0.0, yc, z_btm + thk))
        o_cyl.subtractFrom(o_cin); o_cin.erase()
        o1.uniteWith(o_cyl); o_cyl.erase()

        # (b) 上部外侧扇形凸轮摇臂框架壳体与转轴销 (向左右外侧张开，完全对称于 p.258 图示)
        fh = H_frame * 0.65
        for sx in (-1.0, 1.0):
            xc = sx * (frame_w / 2.0)
            o_fside = BOX(s, L=R_cyl * 1.85, W=fh, H=plate_t).translate((xc, yc + sy * R_cyl * 0.25, z_junc + fh / 2.0))
            slot_h = min(fh * 0.5, max(30.0, Travel_mm * 0.45))
            o_slot = BOX(s, L=max(12.0, R_cyl * 0.14), W=slot_h, H=plate_t * 3.0).rotateX(sy * 25.0).translate((xc, yc + sy * R_cyl * 0.45, z_junc + fh * 0.52))
            o_fside.subtractFrom(o_slot); o_slot.erase()
            o1.uniteWith(o_fside); o_fside.erase()

        # 凸轮转轴销与内部凸轮盘
        o_pin = CYLINDER(s, R=rod_r * 1.2, H=frame_w + plate_t * 3.0, O=0.0).rotateY(90.0).translate((-(frame_w + plate_t * 3.0) / 2.0, yc + sy * R_cyl * 0.55, z_junc + fh * 0.48))
        o_cam = CYLINDER(s, R=fh * 0.34, H=frame_w * 0.48, O=0.0).rotateY(90.0).translate((-(frame_w * 0.24), yc + sy * R_cyl * 0.38, z_junc + fh * 0.45))
        o1.uniteWith(o_pin); o_pin.erase()
        o1.uniteWith(o_cam); o_cam.erase()

        # (c) 上部竖直向上伸出的拉杆与花兰螺丝调节器 (连接至 Z = 0.0)
        y_pull = yc - sy * R_cyl * 0.35
        pull_h = H_frame - fh * 0.4
        o_prod = CYLINDER(s, R=rod_r, H=pull_h + 30.0, O=0.0).translate((0.0, y_pull, -pull_h))
        o_pturn = CYLINDER(s, R=rod_r * 1.8, H=pull_h * 0.52, O=0.0).translate((0.0, y_pull, -pull_h * 0.72))
        o1.uniteWith(o_prod); o_prod.erase()
        o1.uniteWith(o_pturn); o_pturn.erase()

    # 3. 横担梁中心悬吊主吊杆及上下锁紧螺母座 (位于 Y = 0.0)
    center_rod_h = H_cyl + beam_h + 60.0
    o_crod = CYLINDER(s, R=rod_r * 1.25, H=center_rod_h, O=0.0).translate((0.0, 0.0, z_btm - 30.0))
    o_cplate = BOX(s, L=beam_w * 2.2, W=plate_t * 1.5, H=beam_w * 2.4 + beam_gap).translate((0.0, 0.0, z_beam + beam_h / 2.0 + plate_t * 0.75))
    o1.uniteWith(o_crod); o_crod.erase()
    o1.uniteWith(o_cplate); o_cplate.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('W_body', (0.0, -(W_body / 2.0), 0.0), (0.0, (W_body / 2.0), 0.0))
