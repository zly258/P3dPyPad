# -*- coding: utf-8 -*-
# CD-ZD2010 422 双向滚动轴承吊板（双层正交矩形框 + 上下正交两组圆柱滚子 + 中部悬吊耳板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="422双向轴承吊板", TooltipLong="CD-ZD2010 422 双向滚动轴承吊板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L=LENGTH, TooltipShort="总长L", TooltipLong="双向矩形框总长 L", Ask4Dist=True)
@param(W=LENGTH, TooltipShort="总宽W", TooltipLong="双向矩形框总宽 W")
@param(H=LENGTH, TooltipShort="总高H", TooltipLong="双向轴承吊板高度 H")
@param(d=LENGTH, TooltipShort="孔径D", TooltipLong="中部悬吊耳板孔径 D")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_422(s, L=480.0, W=360.0, H=140.0, d=26.0, ID=u"ZD_422", **kw):
    L = float(L); W = float(W); H = float(H); d = float(d)
    if L < 200.0: L = 360.0
    if W < 160.0: W = 260.0
    if H < 80.0: H = 130.0
    if d < 12.0: d = 22.0
    if d > H * 0.45: d = H * 0.22

    # 1. 外层矩形导轨框 (长 L 沿 X，宽 W 沿 Y，框高 frame_h = H * 0.58)
    frame_h = H * 0.58
    t_bar = max(14.0, min(L, W) * 0.065)
    o1 = BOX(s, L=t_bar, W=frame_h, H=L).translate((0.0, -(W / 2.0 - t_bar / 2.0), -(frame_h / 2.0)))
    o_s2 = BOX(s, L=t_bar, W=frame_h, H=L).translate((0.0, (W / 2.0 - t_bar / 2.0), -(frame_h / 2.0)))
    o_e1 = BOX(s, L=W, W=frame_h, H=t_bar).translate((-(L / 2.0 - t_bar / 2.0), 0.0, -(frame_h / 2.0)))
    o_e2 = BOX(s, L=W, W=frame_h, H=t_bar).translate(((L / 2.0 - t_bar / 2.0), 0.0, -(frame_h / 2.0)))
    o1.uniteWith(o_s2); o_s2.erase()
    o1.uniteWith(o_e1); o_e1.erase()
    o1.uniteWith(o_e2); o_e2.erase()

    # 2. 上层横向滚动轴与两侧滚轮 (沿 Y 轴跨越外框，在 X 方向滚动) + 下层纵向正交导轨与中央滚子 (在 Y 方向滚动)
    r_rol = frame_h * 0.34
    z_up = -(frame_h * 0.38)
    z_dn = -(frame_h * 0.68)
    # 两条内部纵向滑轨梁 (沿 Y 轴跨越)
    inner_y = W - 2.0 * t_bar
    rail_x = L * 0.18
    for sx in (-1.0, 1.0):
        o_rail = BOX(s, L=inner_y, W=frame_h * 0.55, H=t_bar * 0.9).translate((sx * rail_x, 0.0, z_up))
        o1.uniteWith(o_rail); o_rail.erase()
    # 上层两端正交滚子 (轴沿 Y)
    for sy in (-1.0, 1.0):
        o_ru = CYLINDER(s, R=r_rol, H=t_bar * 2.2, O=0.0).rotateX(90.0).translate((0.0, sy * (W / 2.0 - t_bar), z_up))
        o1.uniteWith(o_ru); o_ru.erase()
    # 下层中央正交滚子 (轴沿 X，跨越两内部滑轨梁)
    o_rd = CYLINDER(s, R=r_rol * 1.05, H=rail_x * 2.4, O=0.0).rotateY(90.0).translate((-(rail_x * 1.2), 0.0, z_dn))
    o1.uniteWith(o_rd); o_rd.erase()

    # 3. 中部下方悬吊圆头单耳吊板 (向下伸至 Z = -H，带销孔 Ød)
    lug_w = max(d * 2.4, L * 0.16)
    lug_h = H - (-z_dn)
    o_lug = BOX(s, L=t_bar * 1.1, W=lug_h, H=lug_w).translate((0.0, 0.0, z_dn - lug_h / 2.0))
    o_lround = CYLINDER(s, R=lug_w / 2.0, H=t_bar * 1.1, O=0.0).rotateX(90.0).translate((0.0, t_bar * 0.55, -H))
    o_lug.uniteWith(o_lround); o_lround.erase()
    o_hole = CYLINDER(s, R=d / 2.0, H=t_bar * 4.0, O=0.0).rotateX(90.0).translate((0.0, t_bar * 2.0, -H))
    o_lug.subtractFrom(o_hole); o_hole.erase()
    o1.uniteWith(o_lug); o_lug.erase()

    s.setPoint((0.0, 0.0, -H), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (-(L / 2.0), 0.0, 0.0), ((L / 2.0), 0.0, 0.0))
