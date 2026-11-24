# -*- coding: utf-8 -*-
# HG/T 21629-2021 N5 设备上生根的T形架（图 C.13-5）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="设备上生根的T形架", TooltipLong="HG/T 21629-2021 N5 设备上生根的T形架 图C.13-5", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_N5(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"N5", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 40.0: B = 90.0
    if T < 5.0: T = 8.0
    if SPAN < 160.0: SPAN = 400.0
    if SH < 150.0: SH = 360.0
    R1 = D / 2.0; z_beam = -(R1 + B / 2.0); col_h = max(90.0, SH - R1 - B)
    o1 = BOX(s, L=SPAN, W=B, H=B * 0.85).translate((0.0, 0.0, z_beam))
    o_col = BOX(s, L=B, W=col_h, H=B * 0.85).translate((0.0, 0.0, z_beam - B / 2.0 - col_h / 2.0))
    o1.uniteWith(o_col); o_col.erase()
    # 柱根部连接耳座与贴合设备外壁的圆弧预焊垫板（O=0.0）
    eq_r = max(350.0, SPAN * 1.1)
    z_root = -(SH - B * 0.8)
    o_br = BOX(s, L=B * 1.6, W=B * 1.4, H=B * 1.8).translate((0.0, 0.0, z_root))
    o_pad = CYLINDER(s, R=eq_r + T * 1.6, H=B * 2.4, O=0.0).rotateY(90.0).translate((-(B * 1.2), 0.0, -(SH + eq_r)))
    o_pad_i = CYLINDER(s, R=eq_r, H=B * 2.4 + 4.0, O=0.0).rotateY(90.0).translate((-(B * 1.2 + 2.0), 0.0, -(SH + eq_r)))
    o_pad.subtractFrom(o_pad_i); o_pad_i.erase()
    o_pb = BOX(s, L=B * 2.6, W=B * 1.8, H=B * 2.4).translate((0.0, 0.0, -(SH)))
    o_pad.intersectWith(o_pb); o_pb.erase()
    o1.uniteWith(o_br); o_br.erase()
    o1.uniteWith(o_pad); o_pad.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
