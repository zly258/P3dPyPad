# -*- coding: utf-8 -*-
# HG/T 21629-2021 D10 辅助梁（图 C.4-10）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="辅助梁", TooltipLong="HG/T 21629-2021 D10 辅助梁 图C.4-10", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_D10(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"D10", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 50.0: B = 100.0
    if T < 5.0: T = 8.0
    if SPAN < 200.0: SPAN = 600.0
    R1 = D / 2.0; z_b = -(R1 + B / 2.0)
    o1 = BOX(s, L=SPAN, W=B, H=T).translate((0.0, 0.0, z_b))
    o_f1 = BOX(s, L=SPAN, W=T, H=B).translate((0.0, 0.0, z_b + B / 2.0 - T / 2.0))
    o_f2 = BOX(s, L=SPAN, W=T, H=B).translate((0.0, 0.0, z_b - B / 2.0 + T / 2.0))
    o1.uniteWith(o_f1); o_f1.erase()
    o1.uniteWith(o_f2); o_f2.erase()
    for sy in (-1.0, 1.0):
        o_ep = BOX(s, L=T * 1.4, W=B * 1.35, H=B * 1.35).translate((0.0, sy * (SPAN / 2.0), z_b))
        o_stif = BOX(s, L=B * 0.8, W=B - T * 2.0, H=T).translate((0.0, sy * (SPAN * 0.25), z_b))
        o1.uniteWith(o_ep); o_ep.erase()
        o1.uniteWith(o_stif); o_stif.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
