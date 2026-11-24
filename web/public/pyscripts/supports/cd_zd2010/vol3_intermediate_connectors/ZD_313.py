# -*- coding: utf-8 -*-
# CD-ZD2010 313 双孔连接板（长方形钢板上下两端开圆孔）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="313双孔连接板", TooltipLong="CD-ZD2010 313 双孔连接板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L_pitch=LENGTH, TooltipShort="孔距", TooltipLong="上下两孔中心跨距 C", Ask4Dist=True)
@param(W=LENGTH, TooltipShort="板宽", TooltipLong="连接板宽度 B")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="连接板厚度 S")
@param(d=LENGTH, TooltipShort="孔径", TooltipLong="穿销螺栓孔径 D")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_313(s, L_pitch=132.0, W=60.0, T=12.0, d=30.0, ID=u"ZD_313", **kw):
    L_pitch = float(L_pitch); W = float(W); T = float(T); d = float(d)
    if d < 8.0: d = 8.0
    if W <= d * 1.35: W = d * 1.85
    if L_pitch < W: L_pitch = W * 1.8
    L_tot = L_pitch + W

    # 1. 长方形竖立钢板 (厚 T 沿 Y，宽 W 沿 X，总高 L_tot 沿 Z)
    o1 = BOX(s, L=T, W=L_tot, H=W)

    # 2. 上下两端圆孔 (沿 Y 轴穿透板厚 T)
    for sz in (-1.0, 1.0):
        o_h = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateX(90.0).translate((0.0, T * 2.0, sz * (L_pitch / 2.0)))
        o1.subtractFrom(o_h); o_h.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L_pitch', (0.0, 0.0, -(L_pitch / 2.0)), (0.0, 0.0, (L_pitch / 2.0)))
