# -*- coding: utf-8 -*-
# HG/T 21629-2021 G5 地面上生根的门形架（图 C.7-5）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="地面上生根的门形架", TooltipLong="HG/T 21629-2021 G5 地面上生根的门形架 图C.7-5", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_G5(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"G5", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if D < 15.0: D = 60.3
    if B < 40.0: B = 100.0
    if T < 6.0: T = 8.0
    if SPAN < (D + 100.0): SPAN = max(420.0, D * 2.5)
    if SH < (D / 2.0 + B + 80.0): SH = D / 2.0 + B + 280.0
    R1 = D / 2.0; z_beam = -(R1 + B / 2.0); col_h = max(90.0, SH - R1 - B)
    o1 = BOX(s, L=SPAN + B * 1.2, W=B, H=B * 0.9).translate((0.0, 0.0, z_beam))
    bw = B * 2.2
    for sy in (-1.0, 1.0):
        yc = sy * (SPAN / 2.0)
        o_c = BOX(s, L=B, W=col_h, H=B * 0.9).translate((0.0, yc, z_beam - B / 2.0 - col_h / 2.0))
        o_ft = BOX(s, L=bw, W=T * 1.8, H=bw).translate((0.0, yc, -(SH - T * 0.9)))
        o_rib = BOX(s, L=bw * 0.82, W=B * 1.1, H=T).translate((0.0, yc, -(SH - T * 1.8 - B * 0.55)))
        for p in (o_c, o_ft, o_rib):
            o1.uniteWith(p); p.erase()
        for bx in (-1.0, 1.0):
            for by in (-1.0, 1.0):
                o_ab = CYLINDER(s, R=T * 0.75, H=T * 4.5, O=0.0).translate((bx * bw * 0.35, yc + by * bw * 0.35, -(SH + T * 1.2)))
                o1.uniteWith(o_ab); o_ab.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
