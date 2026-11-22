# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"H型钢单柱T型地面管廊架",
    TooltipLong=u"化工厂区沿地面敷设管廊用 H 型钢单立柱 T 型支撑管架 (G1/G2 型，符合 HG/T 21629，含中央H型钢立柱、对称双侧斜撑、水平H型钢挑臂横梁、四向柱脚加劲肋、四孔地脚底板与管道承重鞍托)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"主管道外径", TooltipLong=u"管架顶部主管道公称外径 (mm)")
@param(H=LENGTH, TooltipShort=u"中心高", TooltipLong=u"管道中心至柱脚底板底面的总高度 (mm)")
@param(W_ARM=LENGTH, TooltipShort=u"T型横梁宽", TooltipLong=u"顶部T型水平挑梁总宽度 (mm)")
@param(W_COL=LENGTH, TooltipShort=u"H型钢截面高", TooltipLong=u"立柱与横梁H型钢截面高度/宽度 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"柱脚底板宽", TooltipLong=u"底部方形锚固底板边长 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"管架编号", TooltipLong=u"单柱T型地面管廊架型号编码")
def SUPPORT_PIPE_RACK_TEE(s, D=219.1, H=820.0, W_ARM=680.0, W_COL=120.0, W_BASE=280.0, ID=u"G1-DN200", **kw):
    D = max(32.0, float(D))
    r_pipe = D / 2.0
    W_COL = max(80.0, float(W_COL))
    H = max(r_pipe + W_COL + 280.0, float(H))
    W_ARM = max(D * 1.8 + 180.0, float(W_ARM))
    W_BASE = max(W_COL + 110.0, float(W_BASE))

    z_bot = -H
    h_shoe = 65.0
    z_beam_top = -(r_pipe + h_shoe)
    t_base = 18.0
    t_fl = max(10.0, W_COL * 0.14)
    t_web = max(8.0, W_COL * 0.10)

    # 1. 顶部管道承重鞍托 + 两侧限位挡铁
    o_m = CYLINDER(s, R=r_pipe + 10.0, H=W_COL, O=0.0).rotateY(90.0).translate((-W_COL * 0.5, 0.0, 0.0))
    o_trim = BOX(s, L=(r_pipe + 15.0) * 2.2, W=r_pipe * 1.5, H=W_COL + 10.0).translate((0.0, 0.0, r_pipe * 0.45))
    o_m.subtractFrom(o_trim); o_trim.erase()

    h_sweb = h_shoe + r_pipe * 0.45
    o_shoe_web = BOX(s, L=14.0, W=h_sweb, H=W_COL).translate((0.0, 0.0, z_beam_top + h_sweb * 0.5))
    o_shoe_base = BOX(s, L=D * 0.78, W=14.0, H=W_COL).translate((0.0, 0.0, z_beam_top + 5.0))
    o_m.uniteWith(o_shoe_web); o_shoe_web.erase()
    o_m.uniteWith(o_shoe_base); o_shoe_base.erase()

    # 2. T 型水平 H 型钢横梁 + 两侧对称 45° 斜撑腋板
    b_top = BOX(s, L=W_ARM, W=t_fl, H=W_COL).translate((0.0, 0.0, z_beam_top - t_fl * 0.5))
    b_bot = BOX(s, L=W_ARM, W=t_fl, H=W_COL).translate((0.0, 0.0, z_beam_top - W_COL + t_fl * 0.5))
    b_web = BOX(s, L=W_ARM, W=W_COL, H=t_web).translate((0.0, 0.0, z_beam_top - W_COL * 0.5))
    for p in (b_top, b_bot, b_web):
        o_m.uniteWith(p); p.erase()

    for sy in (-1.0, 1.0):
        brace = BOX(s, L=W_COL * 0.55, W=W_ARM * 0.36, H=W_COL * 0.65).rotateX(-sy * 45.0).translate((0.0, sy * W_ARM * 0.20, z_beam_top - W_COL - W_ARM * 0.12))
        o_m.uniteWith(brace); brace.erase()

    # 3. 中央竖直 H 型钢单立柱 + 柱脚四向加劲肋板 + 四孔锚固底板
    h_col = (z_beam_top - W_COL * 0.5) - (z_bot + t_base)
    z_col_c = z_bot + t_base + h_col * 0.5
    c_f1 = BOX(s, L=t_fl, W=h_col, H=W_COL).translate((0.0, -W_COL * 0.5 + t_fl * 0.5, z_col_c))
    c_f2 = BOX(s, L=t_fl, W=h_col, H=W_COL).translate((0.0, W_COL * 0.5 - t_fl * 0.5, z_col_c))
    c_wb = BOX(s, L=W_COL, W=h_col, H=t_web).translate((0.0, 0.0, z_col_c))
    bp = BOX(s, L=W_BASE, W=t_base, H=W_BASE).translate((0.0, 0.0, z_bot + t_base * 0.5))
    r_x = BOX(s, L=12.0, W=110.0, H=W_BASE * 0.85).translate((0.0, 0.0, z_bot + t_base + 50.0))
    r_y = BOX(s, L=W_BASE * 0.85, W=110.0, H=12.0).translate((0.0, 0.0, z_bot + t_base + 50.0))
    for p in (c_f1, c_f2, c_wb, bp, r_x, r_y):
        o_m.uniteWith(p); p.erase()

    for bx in (-1.0, 1.0):
        for by in (-1.0, 1.0):
            bh = CYLINDER(s, R=10.0, H=t_base + 4.0, O=0.0).translate((bx * W_BASE * 0.36, by * W_BASE * 0.36, z_bot - 2.0))
            o_m.subtractFrom(bh); bh.erase()

    o_cut = CYLINDER(s, R=r_pipe, H=W_COL + 30.0, O=0.0).rotateY(90.0).translate((-(W_COL * 0.5 + 15.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (0.0, 0.0, z_bot), (0.0, 0.0, 0.0))
    s.setLinearDimension("W_ARM", (0.0, -W_ARM / 2.0, z_beam_top), (0.0, W_ARM / 2.0, z_beam_top))
