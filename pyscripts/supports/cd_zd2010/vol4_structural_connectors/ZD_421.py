# -*- coding: utf-8 -*-
# CD-ZD2010 421 单向滚动轴承吊板（倒置槽形/双侧板钢架 + 内部横向圆柱滚子轴承 + 底部悬吊单耳吊板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="421单向轴承吊板", TooltipLong="CD-ZD2010 421 单向滚动轴承吊板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L=LENGTH, TooltipShort="总长L", TooltipLong="轴承吊板框架总长 L", Ask4Dist=True)
@param(W=LENGTH, TooltipShort="总宽W", TooltipLong="轴承架总宽 W")
@param(H=LENGTH, TooltipShort="总高H", TooltipLong="轴承吊板高度 H")
@param(d=LENGTH, TooltipShort="吊孔径D", TooltipLong="下部悬吊耳板销孔直径 D")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_421(s, L=455.0, W=126.0, H=165.0, d=22.0, ID=u"ZD_421", **kw):
    L = float(L); W = float(W); H = float(H); d = float(d)
    if L < 180.0: L = 320.0
    if W < 80.0 or W > 500.0: W = 132.0
    if H < 60.0: H = 140.0
    if d < 12.0: d = 22.0
    if d > H * 0.45: d = H * 0.22

    # 1. 上部倒置槽形钢架：顶板 + 前后两片长侧板 (带两端工字梁连接立耳与长圆滑槽视窗)
    frame_h = H * 0.56
    t_pl = max(12.0, W * 0.11)
    o1 = BOX(s, L=W, W=t_pl, H=L).translate((0.0, 0.0, -(t_pl / 2.0)))
    side_y = W / 2.0 - t_pl / 2.0
    for sy in (-1.0, 1.0):
        o_side = BOX(s, L=t_pl, W=frame_h, H=L).translate((0.0, sy * side_y, -(frame_h / 2.0)))
        o1.uniteWith(o_side); o_side.erase()
    # 两端生根端板
    for sx in (-1.0, 1.0):
        o_end = BOX(s, L=W * 1.15, W=frame_h * 1.15, H=t_pl).translate((sx * (L / 2.0 - t_pl / 2.0), 0.0, -(frame_h / 2.0)))
        o1.uniteWith(o_end); o_end.erase()

    # 2. 框架内部大直径横向圆柱滚子轴承与中心滚子轴 (沿 Y 轴贯通两侧板)
    rol_r = (frame_h - t_pl) * 0.42
    z_rol = -(t_pl + rol_r * 0.95)
    o_roller = CYLINDER(s, R=rol_r, H=W - 2.0 * t_pl - 4.0, O=0.0).rotateX(90.0).translate((0.0, (W - 2.0 * t_pl - 4.0) / 2.0, z_rol))
    o_axle = CYLINDER(s, R=rol_r * 0.38, H=W + t_pl * 1.6, O=0.0).rotateX(90.0).translate((0.0, (W + t_pl * 1.6) / 2.0, z_rol))
    o1.uniteWith(o_roller); o_roller.erase()
    o1.uniteWith(o_axle); o_axle.erase()

    # 3. 底部悬吊圆头单耳吊板 (从滚子轴承包箍向下悬伸至 Z = -H，带吊孔 Ød)
    lug_w = max(d * 2.4, L * 0.16)
    lug_h = H - (-z_rol)
    o_lug = BOX(s, L=t_pl * 1.2, W=lug_h, H=lug_w).translate((0.0, 0.0, z_rol - lug_h / 2.0))
    o_lround = CYLINDER(s, R=lug_w / 2.0, H=t_pl * 1.2, O=0.0).rotateX(90.0).translate((0.0, t_pl * 0.6, -H))
    o_lug.uniteWith(o_lround); o_lround.erase()
    o_hole = CYLINDER(s, R=d / 2.0, H=t_pl * 4.0, O=0.0).rotateX(90.0).translate((0.0, t_pl * 2.0, -H))
    o_lug.subtractFrom(o_hole); o_hole.erase()
    o1.uniteWith(o_lug); o_lug.erase()

    s.setPoint((0.0, 0.0, -H), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (-(L / 2.0), 0.0, 0.0), ((L / 2.0), 0.0, 0.0))
