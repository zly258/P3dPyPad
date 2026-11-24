# -*- coding: utf-8 -*-
# HG/T 21629-2021 G12 混凝土上生根的三角架（图 C.7-12）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="混凝土上生根的三角架", TooltipLong="HG/T 21629-2021 G12 混凝土上生根的三角架 图C.7-12", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_G12(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"G12", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 40.0: B = 75.0
    if T < 5.0: T = 8.0
    if SPAN < 150.0: SPAN = 400.0
    if SH < 150.0: SH = 350.0
    R1 = D / 2.0; z_top = -(R1 + B / 2.0)
    o1 = BOX(s, L=SPAN, W=B, H=T * 1.5).translate((0.0, -(SPAN / 2.0), z_top))
    o_post = BOX(s, L=T * 1.5, W=SH, H=B).translate((0.0, -SPAN + T * 1.2, z_top - SH / 2.0 + B / 2.0))
    diag_l = sqrt(SPAN * SPAN + SH * SH)
    ang = degrees(atan2(SH - B, SPAN))
    o_diag = BOX(s, L=diag_l * 0.92, W=B * 0.85, H=T * 1.4).rotateX(-ang).translate((0.0, -(SPAN * 0.52), z_top - SH * 0.46))
    # 混凝土锚板与 4 套膨胀螺栓
    o_anc = BOX(s, L=T * 1.8, W=SH + B * 0.8, H=B * 2.4).translate((0.0, -SPAN, z_top - SH / 2.0 + B / 2.0))
    for p in (o_post, o_diag, o_anc):
        o1.uniteWith(p); p.erase()
    for sx in (-1.0, 1.0):
        for sz in (z_top - B * 0.2, z_top - SH + B * 1.2):
            o_b = CYLINDER(s, R=T * 0.8, H=B * 1.2, O=0.0).rotateX(90.0).translate((sx * B * 0.75, -SPAN + T * 2.5, sz))
            o1.uniteWith(o_b); o_b.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
