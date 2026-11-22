# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"弯头竖直耳轴支座",
    TooltipLong=u"化工泵进出口及弯头底部竖直耳轴管墩支座 (F2 型，符合 HG/T 21629，含管道补强垫板鞍座、厚壁无缝耳轴立管、四向梯形加劲肋板与四孔地脚锚固底板)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"母管外径", TooltipLong=u"被支承管道或弯头的公称外径 (mm)")
@param(D_TRUN=LENGTH, TooltipShort=u"耳轴管外径", TooltipLong=u"竖直支承耳轴无缝钢管外径 (mm)")
@param(H=LENGTH, TooltipShort=u"中心高", TooltipLong=u"管道中心至支座底板底面的总高度 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"底板边长", TooltipLong=u"方形地脚锚固底板边长 (mm)")
@param(T_BASE=LENGTH, TooltipShort=u"底板厚度", TooltipLong=u"地脚底板及补强垫板壁厚 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"支座编号", TooltipLong=u"弯头竖直耳轴支座型号规格编码")
def SUPPORT_ELBOW_TRUNNION(s, D=219.1, D_TRUN=133.0, H=450.0, W_BASE=260.0, T_BASE=18.0, ID=u"F2-DN200", **kw):
    D = max(48.0, float(D))
    D_TRUN = min(D * 0.9, max(38.0, float(D_TRUN)))
    r_pipe = D / 2.0
    r_trun = D_TRUN / 2.0
    T_BASE = max(10.0, float(T_BASE))
    H = max(r_pipe + 140.0, float(H))
    W_BASE = max(D_TRUN + 90.0, float(W_BASE))

    z_bot = -H

    # 1. 底部四孔方形地脚底板
    o_m = BOX(s, L=W_BASE, W=T_BASE, H=W_BASE).translate((0.0, 0.0, z_bot + T_BASE * 0.5))
    off_b = W_BASE * 0.36
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bh = CYLINDER(s, R=10.0, H=T_BASE + 4.0, O=0.0).translate((sx * off_b, sy * off_b, z_bot - 2.0))
            o_m.subtractFrom(bh); bh.erase()

    # 2. 竖直厚壁耳轴立管 + 根部四向正交加劲肋板
    h_trun = H - r_pipe * 0.55
    o_trun = CYLINDER(s, R=r_trun, H=h_trun, O=0.0).translate((0.0, 0.0, z_bot + T_BASE - 2.0))
    o_m.uniteWith(o_trun); o_trun.erase()

    h_rib = min(140.0, h_trun * 0.42)
    w_gus = W_BASE * 0.86
    g_x = BOX(s, L=12.0, W=h_rib, H=w_gus).translate((0.0, 0.0, z_bot + T_BASE + h_rib * 0.5 - 2.0))
    g_y = BOX(s, L=w_gus, W=h_rib, H=12.0).translate((0.0, 0.0, z_bot + T_BASE + h_rib * 0.5 - 2.0))
    o_m.uniteWith(g_x); g_x.erase()
    o_m.uniteWith(g_y); g_y.erase()

    # 3. 顶部与母管/弯头贴合的弧形补强垫板鞍座
    l_pad = D_TRUN + 60.0
    r_pad = r_pipe + T_BASE * 0.75
    o_pad = CYLINDER(s, R=r_pad, H=l_pad, O=0.0).rotateY(90.0).translate((-l_pad * 0.5, 0.0, 0.0))
    o_trim = BOX(s, L=r_pad * 2.4, W=r_pad * 1.5, H=l_pad + 20.0).translate((0.0, 0.0, r_pad * 0.45))
    o_pad.subtractFrom(o_trim); o_trim.erase()
    o_m.uniteWith(o_pad); o_pad.erase()

    # 切除母管圆柱流道外径
    o_cut = CYLINDER(s, R=r_pipe, H=l_pad + 30.0, O=0.0).rotateY(90.0).translate((-(l_pad * 0.5 + 15.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (0.0, 0.0, z_bot), (0.0, 0.0, 0.0))
    s.setLinearDimension("W_BASE", (-W_BASE / 2.0, -W_BASE / 2.0, z_bot), (W_BASE / 2.0, -W_BASE / 2.0, z_bot))
