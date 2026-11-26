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
          TooltipShort=u"三通法兰球阀 (T型)",
          TooltipLong=u"T型三通法兰钢制球阀，含三端突面法兰(X- / X+ / Y-)、中心球腔、ISO 5211 顶台与长扳手柄",
          LengthUnit="mm",
          Ports="3",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"三通法兰球阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"直通结构长度", TooltipLong=u"X向主通道两端法兰面距 L (mm)", Ask4Dist=True)
@param(L_BRANCH=LENGTH, TooltipShort=u"支口中心距", TooltipLong=u"阀体中心至-Y侧支口法兰端面距离 (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_LEVER=LENGTH, TooltipShort=u"手柄高度", TooltipLong=u"管道中心至手柄顶面高度 H (mm)", Ask4Dist=True)
@param(L_LEVER=LENGTH, TooltipShort=u"手柄长度", TooltipLong=u"阀杆中心至手柄末端长度 (mm)")
def VALVE_BALL_3WAY(
    s,
    D=88.9,
    L_FACE=260.0,
    L_BRANCH=130.0,
    D_FL=200.0,
    C_FL=20.0,
    H_LEVER=205.0,
    L_LEVER=310.0,
    ID=u"VALVE_BALL_3WAY",
    **kw
):
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    L_BRANCH = float(L_BRANCH)
    if L_BRANCH < 1.0:
        L_BRANCH = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    H_LEVER = float(H_LEVER)
    if H_LEVER < 1.0:
        H_LEVER = 1.0
    L_LEVER = max(160.0, float(L_LEVER))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.5
    r_rf = max(r_pipe + 8.0, r_fl * 0.72)
    fl_t = max(10.0, C_FL - rf_t)

    # 1. X- 与 X+ 端突面法兰
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

    # 2. Y- 支口突面法兰 (Port 3: 0, -L_BRANCH, 0)
    o_rf3 = CYLINDER(s, R=r_rf, H=rf_t + 2.0, O=0.0).rotateX(-90.0).translate((0.0, -L_BRANCH, 0.0))
    o_main.uniteWith(o_rf3)
    o_rf3.erase()
    o_fl3 = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).rotateX(-90.0).translate((0.0, -L_BRANCH + rf_t, 0.0))
    o_main.uniteWith(o_fl3)
    o_fl3.erase()

    # 3. 主流道管、支口管与中心球腔
    o_pipe_x = CYLINDER(s, R=r_pipe * 1.15, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe_x)
    o_pipe_x.erase()

    o_pipe_y = CYLINDER(s, R=r_pipe * 1.15, H=L_BRANCH - C_FL + 6.0, O=0.0).rotateX(-90.0).translate((0.0, -(L_BRANCH - C_FL + 3.0), 0.0))
    o_main.uniteWith(o_pipe_y)
    o_pipe_y.erase()

    r_ball = min(r_fl * 0.85, r_pipe * 1.62)
    o_sph = SPHERE(s, R=r_ball)
    o_main.uniteWith(o_sph)
    o_sph.erase()

    # 4. ISO 5211 顶台 + 阀杆 + 手柄
    z_pad = r_ball + 16.0
    o_neck = CYLINDER(s, R=max(22.0, r_pipe * 0.48), H=z_pad + 4.0, O=0.0)
    o_main.uniteWith(o_neck)
    o_neck.erase()

    pad_w = max(62.0, r_pipe * 1.28)
    o_pad = CORNERBOX(s, L=pad_w, W=pad_w, H=12.0).translate((-pad_w / 2.0, -pad_w / 2.0, z_pad - 2.0))
    o_main.uniteWith(o_pad)
    o_pad.erase()

    z_stem_top = H_LEVER - 14.0
    if z_stem_top < z_pad + 34.0:
        z_stem_top = z_pad + 34.0
    o_stem = CYLINDER(s, R=max(12.0, r_pipe * 0.24), H=z_stem_top - z_pad + 6.0, O=0.0).translate((0.0, 0.0, z_pad + 2.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    hub_r = max(18.0, r_pipe * 0.36)
    o_hub = CYLINDER(s, R=hub_r, H=22.0, O=0.0).translate((0.0, 0.0, z_stem_top - 10.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()

    bar_w = max(16.0, r_pipe * 0.3)
    bar_t = max(10.0, r_pipe * 0.17)
    o_arm = CORNERBOX(s, L=L_LEVER * 0.65, W=bar_w, H=bar_t).translate((-hub_r * 0.6, -bar_w / 2.0, H_LEVER - bar_t))
    o_main.uniteWith(o_arm)
    o_arm.erase()

    grip_l = L_LEVER * 0.42
    grip_r = max(11.0, bar_w * 0.65)
    o_grip = CYLINDER(s, R=grip_r, H=grip_l, O=0.0).rotateY(90.0).translate((L_LEVER - grip_l, 0.0, H_LEVER - bar_t / 2.0))
    o_main.uniteWith(o_grip)
    o_grip.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((0.0, -L_BRANCH, 0.0), (0.0, -1.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('L_BRANCH', (0.0, 0.0, 0.0), (0.0, -L_BRANCH, 0.0))
    s.setLinearDimension('H_LEVER', (0.0, 0.0, 0.0), (0.0, 0.0, H_LEVER))
