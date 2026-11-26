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
          TooltipShort=u"法兰直流式截止阀 (GB/T 12235)",
          TooltipLong=u"法兰钢制直流式截止阀，含突面端法兰、标志性球形流道阀体、圆形中法兰阀盖、上支架、阀杆与辐条手轮",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"法兰直流式截止阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_OPEN=LENGTH, TooltipShort=u"全开总高", TooltipLong=u"管道中心至手轮顶面高度 H (mm)", Ask4Dist=True)
@param(D_HW=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"操作手轮外径 (mm)")
def VALVE_GLOBE_GBT12235(
    s,
    D=114.3,
    L_FACE=292.0,
    D_FL=220.0,
    C_FL=20.0,
    H_OPEN=430.0,
    D_HW=280.0,
    ID=u"VALVE_GLOBE_GBT12235",
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

    # 2. 流道颈管 + 标志性球形截止阀中腔 (偏心双球融合显S形流道感)
    o_pipe = CYLINDER(s, R=r_pipe * 1.12, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe)
    o_pipe.erase()

    r_globe = min(half_l - C_FL - 6.0, r_pipe * 1.62)
    o_sph = SPHERE(s, R=r_globe)
    o_main.uniteWith(o_sph)
    o_sph.erase()

    # 3. 圆形中法兰 + 锥形上阀盖
    z_mf = r_globe * 0.86
    mf_t = max(24.0, C_FL * 1.3)
    r_mf = r_globe * 1.06
    o_mf = CYLINDER(s, R=r_mf, H=mf_t, O=0.0).translate((0.0, 0.0, z_mf))
    o_main.uniteWith(o_mf)
    o_mf.erase()

    z_bon_top = z_mf + mf_t + max(42.0, r_pipe * 0.78)
    o_bon = CONE(s, R1=r_mf * 0.72, R2=max(24.0, r_pipe * 0.45), H=z_bon_top - (z_mf + mf_t) + 6.0, E=0.0).translate((0.0, 0.0, z_mf + mf_t - 4.0))
    o_main.uniteWith(o_bon)
    o_bon.erase()

    # 4. 填料函 + 支架 + 阀杆
    z_hw = H_OPEN - max(28.0, D_HW * 0.09)
    if z_hw < z_bon_top + 65.0:
        z_hw = z_bon_top + 65.0
    yoke_h = z_hw - z_bon_top
    leg_w = max(13.0, r_pipe * 0.21)
    span = max(32.0, r_pipe * 0.62)
    for sx in (-1.0, 1.0):
        o_leg = CORNERBOX(s, L=leg_w, W=leg_w * 1.35, H=yoke_h).translate((sx * span - leg_w / 2.0, -leg_w * 0.675, z_bon_top - 4.0))
        o_main.uniteWith(o_leg)
        o_leg.erase()

    o_ybase = CYLINDER(s, R=span + leg_w * 0.5, H=12.0, O=0.0).translate((0.0, 0.0, z_bon_top - 4.0))
    o_main.uniteWith(o_ybase)
    o_ybase.erase()
    o_ytop = CORNERBOX(s, L=span * 2.0 + leg_w, W=leg_w * 1.7, H=16.0).translate((-(span + leg_w / 2.0), -leg_w * 0.85, z_hw - 16.0))
    o_main.uniteWith(o_ytop)
    o_ytop.erase()

    o_gland = CYLINDER(s, R=max(20.0, r_pipe * 0.36), H=max(28.0, yoke_h * 0.32), O=0.0).translate((0.0, 0.0, z_bon_top))
    o_main.uniteWith(o_gland)
    o_gland.erase()

    r_stem = max(9.0, r_pipe * 0.16)
    o_stem = CYLINDER(s, R=r_stem, H=H_OPEN - z_bon_top + 10.0, O=0.0).translate((0.0, 0.0, z_bon_top - 10.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    # 5. 辐条手轮
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
