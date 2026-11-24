# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"双立柱地面生根龙门管架",
    TooltipLong=u"化工装置地面生根 H 型钢双立柱门型管架 (G4 型，符合 HG/T 21629，含横梁顶面管道承重鞍托与U型卡箍、H型钢门型横梁、两侧H型钢立柱、节点斜撑角板与双四孔带肋柱脚底板)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支承主管道公称外径 (mm)")
@param(H=LENGTH, TooltipShort=u"中心高", TooltipLong=u"管道中心至地面柱脚底板底面的总高度 (mm)")
@param(SPAN=LENGTH, TooltipShort=u"龙门跨距", TooltipLong=u"两侧立柱中心线之间的横向跨距 (mm)")
@param(W_COL=LENGTH, TooltipShort=u"H型钢宽", TooltipLong=u"门架立柱与横梁H型钢截面高度/翼缘宽度 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"柱脚底板宽", TooltipLong=u"两侧独立地面柱脚锚固底板边长 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"管架编号", TooltipLong=u"双立柱龙门管架型号规格编码")
def SUPPORT_PORTAL_FRAME(s, D=219.1, H=850.0, SPAN=700.0, W_COL=100.0, W_BASE=220.0, ID=u"G4-DN200", **kw):
    D = max(32.0, float(D))
    r_pipe = D / 2.0
    W_COL = max(65.0, float(W_COL))
    H = max(r_pipe + W_COL + 250.0, float(H))
    SPAN = max(D + W_COL * 2.2, float(SPAN))
    W_BASE = max(W_COL + 80.0, float(W_BASE))

    z_bot = -H
    h_shoe = 65.0
    z_beam_top = -(r_pipe + h_shoe)
    t_base = 16.0
    t_fl = max(10.0, W_COL * 0.14)
    t_web = max(8.0, W_COL * 0.10)

    # 1. 中央管道 T 型滑动管托 + 顶部防脱 U 型抱箍 + 两侧横向限位挡块
    o_m = CYLINDER(s, R=r_pipe + 10.0, H=W_COL, O=0.0).rotateY(90.0).translate((-W_COL * 0.5, 0.0, 0.0))
    o_trim = BOX(s, L=(r_pipe + 15.0) * 2.2, W=r_pipe * 1.5, H=W_COL + 10.0).translate((0.0, 0.0, r_pipe * 0.45))
    o_m.subtractFrom(o_trim); o_trim.erase()

    o_strap = CYLINDER(s, R=r_pipe + 12.0, H=28.0, O=0.0).rotateY(90.0).translate((-14.0, 0.0, 0.0))
    o_m.uniteWith(o_strap); o_strap.erase()

    h_sweb = h_shoe + r_pipe * 0.45
    o_shoe_web = BOX(s, L=14.0, W=h_sweb, H=W_COL).translate((0.0, 0.0, z_beam_top + h_sweb * 0.5))
    o_shoe_base = BOX(s, L=D * 0.78, W=14.0, H=W_COL).translate((0.0, 0.0, z_beam_top + 5.0))
    o_m.uniteWith(o_shoe_web); o_shoe_web.erase()
    o_m.uniteWith(o_shoe_base); o_shoe_base.erase()

    for sy in (-1.0, 1.0):
        stop = BOX(s, L=16.0, W=42.0, H=W_COL * 0.72).translate((0.0, sy * (D * 0.39 + 12.0), z_beam_top + 18.0))
        o_m.uniteWith(stop); stop.erase()

    # 2. 龙门架水平 H 型钢横梁 (上下翼缘 + 中间腹板)
    w_beam_tot = SPAN + W_COL * 1.4
    b_top = BOX(s, L=w_beam_tot, W=t_fl, H=W_COL).translate((0.0, 0.0, z_beam_top - t_fl * 0.5))
    b_bot = BOX(s, L=w_beam_tot, W=t_fl, H=W_COL).translate((0.0, 0.0, z_beam_top - W_COL + t_fl * 0.5))
    b_web = BOX(s, L=w_beam_tot, W=W_COL, H=t_web).translate((0.0, 0.0, z_beam_top - W_COL * 0.5))
    for p in (b_top, b_bot, b_web):
        o_m.uniteWith(p); p.erase()

    # 3. 两侧 H 型钢竖直立柱 + 节点角隅腋板 + 柱脚加劲肋与四孔锚固底板
    h_col = (z_beam_top - W_COL * 0.5) - (z_bot + t_base)
    z_col_c = z_bot + t_base + h_col * 0.5
    for sy in (-1.0, 1.0):
        yc = sy * SPAN * 0.5
        c_f1 = BOX(s, L=t_fl, W=h_col, H=W_COL).translate((0.0, yc - W_COL * 0.5 + t_fl * 0.5, z_col_c))
        c_f2 = BOX(s, L=t_fl, W=h_col, H=W_COL).translate((0.0, yc + W_COL * 0.5 - t_fl * 0.5, z_col_c))
        c_wb = BOX(s, L=W_COL, W=h_col, H=t_web).translate((0.0, yc, z_col_c))
        gus = BOX(s, L=W_COL * 1.35, W=W_COL * 1.35, H=14.0).translate((0.0, yc - sy * W_COL * 0.78, z_beam_top - W_COL * 1.38))
        bp = BOX(s, L=W_BASE, W=t_base, H=W_BASE).translate((0.0, yc, z_bot + t_base * 0.5))
        rib_b = BOX(s, L=W_BASE * 0.82, W=75.0, H=12.0).translate((0.0, yc, z_bot + t_base + 35.0))
        for p in (c_f1, c_f2, c_wb, gus, bp, rib_b):
            o_m.uniteWith(p); p.erase()
        for bx in (-1.0, 1.0):
            for by in (-1.0, 1.0):
                bh = CYLINDER(s, R=9.0, H=t_base + 4.0, O=0.0).translate((bx * W_BASE * 0.36, yc + by * W_BASE * 0.36, z_bot - 2.0))
                o_m.subtractFrom(bh); bh.erase()

    # 切除管道流道
    o_cut = CYLINDER(s, R=r_pipe, H=W_COL + 30.0, O=0.0).rotateY(90.0).translate((-(W_COL * 0.5 + 15.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (0.0, 0.0, z_bot), (0.0, 0.0, 0.0))
    s.setLinearDimension("SPAN", (0.0, -SPAN / 2.0, z_bot), (0.0, SPAN / 2.0, z_bot))
