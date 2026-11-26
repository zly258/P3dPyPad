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
          TooltipShort=u"Y型直流斜杆截止阀",
          TooltipLong=u"Y型直流斜杆法兰截止阀，含突面端法兰、直通低阻流道、45度倾斜阀盖与支架、斜置明杆与手轮",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"Y型直流斜杆截止阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(L_STEM=LENGTH, TooltipShort=u"斜杆总长", TooltipLong=u"阀体中心沿45度斜轴至手轮顶面长度 (mm)", Ask4Dist=True)
@param(D_HW=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"操作手轮外径 (mm)")
def VALVE_GLOBE_Y_TYPE(
    s,
    D=114.3,
    L_FACE=292.0,
    D_FL=220.0,
    C_FL=20.0,
    L_STEM=420.0,
    D_HW=260.0,
    ID=u"VALVE_GLOBE_Y_TYPE",
    **kw
):
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    D_HW = max(120.0, float(D_HW))
    L_STEM = float(L_STEM)
    if L_STEM < 1.0:
        L_STEM = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.5
    r_rf = max(r_pipe + 8.0, r_fl * 0.72)
    fl_t = max(10.0, C_FL - rf_t)

    # 1. 左右突面端法兰 + 主水平流道
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

    o_pipe = CYLINDER(s, R=r_pipe * 1.18, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe)
    o_pipe.erase()

    o_sph = SPHERE(s, R=r_pipe * 1.42)
    o_main.uniteWith(o_sph)
    o_sph.erase()

    # 2. 先在局部竖直 Z 轴构造完整的斜阀盖+支架+明杆+手轮组件，再整体 rotateY(45.0)
    z_mf = r_pipe * 1.25
    mf_t = max(22.0, C_FL * 1.2)
    r_mf = r_pipe * 1.48

    o_y = CYLINDER(s, R=r_pipe * 1.15, H=z_mf + 4.0, O=0.0)
    o_mf = CYLINDER(s, R=r_mf, H=mf_t, O=0.0).translate((0.0, 0.0, z_mf))
    o_y.uniteWith(o_mf)
    o_mf.erase()

    z_bon_top = z_mf + mf_t + max(42.0, r_pipe * 0.75)
    o_bon = CONE(s, R1=r_mf * 0.72, R2=max(22.0, r_pipe * 0.44), H=z_bon_top - (z_mf + mf_t) + 6.0, E=0.0).translate((0.0, 0.0, z_mf + mf_t - 4.0))
    o_y.uniteWith(o_bon)
    o_bon.erase()

    z_hw = L_STEM - max(28.0, D_HW * 0.1)
    if z_hw < z_bon_top + 65.0:
        z_hw = z_bon_top + 65.0
    yoke_h = z_hw - z_bon_top
    leg_w = max(12.0, r_pipe * 0.2)
    span = max(30.0, r_pipe * 0.58)
    for sy in (-1.0, 1.0):
        o_leg = CORNERBOX(s, L=leg_w * 1.35, W=leg_w, H=yoke_h).translate((-leg_w * 0.675, sy * span - leg_w / 2.0, z_bon_top - 4.0))
        o_y.uniteWith(o_leg)
        o_leg.erase()

    o_ybase = CYLINDER(s, R=span + leg_w * 0.5, H=12.0, O=0.0).translate((0.0, 0.0, z_bon_top - 4.0))
    o_y.uniteWith(o_ybase)
    o_ybase.erase()
    o_ytop = CORNERBOX(s, L=leg_w * 1.7, W=span * 2.0 + leg_w, H=16.0).translate((-leg_w * 0.85, -(span + leg_w / 2.0), z_hw - 16.0))
    o_y.uniteWith(o_ytop)
    o_ytop.erase()

    r_stem = max(9.0, r_pipe * 0.16)
    o_stem = CYLINDER(s, R=r_stem, H=L_STEM - z_bon_top + 10.0, O=0.0).translate((0.0, 0.0, z_bon_top - 10.0))
    o_y.uniteWith(o_stem)
    o_stem.erase()

    r_hw = D_HW / 2.0
    r_rim = max(8.5, D_HW * 0.042)
    o_rim = TORUS(s, R1=r_hw - r_rim, R2=r_rim).translate((0.0, 0.0, z_hw))
    o_y.uniteWith(o_rim)
    o_rim.erase()
    o_hub = CYLINDER(s, R=max(18.0, r_stem * 2.1), H=22.0, O=0.0).translate((0.0, 0.0, z_hw - 11.0))
    o_y.uniteWith(o_hub)
    o_hub.erase()
    for ang in (0.0, 90.0):
        o_sp = CYLINDER(s, R=r_rim * 0.72, H=(r_hw - r_rim) * 2.0, O=0.0).rotateY(90.0).translate((-(r_hw - r_rim), 0.0, z_hw)).rotateZ(ang)
        o_y.uniteWith(o_sp)
        o_sp.erase()

    o_y.rotateY(45.0)
    o_main.uniteWith(o_y)
    o_y.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('L_STEM', (0.0, 0.0, 0.0), (L_STEM * 0.7071, 0.0, L_STEM * 0.7071))
