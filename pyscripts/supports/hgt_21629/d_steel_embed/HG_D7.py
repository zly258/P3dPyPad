# -*- coding: utf-8 -*-
# HG/T 21629-2021 D7 L形/倒L形架（图 C.4-7）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="L形/倒L形架", TooltipLong="HG/T 21629-2021 D7 L形/倒L形架 图C.4-7", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_D7(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"D7", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 40.0: B = 80.0
    if T < 5.0: T = 8.0
    if SPAN < 150.0: SPAN = 400.0
    if SH < 120.0: SH = 300.0
    R1 = D / 2.0; z_beam = -(R1 + B / 2.0)
    o1 = BOX(s, L=SPAN, W=T, H=B).translate((0.0, -(SPAN / 2.0), z_beam + B / 2.0 - T / 2.0))
    o_bw = BOX(s, L=SPAN, W=B, H=T).translate((B / 2.0 - T / 2.0, -(SPAN / 2.0), z_beam))
    col_h = max(80.0, SH - R1)
    o_col = BOX(s, L=T, W=col_h, H=B).translate((0.0, -SPAN + T / 2.0, -(R1 + col_h / 2.0)))
    o_cw = BOX(s, L=B, W=col_h, H=T).translate((B / 2.0 - T / 2.0, -SPAN + B / 2.0, -(R1 + col_h / 2.0)))
    o_gus = BOX(s, L=B * 1.4, W=B * 1.4, H=T).translate((-(T / 2.0), -(SPAN - B * 0.7), z_beam - B * 0.5))
    for p in (o_bw, o_col, o_cw, o_gus):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
