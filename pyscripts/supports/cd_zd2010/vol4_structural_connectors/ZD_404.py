# -*- coding: utf-8 -*-
# CD-ZD2010 404 槽钢补强板（槽钢短段 + 槽口内焊接竖向加劲补强板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="404槽钢补强板", TooltipLong="CD-ZD2010 404 槽钢补强板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L=LENGTH, TooltipShort="长度", TooltipLong="槽钢内腔补强板高度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="宽度", TooltipLong="槽口内补强板宽度")
@param(T=LENGTH, TooltipShort="厚度", TooltipLong="补强板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_404(s, L=140.0, B=58.0, T=8.0, ID=u"ZD_404", **kw):
    L = float(L); B = float(B); T = float(T)
    if L < 60.0: L = 100.0
    if B < 30.0: B = 48.0
    if T < 5.0: T = 6.0

    # 1. 槽钢短段 (沿 X 轴长 beam_l，总高 h_tot 沿 Z，翼缘宽 w_tot 沿 Y)
    tf = max(7.5, T * 0.95)
    tw = max(5.5, T * 0.72)
    h_tot = L + 2.0 * tf
    w_tot = B + tw
    beam_l = max(130.0, L * 1.15)
    o1 = BOX(s, L=w_tot, W=h_tot, H=beam_l)
    o_slot = BOX(s, L=B + 4.0, W=L, H=beam_l + 6.0).translate((0.0, tw / 2.0 + 2.0, 0.0))
    o1.subtractFrom(o_slot); o_slot.erase()

    # 2. 槽口内正中焊接竖向补强立板 (厚 T 沿 X，宽 B 沿 Y，高 L 沿 Z)
    o_stiff = BOX(s, L=B, W=L, H=T).translate((0.0, tw / 2.0, 0.0))
    o1.uniteWith(o_stiff); o_stiff.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (0.0, 0.0, -(L / 2.0)), (0.0, 0.0, (L / 2.0)))
