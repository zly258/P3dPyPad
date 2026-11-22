# -*- coding: utf-8 -*-
# HG/T 21629-2021 D17 并排双三角架（图 C.4-17）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="并排双三角架", TooltipLong="HG/T 21629-2021 D17 并排双三角架 图C.4-17", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_D17(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"D17", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 40.0: B = 75.0
    if T < 5.0: T = 8.0
    if SPAN < 150.0: SPAN = 400.0
    if SH < 150.0: SH = 350.0
    R1 = D / 2.0; z_top = -(R1 + B / 2.0)
    o1 = CYLINDER(s, R=0.1, H=0.1, O=0.0)
    sep_x = max(B * 2.2, SPAN * 0.45)
    for sx in (-1.0, 1.0):
        xo = sx * (sep_x / 2.0)
        o_arm = BOX(s, L=SPAN, W=B, H=T * 1.5).translate((xo, -(SPAN / 2.0), z_top))
        o_post = BOX(s, L=T * 1.5, W=SH, H=B).translate((xo, -SPAN, z_top - SH / 2.0 + B / 2.0))
        diag_l = sqrt(SPAN * SPAN + SH * SH)
        ang = degrees(atan2(SH - B, SPAN))
        o_diag = BOX(s, L=diag_l * 0.92, W=B * 0.85, H=T * 1.4).rotateX(-ang).translate((xo, -(SPAN * 0.52), z_top - SH * 0.46))
        for p in (o_arm, o_post, o_diag):
            o1.uniteWith(p); p.erase()
    # 并排两榀三角架之间的横向联系梁与根部横连板
    o_tie1 = BOX(s, L=B, W=T * 1.5, H=sep_x + B).translate((0.0, -(SPAN * 0.25), z_top + B / 2.0))
    o_tie2 = BOX(s, L=T * 1.6, W=B * 1.5, H=sep_x + B * 1.4).translate((0.0, -SPAN, z_top))
    o_tie3 = BOX(s, L=T * 1.6, W=B * 1.5, H=sep_x + B * 1.4).translate((0.0, -SPAN, z_top - SH + B))
    for p in (o_tie1, o_tie2, o_tie3):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
