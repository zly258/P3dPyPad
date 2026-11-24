# -*- coding: utf-8 -*-
# HG/T 21629-2021 H3 大管用可调支架（图 C.8-3）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="大管用可调支架", TooltipLong="HG/T 21629-2021 H3 大管用可调支架 图C.8-3", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_H3(s, D=711.0, SPAN=1764.2, SH=1458.7, B=250.0, T=12.0, ID=u"H3", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if D < 25.0: D = 50.0
    if B < 50.0: B = 100.0
    if T < 6.0: T = 10.0
    R1 = D / 2.0
    if SH < (R1 + 80.0): SH = R1 + (160.0 if False else 320.0)
    base_w = max(B * 1.8, D * 0.65)
    col_r = max(28.0, B * 0.55)
    # 1. 柱脚方形底板与十字加劲肋板
    o1 = BOX(s, L=base_w, W=T * 1.4, H=base_w).translate((0.0, 0.0, -(SH - T * 0.7)))
    low_h = (SH - R1) * (0.48 if False else 0.62)
    # 2. 下部立撑钢管（O=0.0 外圆减内圆）
    o_col = CYLINDER(s, R=col_r, H=low_h, O=0.0).translate((0.0, 0.0, -(SH - T * 1.4)))
    o_col_i = CYLINDER(s, R=max(10.0, col_r - T), H=low_h + 4.0, O=0.0).translate((0.0, 0.0, -(SH - T * 1.4 + 2.0)))
    o_col.subtractFrom(o_col_i); o_col_i.erase()
    o1.uniteWith(o_col); o_col.erase()
    for ang in (0.0, 90.0):
        o_rib = BOX(s, L=base_w * 0.82, W=low_h * 0.42, H=T).rotateZ(ang).translate((0.0, 0.0, -(SH - T * 1.4 - low_h * 0.21)))
        o1.uniteWith(o_rib); o_rib.erase()
    # 3. 中部大六角调节螺母盘与上部升降螺杆
    z_nut = -(SH - T * 1.4 - low_h)
    nut_w = col_r * 2.3
    nut_a = nut_w * 0.57735
    for ang_n in (0.0, 60.0, -60.0):
        o_hn = BOX(s, L=nut_w, W=T * 2.4, H=nut_a).rotateZ(ang_n).translate((0.0, 0.0, z_nut + T * 1.2))
        o1.uniteWith(o_hn); o_hn.erase()
    up_h = max(20.0, SH - R1 - T * 1.4 - low_h)
    o_scr = CYLINDER(s, R=col_r * 0.68, H=up_h + 15.0, O=0.0).translate((0.0, 0.0, z_nut))
    o_plat = CYLINDER(s, R=col_r * 1.25, H=T * 1.2, O=0.0).translate((0.0, 0.0, -(R1 + T * 2.2)))
    o1.uniteWith(o_scr); o_scr.erase()
    o1.uniteWith(o_plat); o_plat.erase()
    # 4. 顶部弧形管托鞍座（O=0.0）
    o_sad = CYLINDER(s, R=R1 + T, H=B * (1.6 if True else 1.1), O=0.0).rotateY(90.0).translate((-(B * (0.8 if True else 0.55)), 0.0, 0.0))
    o_sad_i = CYLINDER(s, R=R1, H=B * 2.0, O=0.0).rotateY(90.0).translate((-B, 0.0, 0.0))
    o_sad.subtractFrom(o_sad_i); o_sad_i.erase()
    o_top = BOX(s, L=(R1 + T) * 2.5, W=(R1 + T) * 1.5, H=B * 2.2).translate((0.0, 0.0, (R1 + T) * 0.75))
    o_sad.subtractFrom(o_top); o_top.erase()
    o1.uniteWith(o_sad); o_sad.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
