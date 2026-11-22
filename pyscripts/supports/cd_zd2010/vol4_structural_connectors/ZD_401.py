# -*- coding: utf-8 -*-
# CD-ZD2010 401 单槽钢吊杆座（一段水平槽钢 + 槽内焊接带孔承重横板与三角形斜撑肋板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="401单槽钢吊杆座", TooltipLong="CD-ZD2010 401 单槽钢吊杆座", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L=LENGTH, TooltipShort="座高A", TooltipLong="吊杆座立面高度 A", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="座宽B", TooltipLong="吊杆座沿梁方向宽度 B")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="钢板厚度")
@param(d=LENGTH, TooltipShort="吊孔径", TooltipLong="穿吊杆通孔直径 D")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_401(s, L=100.0, B=100.0, T=12.0, d=22.0, ID=u"ZD_401", **kw):
    L = float(L); B = float(B); T = float(T); d = float(d)
    if L < 60.0: L = 80.0
    if B < 60.0: B = 80.0
    if T < 6.0: T = 8.0
    if d < 10.0: d = 14.0
    if d > B * 0.45: d = B * 0.3

    # 1. 一段水平槽钢短梁 (沿 X 轴长 B*1.6，高 ch_h 沿 Z，翼缘宽 ch_w 沿 -Y)
    ch_h = L * 1.15
    ch_w = B * 0.62
    ch_t = max(6.0, T * 0.65)
    ch_len = B * 1.65
    o1 = BOX(s, L=ch_w, W=ch_h, H=ch_len).translate((0.0, -(ch_w / 2.0), -(ch_h / 2.0)))
    o_c = BOX(s, L=ch_w - ch_t, W=ch_h - 2.0 * ch_t, H=ch_len + 4.0).translate((0.0, -(ch_w / 2.0 + ch_t / 2.0), -(ch_h / 2.0)))
    o1.subtractFrom(o_c); o_c.erase()

    # 2. 焊于槽钢背面的倒 L 形吊杆座：顶部带孔水平承重板 + 竖向贴合板 + 两侧斜切角三角形肋板 (图集 401 真实外形)
    arm_y = B * 0.85
    o_top = BOX(s, L=arm_y, W=T, H=B).translate((0.0, arm_y / 2.0, -(T / 2.0)))
    o_back = BOX(s, L=T, W=L, H=B).translate((0.0, T / 2.0, -(L / 2.0)))
    o1.uniteWith(o_top); o_top.erase()
    o1.uniteWith(o_back); o_back.erase()

    # 两侧斜撑三角形立肋 (位于 X = ±(B/2 - T/2))
    ang = degrees(atan2(arm_y - T, L - T))
    for sx in (-1.0, 1.0):
        xc = sx * (B / 2.0 - T / 2.0)
        o_rib = BOX(s, L=arm_y, W=L, H=T).translate((xc, arm_y / 2.0, -(L / 2.0)))
        o_cut = BOX(s, L=arm_y * 2.0, W=L * 2.0, H=T * 4.0).translate((0.0, arm_y, 0.0)).rotateX(ang).translate((xc, arm_y * 0.55, -(L * 0.55)))
        o_rib.subtractFrom(o_cut); o_cut.erase()
        o1.uniteWith(o_rib); o_rib.erase()

    # 3. 顶部水平承重板中心吊孔 Ød (沿 Z 轴穿透)
    o_h = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).translate((0.0, arm_y * 0.52, -(T * 2.0)))
    o1.subtractFrom(o_h); o_h.erase()

    s.setPoint((0.0, arm_y * 0.52, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
