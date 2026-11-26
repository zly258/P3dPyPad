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
          TooltipShort=u"法兰夹管阀 (胶管阀)",
          TooltipLong=u"法兰封闭式夹管阀，含左右突面端法兰、鼓形双半拼合弹性护壳、加强肋环、顶部压杆支架与操作手轮",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"法兰夹管阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_OPEN=LENGTH, TooltipShort=u"总高度", TooltipLong=u"管道中心至手轮顶面高度 H (mm)", Ask4Dist=True)
@param(D_HW=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"操作手轮外径 (mm)")
def VALVE_PINCH_FLANGED(
    s,
    D=114.3,
    L_FACE=305.0,
    D_FL=220.0,
    C_FL=20.0,
    H_OPEN=330.0,
    D_HW=260.0,
    ID=u"VALVE_PINCH_FLANGED",
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

    # 2. 标志性鼓形弹性护壳 (左右双锥过渡 + 中部鼓形圆柱 + 水平合箱凸缘)
    body_l = L_FACE - 2.0 * C_FL
    r_drum = min(r_fl * 0.96, r_pipe * 1.72)
    mid_l = body_l * 0.42
    cone_l = (body_l - mid_l) / 2.0 + 4.0

    o_drum = CYLINDER(s, R=r_drum, H=mid_l + 4.0, O=0.0).rotateY(90.0).translate((-(mid_l / 2.0 + 2.0), 0.0, 0.0))
    o_main.uniteWith(o_drum)
    o_drum.erase()

    o_c1 = CONE(s, R1=r_pipe * 1.18, R2=r_drum, H=cone_l, E=0.0).rotateY(90.0).translate((-(half_l - C_FL + 2.0), 0.0, 0.0))
    o_main.uniteWith(o_c1)
    o_c1.erase()

    o_c2 = CONE(s, R1=r_drum, R2=r_pipe * 1.18, H=cone_l, E=0.0).rotateY(90.0).translate((mid_l / 2.0 - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_c2)
    o_c2.erase()

    # 夹管阀水平中分拼合凸缘
    o_seam = CORNERBOX(s, L=body_l * 0.82, W=r_drum * 2.22, H=16.0).translate((-body_l * 0.41, -r_drum * 1.11, -8.0))
    o_main.uniteWith(o_seam)
    o_seam.erase()

    # 3. 顶部压杆导管、桥式支架与操作手轮
    z_top_boss = r_drum + 16.0
    o_boss = CYLINDER(s, R=max(26.0, r_pipe * 0.52), H=z_top_boss - r_drum * 0.5 + 4.0, O=0.0).translate((0.0, 0.0, r_drum * 0.5 - 4.0))
    o_main.uniteWith(o_boss)
    o_boss.erase()

    z_hw = H_OPEN - max(22.0, D_HW * 0.08)
    if z_hw < z_top_boss + 65.0:
        z_hw = z_top_boss + 65.0
    yoke_h = z_hw - z_top_boss
    leg_w = max(13.0, r_pipe * 0.22)
    span = max(36.0, r_pipe * 0.72)
    for sx in (-1.0, 1.0):
        o_leg = CORNERBOX(s, L=leg_w, W=leg_w * 1.4, H=yoke_h + 6.0).translate((sx * span - leg_w / 2.0, -leg_w * 0.7, z_top_boss - 8.0))
        o_main.uniteWith(o_leg)
        o_leg.erase()

    o_ytop = CORNERBOX(s, L=span * 2.0 + leg_w, W=leg_w * 1.8, H=16.0).translate((-(span + leg_w / 2.0), -leg_w * 0.9, z_hw - 16.0))
    o_main.uniteWith(o_ytop)
    o_ytop.erase()

    r_stem = max(10.0, r_pipe * 0.18)
    o_stem = CYLINDER(s, R=r_stem, H=H_OPEN - r_drum * 0.6, O=0.0).translate((0.0, 0.0, r_drum * 0.6))
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
    s.setLinearDimension('H_OPEN', (0.0, 0.0, 0.0), (0.0, 0.0, H_OPEN))
