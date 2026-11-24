# -*- coding: utf-8 -*-
# CD-ZD2010 417 导向底板(II型)（矩形滑动底板 + 左右两侧高立板 + 外侧三角形斜向加劲肋板，与 416 明显区分！）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="417导向底板II型", TooltipLong="CD-ZD2010 417 导向底板（Ⅱ型，带外侧三角形加劲肋）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L=LENGTH, TooltipShort="底板宽A1", TooltipLong="底板横向总宽 A1", Ask4Dist=True)
@param(W=LENGTH, TooltipShort="底板长B1", TooltipLong="底板纵向长度 B1")
@param(T=LENGTH, TooltipShort="板厚t", TooltipLong="底板厚度 t")
@param(Guide_W=LENGTH, TooltipShort="导向间距A", TooltipLong="两侧高立板内净距 A")
@param(Guide_H=LENGTH, TooltipShort="立板高h", TooltipLong="高导向立板高度 h")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_417(s, L=300.0, W=220.0, T=19.0, Guide_W=160.0, Guide_H=70.0, ID=u"ZD_417", **kw):
    L = float(L); W = float(W); T = float(T); Guide_W = float(Guide_W); Guide_H = float(Guide_H)
    if L < 120.0: L = 260.0
    if W < 100.0: W = 180.0
    if T < 10.0: T = 16.0
    if Guide_H < 40.0 or Guide_H > 180.0: Guide_H = 70.0
    if Guide_W <= 50.0 or Guide_W >= L - 50.0: Guide_W = L * 0.52

    # 1. 底部水平矩形基板 (宽 L 沿 Y，长 W 沿 X，厚 T 沿 Z)
    o1 = BOX(s, L=L, W=T, H=W).translate((0.0, 0.0, -(T / 2.0)))

    # 2. 左右两侧 (±Y) 高导向立板 + 外侧各 3 块直角三角形斜向加劲肋板 (严格还原图集 417)
    plate_t = max(12.0, T * 0.72)
    rib_w = (L - Guide_W) / 2.0 - plate_t - 4.0
    if rib_w < 22.0: rib_w = 32.0
    rib_h = Guide_H * 0.92
    theta = degrees(atan2(rib_h, rib_w))
    big = (rib_w + rib_h) * 2.0

    for sy in (-1.0, 1.0):
        y_wall = sy * (Guide_W / 2.0 + plate_t / 2.0)
        o_wall = BOX(s, L=plate_t, W=Guide_H, H=W).translate((0.0, y_wall, Guide_H / 2.0))
        o1.uniteWith(o_wall); o_wall.erase()

        # 外侧 3 道直角三角形加劲肋板 (位于 X = -0.36*W, 0, +0.36*W)
        y0 = sy * (Guide_W / 2.0 + plate_t)
        yc_rib = y0 + sy * (rib_w / 2.0)
        for frac in (-0.36, 0.0, 0.36):
            xc = W * frac
            o_rib = BOX(s, L=rib_w, W=rib_h, H=plate_t * 0.85).translate((xc, yc_rib, rib_h / 2.0))
            o_cut = BOX(s, L=big, W=big, H=plate_t * 3.0).translate((0.0, 0.0, big / 2.0)).rotateX(-sy * theta).translate((xc, yc_rib, rib_h / 2.0))
            o_rib.subtractFrom(o_cut); o_cut.erase()
            o1.uniteWith(o_rib); o_rib.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('L', (0.0, -(L / 2.0), 0.0), (0.0, (L / 2.0), 0.0))
