# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"双可变弹簧鞍式支承座架",
    TooltipLong=u"化工重型热力主管与塔器下引管用对称双可变弹簧座架 (VS-R / HG/T 21629，含重型管道抱箍横梁、两侧对称双可变弹簧缸筒、载荷刻度牌、升降承载柱塞与公用长底板)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支承重型管道公称外径 (mm)")
@param(H=LENGTH, TooltipShort=u"中心高", TooltipLong=u"管道中心至双弹簧公用底板底面的高度 (mm)")
@param(SPAN=LENGTH, TooltipShort=u"双弹簧中心距", TooltipLong=u"左右两台可变弹簧筒中心线横向跨距 (mm)")
@param(D_CAN=LENGTH, TooltipShort=u"弹簧筒直径", TooltipLong=u"单台可变弹簧筒体外径 (mm)")
@param(H_CAN=LENGTH, TooltipShort=u"弹簧筒高度", TooltipLong=u"可变弹簧筒体高度 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"底座顺管宽", TooltipLong=u"底部公用底板顺管道方向宽度 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"支吊架编号", TooltipLong=u"双可变弹簧支承座架型号编码")
def SUPPORT_RISER_SPRING_STAND(s, D=273.0, H=420.0, SPAN=460.0, D_CAN=159.0, H_CAN=220.0, W_BASE=220.0, ID=u"VSR-DN250", **kw):
    D = max(88.9, float(D))
    r_pipe = D / 2.0
    D_CAN = max(108.0, float(D_CAN))
    r_can = D_CAN / 2.0
    H_CAN = max(140.0, float(H_CAN))
    H = max(r_pipe + H_CAN + 55.0, float(H))
    SPAN = max(D + D_CAN * 1.15, float(SPAN))
    W_BASE = max(D_CAN + 45.0, float(W_BASE))

    z_bot = -H
    t_base = 18.0
    l_base = SPAN + D_CAN + 60.0

    # 1. 底部公用长矩形锚固底板 (H=dx=W_BASE, L=dy=l_base, W=dz=t_base)
    o_m = BOX(s, L=l_base, W=t_base, H=W_BASE).translate((0.0, 0.0, z_bot + t_base * 0.5))

    # 2. 左右对称两台座式可变弹簧筒体 + 承载柱塞 + 刻度牌
    z_beam_bot = -(r_pipe + 42.0)
    h_pis = max(25.0, z_beam_bot - (z_bot + t_base + H_CAN) + 12.0)
    for sy in (-1.0, 1.0):
        yc = sy * SPAN * 0.5
        can = CYLINDER(s, R=r_can, H=H_CAN, O=0.0).translate((0.0, yc, z_bot + t_base - 2.0))
        cap = CYLINDER(s, R=r_can * 1.06, H=14.0, O=0.0).translate((0.0, yc, z_bot + t_base + H_CAN - 14.0))
        pis = CYLINDER(s, R=r_can * 0.60, H=h_pis, O=0.0).translate((0.0, yc, z_bot + t_base + H_CAN - 6.0))
        win = BOX(s, L=14.0, W=H_CAN * 0.55, H=38.0).translate((r_can * 0.96, yc, z_bot + t_base + H_CAN * 0.5))
        for p in (can, cap, pis, win):
            o_m.uniteWith(p); p.erase()

    # 3. 上部跨接承重箱梁 + 中央管道重型鞍座与抱箍
    w_beam_y = SPAN + D_CAN * 0.85
    o_beam = BOX(s, L=w_beam_y, W=36.0, H=W_BASE * 0.72).translate((0.0, 0.0, z_beam_bot + 18.0))
    o_clamp = CYLINDER(s, R=r_pipe + 14.0, H=W_BASE * 0.72, O=0.0).rotateY(90.0).translate((-W_BASE * 0.36, 0.0, 0.0))
    o_web = BOX(s, L=D * 0.82, W=r_pipe * 0.65 + 20.0, H=W_BASE * 0.68).translate((0.0, 0.0, z_beam_bot + 28.0))
    for p in (o_beam, o_clamp, o_web):
        o_m.uniteWith(p); p.erase()

    o_cut = CYLINDER(s, R=r_pipe, H=W_BASE + 20.0, O=0.0).rotateY(90.0).translate((-(W_BASE * 0.5 + 10.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (0.0, 0.0, z_bot), (0.0, 0.0, 0.0))
    s.setLinearDimension("SPAN", (0.0, -SPAN / 2.0, z_bot), (0.0, SPAN / 2.0, z_bot))
