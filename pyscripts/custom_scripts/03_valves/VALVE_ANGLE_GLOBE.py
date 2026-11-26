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
          TooltipShort=u"90度角式截止阀 / 放料阀",
          TooltipLong=u"90度法兰角式截止阀(放料阀)。两个口都在水平面内成直角，手轮朝上；请连接在管端(端点)或设备管嘴转弯接管，不可直接插入连续直管中间",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"90度角式截止阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_OUT=LENGTH, TooltipShort=u"中心至侧口距", TooltipLong=u"阀体中心至右侧出口法兰端面距离 (mm)", Ask4Dist=True)
@param(H_IN=LENGTH, TooltipShort=u"中心至底口距", TooltipLong=u"阀体中心至底部入口法兰端面距离 (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"中心至手轮高", TooltipLong=u"阀体中心至手轮顶面高度 (mm)", Ask4Dist=True)
@param(D_HW=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"操作手轮外径 (mm)")
def VALVE_ANGLE_GLOBE(
    s,
    D=88.9,
    L_OUT=140.0,
    H_IN=140.0,
    D_FL=200.0,
    C_FL=20.0,
    H_TOP=360.0,
    D_HW=240.0,
    ID=u"VALVE_ANGLE_GLOBE",
    **kw
):
    D = max(25.0, float(D))
    L_OUT = float(L_OUT)
    if L_OUT < 1.0:
        L_OUT = 1.0
    H_IN = float(H_IN)
    if H_IN < 1.0:
        H_IN = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    D_HW = max(110.0, float(D_HW))
    H_TOP = float(H_TOP)
    if H_TOP < 1.0:
        H_TOP = 1.0

    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.5
    r_rf = max(r_pipe + 8.0, r_fl * 0.72)
    fl_t = max(10.0, C_FL - rf_t)

    # 1. 水平入口，沿 -Y。和 +X 出口正好成 90 度，都在布管平面里。
    #    圆柱默认沿 +Z，绕 X 转 -90 度后沿 +Y 生长，再挪到 y=-H_IN，外法向是 -Y。
    o_main = CYLINDER(s, R=r_rf, H=rf_t + 2.0, O=0.0).rotateX(-90.0).translate((0.0, -H_IN, 0.0))
    o_fl_in = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).rotateX(-90.0).translate((0.0, -H_IN + rf_t, 0.0))
    o_main.uniteWith(o_fl_in)
    o_fl_in.erase()
    o_in_neck = CYLINDER(s, R=r_pipe * 1.14, H=H_IN - C_FL + 6.0, O=0.0).rotateX(-90.0).translate((0.0, -H_IN + C_FL - 2.0, 0.0))
    o_main.uniteWith(o_in_neck)
    o_in_neck.erase()

    # 2. 右侧出口突面法兰 (Port 2: L_OUT, 0, 0)
    o_rf_out = CYLINDER(s, R=r_rf, H=rf_t + 2.0, O=0.0).rotateY(90.0).translate((L_OUT - rf_t - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_rf_out)
    o_rf_out.erase()
    o_fl_out = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).rotateY(90.0).translate((L_OUT - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl_out)
    o_fl_out.erase()
    o_out_neck = CYLINDER(s, R=r_pipe * 1.14, H=L_OUT - C_FL + 6.0, O=0.0).rotateY(90.0).translate((-4.0, 0.0, 0.0))
    o_main.uniteWith(o_out_neck)
    o_out_neck.erase()

    # 3. 球形转角阀体
    r_sph = max(10.0, min(L_OUT - C_FL - 4.0, r_pipe * 1.56))
    o_sph = SPHERE(s, R=r_sph)
    o_main.uniteWith(o_sph)
    o_sph.erase()

    # 4. 圆形中法兰 + 锥形阀盖 + 双柱支架 + 手轮
    z_mf = r_sph * 0.85
    mf_t = max(22.0, C_FL * 1.25)
    r_mf = r_sph * 1.08
    o_mf = CYLINDER(s, R=r_mf, H=mf_t, O=0.0).translate((0.0, 0.0, z_mf))
    o_main.uniteWith(o_mf)
    o_mf.erase()

    z_bon_top = z_mf + mf_t + max(38.0, r_pipe * 0.75)
    o_bon = CONE(s, R1=r_mf * 0.72, R2=max(22.0, r_pipe * 0.46), H=z_bon_top - (z_mf + mf_t) + 6.0, E=0.0).translate((0.0, 0.0, z_mf + mf_t - 4.0))
    o_main.uniteWith(o_bon)
    o_bon.erase()

    z_hw = H_TOP - max(24.0, D_HW * 0.09)
    if z_hw < z_bon_top + 60.0:
        z_hw = z_bon_top + 60.0
    yoke_h = z_hw - z_bon_top
    leg_w = max(12.0, r_pipe * 0.22)
    span = max(28.0, r_pipe * 0.62)
    for sx in (-1.0, 1.0):
        o_leg = CORNERBOX(s, L=leg_w, W=leg_w * 1.35, H=yoke_h).translate((sx * span - leg_w / 2.0, -leg_w * 0.675, z_bon_top - 4.0))
        o_main.uniteWith(o_leg)
        o_leg.erase()

    o_ybase = CYLINDER(s, R=span + leg_w * 0.5, H=12.0, O=0.0).translate((0.0, 0.0, z_bon_top - 4.0))
    o_main.uniteWith(o_ybase)
    o_ybase.erase()
    o_ytop = CORNERBOX(s, L=span * 2.0 + leg_w, W=leg_w * 1.7, H=14.0).translate((-(span + leg_w / 2.0), -leg_w * 0.85, z_hw - 14.0))
    o_main.uniteWith(o_ytop)
    o_ytop.erase()

    r_stem = max(8.5, r_pipe * 0.17)
    o_stem = CYLINDER(s, R=r_stem, H=H_TOP - z_bon_top + 10.0, O=0.0).translate((0.0, 0.0, z_bon_top - 10.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    r_hw = D_HW / 2.0
    r_rim = max(8.5, D_HW * 0.044)
    o_rim = TORUS(s, R1=r_hw - r_rim, R2=r_rim).translate((0.0, 0.0, z_hw))
    o_main.uniteWith(o_rim)
    o_rim.erase()
    o_hub = CYLINDER(s, R=max(18.0, r_stem * 2.1), H=22.0, O=0.0).translate((0.0, 0.0, z_hw - 11.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()
    for ang in (0.0, 90.0):
        o_sp = CYLINDER(s, R=r_rim * 0.72, H=(r_hw - r_rim) * 2.0, O=0.0).rotateY(90.0).translate((-(r_hw - r_rim), 0.0, z_hw)).rotateZ(ang)
        o_main.uniteWith(o_sp)
        o_sp.erase()

    s.setPoint((L_OUT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((0.0, -H_IN, 0.0), (0.0, -1.0, 0.0))
    s.setLinearDimension('L_OUT', (0.0, 0.0, 0.0), (L_OUT, 0.0, 0.0))
    s.setLinearDimension('H_IN', (0.0, 0.0, 0.0), (0.0, -H_IN, 0.0))
    s.setLinearDimension('H_TOP', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
