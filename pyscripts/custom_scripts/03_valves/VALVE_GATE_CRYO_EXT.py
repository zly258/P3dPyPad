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
          TooltipShort=u"低温长颈闸阀 (BS 6364)",
          TooltipLong=u"低温深冷长颈法兰明杆闸阀，含突面端法兰、中法兰、加长保冷长颈、环形保冷滴水盘、梯形支架、明杆与手轮",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"低温长颈闸阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_EXT=LENGTH, TooltipShort=u"保冷长颈高", TooltipLong=u"管道中心至填料函底部的加长颈高度 (mm)", Ask4Dist=True)
@param(H_OPEN=LENGTH, TooltipShort=u"全开总高", TooltipLong=u"管道中心至明杆顶面高度 H (mm)", Ask4Dist=True)
@param(D_HW=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"操作手轮外径 (mm)")
def VALVE_GATE_CRYO_EXT(
    s,
    D=114.3,
    L_FACE=229.0,
    D_FL=220.0,
    C_FL=20.0,
    H_EXT=480.0,
    H_OPEN=820.0,
    D_HW=280.0,
    ID=u"VALVE_GATE_CRYO_EXT",
    **kw
):
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    D_HW = max(120.0, float(D_HW))
    H_EXT = float(H_EXT)
    if H_EXT < 1.0:
        H_EXT = 1.0
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

    # 2. 阀体与中法兰
    o_pipe = CYLINDER(s, R=r_pipe * 1.12, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe)
    o_pipe.erase()

    r_cav = min(half_l - C_FL - 6.0, r_pipe * 1.32)
    z_bot = -r_pipe * 1.2
    z_mf = r_pipe * 1.35
    o_cav = CYLINDER(s, R=r_cav, H=z_mf - z_bot, O=0.0).translate((0.0, 0.0, z_bot))
    o_main.uniteWith(o_cav)
    o_cav.erase()

    mf_t = max(24.0, C_FL * 1.3)
    o_mf = CYLINDER(s, R=r_cav * 1.26, H=mf_t, O=0.0).translate((0.0, 0.0, z_mf - 2.0))
    o_main.uniteWith(o_mf)
    o_mf.erase()

    # 3. 加长低温保冷长颈管 + 滴水盘 (Vapor Barrier / Drip Plate)
    r_ext = max(24.0, r_pipe * 0.46)
    z_ext_start = z_mf + mf_t - 4.0
    o_ext = CYLINDER(s, R=r_ext, H=H_EXT - z_ext_start + 6.0, O=0.0).translate((0.0, 0.0, z_ext_start))
    o_main.uniteWith(o_ext)
    o_ext.erase()

    # 底部过渡锥
    o_cone = CONE(s, R1=r_cav * 0.95, R2=r_ext, H=max(32.0, r_pipe * 0.6), E=0.0).translate((0.0, 0.0, z_ext_start))
    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 标志性保冷滴水盘 (设在长颈 62% 高度处)
    z_drip = z_ext_start + (H_EXT - z_ext_start) * 0.62
    r_drip = max(r_ext * 2.35, r_fl * 0.78)
    o_drip = CYLINDER(s, R=r_drip, H=10.0, O=0.0).translate((0.0, 0.0, z_drip))
    o_main.uniteWith(o_drip)
    o_drip.erase()
    # 滴水盘外缘翻边
    o_drip_lip = CYLINDER(s, R=r_drip, H=16.0, O=r_drip - 6.0).translate((0.0, 0.0, z_drip + 6.0))
    o_main.uniteWith(o_drip_lip)
    o_drip_lip.erase()

    # 4. 顶部填料函 + 梯形支架 + 明杆 + 手轮
    z_gland_top = H_EXT + max(36.0, r_pipe * 0.55)
    o_gland = CYLINDER(s, R=r_ext * 1.18, H=z_gland_top - H_EXT + 6.0, O=0.0).translate((0.0, 0.0, H_EXT - 4.0))
    o_main.uniteWith(o_gland)
    o_gland.erase()

    o_top_fl = CYLINDER(s, R=r_ext * 1.65, H=14.0, O=0.0).translate((0.0, 0.0, H_EXT - 4.0))
    o_main.uniteWith(o_top_fl)
    o_top_fl.erase()

    z_hw = H_OPEN - max(80.0, r_pipe * 1.45)
    if z_hw < z_gland_top + 70.0:
        z_hw = z_gland_top + 70.0
    yoke_h = z_hw - H_EXT
    leg_w = max(13.0, r_pipe * 0.2)
    span = max(32.0, r_ext * 1.15)
    for sx in (-1.0, 1.0):
        o_leg = CORNERBOX(s, L=leg_w, W=leg_w * 1.35, H=yoke_h).translate((sx * span - leg_w / 2.0, -leg_w * 0.675, H_EXT + 4.0))
        o_main.uniteWith(o_leg)
        o_leg.erase()

    o_ytop = CORNERBOX(s, L=span * 2.0 + leg_w, W=leg_w * 1.7, H=16.0).translate((-(span + leg_w / 2.0), -leg_w * 0.85, z_hw - 16.0))
    o_main.uniteWith(o_ytop)
    o_ytop.erase()

    r_stem = max(9.0, r_pipe * 0.16)
    o_stem = CYLINDER(s, R=r_stem, H=H_OPEN - z_gland_top + 10.0, O=0.0).translate((0.0, 0.0, z_gland_top - 10.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

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
    s.setLinearDimension('H_EXT', (0.0, 0.0, 0.0), (0.0, 0.0, H_EXT))
    s.setLinearDimension('H_OPEN', (0.0, 0.0, 0.0), (0.0, 0.0, H_OPEN))
