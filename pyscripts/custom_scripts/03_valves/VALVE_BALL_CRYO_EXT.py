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
          TooltipShort=u"低温长颈法兰球阀 (BS 6364)",
          TooltipLong=u"低温深冷长颈法兰球阀，含突面端法兰、球形阀腔、中法兰、加长保冷长颈、环形保冷滴水盘、防静电杆与长扳手柄",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"低温长颈法兰球阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_EXT=LENGTH, TooltipShort=u"保冷长颈高", TooltipLong=u"管道中心至填料函底部的加长颈高度 (mm)", Ask4Dist=True)
@param(H_TOTAL=LENGTH, TooltipShort=u"总高度", TooltipLong=u"管道中心至手柄顶面总高度 H (mm)", Ask4Dist=True)
@param(L_LEVER=LENGTH, TooltipShort=u"手柄长度", TooltipLong=u"阀杆中心至手柄末端长度 (mm)", Ask4Dist=True)
def VALVE_BALL_CRYO_EXT(
    s,
    D=114.3,
    L_FACE=229.0,
    D_FL=220.0,
    C_FL=20.0,
    H_EXT=480.0,
    H_TOTAL=600.0,
    L_LEVER=360.0,
    ID=u"VALVE_BALL_CRYO_EXT",
    **kw
):
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    H_EXT = float(H_EXT)
    if H_EXT < 1.0:
        H_EXT = 1.0
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0
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

    # 2. 流道颈 + 球形阀腔 + 两片式合箱中环
    o_pipe = CYLINDER(s, R=r_pipe * 1.14, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe)
    o_pipe.erase()

    r_ball = min(r_fl * 0.84, r_pipe * 1.52)
    o_sph = SPHERE(s, R=r_ball)
    o_main.uniteWith(o_sph)
    o_sph.erase()

    o_split = CYLINDER(s, R=r_ball * 1.05, H=16.0, O=0.0).rotateY(90.0).translate((r_ball * 0.25, 0.0, 0.0))
    o_main.uniteWith(o_split)
    o_split.erase()

    # 3. 低温加长保冷长颈 + 底部中法兰 + 环形滴水盘
    z_mf = r_ball * 0.88
    mf_t = max(22.0, C_FL * 1.15)
    r_mf = max(r_ball * 0.78, r_pipe * 0.95)
    o_mf = CYLINDER(s, R=r_mf, H=mf_t, O=0.0).translate((0.0, 0.0, z_mf))
    o_main.uniteWith(o_mf)
    o_mf.erase()

    r_ext = max(24.0, r_pipe * 0.48)
    z_ext_start = z_mf + mf_t - 4.0
    o_ext = CYLINDER(s, R=r_ext, H=H_EXT - z_ext_start + 6.0, O=0.0).translate((0.0, 0.0, z_ext_start))
    o_main.uniteWith(o_ext)
    o_ext.erase()

    o_cone = CONE(s, R1=r_mf * 0.76, R2=r_ext, H=max(30.0, r_pipe * 0.55), E=0.0).translate((0.0, 0.0, z_ext_start))
    o_main.uniteWith(o_cone)
    o_cone.erase()

    z_drip = z_ext_start + (H_EXT - z_ext_start) * 0.62
    r_drip = max(r_ext * 2.35, r_fl * 0.78)
    o_drip = CYLINDER(s, R=r_drip, H=10.0, O=0.0).translate((0.0, 0.0, z_drip))
    o_main.uniteWith(o_drip)
    o_drip.erase()
    o_drip_lip = CYLINDER(s, R=r_drip, H=16.0, O=r_drip - 6.0).translate((0.0, 0.0, z_drip + 6.0))
    o_main.uniteWith(o_drip_lip)
    o_drip_lip.erase()

    # 4. 顶部 ISO 5211 顶台 + 填料压盖 + 防静电手柄
    pad_w = max(64.0, r_pipe * 1.2)
    o_pad = CORNERBOX(s, L=pad_w, W=pad_w, H=12.0).translate((-pad_w / 2.0, -pad_w / 2.0, H_EXT - 4.0))
    o_main.uniteWith(o_pad)
    o_pad.erase()

    z_stem_top = max(H_EXT + 42.0, H_TOTAL - 14.0)
    o_gland = CYLINDER(s, R=r_ext * 1.15, H=26.0, O=0.0).translate((0.0, 0.0, H_EXT + 4.0))
    o_main.uniteWith(o_gland)
    o_gland.erase()

    o_stem = CYLINDER(s, R=max(12.0, r_pipe * 0.22), H=z_stem_top - H_EXT + 4.0, O=0.0).translate((0.0, 0.0, H_EXT + 4.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    hub_r = max(18.0, r_pipe * 0.34)
    o_hub = CYLINDER(s, R=hub_r, H=22.0, O=0.0).translate((0.0, 0.0, z_stem_top - 10.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()

    bar_w = max(16.0, r_pipe * 0.28)
    bar_t = max(10.0, r_pipe * 0.16)
    o_arm = CORNERBOX(s, L=L_LEVER * 0.65, W=bar_w, H=bar_t).translate((-hub_r * 0.6, -bar_w / 2.0, H_TOTAL - bar_t))
    o_main.uniteWith(o_arm)
    o_arm.erase()

    grip_l = L_LEVER * 0.42
    grip_r = max(11.0, bar_w * 0.65)
    o_grip = CYLINDER(s, R=grip_r, H=grip_l, O=0.0).rotateY(90.0).translate((L_LEVER - grip_l, 0.0, H_TOTAL - bar_t / 2.0))
    o_main.uniteWith(o_grip)
    o_grip.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_EXT', (0.0, 0.0, 0.0), (0.0, 0.0, H_EXT))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
    s.setLinearDimension('L_LEVER', (0.0, 0.0, H_TOTAL), (L_LEVER, 0.0, H_TOTAL))
