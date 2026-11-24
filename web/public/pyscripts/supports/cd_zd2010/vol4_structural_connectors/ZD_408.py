# -*- coding: utf-8 -*-
# CD-ZD2010 408 单耳吊板（顶部水平矩形焊接底板 + 下部垂直圆头单耳吊板带销孔）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="408单耳吊板", TooltipLong="CD-ZD2010 408 单耳吊板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L=LENGTH, TooltipShort="耳板宽", TooltipLong="吊耳板宽度 B", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="下垂高", TooltipLong="梁底至销孔中心高度 H")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="耳板厚度 t")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="穿销轴孔径 D")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_408(s, L=100.0, H=80.0, T=20.0, d=33.0, ID=u"ZD_408", **kw):
    L = float(L); H = float(H); T = float(T); d = float(d)
    if d < 10.0: d = 13.5
    if T < 6.0: T = 8.0
    if L <= d * 1.8: L = d * 2.4
    if H <= d * 1.1: H = d * 1.8
    r_ear = L / 2.0

    # 1. 顶部水平矩形焊接底板/坡口台肩 (长 L*1.18 沿 X，宽 T*2.6 沿 Y，厚 pad_t 沿 Z)
    pad_t = max(8.0, T * 0.55)
    o1 = BOX(s, L=T * 2.6, W=pad_t, H=L * 1.18).translate((0.0, 0.0, -(pad_t / 2.0)))

    # 2. 下部垂直圆头单耳吊板 (上部矩形段 Z in [0, -H] + 下部半圆弧头 R = L/2)
    o_rect = BOX(s, L=T, W=H, H=L).translate((0.0, 0.0, -(H / 2.0)))
    o_round = CYLINDER(s, R=r_ear, H=T, O=0.0).rotateX(90.0).translate((0.0, T / 2.0, -H))
    o1.uniteWith(o_rect); o_rect.erase()
    o1.uniteWith(o_round); o_round.erase()

    # 3. 底部中心圆孔 Ød (在 Z = -H 处沿 Y 轴穿透板厚 T)
    o_h = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateX(90.0).translate((0.0, T * 2.0, -H))
    o1.subtractFrom(o_h); o_h.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, -H))
