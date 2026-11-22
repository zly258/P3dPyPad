# -*- coding: utf-8 -*-
# HG/T 21629-2021 G2 混凝土锚板（膨胀螺栓）（图 C.7-2）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="混凝土锚板（膨胀螺栓）", TooltipLong="HG/T 21629-2021 G2 混凝土锚板（膨胀螺栓） 图C.7-2", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_G2(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"G2", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if SPAN < 100.0: SPAN = 260.0
    if B < 80.0: B = SPAN
    if T < 8.0: T = 14.0
    if SH < 80.0: SH = 160.0
    o1 = BOX(s, L=SPAN, W=T, H=B).translate((0.0, 0.0, -(T / 2.0)))
    bolt_r = max(6.0, T * 0.55)
    dx = B * 0.34; dy = SPAN * 0.34
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            o_b = CYLINDER(s, R=bolt_r, H=SH + bolt_r * 2.5, O=0.0).translate((sx * dx, sy * dy, -SH))
            o_w = CYLINDER(s, R=bolt_r * 2.0, H=T * 0.25, O=0.0).translate((sx * dx, sy * dy, 0.0))
            o_n = CYLINDER(s, R=bolt_r * 1.6, H=bolt_r * 1.4, O=0.0).translate((sx * dx, sy * dy, T * 0.25))
            o_exp = CONE(s, R1=bolt_r * 1.55, R2=bolt_r * 1.1, H=SH * 0.45, E=0.0).translate((sx * dx, sy * dy, -(SH * 0.92)))
            for p in (o_b, o_w, o_n, o_exp):
                o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
