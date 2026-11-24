# -*- coding: utf-8 -*-
# CD-ZD2010 413 槽钢加强板（两根背靠背槽钢短段 + 顶部跨接方形垫板带中心吊孔）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="413槽钢加强板", TooltipLong="CD-ZD2010 413 槽钢加强板（双槽钢顶跨接加强板）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L=LENGTH, TooltipShort="长A", TooltipLong="跨接加强板长 A", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="宽B", TooltipLong="跨接加强板宽 B")
@param(T=LENGTH, TooltipShort="厚t", TooltipLong="加强钢板厚度 t")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_413(s, L=160.0, B=110.0, T=12.0, ID=u"ZD_413", **kw):
    L = float(L); B = float(B); T = float(T)
    if L < 80.0 or L > 1000.0: L = 160.0
    if B < 60.0 or B > 800.0: B = 110.0
    if T < 6.0: T = 10.0

    # 1. 下部两根背靠背槽钢短段 (沿 X 轴长 ch_len，位于 Y = ±(gap_y/2 + ch_w/2)，Z in [-ch_h, 0])
    gap_y = max(24.0, L * 0.18)
    ch_h = L * 0.85
    ch_w = (L - gap_y) * 0.45
    ch_t = max(6.0, ch_h * 0.08)
    ch_len = B * 2.1
    yc = gap_y / 2.0 + ch_w / 2.0

    o1 = BOX(s, L=ch_w, W=ch_h, H=ch_len).translate((0.0, -yc, -(ch_h / 2.0)))
    o_c1 = BOX(s, L=ch_w - ch_t, W=ch_h - 2.0 * ch_t, H=ch_len + 4.0).translate((0.0, -(yc + ch_t / 2.0), -(ch_h / 2.0)))
    o1.subtractFrom(o_c1); o_c1.erase()

    o2 = BOX(s, L=ch_w, W=ch_h, H=ch_len).translate((0.0, yc, -(ch_h / 2.0)))
    o_c2 = BOX(s, L=ch_w - ch_t, W=ch_h - 2.0 * ch_t, H=ch_len + 4.0).translate((0.0, (yc + ch_t / 2.0), -(ch_h / 2.0)))
    o2.subtractFrom(o_c2); o_c2.erase()
    o1.uniteWith(o2); o2.erase()

    # 2. 顶部跨接方形加强垫板 (宽 L 沿 Y 跨越双槽钢，长 B 沿 X，厚 T 沿 Z in [0, T]) + 中心吊孔
    o_cap = BOX(s, L=L, W=T, H=B).translate((0.0, 0.0, T / 2.0))
    hole_r = gap_y * 0.42
    o_h = CYLINDER(s, R=hole_r, H=T * 4.0, O=0.0).translate((0.0, 0.0, -T))
    o_cap.subtractFrom(o_h); o_h.erase()
    o1.uniteWith(o_cap); o_cap.erase()

    s.setPoint((0.0, 0.0, T), (0.0, 0.0, 1.0))
    s.setLinearDimension('L', (0.0, -(L / 2.0), T), (0.0, (L / 2.0), T))
