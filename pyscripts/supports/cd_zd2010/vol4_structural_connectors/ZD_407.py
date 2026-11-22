# -*- coding: utf-8 -*-
# CD-ZD2010 407 单孔垫板（平底方形钢板 + 中心圆孔）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="407单孔垫板", TooltipLong="CD-ZD2010 407 单孔垫板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(A=LENGTH, TooltipShort="长A", TooltipLong="垫板长边", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="宽B", TooltipLong="垫板宽边")
@param(T=LENGTH, TooltipShort="厚度", TooltipLong="垫板厚度")
@param(d=LENGTH, TooltipShort="孔径", TooltipLong="穿螺栓孔径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_407(s, A=100.0, B=100.0, T=12.0, d=23.0, ID=u"ZD_407", **kw):
    A = float(A); B = float(B); T = float(T); d = float(d)
    if A < 30.0: A = 60.0
    if B < 30.0: B = 60.0
    if T < 4.0: T = 8.0
    if d >= min(A, B) * 0.75: d = min(A, B) * 0.4

    o1 = BOX(s, L=B, W=T, H=A).translate((0.0, 0.0, -(T / 2.0)))
    o_h = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).translate((0.0, 0.0, -(T * 2.0)))
    o1.subtractFrom(o_h); o_h.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('A', (-(A / 2.0), 0.0, 0.0), ((A / 2.0), 0.0, 0.0))
