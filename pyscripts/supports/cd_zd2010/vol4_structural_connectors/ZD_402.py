# -*- coding: utf-8 -*-
# CD-ZD2010 402 焊缝加强板（槽钢端部翼缘外侧焊接折角切边加强立板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="402焊缝加强板", TooltipLong="CD-ZD2010 402 焊缝加强板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L=LENGTH, TooltipShort="板高A", TooltipLong="加强板高度 A", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="板宽B", TooltipLong="加强板宽度 B")
@param(T=LENGTH, TooltipShort="板厚t", TooltipLong="加强板厚度 t")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_402(s, L=170.0, B=71.0, T=14.0, ID=u"ZD_402", **kw):
    L = float(L); B = float(B); T = float(T)
    if L < 60.0: L = 113.0
    if B < 35.0: B = 50.0
    if T < 6.0: T = 10.0

    # 1. 被加固的水平槽钢梁端短段 (沿 X 轴长 B*2.2，槽高 ch_h = L*0.82，翼缘宽 ch_w = B*0.75)
    ch_h = L * 0.82
    ch_w = B * 0.78
    ch_t = max(6.0, T * 0.55)
    ch_len = B * 2.2
    o1 = BOX(s, L=ch_w, W=ch_h, H=ch_len).translate((-(ch_len / 2.0) + B, 0.0, 0.0))
    o_slot = BOX(s, L=ch_w - ch_t, W=ch_h - 2.0 * ch_t, H=ch_len + 4.0).translate((-(ch_len / 2.0) + B, ch_t / 2.0, 0.0))
    o1.subtractFrom(o_slot); o_slot.erase()

    # 2. 焊于槽钢开口侧翼缘端部的五边形折角焊缝加强板 (高 L 沿 Z，宽 B 沿 X，厚 T 沿 Y，上下带斜切角)
    yc = ch_w / 2.0 + T / 2.0
    o_pl = BOX(s, L=T, W=L, H=B).translate((B / 2.0, yc, 0.0))
    cham = B * 0.55
    c_diag = cham * 1.414
    for sz in (-1.0, 1.0):
        o_cut = BOX(s, L=T * 4.0, W=c_diag, H=c_diag).rotateY(45.0).translate((0.0, yc, sz * (L / 2.0)))
        o_pl.subtractFrom(o_cut); o_cut.erase()
    o1.uniteWith(o_pl); o_pl.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (B / 2.0, yc, -(L / 2.0)), (B / 2.0, yc, (L / 2.0)))
