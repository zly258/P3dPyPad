# -*- coding: utf-8 -*-
# HG/T 21629-2021 A18 横担（图 C.1-18）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="横担", TooltipLong="HG/T 21629-2021 A18 横担 图C.1-18", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A18(s, D=36.0, SPAN=792.0, SH=150.0, B=85.0, T=12.5, ID=u"A18", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 40.0: B = 50.0
    if T < 4.0: T = 6.0
    if SH < 50.0: SH = max(80.0, B * 1.6)
    if SPAN < 150.0: SPAN = 300.0
    gap = max(16.0, T * 2.5)
    flange_w = max(35.0, B * 0.65)
    o1 = CYLINDER(s, R=0.1, H=0.1, O=0.0)
    for sx in (-1.0, 1.0):
        xc = sx * (gap / 2.0 + flange_w / 2.0)
        o_ch = BOX(s, L=SPAN, W=SH, H=flange_w).translate((xc, 0.0, -(SH / 2.0)))
        o_cut = BOX(s, L=SPAN + 10.0, W=max(10.0, SH - T * 2.0), H=max(5.0, flange_w - T)).translate((xc + sx * (T / 2.0), 0.0, -(SH / 2.0)))
        o_ch.subtractFrom(o_cut); o_cut.erase()
        o1.uniteWith(o_ch); o_ch.erase()
    end_w = gap + flange_w * 2.0
    for y_end in (-(SPAN / 2.0 - T / 2.0), (SPAN / 2.0 - T / 2.0)):
        o_end = BOX(s, L=T, W=SH, H=end_w).translate((0.0, y_end, -(SH / 2.0)))
        o1.uniteWith(o_end); o_end.erase()
    o_top_p = BOX(s, L=end_w * 0.9, W=T * 1.5, H=end_w).translate((0.0, 0.0, T * 0.75))
    o_hole = CYLINDER(s, R=gap * 0.45, H=SH + T * 4.0, O=0.0).translate((0.0, 0.0, -(SH + T)))
    o_top_p.subtractFrom(o_hole); o_hole.erase()
    o1.uniteWith(o_top_p); o_top_p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
