# -*- coding: utf-8 -*-
# HG/T 21629-2021 D16 水平门形/井形架（图 C.4-16）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="水平门形/井形架", TooltipLong="HG/T 21629-2021 D16 水平门形/井形架 图C.4-16", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_D16(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"D16", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 50.0: B = 100.0
    if T < 6.0: T = 8.0
    if SPAN < 250.0: SPAN = 600.0
    if SH < 250.0: SH = 500.0
    R1 = D / 2.0; z_grid = -(R1 + B / 2.0)
    o1 = CYLINDER(s, R=0.1, H=0.1, O=0.0)
    # 1. 左右两根沿 Y 轴平行悬挑的 H 型钢纵梁（X = ±SPAN*0.42，长 SH）
    for sx in (-1.0, 1.0):
        xc = sx * (SPAN * 0.42)
        o_w = BOX(s, L=SH, W=B, H=T).translate((xc, -(SH / 2.0), z_grid))
        o_f1 = BOX(s, L=SH, W=T, H=B).translate((xc, -(SH / 2.0), z_grid + B / 2.0 - T / 2.0))
        o_f2 = BOX(s, L=SH, W=T, H=B).translate((xc, -(SH / 2.0), z_grid - B / 2.0 + T / 2.0))
        o_rt = BOX(s, L=T * 1.5, W=B * 1.5, H=B * 1.5).translate((xc, -SH, z_grid))
        for p in (o_w, o_f1, o_f2, o_rt):
            o1.uniteWith(p); p.erase()
    # 2. 前后两根沿 X 轴正交交错的 H 型钢横梁（Y = -SH*0.18 与 -SH*0.65，长 SPAN + B）
    for yc in (-(SH * 0.18), -(SH * 0.65)):
        o_cw = BOX(s, L=T, W=B, H=SPAN + B).translate((0.0, yc, z_grid))
        o_cf1 = BOX(s, L=B, W=T, H=SPAN + B).translate((0.0, yc, z_grid + B / 2.0 - T / 2.0))
        o_cf2 = BOX(s, L=B, W=T, H=SPAN + B).translate((0.0, yc, z_grid - B / 2.0 + T / 2.0))
        for p in (o_cw, o_cf1, o_cf2):
            o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
