# -*- coding: utf-8 -*-
# HG/T 21629-2021 F3 水平管的竖直耳轴（图 C.6-3）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="水平管的竖直耳轴", TooltipLong="HG/T 21629-2021 F3 水平管的竖直耳轴 图C.6-3", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_F3(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"F3", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 25.0: D = 114.3
    if LEG_D < 20.0: LEG_D = max(33.7, D * 0.55)
    if ST < 4.0: ST = 8.0
    R1 = D / 2.0
    if SH < (R1 + 80.0): SH = R1 + 180.0
    R_leg = LEG_D / 2.0; R_leg_in = max(5.0, R_leg - ST)
    pipe_l = max(LEG_D * 2.6, D * 1.5)
    # 1. 上部水平母管段（沿 X 轴空心圆管，O=0.0）
    o1 = CYLINDER(s, R=R1, H=pipe_l, O=0.0).rotateY(90.0).translate((-(pipe_l / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=max(5.0, R1 - ST * 0.8), H=pipe_l + 4.0, O=0.0).rotateY(90.0).translate((-(pipe_l / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    # 2. 管底弧形补强板（O=0.0）与下部竖直圆管耳轴支腿
    pad_w = LEG_D * 1.5
    o_pad = CYLINDER(s, R=R1 + ST, H=pad_w, O=0.0).rotateY(90.0).translate((-(pad_w / 2.0), 0.0, 0.0))
    o_pad_i = CYLINDER(s, R=R1, H=pad_w + 4.0, O=0.0).rotateY(90.0).translate((-(pad_w / 2.0 + 2.0), 0.0, 0.0))
    o_pad.subtractFrom(o_pad_i); o_pad_i.erase()
    o_top = BOX(s, L=(R1 + ST) * 2.5, W=(R1 + ST) * 1.5, H=pad_w + 8.0).translate((0.0, 0.0, (R1 + ST) * 0.75))
    o_pad.subtractFrom(o_top); o_top.erase()
    leg_h = max(30.0, SH - R1 * 0.85 - ST)
    o_leg = CYLINDER(s, R=R_leg, H=leg_h, O=0.0).translate((0.0, 0.0, -(SH - ST)))
    o_leg_i = CYLINDER(s, R=R_leg_in, H=leg_h + 4.0, O=0.0).translate((0.0, 0.0, -(SH - ST + 2.0)))
    o_leg.subtractFrom(o_leg_i); o_leg_i.erase()
    o_base = BOX(s, L=LEG_D * 2.2, W=ST * 1.4, H=LEG_D * 2.0).translate((0.0, 0.0, -(SH - ST * 0.7)))
    for p in (o_pad, o_leg, o_base):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
