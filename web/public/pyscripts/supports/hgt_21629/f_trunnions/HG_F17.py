# -*- coding: utf-8 -*-
# HG/T 21629-2021 F17 立管用耳座（图 C.6-12）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="立管用耳座", TooltipLong="HG/T 21629-2021 F17 立管用耳座 图C.6-12", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_F17(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"F17", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 25.0: D = 114.3
    if LEG_D < 30.0: LEG_D = max(60.0, D * 0.55)
    if ST < 6.0: ST = 10.0
    R1 = D / 2.0
    if SH < (R1 + 60.0): SH = R1 + 140.0
    pipe_h = max(LEG_D * 2.6, D * 1.4)
    # 1. 竖直立管沿 Z 轴（O=0.0）与弧形补强圈
    o1 = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0)))
    o_in = CYLINDER(s, R=max(6.0, R1 - ST * 0.8), H=pipe_h + 4.0, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0 + 2.0)))
    o1.subtractFrom(o_in); o_in.erase()
    pad_h = LEG_D * 1.6
    o_pad = CYLINDER(s, R=R1 + ST, H=pad_h, O=0.0).translate((0.0, 0.0, -(pad_h / 2.0)))
    o_pad_i = CYLINDER(s, R=R1, H=pad_h + 4.0, O=0.0).translate((0.0, 0.0, -(pad_h / 2.0 + 2.0)))
    o_pad.subtractFrom(o_pad_i); o_pad_i.erase()
    o1.uniteWith(o_pad); o_pad.erase()
    # 2. 左右两侧（±Y 轴）对称焊接的三角形耳座立筋板 + 底部水平耳座承重板
    ear_w = max(55.0, SH - R1)
    rib_h = LEG_D * 1.35
    for sy in (-1.0, 1.0):
        yc = sy * (R1 + ST + ear_w / 2.0)
        o_rib = BOX(s, L=ear_w, W=rib_h, H=ST * 1.2).translate((0.0, yc, 0.0))
        ang_c = degrees(atan2(ear_w, rib_h))
        o_tcut = BOX(s, L=ear_w * 1.6, W=rib_h * 1.6, H=ST * 4.0).rotateX(sy * ang_c).translate((0.0, yc + sy * ear_w * 0.42, rib_h * 0.25))
        o_rib.subtractFrom(o_tcut); o_tcut.erase()
        o_seat = BOX(s, L=ear_w * 1.1, W=ST * 1.5, H=LEG_D * 1.1).translate((0.0, yc, -(rib_h / 2.0 + ST * 0.75)))
        o1.uniteWith(o_rib); o_rib.erase()
        o1.uniteWith(o_seat); o_seat.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
