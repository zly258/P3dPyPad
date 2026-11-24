# -*- coding: utf-8 -*-
# CD-ZD2010 403 H型钢/工字钢补强板（已合并 403/405：H型钢短段 + 腹板两侧对称焊接竖向加劲补强板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="403H型钢补强板", TooltipLong="CD-ZD2010 403/405 H型钢及工字钢补强板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L=LENGTH, TooltipShort="补强高", TooltipLong="H型钢内腔补强板高度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="补强宽", TooltipLong="单侧补强板宽度")
@param(T=LENGTH, TooltipShort="厚度", TooltipLong="补强钢板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_403(s, L=160.0, B=75.0, T=10.0, ID=u"ZD_403", **kw):
    L = float(L); B = float(B); T = float(T)
    if L < 60.0: L = 120.0
    if B < 30.0: B = 55.0
    if T < 5.0: T = 8.0

    # 1. H 型钢短段 (沿 X 轴长 beam_l，总高 h_tot 沿 Z，总宽 w_tot 沿 Y)
    tf = max(8.0, T * 0.95)
    tw = max(6.0, T * 0.70)
    h_tot = L + 2.0 * tf
    w_tot = B * 2.0 + tw
    beam_l = max(140.0, L * 1.15)
    o1 = BOX(s, L=w_tot, W=tf, H=beam_l).translate((0.0, 0.0, (h_tot - tf) / 2.0))
    o_fl_b = BOX(s, L=w_tot, W=tf, H=beam_l).translate((0.0, 0.0, -((h_tot - tf) / 2.0)))
    o_web = BOX(s, L=tw, W=L + 2.0, H=beam_l)
    o1.uniteWith(o_fl_b); o_fl_b.erase()
    o1.uniteWith(o_web); o_web.erase()

    # 2. 腹板左右两侧 (±Y) 对称焊接的竖向带切角补强肋板 (厚 T 沿 X，宽 B 沿 Y，高 L 沿 Z)
    for sy in (-1.0, 1.0):
        yc = sy * (tw / 2.0 + B / 2.0)
        o_stiff = BOX(s, L=B, W=L, H=T).translate((0.0, yc, 0.0))
        o1.uniteWith(o_stiff); o_stiff.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (0.0, 0.0, -(L / 2.0)), (0.0, 0.0, (L / 2.0)))
