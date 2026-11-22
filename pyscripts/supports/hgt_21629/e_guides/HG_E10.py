# -*- coding: utf-8 -*-
# HG/T 21629-2021 E10 保温/保冷立管的承重/导向架（1/2"~6")（图 C.5-10）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="保温/保冷立管的承重/导向架（1/2", TooltipLong="HG/T 21629-2021 E10 保温/保冷立管的承重/导向架（1/2~6) 图C.5-10", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至导向底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="导向长", TooltipLong="沿管道轴线导向座长度")
@param(SW=LENGTH, TooltipShort="导向宽", TooltipLong="导向底座总宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="导向翼板与底板厚度")
@param(GW=LENGTH, TooltipShort="导向间隙", TooltipLong="导向板与管托/管道单侧间隙")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_E10(s, D=114.3, SH=142.2, SL=177.2, SW=171.4, ST=8.0, GW=3.0, ID=u"E10", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); GW = float(GW)
    if D < 15.0: D = 60.3
    if ST < 4.0: ST = 6.0
    if GW < 1.0: GW = 3.0
    if SL < 80.0: SL = 160.0
    if SW < (D + 40.0): SW = D + 80.0
    R1 = D / 2.0
    if SH < (R1 + 80.0): SH = R1 + 160.0
    # 1. 竖直立管段（沿 Z 轴，O=0.0 外圆减内圆）与管壁上下两对承重挡耳
    pipe_h = SL * 1.6
    o_main = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0)))
    o_in = CYLINDER(s, R=max(5.0, R1 - ST * 0.8), H=pipe_h + 4.0, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0 + 2.0)))
    o_main.subtractFrom(o_in); o_in.erase()
    for z_lug in (SL * 0.35, -(SL * 0.35)):
        o_lug = BOX(s, L=SW * 0.85, W=ST * 2.5, H=ST * 1.6).translate((0.0, 0.0, z_lug))
        o_main.uniteWith(o_lug); o_lug.erase()
    # 2. 中央承重/导向水平槽钢托座（向 Y = -SH 延伸生根）与前部抱卡
    arm_l = SH + R1 + GW + ST
    o_arm = BOX(s, L=arm_l, W=SL * 0.45, H=SW * 0.95).translate((0.0, (-SH + R1 + GW + ST) * 0.5, 0.0))
    o_hole = CYLINDER(s, R=R1 + GW, H=SL, O=0.0).translate((0.0, 0.0, -(SL / 2.0)))
    o_arm.subtractFrom(o_hole); o_hole.erase()
    o_root = BOX(s, L=ST * 1.8, W=SL * 0.9, H=SW * 1.3).translate((0.0, -SH, 0.0))
    o_strap = BOX(s, L=ST * 1.5, W=SL * 0.35, H=SW * 1.1).translate((0.0, R1 + GW + ST, 0.0))
    for p in (o_arm, o_root, o_strap):
        o_main.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
