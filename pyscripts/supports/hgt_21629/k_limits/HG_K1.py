# -*- coding: utf-8 -*-
# HG/T 21629-2021 K1 不保温管的限位架（1/2"~36"）（图 C.10-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="不保温管的限位架（1/2~36）", TooltipLong="HG/T 21629-2021 K1 不保温管的限位架（1/2~36） 图C.10-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至限位架底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="限位长", TooltipLong="沿管轴线限位座总长")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="限位座底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="止推挡板与腹板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_K1(s, D=114.3, SH=157.2, SL=188.6, SW=114.3, ST=8.0, ID=u"K1", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 6.0
    if SL < 60.0: SL = max(100.0, D * 0.9)
    if SW < 50.0: SW = max(80.0, D * 0.7)
    R1 = D / 2.0
    if SH < (R1 + ST * 2.0 + 20.0): SH = R1 + max(70.0, D * 0.5)
    # 1. 管底弧形补强垫板（O=0.0）
    o_main = CYLINDER(s, R=R1 + ST, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    o_top = BOX(s, L=(R1 + ST) * 2.5, W=(R1 + ST) * 1.4, H=SL + 10.0).translate((0.0, 0.0, (R1 + ST) * 0.7))
    o_main.subtractFrom(o_top); o_top.erase()
    # 2. 前后成对轴向止推限位挡块（卡在下部钢梁两侧 X = ±SL*0.28）
    stop_h = SH - R1
    for sx in (-1.0, 1.0):
        o_stop = BOX(s, L=SW * 0.75, W=stop_h, H=ST * 1.8).translate((sx * (SL * 0.26), 0.0, -(R1 + stop_h / 2.0)))
        o_gus = BOX(s, L=ST * 1.4, W=stop_h * 0.85, H=SL * 0.22).translate((sx * (SL * 0.38), 0.0, -(R1 + stop_h * 0.42)))
        o_main.uniteWith(o_stop); o_stop.erase()
        o_main.uniteWith(o_gus); o_gus.erase()
    # 3. 中央生根H型钢横梁座（被前后止推块夹持）
    o_beam = BOX(s, L=SW * 1.2, W=ST * 1.5, H=SL * 0.42).translate((0.0, 0.0, -(SH - ST * 0.75)))
    o_main.uniteWith(o_beam); o_beam.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
