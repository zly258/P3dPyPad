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
          TooltipShort=u"双阻塞与泄放阀 (DBB)",
          TooltipLong=u"单阀体整体式双阻塞与泄放阀(Double Block & Bleed)，含突面端法兰、整体式锻钢阀体、顶部双球阀操纵杆及侧向针型泄放阀",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"双阻塞与泄放阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_LEVER=LENGTH, TooltipShort=u"操纵杆高度", TooltipLong=u"管道中心至顶部双操纵杆顶面高度 H (mm)", Ask4Dist=True)
@param(L_LEVER=LENGTH, TooltipShort=u"操纵杆长度", TooltipLong=u"阀杆中心至操纵杆末端长度 (mm)", Ask4Dist=True)
def VALVE_DBB_DOUBLE_BLOCK(
    s,
    D=114.3,
    L_FACE=356.0,
    D_FL=220.0,
    C_FL=20.0,
    H_LEVER=235.0,
    L_LEVER=290.0,
    ID=u"VALVE_DBB_DOUBLE_BLOCK",
    **kw
):
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    H_LEVER = float(H_LEVER)
    if H_LEVER < 1.0:
        H_LEVER = 1.0
    L_LEVER = float(L_LEVER)
    if L_LEVER < 1.0:
        L_LEVER = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.5
    r_rf = max(r_pipe + 8.0, r_fl * 0.72)
    fl_t = max(10.0, C_FL - rf_t)

    # 1. 左右突面端法兰
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

    # 2. 流道颈 + 整体式锻钢单阀体 (含中部加厚方箱体)
    body_span = L_FACE - 2.0 * C_FL
    o_pipe = CYLINDER(s, R=r_pipe * 1.15, H=body_span + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe)
    o_pipe.erase()

    box_l = max(100.0, body_span * 0.78)
    box_w = min(r_fl * 1.55, max(95.0, r_pipe * 2.45))
    box_h = box_w
    o_body = CORNERBOX(s, L=box_l, W=box_w, H=box_h).translate((-box_l / 2.0, -box_w / 2.0, -box_h / 2.0))
    o_main.uniteWith(o_body)
    o_body.erase()

    # 3. 顶部双阻塞球阀结构 (左右对称双阀盖 + 双阀杆 + 双平行操纵杆)
    dx_stem = max(36.0, box_l * 0.28)
    z_body_top = box_h / 2.0
    r_gland = max(18.0, r_pipe * 0.36)
    z_gland_top = z_body_top + max(22.0, r_pipe * 0.38)
    z_stem_top = max(z_gland_top + 28.0, H_LEVER - 14.0)

    hub_r = max(16.0, r_pipe * 0.28)
    bar_w = max(14.0, r_pipe * 0.22)
    bar_t = max(9.0, r_pipe * 0.14)
    grip_l = L_LEVER * 0.42
    grip_r = max(10.0, bar_w * 0.65)

    for sx in (-1.0, 1.0):
        cx = sx * dx_stem
        o_gl = CYLINDER(s, R=r_gland, H=z_gland_top - z_body_top + 6.0, O=0.0).translate((cx, 0.0, z_body_top - 4.0))
        o_main.uniteWith(o_gl)
        o_gl.erase()

        o_pad = CORNERBOX(s, L=r_gland * 2.3, W=r_gland * 2.3, H=10.0).translate((cx - r_gland * 1.15, -r_gland * 1.15, z_gland_top - 4.0))
        o_main.uniteWith(o_pad)
        o_pad.erase()

        o_st = CYLINDER(s, R=max(10.0, r_pipe * 0.18), H=z_stem_top - z_gland_top + 6.0, O=0.0).translate((cx, 0.0, z_gland_top))
        o_main.uniteWith(o_st)
        o_st.erase()

        o_hub = CYLINDER(s, R=hub_r, H=20.0, O=0.0).translate((cx, 0.0, z_stem_top - 8.0))
        o_main.uniteWith(o_hub)
        o_hub.erase()

        # 操纵杆沿 +Y 方向平行伸出，避免双杆相互干涉
        o_arm = CORNERBOX(s, L=bar_w, W=L_LEVER * 0.65, H=bar_t).translate((cx - bar_w / 2.0, -hub_r * 0.5, H_LEVER - bar_t))
        o_main.uniteWith(o_arm)
        o_arm.erase()

        o_grip = CYLINDER(s, R=grip_r, H=grip_l, O=0.0).rotateX(-90.0).translate((cx, L_LEVER - grip_l, H_LEVER - bar_t / 2.0))
        o_main.uniteWith(o_grip)
        o_grip.erase()

    # 4. 侧向针型泄放阀 (-Y 前侧中央位置)
    y_side = -box_w / 2.0
    bleed_len = max(48.0, r_pipe * 0.85)
    r_bleed = max(13.0, r_pipe * 0.22)
    o_b_boss = CYLINDER(s, R=r_bleed * 1.35, H=22.0, O=0.0).rotateX(90.0).translate((0.0, y_side + 4.0, 0.0))
    o_main.uniteWith(o_b_boss)
    o_b_boss.erase()

    o_b_stem = CYLINDER(s, R=r_bleed * 0.65, H=bleed_len, O=0.0).rotateX(90.0).translate((0.0, y_side - 12.0, 0.0))
    o_main.uniteWith(o_b_stem)
    o_b_stem.erase()

    y_tbar = y_side - 12.0 - bleed_len
    tbar_l = max(56.0, r_pipe * 0.95)
    o_tbar = CYLINDER(s, R=max(6.0, r_bleed * 0.42), H=tbar_l, O=0.0).rotateY(90.0).translate((-tbar_l / 2.0, y_tbar + 5.0, 0.0))
    o_main.uniteWith(o_tbar)
    o_tbar.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_LEVER', (0.0, 0.0, 0.0), (0.0, 0.0, H_LEVER))
    s.setLinearDimension('L_LEVER', (dx_stem, 0.0, H_LEVER), (dx_stem, L_LEVER, H_LEVER))
