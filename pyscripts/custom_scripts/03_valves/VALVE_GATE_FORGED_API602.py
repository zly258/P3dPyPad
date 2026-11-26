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
          TooltipShort=u"锻钢承插焊小闸阀 (API 602)",
          TooltipLong=u"API 602 高压锻钢承插焊(SW)小口径闸阀，含锻造六角/阶梯承插端、螺栓压盖中法兰、紧凑支架、明杆与小手轮",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="SW")
@group("MainDimensions", TooltipLong=u"锻钢承插焊小闸阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"承插端面至端面总长 L (mm)", Ask4Dist=True)
@param(D_BOSS=LENGTH, TooltipShort=u"承插端外径", TooltipLong=u"承插焊端锻造凸台外径 (mm)")
@param(H_OPEN=LENGTH, TooltipShort=u"全开总高", TooltipLong=u"管道中心至阀杆顶面高度 H (mm)", Ask4Dist=True)
@param(D_HW=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"操作手轮外径 (mm)")
def VALVE_GATE_FORGED_API602(
    s,
    D=33.4,
    L_FACE=111.0,
    D_BOSS=52.0,
    H_OPEN=225.0,
    D_HW=110.0,
    ID=u"VALVE_GATE_FORGED_API602",
    **kw
):
    D = max(14.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_BOSS = max(D + 12.0, float(D_BOSS))
    D_HW = max(75.0, float(D_HW))
    H_OPEN = float(H_OPEN)
    if H_OPEN < 1.0:
        H_OPEN = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_boss = D_BOSS / 2.0
    sw_l = max(20.0, L_FACE * 0.24)

    # 1. 左右锻造承插焊端 (圆形厚壁承口 + 过渡颈)
    o_main = CYLINDER(s, R=r_boss, H=sw_l, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_sw2 = CYLINDER(s, R=r_boss, H=sw_l, O=0.0).rotateY(90.0).translate((half_l - sw_l, 0.0, 0.0))
    o_main.uniteWith(o_sw2)
    o_sw2.erase()

    o_mid_pipe = CYLINDER(s, R=r_boss * 0.86, H=L_FACE - 2.0 * sw_l + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - sw_l + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_mid_pipe)
    o_mid_pipe.erase()

    # 2. 锻造中腔体与方形螺栓中法兰
    body_l = max(36.0, L_FACE * 0.44)
    body_w = max(D_BOSS * 1.15, 56.0)
    z_bot = -r_boss * 1.08
    z_mf = r_boss * 1.15
    o_body = CORNERBOX(s, L=body_l, W=body_w, H=z_mf - z_bot).translate((-body_l / 2.0, -body_w / 2.0, z_bot))
    o_main.uniteWith(o_body)
    o_body.erase()

    mf_w = body_w * 1.26
    mf_l = body_l * 1.24
    mf_t = max(16.0, r_boss * 0.65)
    o_mf = CORNERBOX(s, L=mf_l, W=mf_w, H=mf_t).translate((-mf_l / 2.0, -mf_w / 2.0, z_mf - 2.0))
    o_main.uniteWith(o_mf)
    o_mf.erase()

    # 四个角部螺栓头凸台
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            o_bolt = CYLINDER(s, R=max(4.5, mf_w * 0.08), H=mf_t + 10.0, O=0.0).translate((sx * mf_l * 0.36, sy * mf_w * 0.36, z_mf - 7.0))
            o_main.uniteWith(o_bolt)
            o_bolt.erase()

    # 3. 锻钢一体式阀盖与紧凑双柱支架
    z_bon_top = z_mf + mf_t + max(24.0, r_boss * 0.9)
    o_bon = CYLINDER(s, R=r_boss * 0.72, H=z_bon_top - (z_mf + mf_t) + 6.0, O=0.0).translate((0.0, 0.0, z_mf + mf_t - 4.0))
    o_main.uniteWith(o_bon)
    o_bon.erase()

    z_hw = H_OPEN - max(32.0, H_OPEN * 0.16)
    if z_hw < z_bon_top + 42.0:
        z_hw = z_bon_top + 42.0
    yoke_h = z_hw - z_bon_top
    leg_w = max(9.0, r_boss * 0.32)
    span = max(18.0, r_boss * 0.68)
    for sx in (-1.0, 1.0):
        o_leg = CORNERBOX(s, L=leg_w, W=leg_w * 1.3, H=yoke_h + 4.0).translate((sx * span - leg_w / 2.0, -leg_w * 0.65, z_bon_top - 4.0))
        o_main.uniteWith(o_leg)
        o_leg.erase()

    o_ytop = CORNERBOX(s, L=span * 2.0 + leg_w, W=leg_w * 1.6, H=12.0).translate((-(span + leg_w / 2.0), -leg_w * 0.8, z_hw - 12.0))
    o_main.uniteWith(o_ytop)
    o_ytop.erase()

    # 填料压盖
    o_gland = CORNERBOX(s, L=span * 1.4, W=leg_w * 1.6, H=8.0).translate((-span * 0.7, -leg_w * 0.8, z_bon_top + yoke_h * 0.28))
    o_main.uniteWith(o_gland)
    o_gland.erase()

    # 4. 明杆 + 手轮
    r_stem = max(5.5, r_pipe * 0.32)
    o_stem = CYLINDER(s, R=r_stem, H=H_OPEN - z_bon_top + 10.0, O=0.0).translate((0.0, 0.0, z_bon_top - 10.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    r_hw = D_HW / 2.0
    r_rim = max(6.0, D_HW * 0.055)
    o_rim = TORUS(s, R1=r_hw - r_rim, R2=r_rim).translate((0.0, 0.0, z_hw))
    o_main.uniteWith(o_rim)
    o_rim.erase()
    o_hub = CYLINDER(s, R=max(13.0, r_stem * 2.2), H=16.0, O=0.0).translate((0.0, 0.0, z_hw - 8.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()
    for ang in (0.0, 90.0):
        o_sp = CYLINDER(s, R=r_rim * 0.7, H=(r_hw - r_rim) * 2.0, O=0.0).rotateY(90.0).translate((-(r_hw - r_rim), 0.0, z_hw)).rotateZ(ang)
        o_main.uniteWith(o_sp)
        o_sp.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_OPEN', (0.0, 0.0, 0.0), (0.0, 0.0, H_OPEN))
