# -*- coding: utf-8 -*-
# HG/T 21629-2021 N6 设备上生根的等高门形架（图 C.13-6）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="设备上生根的等高门形架", TooltipLong="HG/T 21629-2021 N6 设备上生根的等高门形架 图C.13-6", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_N6(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"N6", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if D < 15.0: D = 60.3
    if B < 40.0: B = 100.0
    if T < 5.0: T = 8.0
    if SPAN < (D + 100.0): SPAN = max(400.0, D * 2.5)
    if SH < (D / 2.0 + B + 80.0): SH = D / 2.0 + B + 260.0
    R1 = D / 2.0; z_beam = -(R1 + B / 2.0); col_h = max(80.0, SH - R1 - B)
    o1 = BOX(s, L=SPAN + B, W=B, H=B * 0.85).translate((0.0, 0.0, z_beam))
    for sy in (-1.0, 1.0):
        yc = sy * (SPAN / 2.0)
        o_c = BOX(s, L=B, W=col_h, H=B * 0.85).translate((0.0, yc, z_beam - B / 2.0 - col_h / 2.0))
        o_lug = BOX(s, L=B * 1.5, W=B * 0.8, H=B * 1.5).translate((0.0, yc, -(SH - B * 0.4)))
        o1.uniteWith(o_c); o_c.erase()
        o1.uniteWith(o_lug); o_lug.erase()
    # 下部贴合设备圆筒/封头的弧形预焊垫板（O=0.0）
    eq_r = max(SPAN * 0.95, 380.0)
    o_eq = CYLINDER(s, R=eq_r + T * 1.6, H=B * 2.2, O=0.0).rotateY(90.0).translate((-(B * 1.1), 0.0, -(SH + eq_r * 0.88)))
    o_eq_i = CYLINDER(s, R=eq_r, H=B * 2.2 + 4.0, O=0.0).rotateY(90.0).translate((-(B * 1.1 + 2.0), 0.0, -(SH + eq_r * 0.88)))
    o_eq.subtractFrom(o_eq_i); o_eq_i.erase()
    o_eb = BOX(s, L=SPAN + B * 2.4, W=B * 2.2, H=B * 2.2).translate((0.0, 0.0, -(SH + B * 0.3)))
    o_eq.intersectWith(o_eb); o_eb.erase()
    o1.uniteWith(o_eq); o_eq.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
