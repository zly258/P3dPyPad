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
          TooltipShort=u"夹套保温法兰球阀",
          TooltipLong=u"夹套保温法兰球阀，含缩径加宽突面端法兰、外包加粗圆柱保温夹套壳体、上下双伴热介质小法兰口、ISO顶台与长手柄",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"夹套保温法兰球阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(D_JACKET=LENGTH, TooltipShort=u"夹套壳外径", TooltipLong=u"外包保温夹套筒体外径 (mm)")
@param(H_LEVER=LENGTH, TooltipShort=u"手柄高度", TooltipLong=u"管道中心至手柄顶面高度 H (mm)", Ask4Dist=True)
@param(L_LEVER=LENGTH, TooltipShort=u"手柄长度", TooltipLong=u"阀杆中心至手柄末端长度 (mm)")
def VALVE_BALL_JACKETED(
    s,
    D=114.3,
    L_FACE=267.0,
    D_FL=285.0,
    C_FL=22.0,
    D_JACKET=210.0,
    H_LEVER=255.0,
    L_LEVER=360.0,
    ID=u"VALVE_BALL_JACKETED",
    **kw
):
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 60.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    D_JACKET = max(D + 45.0, min(D_FL * 0.9, float(D_JACKET)))
    H_LEVER = float(H_LEVER)
    if H_LEVER < 1.0:
        H_LEVER = 1.0
    L_LEVER = max(160.0, float(L_LEVER))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.5
    r_rf = max(r_pipe + 10.0, r_fl * 0.72)
    fl_t = max(10.0, C_FL - rf_t)
    r_jk = D_JACKET / 2.0

    # 1. 左右加宽突面端法兰 (夹套阀通常采用大一档法兰)
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

    # 2. 内部连接颈管 + 外包加粗保温夹套壳体
    o_pipe = CYLINDER(s, R=r_pipe * 1.15, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe)
    o_pipe.erase()

    jk_l = max(60.0, L_FACE - 2.0 * C_FL - 18.0)
    o_jk = CYLINDER(s, R=r_jk, H=jk_l, O=0.0).rotateY(90.0).translate((-jk_l / 2.0, 0.0, 0.0))
    o_main.uniteWith(o_jk)
    o_jk.erase()
    # 夹套两端加强焊环
    for sx in (-1.0, 1.0):
        o_ring = CYLINDER(s, R=r_jk * 1.04, H=10.0, O=0.0).rotateY(90.0).translate((sx * (jk_l / 2.0 - 5.0) - 5.0, 0.0, 0.0))
        o_main.uniteWith(o_ring)
        o_ring.erase()

    # 3. 标志性双伴热加热小口 (位于 -Y 侧上/下对角位置，带小法兰)
    r_noz = max(11.0, r_pipe * 0.22)
    r_nfl = max(24.0, r_noz * 2.15)
    noz_len = max(38.0, r_jk * 0.42)
    for sx, sz in ((-1.0, 1.0), (1.0, -1.0)):
        nx = sx * jk_l * 0.24
        nz = sz * r_jk * 0.46
        o_npipe = CYLINDER(s, R=r_noz, H=noz_len + 18.0, O=0.0).rotateX(90.0).translate((nx, -(r_jk * 0.85 - 12.0), nz))
        o_main.uniteWith(o_npipe)
        o_npipe.erase()
        o_nfl = CYLINDER(s, R=r_nfl, H=10.0, O=0.0).rotateX(90.0).translate((nx, -(r_jk * 0.85 + noz_len - 4.0), nz))
        o_main.uniteWith(o_nfl)
        o_nfl.erase()

    # 4. ISO 5211 顶台 + 阀杆 + 长手柄
    z_pad = r_jk + 18.0
    o_neck = CYLINDER(s, R=max(22.0, r_pipe * 0.46), H=z_pad + 4.0, O=0.0)
    o_main.uniteWith(o_neck)
    o_neck.erase()

    pad_w = max(64.0, r_pipe * 1.22)
    o_pad = CORNERBOX(s, L=pad_w, W=pad_w, H=12.0).translate((-pad_w / 2.0, -pad_w / 2.0, z_pad - 2.0))
    o_main.uniteWith(o_pad)
    o_pad.erase()

    z_stem_top = H_LEVER - 14.0
    if z_stem_top < z_pad + 34.0:
        z_stem_top = z_pad + 34.0
    o_stem = CYLINDER(s, R=max(12.0, r_pipe * 0.22), H=z_stem_top - z_pad + 6.0, O=0.0).translate((0.0, 0.0, z_pad + 2.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    hub_r = max(18.0, r_pipe * 0.34)
    o_hub = CYLINDER(s, R=hub_r, H=22.0, O=0.0).translate((0.0, 0.0, z_stem_top - 10.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()

    bar_w = max(16.0, r_pipe * 0.28)
    bar_t = max(10.0, r_pipe * 0.16)
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
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_LEVER', (0.0, 0.0, 0.0), (0.0, 0.0, H_LEVER))
