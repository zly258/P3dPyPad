# -*- coding: utf-8 -*-
# HG/T 21629-2021 N3 设备上生根的单三角架（图 C.13-3）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="设备上生根的单三角架", TooltipLong="HG/T 21629-2021 N3 设备上生根的单三角架 图C.13-3", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_N3(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"N3", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 40.0: B = 75.0
    if T < 5.0: T = 8.0
    if SPAN < 150.0: SPAN = 400.0
    if SH < 150.0: SH = 350.0
    R1 = D / 2.0; z_top = -(R1 + B / 2.0)
    o1 = BOX(s, L=SPAN, W=B, H=T * 1.5).translate((0.0, -(SPAN / 2.0), z_top))
    o_post = BOX(s, L=T * 1.5, W=SH, H=B).translate((0.0, -SPAN + B * 0.5, z_top - SH / 2.0 + B / 2.0))
    diag_l = sqrt(SPAN * SPAN + SH * SH)
    ang = degrees(atan2(SH - B, SPAN))
    o_diag = BOX(s, L=diag_l * 0.9, W=B * 0.85, H=T * 1.4).rotateX(-ang).translate((0.0, -(SPAN * 0.5), z_top - SH * 0.45))
    o1.uniteWith(o_post); o_post.erase()
    o1.uniteWith(o_diag); o_diag.erase()
    # 设备筒体侧上下两处弧形预焊垫板与连接耳板
    eq_r = max(350.0, SPAN * 1.1)
    for zp in (z_top, z_top - SH + B):
        o_lug = BOX(s, L=B * 0.9, W=B * 1.4, H=B * 1.4).translate((0.0, -(SPAN - B * 0.2), zp))
        o_pad = CYLINDER(s, R=eq_r + T * 1.5, H=B * 2.0, O=0.0).translate((0.0, -(SPAN + eq_r), zp - B))
        o_pad_i = CYLINDER(s, R=eq_r, H=B * 2.0 + 4.0, O=0.0).translate((0.0, -(SPAN + eq_r), zp - B - 2.0))
        o_pad.subtractFrom(o_pad_i); o_pad_i.erase()
        o_pb = BOX(s, L=B * 1.5, W=B * 2.0, H=B * 2.2).translate((0.0, -SPAN, zp))
        o_pad.intersectWith(o_pb); o_pb.erase()
        o1.uniteWith(o_lug); o_lug.erase()
        o1.uniteWith(o_pad); o_pad.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
