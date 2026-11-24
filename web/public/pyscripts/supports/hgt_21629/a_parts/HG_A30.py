# -*- coding: utf-8 -*-
# HG/T 21629-2021 A30 单孔U形吊耳（图 C.1-30）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="单孔U形吊耳", TooltipLong="HG/T 21629-2021 A30 单孔U形吊耳 图C.1-30", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径或基准直径")
@param(H=LENGTH, TooltipShort="吊板高", TooltipLong="吊孔中心至底端/管壁高度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="吊板宽", TooltipLong="吊板/吊耳宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="吊板/耳板厚度")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="吊孔/销子直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A30(s, D=20.0, H=104.0, B=60.0, T=16.0, d=26.0, ID=u"A30", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if T < 6.0: T = 8.0
    if d < 10.0: d = 14.0
    if B < d * 2.0: B = d * 2.5
    if H < B * 1.2: H = B * 1.8
    inner_w = max(d * 2.4, B * 1.2)
    tot_w = inner_w + T * 2.0
    # 1. U形折弯扁钢底面水平板（位于 Z = 0 ~ T，中心开单孔供吊杆穿过）
    o1 = BOX(s, L=tot_w, W=T, H=B).translate((0.0, 0.0, T / 2.0))
    o_hole = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).translate((0.0, 0.0, -T))
    o1.subtractFrom(o_hole); o_hole.erase()
    # 2. 左右两侧向上延伸的竖直扁钢长腿（焊接于上部钢梁两侧或底面）
    leg_h = H - T
    for sy in (-(inner_w / 2.0 + T / 2.0), (inner_w / 2.0 + T / 2.0)):
        o_leg = BOX(s, L=T, W=leg_h, H=B).translate((0.0, sy, T + leg_h / 2.0))
        o1.uniteWith(o_leg); o_leg.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
