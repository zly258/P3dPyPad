# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except (NameError, AttributeError):
    pass

from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *

@activate(Group="Valve",
          TooltipShort=u"法兰明杆楔式闸阀 (GB/T 12221)",
          TooltipLong=u"法兰连接明杆楔式弹性闸阀，含突面端法兰、扁圆中腔、中法兰阀盖、梯形支架、明杆与辐条手轮",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"法兰明杆楔式闸阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_OPEN=LENGTH, TooltipShort=u"全开总高", TooltipLong=u"管道中心至明杆顶部全开高度 H (mm)", Ask4Dist=True)
@param(D_HW=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"操作手轮外径 (mm)")
def VALVE_GATE_GBT12221(
    s,
    D=114.3,
    L_FACE=229.0,
    D_FL=220.0,
    C_FL=20.0,
    H_OPEN=520.0,
    D_HW=280.0,
    ID=u"VALVE_GATE_GBT12221",
    **kw
):
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    D_HW = max(120.0, float(D_HW))
    H_OPEN = float(H_OPEN)
    if H_OPEN < 1.0:
        H_OPEN = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.5
    r_rf = max(r_pipe + 8.0, r_fl * 0.72)
    fl_t = max(10.0, C_FL - rf_t)

    # 1. 左右突面端法兰 (RF 台阶 + 法兰盘)
    o_main = CYLINDER(s, R=r_rf, H=rf_t + 2.0, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl1 = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).rotateY(90.0).translate((-half_l + rf_t, 0.0, 0.0))
    o_main.uniteWith(o_fl1)
    o_fl1.erase()

    o_rf2 = CYLINDER(s, R=r_rf, H=rf_t + 2.0, O=0.0).rotateY(90.0).translate((half_l - rf_t - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_rf2)
    o_rf2.erase()
    o_fl2 = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    # 2. 流道颈管与扁圆/圆柱形闸板中腔
    o_pipe = CYLINDER(s, R=r_pipe * 1.12, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe)
    o_pipe.erase()

    cav_x = min(L_FACE - 2.0 * C_FL - 12.0, max(r_pipe * 1.15, 52.0))
    cav_y = max(r_pipe * 1.55, 68.0)
    z_bot = -r_pipe * 1.25
    z_mid_fl = r_pipe * 1.38
    o_cav = CORNERBOX(s, L=cav_x, W=cav_y, H=z_mid_fl - z_bot).translate((-cav_x / 2.0, -cav_y / 2.0, z_bot))
    o_main.uniteWith(o_cav)
    o_cav.erase()
    for sy in (-1.0, 1.0):
        o_rib = CYLINDER(s, R=cav_x * 0.48, H=z_mid_fl - z_bot, O=0.0).translate((0.0, sy * (cav_y * 0.45), z_bot))
        o_main.uniteWith(o_rib)
        o_rib.erase()

    # 3. 椭圆形/跑道形中法兰 (上下两片压紧)
    mf_t = max(24.0, C_FL * 1.35)
    mf_rx = cav_x * 0.65
    mf_dy = cav_y * 0.48
    o_mf_box = CORNERBOX(s, L=mf_rx * 2.0, W=mf_dy * 2.0, H=mf_t).translate((-mf_rx, -mf_dy, z_mid_fl - 2.0))
    o_main.uniteWith(o_mf_box)
    o_mf_box.erase()
    for sy in (-1.0, 1.0):
        o_mf_end = CYLINDER(s, R=mf_rx, H=mf_t, O=0.0).translate((0.0, sy * mf_dy, z_mid_fl - 2.0))
        o_main.uniteWith(o_mf_end)
        o_mf_end.erase()

    # 4. 锥形上阀盖 + 填料函
    z_bon_top = z_mid_fl + mf_t + max(42.0, r_pipe * 0.85)
    o_bon = CONE(s, R1=min(mf_rx * 0.88, r_pipe * 0.85), R2=max(24.0, r_pipe * 0.48), H=z_bon_top - (z_mid_fl + mf_t) + 6.0, E=0.0).translate((0.0, 0.0, z_mid_fl + mf_t - 4.0))
    o_main.uniteWith(o_bon)
    o_bon.erase()

    z_gland_top = z_bon_top + max(28.0, r_pipe * 0.45)
    o_gland = CYLINDER(s, R=max(22.0, r_pipe * 0.42), H=z_gland_top - z_bon_top + 6.0, O=0.0).translate((0.0, 0.0, z_bon_top - 4.0))
    o_main.uniteWith(o_gland)
    o_gland.erase()
    o_gfl = CORNERBOX(s, L=max(56.0, r_pipe * 1.0), W=max(32.0, r_pipe * 0.55), H=10.0).translate((-max(28.0, r_pipe * 0.5), -max(16.0, r_pipe * 0.275), z_gland_top - 8.0))
    o_main.uniteWith(o_gfl)
    o_gfl.erase()

    # 5. 梯形支架 (双立柱 + 顶横梁与支架螺母)
    z_hw = H_OPEN - max(75.0, r_pipe * 1.45)
    if z_hw < z_gland_top + 70.0:
        z_hw = z_gland_top + 70.0
    yoke_h = z_hw - z_bon_top
    leg_w = max(14.0, r_pipe * 0.22)
    leg_span_bot = max(38.0, r_pipe * 0.72)
    leg_span_top = max(24.0, r_pipe * 0.46)
    for sx in (-1.0, 1.0):
        # 用上下两段拼接形成稳固梯形支架腿
        o_l1 = CORNERBOX(s, L=leg_w, W=leg_w * 1.35, H=yoke_h * 0.55).translate((sx * leg_span_bot - leg_w / 2.0, -leg_w * 0.675, z_bon_top - 4.0))
        o_main.uniteWith(o_l1)
        o_l1.erase()
        o_l2 = CORNERBOX(s, L=leg_w, W=leg_w * 1.35, H=yoke_h * 0.55).translate((sx * leg_span_top - leg_w / 2.0, -leg_w * 0.675, z_bon_top + yoke_h * 0.45))
        o_main.uniteWith(o_l2)
        o_l2.erase()
        o_tie = CORNERBOX(s, L=abs(leg_span_bot - leg_span_top) + leg_w, W=leg_w * 1.35, H=leg_w).translate((min(sx * leg_span_bot, sx * leg_span_top) - leg_w / 2.0, -leg_w * 0.675, z_bon_top + yoke_h * 0.46))
        o_main.uniteWith(o_tie)
        o_tie.erase()

    o_yoke_base = CORNERBOX(s, L=leg_span_bot * 2.0 + leg_w, W=leg_w * 1.6, H=12.0).translate((-(leg_span_bot + leg_w / 2.0), -leg_w * 0.8, z_bon_top - 4.0))
    o_main.uniteWith(o_yoke_base)
    o_yoke_base.erase()

    o_yoke_top = CORNERBOX(s, L=leg_span_top * 2.0 + leg_w, W=leg_w * 1.8, H=16.0).translate((-(leg_span_top + leg_w / 2.0), -leg_w * 0.9, z_hw - 16.0))
    o_main.uniteWith(o_yoke_top)
    o_yoke_top.erase()

    o_nut = CYLINDER(s, R=max(18.0, r_pipe * 0.34), H=34.0, O=0.0).translate((0.0, 0.0, z_hw - 22.0))
    o_main.uniteWith(o_nut)
    o_nut.erase()

    # 6. 明杆 (贯穿填料函至全开顶高)
    r_stem = max(9.0, r_pipe * 0.16)
    o_stem = CYLINDER(s, R=r_stem, H=H_OPEN - z_gland_top + 10.0, O=0.0).translate((0.0, 0.0, z_gland_top - 10.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    # 7. 辐条手轮 (圆环 + 4 根辐条 + 轮毂)
    r_hw = D_HW / 2.0
    r_rim = max(9.0, D_HW * 0.042)
    o_rim = TORUS(s, R1=r_hw - r_rim, R2=r_rim).translate((0.0, 0.0, z_hw))
    o_main.uniteWith(o_rim)
    o_rim.erase()
    o_hub = CYLINDER(s, R=max(20.0, r_stem * 2.1), H=24.0, O=0.0).translate((0.0, 0.0, z_hw - 12.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()
    for ang in (0.0, 90.0):
        o_sp = CYLINDER(s, R=r_rim * 0.72, H=(r_hw - r_rim) * 2.0, O=0.0).rotateY(90.0).translate((-(r_hw - r_rim), 0.0, z_hw)).rotateZ(ang)
        o_main.uniteWith(o_sp)
        o_sp.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_OPEN', (0.0, 0.0, 0.0), (0.0, 0.0, H_OPEN))
