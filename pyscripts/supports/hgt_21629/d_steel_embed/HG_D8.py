# -*- coding: utf-8 -*-
# HG/T 21629-2021 D8 门形/倒门形架（角钢和槽钢）（图 C.4-8）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="门形/倒门形架（角钢和槽钢）", TooltipLong="HG/T 21629-2021 D8 门形/倒门形架（角钢和槽钢） 图C.4-8", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_D8(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"D8", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if D < 15.0: D = 60.3
    if B < 40.0: B = 100.0
    if T < 5.0: T = 8.0
    if SPAN < (D + 100.0): SPAN = max(400.0, D * 2.5)
    if SH < (D / 2.0 + B + 60.0): SH = D / 2.0 + B + 250.0
    R1 = D / 2.0; z_beam = -(R1 + B / 2.0); col_h = max(80.0, SH - R1 - B)
    o1 = BOX(s, L=SPAN + B, W=B, H=T).translate((0.0, 0.0, z_beam))
    o_f1 = BOX(s, L=SPAN + B, W=T, H=B).translate((0.0, 0.0, z_beam + B / 2.0 - T / 2.0))
    o_f2 = BOX(s, L=SPAN + B, W=T, H=B).translate((0.0, 0.0, z_beam - B / 2.0 + T / 2.0))
    o1.uniteWith(o_f1); o_f1.erase()
    o1.uniteWith(o_f2); o_f2.erase()
    for sy in (-1.0, 1.0):
        yc = sy * (SPAN / 2.0)
        o_c = BOX(s, L=B, W=col_h, H=T).translate((0.0, yc, z_beam - B / 2.0 - col_h / 2.0))
        o_cf1 = BOX(s, L=T, W=col_h, H=B).translate((0.0, yc - B / 2.0 + T / 2.0, z_beam - B / 2.0 - col_h / 2.0))
        o_cf2 = BOX(s, L=T, W=col_h, H=B).translate((0.0, yc + B / 2.0 - T / 2.0, z_beam - B / 2.0 - col_h / 2.0))
        o_gus = BOX(s, L=B * 1.2, W=B * 1.2, H=T).translate((T, yc - sy * (B * 0.6), z_beam - B * 0.6))
        for p in (o_c, o_cf1, o_cf2, o_gus):
            o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
