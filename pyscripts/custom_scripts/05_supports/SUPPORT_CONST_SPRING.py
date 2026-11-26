# -*- coding: utf-8 -*-
import math
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

@activate(Group="Support",
          TooltipShort=u"恒力弹簧支吊架 (NB/T 47038 CS)",
          TooltipLong=u"恒力弹簧支吊架，含矩形主弹簧箱体、侧置偏心凸轮罩壳与主轴boss、下吊杆双耳管夹与顶部生根吊耳",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"恒力弹簧支吊架主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被悬吊管道外径 D (mm)")
@param(H_TOT=LENGTH, TooltipShort=u"安装总高", TooltipLong=u"管道中心至顶部生根板顶面总高度 H_TOT (mm)", Ask4Dist=True)
@param(BOX_L=LENGTH, TooltipShort=u"箱体长度", TooltipLong=u"恒力弹簧矩形主箱体长度 (mm)")
@param(BOX_W=LENGTH, TooltipShort=u"箱体宽度", TooltipLong=u"矩形主箱体宽度 (mm)")
@param(BOX_H=LENGTH, TooltipShort=u"箱体高度", TooltipLong=u"矩形主箱体高度 (mm)")
@param(ROD_D=LENGTH, TooltipShort=u"吊杆直径", TooltipLong=u"下吊杆公称直径 (mm)")
def SUPPORT_CONST_SPRING(
    s,
    D=168.3,
    H_TOT=520.0,
    BOX_L=250.0,
    BOX_W=130.0,
    BOX_H=150.0,
    ROD_D=18.0,
    ID=u"SUPPORT_CONST_SPRING",
    **kw
):
    u"""恒力弹簧支吊架 (原点在管道中心线, 管道沿 X 轴, 恒力箱体在 +Z 侧)。"""
    D = max(50.0, float(D))
    r_p = D / 2.0
    BOX_L = float(BOX_L)
    if BOX_L < 1.0:
        BOX_L = 1.0
    BOX_W = max(90.0, float(BOX_W))
    BOX_H = max(100.0, float(BOX_H))
    ROD_D = max(14.0, float(ROD_D))
    H_TOT = float(H_TOT)
    if H_TOT < 1.0:
        H_TOT = 1.0

    clamp_w = max(40.0, ROD_D * 2.4)
    clamp_t = max(8.0, ROD_D * 0.48)
    r_out = r_p + clamp_t
    ear_gap = max(10.0, clamp_t * 1.1)
    top_t = max(14.0, ROD_D * 0.8)
    z_top = H_TOT
    z_tplt_bot = z_top - top_t

    # 1. 下部双耳管夹
    o_main = CYLINDER(s, R=r_out, H=clamp_w, O=r_p).rotateY(90.0).translate((-clamp_w / 2.0, 0.0, 0.0))
    o_slot = CORNERBOX(s, L=clamp_w + 8.0, W=ear_gap, H=r_out * 2.6).translate(
        (-(clamp_w / 2.0 + 4.0), -ear_gap / 2.0, -r_out * 1.3))
    o_main.subtractFrom(o_slot)
    o_slot.erase()

    bot_ear_h = max(30.0, ROD_D * 1.7)
    top_ear_h = max(55.0, ROD_D * 3.0)
    for sy in (-1.0, 1.0):
        ey = (ear_gap / 2.0) if sy > 0 else -(ear_gap / 2.0 + clamp_t)
        o_be = CORNERBOX(s, L=clamp_w, W=clamp_t, H=bot_ear_h).translate((-clamp_w / 2.0, ey, -(r_p + bot_ear_h)))
        o_main.uniteWith(o_be)
        o_be.erase()
        o_te = CORNERBOX(s, L=clamp_w, W=clamp_t, H=top_ear_h).translate((-clamp_w / 2.0, ey, r_p))
        o_main.uniteWith(o_te)
        o_te.erase()

    bw = ear_gap + clamp_t * 2.0 + ROD_D * 1.4
    z_pin_bot = r_out + top_ear_h * 0.72
    for bz in (-(r_out + bot_ear_h * 0.45), z_pin_bot):
        o_b = CYLINDER(s, R=ROD_D * 0.5, H=bw, O=0.0).rotateX(-90.0).translate((0.0, -bw / 2.0, bz))
        o_main.uniteWith(o_b)
        o_b.erase()

    # 2. 恒力弹簧矩形主箱体（偏心布置于载荷轴线 (0,0) 一侧，体现力臂杠杆特征）
    z_box_mid = (z_pin_bot + z_tplt_bot) * 0.58
    z_box_bot = z_box_mid - BOX_H / 2.0
    z_box_top = z_box_mid + BOX_H / 2.0
    cam_r = BOX_H * 0.46
    # 主矩形弹簧缸箱向 -Y 延伸，偏心凸轮罩位于 y=0 载荷线上方
    o_box = CORNERBOX(s, L=BOX_W, W=BOX_L * 0.72, H=BOX_H).translate(
        (-BOX_W / 2.0, -BOX_L * 0.72, z_box_bot))
    o_main.uniteWith(o_box)
    o_box.erase()

    # 箱体后侧圆柱弹簧盖板凸台
    o_endcap = CYLINDER(s, R=BOX_W * 0.42, H=24.0, O=0.0).rotateX(-90.0).translate(
        (0.0, -BOX_L * 0.72 - 22.0, z_box_mid))
    o_main.uniteWith(o_endcap)
    o_endcap.erase()

    # 3. 偏心凸轮罩壳（位于载荷中心 y=0 附近，圆弧外轮廓+双侧主转轴凸台+行程指示牌）
    cam_w = BOX_W * 0.86
    o_cam_cyl = CYLINDER(s, R=cam_r, H=cam_w, O=0.0).rotateY(90.0).translate((-cam_w / 2.0, 0.0, z_box_mid))
    o_main.uniteWith(o_cam_cyl)
    o_cam_cyl.erase()

    # 连接凸轮罩与主箱体的过渡壳体
    o_bridge = CORNERBOX(s, L=cam_w, W=cam_r * 1.1, H=BOX_H * 0.86).translate(
        (-cam_w / 2.0, -cam_r * 0.8, z_box_mid - BOX_H * 0.43))
    o_main.uniteWith(o_bridge)
    o_bridge.erase()

    # 主转轴与偏心凸轮轴端盖凸台（±X 两侧突出，辨识度极高）
    for py, pz, pr in ((0.0, z_box_mid, ROD_D * 1.15), (-BOX_L * 0.25, z_box_mid - BOX_H * 0.18, ROD_D * 0.85)):
        o_boss = CYLINDER(s, R=pr, H=BOX_W + 24.0, O=0.0).rotateY(90.0).translate((-(BOX_W + 24.0) / 2.0, py, pz))
        o_main.uniteWith(o_boss)
        o_boss.erase()

    # 4. 下吊杆 + 载荷调节花篮套筒（从管夹直连凸轮罩底端载荷销）
    o_rod = CYLINDER(s, R=ROD_D * 0.5, H=(z_box_mid - z_pin_bot), O=0.0).translate((0.0, 0.0, z_pin_bot))
    o_main.uniteWith(o_rod)
    o_rod.erase()
    z_tb = (z_pin_bot + z_box_bot) * 0.52
    o_tb = CYLINDER(s, R=ROD_D * 0.95, H=ROD_D * 2.8, O=0.0).translate((0.0, 0.0, z_tb - ROD_D * 1.4))
    o_main.uniteWith(o_tb)
    o_tb.erase()

    # 5. 上部主悬挂吊耳 + 顶部生根底板（正对载荷线 y=0 平衡）
    lug_h = z_tplt_bot - z_box_top + 20.0
    lug_t = max(14.0, ROD_D * 0.8)
    lug_w = max(56.0, ROD_D * 3.0)
    o_ulug = CORNERBOX(s, L=lug_t, W=lug_w, H=lug_h).translate((-lug_t / 2.0, -lug_w / 2.0, z_box_top - 16.0))
    o_main.uniteWith(o_ulug)
    o_ulug.erase()

    top_l = max(140.0, BOX_W * 1.1)
    top_w = max(140.0, BOX_W * 1.1)
    o_tplt = CORNERBOX(s, L=top_l, W=top_w, H=top_t).translate((-top_l / 2.0, -top_w / 2.0, z_tplt_bot))
    o_main.uniteWith(o_tplt)
    o_tplt.erase()

    # 上吊耳横向销轴
    o_upin = CYLINDER(s, R=ROD_D * 0.65, H=lug_t + 26.0, O=0.0).rotateY(90.0).translate(
        (-(lug_t + 26.0) / 2.0, 0.0, (z_box_top + z_tplt_bot) * 0.52))
    o_main.uniteWith(o_upin)
    o_upin.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOT', (0.0, 0.0, 0.0), (0.0, 0.0, z_top))
    s.setLinearDimension('BOX_L', (0.0, -BOX_L * 0.72, z_box_mid), (0.0, cam_r, z_box_mid))
