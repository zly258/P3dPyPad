# -*- coding: utf-8 -*-
# HG/T 21629-2021 L14 耳轴管的保冷块（1/2"~72"）（图 C.11-14）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="耳轴管的保冷块（1/2~72）", TooltipLong="HG/T 21629-2021 L14 耳轴管的保冷块（1/2~72） 图C.11-14", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_L14(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"L14", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 25.0: D = 114.3
    if LEG_D < 20.0: LEG_D = max(48.3, D * 0.55)
    if ST < 4.0: ST = 8.0
    R1 = D / 2.0; R_leg = LEG_D / 2.0; R_leg_in = max(5.0, R_leg - ST)
    if SH < (R1 + 80.0): SH = R1 + 180.0
    pipe_l = max(160.0, D * 1.5)
    # 1. 上部水平母管段（沿 X 轴，O=0.0）
    o1 = CYLINDER(s, R=R1, H=pipe_l, O=0.0).rotateY(90.0).translate((-(pipe_l / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=max(6.0, R1 - ST), H=pipe_l + 4.0, O=0.0).rotateY(90.0).translate((-(pipe_l / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    # 2. 下部竖直圆管耳轴支腿 + 下半部包覆的大直径圆柱保冷块与底部加劲钢靴底板
    leg_h = max(40.0, SH - R1 * 0.85)
    o_leg = CYLINDER(s, R=R_leg, H=leg_h, O=0.0).translate((0.0, 0.0, -SH))
    o_leg_i = CYLINDER(s, R=R_leg_in, H=leg_h + 4.0, O=0.0).translate((0.0, 0.0, -(SH + 2.0)))
    o_leg.subtractFrom(o_leg_i); o_leg_i.erase()
    blk_h = leg_h * 0.55
    o_cblk = CYLINDER(s, R=R_leg * 1.95, H=blk_h, O=0.0).translate((0.0, 0.0, -(SH - ST)))
    o_boot = BOX(s, L=LEG_D * 2.5, W=ST * 3.5, H=LEG_D * 2.5).translate((0.0, 0.0, -(SH - ST * 1.75)))
    for p in (o_leg, o_cblk, o_boot):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
