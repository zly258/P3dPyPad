# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"双向轴向止推固定管托",
    TooltipLong=u"化工热力补偿管段双向轴向止推限位固定管托 (K1 型，符合 HG/T 21629，含双环带耳抱箍止推板、H型双腹板管托、四向止推斜肋板与底部十字抗剪键)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被锚固限位管道公称外径 (mm)")
@param(H=LENGTH, TooltipShort=u"管托中心高", TooltipLong=u"管道中心至管托底板底面的距离 (mm)")
@param(L=LENGTH, TooltipShort=u"管托总长", TooltipLong=u"止推管托轴向总长度 (mm)")
@param(W=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"锚固底板横向宽度 (mm)")
@param(T_SHOE=LENGTH, TooltipShort=u"主板壁厚", TooltipLong=u"底板、止推环及腹板名义厚度 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"管托编号", TooltipLong=u"双向轴向止推固定管托型号规格编码")
def SUPPORT_AXIAL_STOP(s, D=219.1, H=210.0, L=320.0, W=240.0, T_SHOE=14.0, ID=u"K1-DN200", **kw):
    D = max(32.0, float(D))
    r_pipe = D / 2.0
    T_SHOE = max(10.0, float(T_SHOE))
    H = max(r_pipe + 75.0, float(H))
    L = max(220.0, float(L))
    W = max(D * 0.85 + 40.0, float(W))

    z_bot = -H

    # 1. 底部加宽四孔锚固底板 (Z: [z_bot, z_bot + T_SHOE])
    o_m = BOX(s, L=W, W=T_SHOE, H=L).translate((0.0, 0.0, z_bot + T_SHOE * 0.5))
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bh = CYLINDER(s, R=9.0, H=T_SHOE + 4.0, O=0.0).translate((sx * L * 0.38, sy * W * 0.36, z_bot - 2.0))
            o_m.subtractFrom(bh); bh.erase()

    # 2. 双道全周重型止推抱箍 + 水平螺栓耳板 + 横向高耸止推抗剪墙
    r_ring = r_pipe + T_SHOE * 1.85
    h_rib = H - T_SHOE
    for sx in (-0.26, 0.26):
        rg = CYLINDER(s, R=r_ring, H=T_SHOE * 1.8, O=0.0).rotateY(90.0).translate((sx * L - T_SHOE * 0.9, 0.0, 0.0))
        ear = BOX(s, L=r_ring * 2.38, W=T_SHOE * 2.6, H=T_SHOE * 2.2).translate((sx * L, 0.0, 0.0))
        rb = BOX(s, L=W * 0.92, W=h_rib, H=T_SHOE * 1.4).translate((sx * L, 0.0, z_bot + T_SHOE + h_rib * 0.5))
        for p in (rg, ear, rb):
            o_m.uniteWith(p); p.erase()

    # 中央承重鞍座与双纵向腹板
    o_sad = CYLINDER(s, R=r_pipe + T_SHOE, H=L * 0.86, O=0.0).rotateY(90.0).translate((-L * 0.43, 0.0, 0.0))
    o_trim = BOX(s, L=r_ring * 2.2, W=r_ring * 1.4, H=L).translate((0.0, 0.0, r_ring * 0.45))
    o_sad.subtractFrom(o_trim); o_trim.erase()
    o_m.uniteWith(o_sad); o_sad.erase()

    h_web = H - r_pipe * 0.45
    for sy in (-0.22, 0.22):
        wb = BOX(s, L=T_SHOE, W=h_web, H=L * 0.86).translate((0.0, sy * W, z_bot + T_SHOE + h_web * 0.5))
        o_m.uniteWith(wb); wb.erase()

    # 3. 切除中心管道圆柱通孔
    o_cut = CYLINDER(s, R=r_pipe, H=L + 30.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 15.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (0.0, 0.0, z_bot), (0.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, z_bot), (L / 2.0, 0.0, z_bot))
    s.setLinearDimension("W", (0.0, -W / 2.0, z_bot), (0.0, W / 2.0, z_bot))
