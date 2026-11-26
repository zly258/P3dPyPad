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
          TooltipShort=u"气动对夹蝶阀 (带气缸执行器)",
          TooltipLong=u"气动对夹式蝶阀，含短圆环对夹阀体与定位耳、长阀杆颈、ISO支架、双作用水平气缸执行器、顶部回讯器与侧挂电磁阀",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="WAF")
@group("MainDimensions", TooltipLong=u"气动对夹蝶阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"对夹阀体端面至端面厚度 L (mm)", Ask4Dist=True)
@param(D_BODY=LENGTH, TooltipShort=u"阀体外径", TooltipLong=u"对夹圆环阀体外径 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"总高度", TooltipLong=u"管道中心至顶部回讯器顶面高度 H (mm)", Ask4Dist=True)
@param(L_ACT=LENGTH, TooltipShort=u"气缸长度", TooltipLong=u"水平气缸执行器总长 (mm)")
@param(D_ACT=LENGTH, TooltipShort=u"气缸外径", TooltipLong=u"气缸执行器缸体外径 (mm)")
def VALVE_BUTTERFLY_PNEU(
    s,
    D=168.3,
    L_FACE=56.0,
    D_BODY=212.0,
    H_TOTAL=520.0,
    L_ACT=360.0,
    D_ACT=135.0,
    ID=u"VALVE_BUTTERFLY_PNEU",
    **kw
):
    D = max(40.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_BODY = max(D + 24.0, float(D_BODY))
    D_ACT = max(70.0, float(D_ACT))
    L_ACT = max(180.0, float(L_ACT))
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_body = D_BODY / 2.0
    r_act = D_ACT / 2.0

    # 1. 对夹短圆环阀体 + 4耳定位
    o_main = CYLINDER(s, R=r_body, H=L_FACE - 4.0, O=0.0).rotateY(90.0).translate((-(half_l - 2.0), 0.0, 0.0))
    o_seal = CYLINDER(s, R=r_body * 0.88, H=L_FACE, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_main.uniteWith(o_seal)
    o_seal.erase()

    lug_r = max(12.0, r_body * 0.15)
    lug_dist = r_body + lug_r * 0.42
    for sy in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            o_lug = CYLINDER(s, R=lug_r, H=L_FACE - 8.0, O=0.0).rotateY(90.0).translate((-(half_l - 4.0), sy * lug_dist * 0.7071, sz * lug_dist * 0.7071))
            o_main.uniteWith(o_lug)
            o_lug.erase()

    o_bot = CYLINDER(s, R=max(18.0, r_body * 0.2), H=26.0, O=0.0).translate((0.0, 0.0, -(r_body + 16.0)))
    o_main.uniteWith(o_bot)
    o_bot.erase()

    # 2. 长阀杆颈 + ISO 5211 顶台 + 气缸支架
    z_act_bot = H_TOTAL - D_ACT - 74.0
    z_pad = z_act_bot - 48.0
    if z_pad < r_body + 65.0:
        z_pad = r_body + 65.0
        z_act_bot = z_pad + 48.0

    r_neck = max(19.0, r_pipe * 0.28)
    o_neck = CYLINDER(s, R=r_neck, H=z_pad - r_body * 0.7 + 4.0, O=0.0).translate((0.0, 0.0, r_body * 0.7 - 4.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    pad_w = max(66.0, r_neck * 3.1)
    o_pad = CORNERBOX(s, L=pad_w, W=pad_w, H=12.0).translate((-pad_w / 2.0, -pad_w / 2.0, z_pad - 6.0))
    o_main.uniteWith(o_pad)
    o_pad.erase()

    brk_h = z_act_bot - z_pad
    for sx in (-1.0, 1.0):
        o_leg = CORNERBOX(s, L=10.0, W=pad_w * 0.8, H=brk_h + 6.0).translate((sx * pad_w * 0.38 - 5.0, -pad_w * 0.4, z_pad + 2.0))
        o_main.uniteWith(o_leg)
        o_leg.erase()

    o_coup = CYLINDER(s, R=max(14.0, r_neck * 0.65), H=brk_h + 14.0, O=0.0).translate((0.0, 0.0, z_pad))
    o_main.uniteWith(o_coup)
    o_coup.erase()

    o_tpl = CORNERBOX(s, L=pad_w * 1.1, W=pad_w * 1.1, H=12.0).translate((-pad_w * 0.55, -pad_w * 0.55, z_act_bot - 4.0))
    o_main.uniteWith(o_tpl)
    o_tpl.erase()

    # 3. 水平双缸气缸执行器 (沿 Y 轴或 X 轴，沿 X 轴对称布置)
    z_act_ctr = z_act_bot + r_act
    cap_t = max(20.0, L_ACT * 0.08)
    o_cyl = CYLINDER(s, R=r_act * 0.94, H=L_ACT - 2.0 * cap_t + 4.0, O=0.0).rotateY(90.0).translate((-(L_ACT / 2.0 - cap_t + 2.0), 0.0, z_act_ctr))
    o_main.uniteWith(o_cyl)
    o_cyl.erase()

    mid_l = L_ACT * 0.28
    o_mid = CORNERBOX(s, L=mid_l, W=D_ACT * 1.04, H=D_ACT * 1.04).translate((-mid_l / 2.0, -D_ACT * 0.52, z_act_ctr - D_ACT * 0.52))
    o_main.uniteWith(o_mid)
    o_mid.erase()

    cap_w = D_ACT * 1.08
    for sx in (-1.0, 1.0):
        cx = -L_ACT / 2.0 if sx < 0.0 else (L_ACT / 2.0 - cap_t)
        o_cap = CORNERBOX(s, L=cap_t, W=cap_w, H=cap_w).translate((cx, -cap_w / 2.0, z_act_ctr - cap_w / 2.0))
        o_main.uniteWith(o_cap)
        o_cap.erase()

    # 4. 顶部回讯器 + 侧挂电磁阀
    z_act_top = z_act_ctr + r_act
    sw_l = max(84.0, D_ACT * 0.72)
    sw_w = max(72.0, D_ACT * 0.62)
    sw_h = max(44.0, H_TOTAL - z_act_top - 22.0)
    o_swn = CYLINDER(s, R=max(15.0, r_act * 0.28), H=20.0, O=0.0).translate((0.0, 0.0, z_act_top - 4.0))
    o_main.uniteWith(o_swn)
    o_swn.erase()

    o_sw = CORNERBOX(s, L=sw_l, W=sw_w, H=sw_h).translate((-sw_l / 2.0, -sw_w / 2.0, z_act_top + 12.0))
    o_main.uniteWith(o_sw)
    o_sw.erase()

    o_ind = CYLINDER(s, R=max(17.0, sw_w * 0.28), H=14.0, O=0.0).translate((0.0, 0.0, z_act_top + 12.0 + sw_h - 2.0))
    o_main.uniteWith(o_ind)
    o_ind.erase()

    sol_l = max(68.0, L_ACT * 0.24)
    sol_w = max(40.0, D_ACT * 0.34)
    sol_h = max(52.0, D_ACT * 0.44)
    o_sol = CORNERBOX(s, L=sol_l, W=sol_w, H=sol_h).translate((-sol_l / 2.0, -(r_act + sol_w - 6.0), z_act_ctr - sol_h / 2.0))
    o_main.uniteWith(o_sol)
    o_sol.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
