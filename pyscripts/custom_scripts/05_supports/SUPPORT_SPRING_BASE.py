# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"座式可变弹簧支座",
    TooltipLong=u"化工管道底部支撑用座式可变弹簧支座 (VS-F 型，符合 NB/T 47039 / HG/T 21629，含弧形管托鞍板、承载柱塞顶板、带刻度窗弹簧外壳筒体与四孔地脚底板)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支承管道公称外径 (mm)")
@param(H=LENGTH, TooltipShort=u"中心高", TooltipLong=u"管道中心至支座底板底面的安装高度 (mm)")
@param(D_CAN=LENGTH, TooltipShort=u"弹簧筒外径", TooltipLong=u"可变弹簧圆柱外壳筒体外径 (mm)")
@param(H_CAN=LENGTH, TooltipShort=u"弹簧筒高度", TooltipLong=u"可变弹簧外壳筒体高度 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"底板边长", TooltipLong=u"方形地脚锚固底板边长 (mm)")
@param(T_BASE=LENGTH, TooltipShort=u"底板厚度", TooltipLong=u"方形地脚锚固底板厚度 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"支座编号", TooltipLong=u"座式可变弹簧支座型号规格编码")
def SUPPORT_SPRING_BASE(s, D=219.1, H=380.0, D_CAN=168.0, H_CAN=210.0, W_BASE=230.0, T_BASE=16.0, ID=u"VSF-DN200", **kw):
    D = max(32.0, float(D))
    r_pipe = D / 2.0
    T_BASE = max(10.0, float(T_BASE))
    H_CAN = max(120.0, float(H_CAN))
    H = max(r_pipe + H_CAN + 45.0, float(H))
    D_CAN = max(95.0, float(D_CAN))
    W_BASE = max(D_CAN + 45.0, float(W_BASE))

    z_bot = -H
    r_can = D_CAN / 2.0

    # 1. 底部四孔方形地脚锚固底板 (Z: [z_bot, z_bot + T_BASE])
    o_m = BOX(s, L=W_BASE, W=T_BASE, H=W_BASE).translate((0.0, 0.0, z_bot + T_BASE * 0.5))
    off_b = W_BASE * 0.36
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bh = CYLINDER(s, R=9.0, H=T_BASE + 4.0, O=0.0).translate((sx * off_b, sy * off_b, z_bot - 2.0))
            o_m.subtractFrom(bh); bh.erase()

    # 2. 可变弹簧圆筒外壳 + 4片底部加劲筋板 + 侧面载荷刻度牌凸窗
    o_can = CYLINDER(s, R=r_can, H=H_CAN, O=0.0).translate((0.0, 0.0, z_bot + T_BASE - 2.0))
    o_cap = CYLINDER(s, R=r_can * 1.06, H=12.0, O=0.0).translate((0.0, 0.0, z_bot + T_BASE + H_CAN - 12.0))
    o_win = BOX(s, L=36.0, W=H_CAN * 0.58, H=16.0).translate((r_can * 0.96, 0.0, z_bot + T_BASE + H_CAN * 0.5))
    for p in (o_can, o_cap, o_win):
        o_m.uniteWith(p); p.erase()

    l_rib = W_BASE * 0.44 - r_can * 0.75
    for ang_deg in (0.0, 90.0, 180.0, 270.0):
        rib = BOX(s, L=10.0, W=45.0, H=l_rib).translate((r_can * 0.75 + l_rib * 0.5, 0.0, z_bot + T_BASE + 20.0)).rotateZ(ang_deg)
        o_m.uniteWith(rib); rib.erase()

    # 3. 承载升降柱塞 + 荷载顶板 + 管道底部弧形鞍座管托
    z_can_top = z_bot + T_BASE + H_CAN
    z_saddle_bot = -r_pipe - 14.0
    h_piston = max(20.0, z_saddle_bot - z_can_top + 14.0)
    o_pis = CYLINDER(s, R=r_can * 0.62, H=h_piston, O=0.0).translate((0.0, 0.0, z_can_top - 6.0))
    o_load_pl = CYLINDER(s, R=r_can * 0.88, H=16.0, O=0.0).translate((0.0, 0.0, z_saddle_bot - 14.0))
    o_m.uniteWith(o_pis); o_pis.erase()
    o_m.uniteWith(o_load_pl); o_load_pl.erase()

    # 弧形鞍座 + 纵向腹板连接管道底面
    l_sad = min(W_BASE * 0.85, max(120.0, D * 0.75))
    t_sad = max(10.0, D * 0.05)
    r_sad = r_pipe + t_sad
    o_sad = CYLINDER(s, R=r_sad, H=l_sad, O=0.0).rotateY(90.0).translate((-l_sad * 0.5, 0.0, 0.0))
    o_trim_top = BOX(s, L=r_sad * 2.4, W=r_sad * 1.45, H=l_sad + 10.0).translate((0.0, 0.0, r_sad * 0.45))
    o_sad.subtractFrom(o_trim_top); o_trim_top.erase()

    h_web = r_pipe * 0.55 + 22.0
    o_web = BOX(s, L=14.0, W=h_web, H=l_sad * 0.8).translate((0.0, 0.0, z_saddle_bot + h_web * 0.5 - 4.0))
    o_m.uniteWith(o_sad); o_sad.erase()
    o_m.uniteWith(o_web); o_web.erase()

    o_cut = CYLINDER(s, R=r_pipe, H=l_sad + 20.0, O=0.0).rotateY(90.0).translate((-(l_sad * 0.5 + 10.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (0.0, 0.0, z_bot), (0.0, 0.0, 0.0))
    s.setLinearDimension("W_BASE", (-W_BASE / 2.0, -W_BASE / 2.0, z_bot), (W_BASE / 2.0, -W_BASE / 2.0, z_bot))
