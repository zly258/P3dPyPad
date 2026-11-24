# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"大口径双腹板重型鞍式管托",
    TooltipLong=u"化工大口径管道双腹板重型鞍式滑动管托 (J3/J4 型，符合 HG/T 21629，含 120° 弧形承重鞍板、双纵腹板、横向加劲肋与底部 PTFE 聚四氟乙烯滑板)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支承大口径管道公称外径 (mm)")
@param(H=LENGTH, TooltipShort=u"管托中心高", TooltipLong=u"管道中心至管托底板底面的距离 (mm)")
@param(L=LENGTH, TooltipShort=u"管托长度", TooltipLong=u"管托沿管道轴向的总长度 (mm)")
@param(W=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"下部承重底板横向宽度 (mm)")
@param(T_BASE=LENGTH, TooltipShort=u"底板厚度", TooltipLong=u"管托底板与鞍板名义壁厚 (mm)")
@param(T_WEB=LENGTH, TooltipShort=u"腹板厚度", TooltipLong=u"双纵向腹板与横向筋板壁厚 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"管托编号", TooltipLong=u"重型鞍式管托型号规格编码")
def SUPPORT_CRADLE_SADDLE(s, D=406.4, H=305.0, L=350.0, W=320.0, T_BASE=16.0, T_WEB=12.0, ID=u"J3-DN400", **kw):
    D = max(159.0, float(D))
    r_pipe = D / 2.0
    H = max(r_pipe + 65.0, float(H))
    L = max(200.0, float(L))
    W = max(D * 0.68, float(W))
    T_BASE = max(10.0, float(T_BASE))
    T_WEB = max(8.0, float(T_WEB))

    z_bot = -H
    r_sad = r_pipe + T_BASE

    # 1. 底部滑动钢底板 + 底部中央 PTFE 聚四氟乙烯耐磨滑片台 (H沿X=L, L沿Y=W, W沿Z=T)
    o_m = BOX(s, L=W, W=T_BASE, H=L).translate((0.0, 0.0, z_bot + 4.0 + T_BASE * 0.5))
    o_ptfe = BOX(s, L=W * 0.88, W=6.0, H=L * 0.88).translate((0.0, 0.0, z_bot + 3.0))
    o_m.uniteWith(o_ptfe); o_ptfe.erase()

    # 2. 120° 包角弧形鞍式托板
    o_sad = CYLINDER(s, R=r_sad, H=L, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    o_trim_top = BOX(s, L=r_sad * 2.4, W=r_sad * 1.55, H=L + 20.0).translate((0.0, 0.0, r_sad * 0.45))
    o_sad.subtractFrom(o_trim_top); o_trim_top.erase()
    o_m.uniteWith(o_sad); o_sad.erase()

    # 3. 对称双纵向承重腹板 + 3 道横向加劲肋板
    y_web = min(W * 0.34, r_pipe * 0.55)
    h_web = H - r_pipe * 0.45
    z_web_c = z_bot + T_BASE + h_web * 0.5
    for sy in (-1.0, 1.0):
        wb = BOX(s, L=T_WEB, W=h_web, H=L * 0.94).translate((0.0, sy * y_web, z_web_c))
        o_m.uniteWith(wb); wb.erase()

    for sx in (-0.38, 0.0, 0.38):
        rib = BOX(s, L=W * 0.88, W=h_web * 0.92, H=T_WEB).translate((sx * L, 0.0, z_bot + T_BASE + h_web * 0.46))
        o_m.uniteWith(rib); rib.erase()

    # 4. 切除上方管道圆柱面确保 100% 贴合
    o_cut = CYLINDER(s, R=r_pipe, H=L + 30.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 15.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (0.0, 0.0, z_bot), (0.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, z_bot), (L / 2.0, 0.0, z_bot))
    s.setLinearDimension("W", (0.0, -W / 2.0, z_bot), (0.0, W / 2.0, z_bot))
