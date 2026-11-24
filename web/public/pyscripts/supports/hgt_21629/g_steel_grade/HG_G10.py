# -*- coding: utf-8 -*-
# HG/T 21629-2021 G10 软管站用支架（图 C.7-10）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="软管站用支架", TooltipLong="HG/T 21629-2021 G10 软管站用支架 图C.7-10", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_G10(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"G10", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 45.0: B = 60.3
    if T < 4.0: T = 8.0
    if SPAN < 280.0: SPAN = 600.0
    if SH < 400.0: SH = 1100.0
    r_post = max(20.0, B * 0.42)
    r_post_in = max(10.0, r_post - T * 0.6)
    R_saddle = SPAN * 0.46
    sad_w = max(140.0, B * 2.5)
    # 1. 下部左右两根竖直圆管立柱（Y = ±SPAN/2，从 Z = -SH 延伸至顶部 Z = 0）与各自柱底方形 4 孔法兰板
    o1 = CYLINDER(s, R=0.1, H=0.1, O=0.0)
    base_w = max(180.0, r_post * 6.5)
    for sy in (-1.0, 1.0):
        yc = sy * (SPAN / 2.0)
        o_col = CYLINDER(s, R=r_post, H=SH, O=0.0).translate((0.0, yc, -SH))
        o_col_i = CYLINDER(s, R=r_post_in, H=SH + 4.0, O=0.0).translate((0.0, yc, -(SH + 2.0)))
        o_col.subtractFrom(o_col_i); o_col_i.erase()
        o_bp = BOX(s, L=base_w, W=T * 1.4, H=base_w).translate((0.0, yc, -(SH - T * 0.7)))
        o1.uniteWith(o_col); o_col.erase()
        o1.uniteWith(o_bp); o_bp.erase()
    # 2. 门式框架顶部横管（Z = -r_post）与中部横档圆管（Z = -SH * 0.38）
    for z_bar in (-r_post, -(SH * 0.38)):
        o_hbar = CYLINDER(s, R=r_post * 0.88, H=SPAN, O=0.0).rotateX(90.0).translate((0.0, SPAN / 2.0, z_bar))
        o1.uniteWith(o_hbar); o_hbar.erase()
    # 3. 顶部半圆弧形软管挂架鞍板（圆心在 Z = -(R_saddle + r_post*1.5)，上半圆弧托槽 + 3根防滑圆钢档杆）
    z_sc = -(R_saddle * 0.95)
    o_sad = CYLINDER(s, R=R_saddle, H=sad_w, O=0.0).rotateY(90.0).translate((-(sad_w / 2.0), -r_post * 1.2, z_sc))
    o_sad_i = CYLINDER(s, R=R_saddle - T, H=sad_w + 4.0, O=0.0).rotateY(90.0).translate((-(sad_w / 2.0 + 2.0), -r_post * 1.2, z_sc))
    o_sad.subtractFrom(o_sad_i); o_sad_i.erase()
    o_low_cut = BOX(s, L=R_saddle * 2.5, W=R_saddle * 1.5, H=sad_w + 10.0).translate((0.0, -r_post * 1.2, z_sc - R_saddle * 0.75))
    o_sad.subtractFrom(o_low_cut); o_low_cut.erase()
    o1.uniteWith(o_sad); o_sad.erase()
    for ang_r in (-50.0, 0.0, 50.0):
        rad_a = radians(ang_r)
        yr = -r_post * 1.2 + (R_saddle + T * 0.8) * sin(rad_a)
        zr = z_sc + (R_saddle + T * 0.8) * cos(rad_a)
        o_rod = CYLINDER(s, R=T * 0.75, H=sad_w + T * 4.0, O=0.0).rotateY(90.0).translate((-(sad_w / 2.0 + T * 2.0), yr, zr))
        o1.uniteWith(o_rod); o_rod.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
