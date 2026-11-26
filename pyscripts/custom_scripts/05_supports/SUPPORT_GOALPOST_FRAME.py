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


def _pos(value):
    value = float(value)
    if value < 1.0:
        return 1.0
    return value


@activate(Group="Support",
          TooltipShort=u"槽钢落地门式管架 (HG/T 21629 L1)",
          TooltipLong=u"槽钢落地门式管架，含左右槽钢立柱、顶部槽钢横梁、梁柱加劲板、管底垫块与底部锚固板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"槽钢落地门式管架主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支撑管道外径 D (mm)")
@param(W_SPAN=LENGTH, TooltipShort=u"门架跨度", TooltipLong=u"左右立柱中心跨度 W_SPAN (mm)", Ask4Dist=True)
@param(H_COL=LENGTH, TooltipShort=u"支架高度", TooltipLong=u"管道中心至底部锚固板底面高度 H_COL (mm)", Ask4Dist=True)
@param(CH_H=LENGTH, TooltipShort=u"槽钢高度", TooltipLong=u"立柱与横梁槽钢截面高度 (mm)")
@param(CH_B=LENGTH, TooltipShort=u"槽钢腿宽", TooltipLong=u"立柱与横梁槽钢腿宽 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"底板厚度", TooltipLong=u"柱脚锚固底板厚度 (mm)")
def SUPPORT_GOALPOST_FRAME(
    s,
    D=168.3,
    W_SPAN=540.0,
    H_COL=540.0,
    CH_H=100.0,
    CH_B=48.0,
    T_PLT=14.0,
    ID=u"SUPPORT_GOALPOST_FRAME",
    **kw
):
    u"""槽钢落地门式管架。原点在管道中心，管道沿 X，跨度沿 Y，底板在 Z=-H_COL。

    握点长度必须等于传入的 W_SPAN / H_COL，不能再用 max() 把它们抬高。
    第一笔几何用原生圆柱当种子，槽钢用平板拼，避免子脚本 CSTE_U 和斜切布尔在 ACIS 里失败。
    """
    D = _pos(D)
    W_SPAN = _pos(W_SPAN)
    H_COL = _pos(H_COL)
    CH_H = _pos(CH_H)
    CH_B = _pos(CH_B)
    T_PLT = _pos(T_PLT)

    r_p = D / 2.0
    ch_t = min(CH_H, CH_B) * 0.16
    if ch_t < 4.0:
        ch_t = 4.0
    if ch_t * 2.2 >= CH_H:
        ch_t = CH_H / 3.0
    if ch_t * 2.2 >= CH_B:
        ch_t = CH_B / 3.0
    plate_t = T_PLT
    if plate_t > H_COL * 0.45:
        plate_t = H_COL * 0.45
    if plate_t < 4.0:
        plate_t = 4.0

    z_floor = -H_COL
    z_base_top = z_floor + plate_t
    z_beam_top = -r_p
    z_beam_bot = z_beam_top - CH_H
    col_h = (z_beam_bot + ch_t) - (z_base_top - 1.0)
    if col_h < 4.0:
        col_h = 4.0

    # 种子体先占住 s，后面的平板都并进来。
    o_main = CYLINDER(s, R=2.0, H=2.0, O=0.0).translate((0.0, 0.0, z_beam_top - 3.0))

    # 横梁：腹板 + 上下翼缘，长度正好是 W_SPAN。
    o_web = CORNERBOX(s, L=ch_t, W=W_SPAN, H=CH_H).translate((-ch_t / 2.0, -W_SPAN / 2.0, z_beam_bot))
    o_main.uniteWith(o_web)
    o_web.erase()
    o_ft = CORNERBOX(s, L=CH_B, W=W_SPAN, H=ch_t).translate((-CH_B / 2.0, -W_SPAN / 2.0, z_beam_top - ch_t))
    o_main.uniteWith(o_ft)
    o_ft.erase()
    o_fb = CORNERBOX(s, L=CH_B, W=W_SPAN, H=ch_t).translate((-CH_B / 2.0, -W_SPAN / 2.0, z_beam_bot))
    o_main.uniteWith(o_fb)
    o_fb.erase()

    base_l = CH_B * 2.4
    if base_l < 140.0:
        base_l = 140.0
    base_w = CH_H * 1.7
    if base_w < 160.0:
        base_w = 160.0
    gus = CH_H * 0.45
    if gus < 36.0:
        gus = 36.0

    for sy in (-1.0, 1.0):
        cy = sy * (W_SPAN / 2.0)
        o_cweb = CORNERBOX(s, L=ch_t, W=CH_H, H=col_h).translate(
            (-ch_t / 2.0, cy - CH_H / 2.0, z_base_top - 1.0))
        o_main.uniteWith(o_cweb)
        o_cweb.erase()
        for fy in (-1.0, 1.0):
            y0 = cy + fy * (CH_H / 2.0 - ch_t)
            o_cfl = CORNERBOX(s, L=CH_B, W=ch_t, H=col_h).translate(
                (-CH_B / 2.0, y0, z_base_top - 1.0))
            o_main.uniteWith(o_cfl)
            o_cfl.erase()

        o_base = CORNERBOX(s, L=base_l, W=base_w, H=plate_t).translate(
            (-base_l / 2.0, cy - base_w / 2.0, z_floor))
        o_main.uniteWith(o_base)
        o_base.erase()

        if sy > 0.0:
            gy = cy - CH_H / 2.0 - gus + ch_t
        else:
            gy = cy + CH_H / 2.0 - ch_t
        o_gus = CORNERBOX(s, L=ch_t * 1.6, W=gus, H=gus).translate(
            (-ch_t * 0.8, gy, z_beam_bot - gus + ch_t))
        o_main.uniteWith(o_gus)
        o_gus.erase()

    pad_l = CH_B + 16.0
    if pad_l < 48.0:
        pad_l = 48.0
    pad_w = D * 0.55
    if pad_w < 40.0:
        pad_w = 40.0
    pad_h = 8.0
    o_pad = CORNERBOX(s, L=pad_l, W=pad_w, H=pad_h).translate(
        (-pad_l / 2.0, -pad_w / 2.0, z_beam_top - pad_h + 1.0))
    o_main.uniteWith(o_pad)
    o_pad.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('W_SPAN', (0.0, -W_SPAN / 2.0, z_floor), (0.0, W_SPAN / 2.0, z_floor))
    s.setLinearDimension('H_COL', (0.0, 0.0, 0.0), (0.0, 0.0, z_floor))
