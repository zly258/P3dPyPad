# -*- coding: utf-8 -*-
# HG/T 21629-2021 G8 U形螺栓/管卡型管道支腿(1/2"~6")（图 C.7-8）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="U形螺栓/管卡型管道支腿(1/2~", TooltipLong="HG/T 21629-2021 G8 U形螺栓/管卡型管道支腿(1/2~6) 图C.7-8", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_G8(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"G8", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 15.0: D = 60.3
    if LEG_D < 35.0: LEG_D = 75.0
    if ST < 5.0: ST = 7.0
    R1 = D / 2.0
    if SH < (R1 + 80.0): SH = R1 + 180.0
    rod_r = max(4.5, ST * 0.7)
    R_ub = R1 + rod_r
    # 1. 顶部 U 形螺栓（半圆环 TORUS + 双竖腿 + 螺母）
    o1 = TORUS(s, R1=R_ub, R2=rod_r).rotateY(90.0)
    o_cut = BOX(s, L=(R_ub + rod_r) * 3.0, W=(R_ub + rod_r) * 2.2, H=rod_r * 6.0).translate((0.0, 0.0, -(R_ub + rod_r)))
    o1.subtractFrom(o_cut); o_cut.erase()
    z_seat = -(R1 + ST / 2.0)
    for sy in (-1.0, 1.0):
        o_ul = CYLINDER(s, R=rod_r, H=R1 + ST * 3.5, O=0.0).translate((0.0, sy * R_ub, -(R1 + ST * 3.5)))
        o_un = CYLINDER(s, R=rod_r * 1.75, H=rod_r * 1.5, O=0.0).translate((0.0, sy * R_ub, -(R1 + ST * 3.2)))
        o1.uniteWith(o_ul); o_ul.erase()
        o1.uniteWith(o_un); o_un.erase()
    # 2. 顶部水平角钢短横托座 + 下部单根竖直角钢/槽钢支腿 + 底部底板
    seat_w = D + LEG_D * 0.9
    o_s1 = BOX(s, L=seat_w, W=ST, H=LEG_D).translate((0.0, 0.0, z_seat))
    o_s2 = BOX(s, L=seat_w, W=LEG_D * 0.65, H=ST).translate((-(LEG_D / 2.0 - ST / 2.0), 0.0, z_seat - LEG_D * 0.325))
    post_h = max(40.0, SH - R1 - ST)
    o_p1 = BOX(s, L=LEG_D, W=post_h, H=ST).translate((0.0, 0.0, -(R1 + ST + post_h / 2.0)))
    o_p2 = BOX(s, L=ST, W=post_h, H=LEG_D).translate((LEG_D / 2.0 - ST / 2.0, -(LEG_D / 2.0 - ST / 2.0), -(R1 + ST + post_h / 2.0)))
    o_base = BOX(s, L=LEG_D * 2.4, W=ST * 1.5, H=LEG_D * 2.2).translate((0.0, 0.0, -(SH - ST * 0.75)))
    for p in (o_s1, o_s2, o_p1, o_p2, o_base):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
