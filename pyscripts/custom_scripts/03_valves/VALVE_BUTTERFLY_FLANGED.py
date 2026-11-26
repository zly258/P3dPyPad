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
          TooltipShort=u"双法兰偏心蝶阀 (蜗轮传动)",
          TooltipLong=u"双法兰三偏心金属密封蝶阀，含左右突面端法兰、短圆环偏心阀体、长阀杆颈、顶置蜗轮箱与侧装辐条手轮",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"双法兰偏心蝶阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_NECK=LENGTH, TooltipShort=u"阀杆颈高度", TooltipLong=u"管道中心至蜗轮箱底面高度 (mm)", Ask4Dist=True)
@param(D_HW=LENGTH, TooltipShort=u"侧手轮直径", TooltipLong=u"蜗轮箱侧面手轮外径 (mm)")
def VALVE_BUTTERFLY_FLANGED(
    s,
    D=219.1,
    L_FACE=152.0,
    D_FL=340.0,
    C_FL=24.0,
    H_NECK=265.0,
    D_HW=280.0,
    ID=u"VALVE_BUTTERFLY_FLANGED",
    **kw
):
    D = max(80.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 55.0, float(D_FL))
    C_FL = max(16.0, float(C_FL))
    H_NECK = float(H_NECK)
    if H_NECK < 1.0:
        H_NECK = 1.0
    D_HW = max(160.0, float(D_HW))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.5
    r_rf = max(r_pipe + 10.0, r_fl * 0.74)
    fl_t = max(12.0, C_FL - rf_t)

    # 1. 左右突面端法兰 + 短圆环阀体
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

    o_body = CYLINDER(s, R=r_pipe * 1.18, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_body)
    o_body.erase()

    # 底部轴端盲盖
    o_bot = CYLINDER(s, R=max(24.0, r_pipe * 0.28), H=28.0, O=0.0).translate((0.0, 0.0, -(r_pipe * 1.18 + 20.0)))
    o_main.uniteWith(o_bot)
    o_bot.erase()

    # 2. 长阀杆颈 + ISO 5211 顶台
    r_neck = max(22.0, r_pipe * 0.28)
    o_neck = CYLINDER(s, R=r_neck, H=H_NECK - r_pipe * 0.8 + 4.0, O=0.0).translate((0.0, 0.0, r_pipe * 0.8 - 4.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    r_pad = max(48.0, r_neck * 1.9)
    o_pad = CYLINDER(s, R=r_pad, H=14.0, O=0.0).translate((0.0, 0.0, H_NECK - 12.0))
    o_main.uniteWith(o_pad)
    o_pad.erase()

    # 3. 顶部蜗轮减速箱 (扇形/圆形主壳 + 蜗杆侧筒 + 顶部开度指针盘)
    gb_h = max(72.0, D_HW * 0.28)
    gb_r = max(58.0, D_HW * 0.24)
    z_gb_ctr = H_NECK + gb_h / 2.0
    o_gb = CYLINDER(s, R=gb_r, H=gb_h, O=0.0).translate((0.0, 0.0, H_NECK - 2.0))
    o_main.uniteWith(o_gb)
    o_gb.erase()

    # 顶部开度指示盖
    o_ind = CYLINDER(s, R=gb_r * 0.45, H=16.0, O=0.0).translate((0.0, 0.0, H_NECK + gb_h - 4.0))
    o_main.uniteWith(o_ind)
    o_ind.erase()

    # 蜗杆输入轴箱体 (偏向 -Y 侧，轴线沿 -Y 伸出接侧手轮)
    worm_r = max(24.0, gb_h * 0.36)
    worm_len = max(110.0, gb_r * 1.9)
    o_worm_box = CYLINDER(s, R=worm_r, H=worm_len, O=0.0).rotateX(90.0).translate((gb_r * 0.55, 0.0, z_gb_ctr))
    o_main.uniteWith(o_worm_box)
    o_worm_box.erase()
    # 蜗杆箱与主壳体过渡筋块
    o_bridge = CORNERBOX(s, L=gb_r * 0.9, W=worm_r * 2.0, H=gb_h * 0.85).translate((0.0, -worm_r, H_NECK + gb_h * 0.08))
    o_main.uniteWith(o_bridge)
    o_bridge.erase()

    # 4. 侧装输入轴 + 辐条手轮 (位于 -Y 侧，绕 Y 轴旋转平面)
    y_hw = -(worm_len + 42.0)
    o_shaft = CYLINDER(s, R=max(11.0, worm_r * 0.45), H=65.0, O=0.0).rotateX(90.0).translate((gb_r * 0.55, -(worm_len - 10.0), z_gb_ctr))
    o_main.uniteWith(o_shaft)
    o_shaft.erase()

    r_hw = D_HW / 2.0
    r_rim = max(9.0, D_HW * 0.042)
    o_hw = TORUS(s, R1=r_hw - r_rim, R2=r_rim)
    o_hub = CYLINDER(s, R=max(18.0, worm_r * 0.72), H=24.0, O=0.0).translate((0.0, 0.0, -12.0))
    o_hw.uniteWith(o_hub)
    o_hub.erase()
    for ang in (0.0, 90.0):
        o_sp = CYLINDER(s, R=r_rim * 0.72, H=(r_hw - r_rim) * 2.0, O=0.0).rotateY(90.0).translate((-(r_hw - r_rim), 0.0, 0.0)).rotateZ(ang)
        o_hw.uniteWith(o_sp)
        o_sp.erase()
    o_hw.rotateX(90.0).translate((gb_r * 0.55, y_hw, z_gb_ctr))
    o_main.uniteWith(o_hw)
    o_hw.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_NECK', (0.0, 0.0, 0.0), (0.0, 0.0, H_NECK))
