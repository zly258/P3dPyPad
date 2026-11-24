# -*- coding: utf-8 -*-
# HG/T 21629-2021 G4 地面上生根的T形架（图 C.7-4）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="地面上生根的T形架", TooltipLong="HG/T 21629-2021 G4 地面上生根的T形架 图C.7-4", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_G4(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"G4", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 40.0: B = 100.0
    if T < 6.0: T = 8.0
    if SPAN < 160.0: SPAN = 400.0
    if SH < 150.0: SH = 380.0
    R1 = D / 2.0; z_beam = -(R1 + B / 2.0); col_h = max(90.0, SH - R1 - B)
    o1 = BOX(s, L=SPAN, W=B, H=T).translate((0.0, 0.0, z_beam))
    o_tf1 = BOX(s, L=SPAN, W=T, H=B).translate((0.0, 0.0, z_beam + B / 2.0 - T / 2.0))
    o_tf2 = BOX(s, L=SPAN, W=T, H=B).translate((0.0, 0.0, z_beam - B / 2.0 + T / 2.0))
    o_col = BOX(s, L=B, W=col_h, H=B).translate((0.0, 0.0, z_beam - B / 2.0 - col_h / 2.0))
    base_w = B * 2.4
    o_base = BOX(s, L=base_w, W=T * 1.8, H=base_w).translate((0.0, 0.0, -(SH - T * 0.9)))
    for p in (o_tf1, o_tf2, o_col, o_base):
        o1.uniteWith(p); p.erase()
    for ang in (0.0, 90.0):
        o_stif = BOX(s, L=base_w * 0.85, W=B * 1.2, H=T).rotateZ(ang).translate((0.0, 0.0, -(SH - T * 1.8 - B * 0.6)))
        o1.uniteWith(o_stif); o_stif.erase()
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            o_ab = CYLINDER(s, R=T * 0.8, H=T * 5.0, O=0.0).translate((sx * base_w * 0.36, sy * base_w * 0.36, -(SH + T * 1.5)))
            o1.uniteWith(o_ab); o_ab.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
