# -*- coding: utf-8 -*-
# HG/T 21629-2021 F1 耳轴的补强板（图 C.6-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="耳轴的补强板", TooltipLong="HG/T 21629-2021 F1 耳轴的补强板 图C.6-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_F1(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"F1", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 25.0: D = 114.3
    if LEG_D < 20.0: LEG_D = max(33.7, D * 0.5)
    if ST < 4.0: ST = 8.0
    R1 = D / 2.0
    R_pad_outer = max(LEG_D * 0.92, R1 * 0.72)
    R_hole = LEG_D * 0.5
    pad_len = R_pad_outer * 2.2
    # 1. 母管外表面圆筒壳（外径 R1+ST，内径 R1，O=0.0 显式差集）
    o1 = CYLINDER(s, R=R1 + ST, H=pad_len, O=0.0).rotateY(90.0).translate((-(pad_len / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=pad_len + 4.0, O=0.0).rotateY(90.0).translate((-(pad_len / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    # 2. 与沿 -Z 轴的补强板外轮廓圆柱求交，形成贴合母管下半周的马鞍形弧面补强圈
    o_bound = CYLINDER(s, R=R_pad_outer, H=R1 + ST * 3.0, O=0.0).translate((0.0, 0.0, -(R1 + ST * 2.0)))
    o1.intersectWith(o_bound); o_bound.erase()
    # 3. 切除中心耳轴过孔（R = LEG_D / 2.0）
    o_hole = CYLINDER(s, R=R_hole, H=R1 + ST * 4.0, O=0.0).translate((0.0, 0.0, -(R1 + ST * 2.5)))
    o1.subtractFrom(o_hole); o_hole.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
