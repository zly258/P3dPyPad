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
          TooltipShort=u"对夹式蝶阀 (API 609 / GB/T 12238)",
          TooltipLong=u"手柄对夹式软密封蝶阀，含短圆环阀体、4耳对中定位耳、长阀杆保温颈、ISO顶台、扇形限位齿板与长手柄",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="WAF")
@group("MainDimensions", TooltipLong=u"对夹式蝶阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"对夹式阀体端面至端面厚度 L (mm)", Ask4Dist=True)
@param(D_BODY=LENGTH, TooltipShort=u"阀体外径", TooltipLong=u"对夹圆环阀体外径 (mm)")
@param(H_NECK=LENGTH, TooltipShort=u"阀杆颈高度", TooltipLong=u"管道中心至顶部 ISO 法兰顶面高度 (mm)", Ask4Dist=True)
@param(L_LEVER=LENGTH, TooltipShort=u"手柄长度", TooltipLong=u"阀杆中心至手柄末端长度 (mm)")
def VALVE_BUTTERFLY_WAFER(
    s,
    D=114.3,
    L_FACE=52.0,
    D_BODY=156.0,
    H_NECK=195.0,
    L_LEVER=260.0,
    ID=u"VALVE_BUTTERFLY_WAFER",
    **kw
):
    D = max(40.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_BODY = max(D + 24.0, float(D_BODY))
    H_NECK = float(H_NECK)
    if H_NECK < 1.0:
        H_NECK = 1.0
    L_LEVER = max(160.0, float(L_LEVER))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_body = D_BODY / 2.0

    # 1. 短圆环阀体 + 两侧突面密封胶圈台阶
    o_main = CYLINDER(s, R=r_body, H=L_FACE - 4.0, O=0.0).rotateY(90.0).translate((-(half_l - 2.0), 0.0, 0.0))
    o_seal = CYLINDER(s, R=r_body * 0.88, H=L_FACE, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_main.uniteWith(o_seal)
    o_seal.erase()

    # 4 个对夹对中定位耳 (位于 45/135/225/315 度)
    lug_r = max(12.0, r_body * 0.16)
    lug_dist = r_body + lug_r * 0.42
    for sy in (-1.0, 1.0):
        for sz in (-1.0, 1.0):
            o_lug = CYLINDER(s, R=lug_r, H=L_FACE - 8.0, O=0.0).rotateY(90.0).translate((-(half_l - 4.0), sy * lug_dist * 0.7071, sz * lug_dist * 0.7071))
            o_main.uniteWith(o_lug)
            o_lug.erase()

    # 底部阀轴凸台
    o_bot_boss = CYLINDER(s, R=max(16.0, r_body * 0.22), H=24.0, O=0.0).translate((0.0, 0.0, -(r_body + 16.0)))
    o_main.uniteWith(o_bot_boss)
    o_bot_boss.erase()

    # 2. 长阀杆保温颈 + ISO 5211 顶台
    r_neck = max(17.0, r_pipe * 0.34)
    o_neck = CYLINDER(s, R=r_neck, H=H_NECK - r_body * 0.7 + 4.0, O=0.0).translate((0.0, 0.0, r_body * 0.7 - 4.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    r_pad = max(36.0, r_neck * 1.9)
    o_pad = CYLINDER(s, R=r_pad, H=12.0, O=0.0).translate((0.0, 0.0, H_NECK - 10.0))
    o_main.uniteWith(o_pad)
    o_pad.erase()

    # 扇形限位齿板
    o_notch = CORNERBOX(s, L=r_pad * 1.35, W=r_pad * 1.25, H=8.0).translate((-r_pad * 0.2, -r_pad * 0.625, H_NECK + 2.0))
    o_main.uniteWith(o_notch)
    o_notch.erase()

    # 3. 阀杆头 + 长扳手柄
    o_stem = CYLINDER(s, R=max(11.0, r_neck * 0.58), H=42.0, O=0.0).translate((0.0, 0.0, H_NECK - 2.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    z_lev = H_NECK + 36.0
    hub_r = max(16.0, r_neck * 0.85)
    o_hub = CYLINDER(s, R=hub_r, H=20.0, O=0.0).translate((0.0, 0.0, z_lev - 12.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()

    bar_w = max(16.0, r_neck * 0.82)
    bar_t = max(9.0, r_neck * 0.45)
    o_arm = CORNERBOX(s, L=L_LEVER * 0.7, W=bar_w, H=bar_t).translate((-hub_r * 0.5, -bar_w / 2.0, z_lev - bar_t / 2.0))
    o_main.uniteWith(o_arm)
    o_arm.erase()

    grip_l = L_LEVER * 0.36
    o_grip = CYLINDER(s, R=max(10.0, bar_w * 0.62), H=grip_l, O=0.0).rotateY(90.0).translate((L_LEVER - grip_l, 0.0, z_lev))
    o_main.uniteWith(o_grip)
    o_grip.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_NECK', (0.0, 0.0, 0.0), (0.0, 0.0, H_NECK))
