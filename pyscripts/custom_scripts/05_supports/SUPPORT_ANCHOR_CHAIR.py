# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"双U型螺栓带肋固定管座",
    TooltipLong=u"化工工艺管线固定点用双U型螺栓加劲肋管座 (X1/X2 型，符合 HG/T 21629，含弧形承重鞍座、纵向主腹板、前后两道加宽U型螺栓横担挑翼、双U型圆钢卡箍与双螺母及四孔底板)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被锚固管道外径 (mm)")
@param(H=LENGTH, TooltipShort=u"中心高", TooltipLong=u"管道中心至管座底板底面的高度 (mm)")
@param(L=LENGTH, TooltipShort=u"管座长度", TooltipLong=u"管座顺管道方向总长 (mm)")
@param(W=LENGTH, TooltipShort=u"横担总宽", TooltipLong=u"两侧U型螺栓横担挑臂总宽度 (mm)")
@param(ROD_D=LENGTH, TooltipShort=u"U型螺栓径", TooltipLong=u"双U型螺栓圆钢直径 (mm)")
@param(T_PLATE=LENGTH, TooltipShort=u"钢板厚度", TooltipLong=u"底板与腹板厚度 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"管座编号", TooltipLong=u"双U型螺栓固定管座型号编码")
def SUPPORT_ANCHOR_CHAIR(s, D=168.3, H=195.0, L=300.0, W=250.0, ROD_D=16.0, T_PLATE=14.0, ID=u"X1-DN150", **kw):
    D = max(25.0, float(D))
    r_pipe = D / 2.0
    T_PLATE = max(10.0, float(T_PLATE))
    ROD_D = max(10.0, float(ROD_D))
    H = max(r_pipe + 65.0, float(H))
    L = max(180.0, float(L))
    W = max(D + ROD_D * 4.5, float(W))

    z_bot = -H
    r_rod = ROD_D / 2.0
    r_ub = r_pipe + r_rod

    # 1. 底部锚固底板 + 纵向主腹板 + 120° 弧形鞍座
    o_m = BOX(s, L=W * 0.88, W=T_PLATE, H=L).translate((0.0, 0.0, z_bot + T_PLATE * 0.5))
    h_web = H - r_pipe * 0.45
    o_web = BOX(s, L=T_PLATE, W=h_web, H=L).translate((0.0, 0.0, z_bot + T_PLATE + h_web * 0.5))
    o_sad = CYLINDER(s, R=r_pipe + T_PLATE, H=L, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    o_trim = BOX(s, L=(r_pipe + T_PLATE) * 2.3, W=r_pipe * 1.5, H=L + 20.0).translate((0.0, 0.0, r_pipe * 0.45))
    o_sad.subtractFrom(o_trim); o_trim.erase()
    o_m.uniteWith(o_web); o_web.erase()
    o_m.uniteWith(o_sad); o_sad.erase()

    # 2. 前后两道横向承重肋板 + 横担翼板 + 双 U 型螺栓环与紧固螺母
    z_xbar = -r_pipe * 0.52
    h_rib = (z_xbar + T_PLATE) - (z_bot + T_PLATE)
    for sx in (-0.32, 0.32):
        xp = sx * L
        rib = BOX(s, L=W * 0.86, W=h_rib, H=T_PLATE).translate((xp, 0.0, z_bot + T_PLATE + h_rib * 0.5))
        xbar = BOX(s, L=W, W=T_PLATE * 1.2, H=ROD_D * 2.8).translate((xp, 0.0, z_xbar))
        o_m.uniteWith(rib); rib.erase()
        o_m.uniteWith(xbar); xbar.erase()

        # U型螺栓上半圆弧 (TORUS 切掉下半部) + 两侧直腿与双螺母
        ub_arc = TORUS(s, R1=r_ub, R2=r_rod).rotateY(90.0).translate((xp, 0.0, 0.0))
        cut_low = BOX(s, L=(r_ub + r_rod) * 2.4, W=(r_ub + r_rod) * 1.4, H=ROD_D * 3.0).translate((xp, 0.0, -(r_ub + r_rod) * 0.7))
        ub_arc.subtractFrom(cut_low); cut_low.erase()
        o_m.uniteWith(ub_arc); ub_arc.erase()

        h_leg = abs(z_xbar) + T_PLATE * 2.5
        for sy in (-1.0, 1.0):
            leg = CYLINDER(s, R=r_rod, H=h_leg, O=0.0).translate((xp, sy * r_ub, -h_leg + 4.0))
            nut = BOX(s, L=ROD_D * 1.8, W=ROD_D * 1.4, H=ROD_D * 1.8).translate((xp, sy * r_ub, z_xbar - T_PLATE * 1.1))
            o_m.uniteWith(leg); leg.erase()
            o_m.uniteWith(nut); nut.erase()

    # 切除管道流道
    o_cut = CYLINDER(s, R=r_pipe, H=L + 30.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 15.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (0.0, 0.0, z_bot), (0.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, z_bot), (L / 2.0, 0.0, z_bot))
    s.setLinearDimension("W", (0.0, -W / 2.0, z_xbar), (0.0, W / 2.0, z_xbar))
