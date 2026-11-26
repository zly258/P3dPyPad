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
from varmain.divsub.cste_u import *

@activate(Group="Support",
          TooltipShort=u"门式双吊杆横担架 (HG/T 21629 H3)",
          TooltipLong=u"门式双吊杆横担架，含底部槽钢横梁、管道托垫、左右双拉杆、锁紧螺母与顶部生根板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"门式双吊杆横担架主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支撑管道外径 D (mm)")
@param(W_SPAN=LENGTH, TooltipShort=u"横梁总宽", TooltipLong=u"底部槽钢横梁总跨度 W_SPAN (mm)", Ask4Dist=True)
@param(H_ROD=LENGTH, TooltipShort=u"吊架高度", TooltipLong=u"管道中心至顶部生根板顶面高度 H_ROD (mm)", Ask4Dist=True)
@param(ROD_D=LENGTH, TooltipShort=u"吊杆直径", TooltipLong=u"左右双吊杆直径 (mm)")
@param(CH_H=LENGTH, TooltipShort=u"槽钢高度", TooltipLong=u"底部横担槽钢截面高度 (mm)")
@param(CH_B=LENGTH, TooltipShort=u"槽钢腿宽", TooltipLong=u"底部横担槽钢腿宽 (mm)")
def SUPPORT_TRAPEZE_FRAME(
    s,
    D=168.3,
    W_SPAN=440.0,
    H_ROD=380.0,
    ROD_D=16.0,
    CH_H=100.0,
    CH_B=48.0,
    ID=u"SUPPORT_TRAPEZE_FRAME",
    **kw
):
    u"""门式双吊杆横担架 (原点在管道中心线, 管道沿 X 轴, 横梁沿 Y 轴, 吊杆向 +Z)。"""
    D = max(32.0, float(D))
    r_p = D / 2.0
    ROD_D = max(12.0, float(ROD_D))
    CH_H = max(63.0, float(CH_H))
    CH_B = max(36.0, float(CH_B))
    W_SPAN = float(W_SPAN)
    if W_SPAN < 1.0:
        W_SPAN = 1.0
    H_ROD = float(H_ROD)
    if H_ROD < 1.0:
        H_ROD = 1.0

    ch_t = max(6.0, CH_H * 0.08)
    z_beam_top = -r_p
    z_beam_mid = z_beam_top - CH_H / 2.0
    z_beam_bot = z_beam_top - CH_H
    rod_y = W_SPAN / 2.0 - max(42.0, CH_B * 0.85)
    top_t = max(12.0, ROD_D * 0.75)
    z_top = H_ROD
    z_tplt_bot = z_top - top_t

    # 1. 底部水平槽钢横梁（沿 Y 方向横跨）
    o_main = CSTE_U(s, W=CH_H, H=CH_B, T=ch_t, L=W_SPAN).rotateZ(90.0).rotateX(-90.0).translate(
        (0.0, -W_SPAN / 2.0, z_beam_mid))

    # 2. 横梁中部小型管道限位托垫（贴合管底，清晰标示管道承托位）
    pad_l = max(CH_B + 16.0, 64.0)
    pad_w = max(80.0, D * 0.65)
    o_pad = CORNERBOX(s, L=pad_l, W=pad_w, H=r_p * 0.25 + 6.0).translate(
        (-pad_l / 2.0, -pad_w / 2.0, z_beam_top - 2.0))
    o_pcut = CYLINDER(s, R=r_p, H=pad_l + 30.0, O=0.0).rotateY(90.0).translate((-(pad_l / 2.0 + 15.0), 0.0, 0.0))
    o_pad.subtractFrom(o_pcut)
    o_pcut.erase()
    o_main.uniteWith(o_pad)
    o_pad.erase()

    # 3. 左右双竖直吊杆 + 底部垫板螺母 + 顶部生根耳板
    top_plt_l = max(100.0, CH_B * 2.0)
    top_plt_w = max(100.0, CH_B * 2.0)
    nut_r = ROD_D * 0.92
    nut_h = ROD_D * 0.85
    ear_h = max(36.0, ROD_D * 2.2)
    ear_t = max(10.0, ROD_D * 0.65)
    z_rod_bot = z_beam_bot - nut_h * 2.2

    for sy in (-1.0, 1.0):
        ry = sy * rod_y
        # 竖直吊杆
        o_rod = CYLINDER(s, R=ROD_D * 0.5, H=(z_tplt_bot - z_rod_bot) + 2.0, O=0.0).translate(
            (0.0, ry, z_rod_bot))
        o_main.uniteWith(o_rod)
        o_rod.erase()

        # 槽钢底部方形垫片与双锁紧螺母
        wash_w = max(CH_B + 12.0, ROD_D * 3.0)
        o_wash = CORNERBOX(s, L=wash_w, W=wash_w, H=top_t * 0.7).translate(
            (-wash_w / 2.0, ry - wash_w / 2.0, z_beam_bot - top_t * 0.7 + 1.0))
        o_main.uniteWith(o_wash)
        o_wash.erase()
        for nz in (z_beam_bot - top_t * 0.7 - nut_h + 1.5, z_beam_top - 1.0):
            o_nut = CYLINDER(s, R=nut_r, H=nut_h, O=0.0).translate((0.0, ry, nz))
            o_main.uniteWith(o_nut)
            o_nut.erase()

        # 中段调节螺母套筒
        z_mid = (z_beam_top + z_tplt_bot) * 0.50
        o_coupl = CYLINDER(s, R=ROD_D * 0.95, H=ROD_D * 3.0, O=0.0).translate((0.0, ry, z_mid - ROD_D * 1.5))
        o_main.uniteWith(o_coupl)
        o_coupl.erase()

        # 顶部独立生根板 + 吊耳座
        o_tplt = CORNERBOX(s, L=top_plt_l, W=top_plt_w, H=top_t).translate(
            (-top_plt_l / 2.0, ry - top_plt_w / 2.0, z_tplt_bot))
        o_main.uniteWith(o_tplt)
        o_tplt.erase()

        o_ear = CORNERBOX(s, L=ROD_D * 2.6, W=ear_t * 2.4, H=ear_h).translate(
            (-ROD_D * 1.3, ry - ear_t * 1.2, z_tplt_bot - ear_h + 1.0))
        o_main.uniteWith(o_ear)
        o_ear.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('W_SPAN', (0.0, -W_SPAN / 2.0, z_beam_bot), (0.0, W_SPAN / 2.0, z_beam_bot))
    s.setLinearDimension('H_ROD', (0.0, 0.0, 0.0), (0.0, 0.0, z_top))
