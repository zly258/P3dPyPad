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
          TooltipShort=u"气动紧急切断球阀 XV/SDV",
          TooltipLong=u"气动紧急切断法兰球阀 (XV/SDV)，含突面端法兰球阀主体、ISO 5211 支架、水平双缸气缸执行器、顶部回讯器与侧挂电磁阀",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"气动紧急切断球阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"总高度", TooltipLong=u"管道中心至顶部回讯器顶面高度 H (mm)", Ask4Dist=True)
@param(L_ACT=LENGTH, TooltipShort=u"气缸长度", TooltipLong=u"双作用水平气缸执行器总长 (mm)")
@param(D_ACT=LENGTH, TooltipShort=u"气缸外径", TooltipLong=u"气缸执行器缸体外径 (mm)")
def VALVE_BALL_PNEU_SDV(
    s,
    D=114.3,
    L_FACE=229.0,
    D_FL=220.0,
    C_FL=20.0,
    H_TOTAL=460.0,
    L_ACT=380.0,
    D_ACT=145.0,
    ID=u"VALVE_BALL_PNEU_SDV",
    **kw
):
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    D_ACT = max(70.0, float(D_ACT))
    L_ACT = max(180.0, float(L_ACT))
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.5
    r_rf = max(r_pipe + 8.0, r_fl * 0.72)
    fl_t = max(10.0, C_FL - rf_t)
    r_ball = min(r_fl * 0.84, r_pipe * 1.5)
    r_act = D_ACT / 2.0

    # 1. 突面端法兰球阀主体
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

    o_body = CYLINDER(s, R=r_pipe * 1.14, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_body)
    o_body.erase()

    o_sph = SPHERE(s, R=r_ball)
    o_main.uniteWith(o_sph)
    o_sph.erase()

    # 2. ISO 5211 阀顶平台与双侧门式支架
    z_pad = r_ball + 16.0
    o_neck = CYLINDER(s, R=max(22.0, r_pipe * 0.46), H=z_pad + 4.0, O=0.0)
    o_main.uniteWith(o_neck)
    o_neck.erase()

    pad_w = max(65.0, r_pipe * 1.25)
    o_pad = CORNERBOX(s, L=pad_w, W=pad_w, H=12.0).translate((-pad_w / 2.0, -pad_w / 2.0, z_pad - 2.0))
    o_main.uniteWith(o_pad)
    o_pad.erase()

    z_act_bot = H_TOTAL - D_ACT - 76.0
    if z_act_bot < z_pad + 44.0:
        z_act_bot = z_pad + 44.0
    brk_h = z_act_bot - (z_pad + 6.0)
    for sx in (-1.0, 1.0):
        o_leg = CORNERBOX(s, L=10.0, W=pad_w * 0.82, H=brk_h + 6.0).translate((sx * (pad_w * 0.38) - 5.0, -pad_w * 0.41, z_pad + 4.0))
        o_main.uniteWith(o_leg)
        o_leg.erase()

    o_coup = CYLINDER(s, R=max(14.0, r_pipe * 0.28), H=brk_h + 16.0, O=0.0).translate((0.0, 0.0, z_pad + 2.0))
    o_main.uniteWith(o_coup)
    o_coup.erase()

    o_top_pl = CORNERBOX(s, L=pad_w * 1.1, W=pad_w * 1.1, H=12.0).translate((-pad_w * 0.55, -pad_w * 0.55, z_act_bot - 4.0))
    o_main.uniteWith(o_top_pl)
    o_top_pl.erase()

    # 3. 水平双缸气缸执行器 (中央齿条壳 + 左右双活塞缸筒 + 端盖)
    z_act_ctr = z_act_bot + r_act
    cap_t = max(20.0, L_ACT * 0.08)
    mid_l = L_ACT * 0.28
    o_mid = CORNERBOX(s, L=mid_l, W=D_ACT * 1.04, H=D_ACT * 1.04).translate((-mid_l / 2.0, -D_ACT * 0.52, z_act_ctr - D_ACT * 0.52))
    o_main.uniteWith(o_mid)
    o_mid.erase()

    o_cyl = CYLINDER(s, R=r_act * 0.94, H=L_ACT - 2.0 * cap_t + 4.0, O=0.0).rotateY(90.0).translate((-(L_ACT / 2.0 - cap_t + 2.0), 0.0, z_act_ctr))
    o_main.uniteWith(o_cyl)
    o_cyl.erase()

    cap_w = D_ACT * 1.08
    for sx in (-1.0, 1.0):
        cx = -L_ACT / 2.0 if sx < 0.0 else (L_ACT / 2.0 - cap_t)
        o_cap = CORNERBOX(s, L=cap_t, W=cap_w, H=cap_w).translate((cx, -cap_w / 2.0, z_act_ctr - cap_w / 2.0))
        o_main.uniteWith(o_cap)
        o_cap.erase()

    # 4. 顶部限位开关回讯器 + 圆顶视觉指示器
    z_act_top = z_act_ctr + r_act
    sw_l = max(86.0, D_ACT * 0.72)
    sw_w = max(76.0, D_ACT * 0.64)
    sw_h = max(46.0, H_TOTAL - z_act_top - 24.0)
    o_sw_neck = CYLINDER(s, R=max(16.0, r_act * 0.28), H=22.0, O=0.0).translate((0.0, 0.0, z_act_top - 4.0))
    o_main.uniteWith(o_sw_neck)
    o_sw_neck.erase()

    o_sw = CORNERBOX(s, L=sw_l, W=sw_w, H=sw_h).translate((-sw_l / 2.0, -sw_w / 2.0, z_act_top + 14.0))
    o_main.uniteWith(o_sw)
    o_sw.erase()

    o_ind = CYLINDER(s, R=max(18.0, sw_w * 0.28), H=16.0, O=0.0).translate((0.0, 0.0, z_act_top + 14.0 + sw_h - 2.0))
    o_main.uniteWith(o_ind)
    o_ind.erase()

    # 5. 侧挂 NAMUR 电磁阀箱 (-Y 侧)
    sol_l = max(72.0, L_ACT * 0.24)
    sol_w = max(42.0, D_ACT * 0.34)
    sol_h = max(55.0, D_ACT * 0.45)
    o_sol = CORNERBOX(s, L=sol_l, W=sol_w, H=sol_h).translate((-sol_l / 2.0, -(r_act + sol_w - 6.0), z_act_ctr - sol_h / 2.0))
    o_main.uniteWith(o_sol)
    o_sol.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
