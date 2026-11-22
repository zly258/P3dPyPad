# -*- coding: utf-8 -*-
# HG/T 21629-2021 F6~F7 立管的耳轴（图 C.6-6）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="立管的耳轴", TooltipLong="HG/T 21629-2021 F6~F7 立管的耳轴 图C.6-6", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_F6(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"F6", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 25.0: D = 114.3
    if LEG_D < 20.0: LEG_D = max(33.7, D * 0.5)
    if ST < 4.0: ST = 8.0
    R1 = D / 2.0
    if SH < (R1 + 60.0): SH = R1 + 150.0
    R_leg = LEG_D / 2.0; R_leg_in = max(5.0, R_leg - ST)
    pipe_h = max(LEG_D * 2.6, D * 1.4)
    # 1. 竖直立管沿 Z 轴（O=0.0 空心圆管）与环向补强板圈
    o1 = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0)))
    o_in = CYLINDER(s, R=max(5.0, R1 - ST * 0.8), H=pipe_h + 4.0, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0 + 2.0)))
    o1.subtractFrom(o_in); o_in.erase()
    pad_h = LEG_D * 1.5
    o_pad = CYLINDER(s, R=R1 + ST, H=pad_h, O=0.0).translate((0.0, 0.0, -(pad_h / 2.0)))
    o_pad_i = CYLINDER(s, R=R1, H=pad_h + 4.0, O=0.0).translate((0.0, 0.0, -(pad_h / 2.0 + 2.0)))
    o_pad.subtractFrom(o_pad_i); o_pad_i.erase()
    o1.uniteWith(o_pad); o_pad.erase()
    # 2. 左右两侧（±Y 轴）对称水平伸出的空心圆管耳轴
    tr_l = max(45.0, SH - R1 * 0.8)
    for sy in (-1.0, 1.0):
        o_tr = CYLINDER(s, R=R_leg, H=tr_l, O=0.0).rotateX(-90.0 * sy).translate((0.0, sy * R1 * 0.8, 0.0))
        o_tri = CYLINDER(s, R=R_leg_in, H=tr_l + 4.0, O=0.0).rotateX(-90.0 * sy).translate((0.0, sy * (R1 * 0.8 - 2.0), 0.0))
        o_tr.subtractFrom(o_tri); o_tr_i = o_tri; o_tr_i.erase()
        o1.uniteWith(o_tr); o_tr.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
