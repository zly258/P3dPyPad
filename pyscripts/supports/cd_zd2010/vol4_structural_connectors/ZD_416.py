# -*- coding: utf-8 -*-
# CD-ZD2010 416 导向底板(I型)（矩形滑动底板 + 左右两侧向上折起的 L 形导向挡边，无外侧斜肋）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="416导向底板I型", TooltipLong="CD-ZD2010 416 导向底板（Ⅰ型）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L=LENGTH, TooltipShort="底板宽A1", TooltipLong="底板横向总宽 A1", Ask4Dist=True)
@param(W=LENGTH, TooltipShort="底板长B1", TooltipLong="底板纵向长度 B1")
@param(T=LENGTH, TooltipShort="板厚t", TooltipLong="底板厚度 t")
@param(Guide_W=LENGTH, TooltipShort="导向槽宽A", TooltipLong="两侧导向挡边内净宽 A")
@param(Guide_H=LENGTH, TooltipShort="挡边高h", TooltipLong="导向挡边高度 h")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_416(s, L=220.0, W=140.0, T=16.0, Guide_W=142.0, Guide_H=25.0, ID=u"ZD_416", **kw):
    L = float(L); W = float(W); T = float(T); Guide_W = float(Guide_W); Guide_H = float(Guide_H)
    if L < 80.0: L = 180.0
    if W < 60.0: W = 120.0
    if T < 8.0: T = 14.0
    if Guide_H < 15.0: Guide_H = 24.0
    if Guide_W <= 40.0 or Guide_W >= L - 24.0: Guide_W = L * 0.64

    # 1. 底部水平矩形基板 (宽 L 沿 Y，长 W 沿 X，厚 T 沿 Z) + 中央滑片凸台
    o1 = BOX(s, L=L, W=T, H=W).translate((0.0, 0.0, -(T / 2.0)))
    o_pad = BOX(s, L=Guide_W * 0.92, W=4.0, H=W * 0.92).translate((0.0, 0.0, 2.0))
    o1.uniteWith(o_pad); o_pad.erase()

    # 2. 左右两侧 (±Y) 向上折起的 L 形导向挡边 (高 Guide_H，带内折小唇边，无外侧三角肋)
    bar_w = min(22.0, (L - Guide_W) * 0.42)
    for sy in (-1.0, 1.0):
        yc = sy * (Guide_W / 2.0 + bar_w / 2.0)
        o_g = BOX(s, L=bar_w, W=Guide_H, H=W).translate((0.0, yc, Guide_H / 2.0))
        o_lip = BOX(s, L=bar_w * 1.35, W=Guide_H * 0.28, H=W).translate((0.0, sy * (Guide_W / 2.0 + bar_w * 0.32), Guide_H - Guide_H * 0.14))
        o1.uniteWith(o_g); o_g.erase()
        o1.uniteWith(o_lip); o_lip.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('L', (0.0, -(L / 2.0), 0.0), (0.0, (L / 2.0), 0.0))
