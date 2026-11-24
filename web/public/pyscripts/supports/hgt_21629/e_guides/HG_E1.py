# -*- coding: utf-8 -*-
# HG/T 21629-2021 E1 不保温管的导向架（1/2"~36")（图 C.5-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="不保温管的导向架（1/2~36)", TooltipLong="HG/T 21629-2021 E1 不保温管的导向架（1/2~36) 图C.5-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至导向底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="导向长", TooltipLong="沿管道轴线导向座长度")
@param(SW=LENGTH, TooltipShort="导向宽", TooltipLong="导向底座总宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="导向翼板与底板厚度")
@param(GW=LENGTH, TooltipShort="导向间隙", TooltipLong="导向板与管托/管道单侧间隙")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_E1(s, D=114.3, SH=142.2, SL=177.2, SW=171.4, ST=8.0, GW=3.0, ID=u"E1", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); GW = float(GW)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 6.0
    if GW < 1.0: GW = 3.0
    if SL < 40.0: SL = max(80.0, D * 0.8)
    if SW < (D + 30.0): SW = D + 60.0
    R1 = D / 2.0
    if SH < (R1 + ST * 2.0 + 15.0): SH = R1 + max(60.0, D * 0.45)
    # 1. 底部导向生根底板
    o_main = BOX(s, L=SW * 1.25, W=ST, H=SL).translate((0.0, 0.0, -(SH - ST / 2.0)))
    # 2. 双侧直立L形导向翼板（夹住裸管两侧 Y = ±(R1 + GW)）
    gh = SH + R1 * 0.65 - ST
    for sy in (-1.0, 1.0):
        gy = R1 + GW + ST / 2.0
        o_gw = BOX(s, L=ST, W=gh, H=SL * 0.75).translate((0.0, sy * gy, -(SH - ST - gh / 2.0)))
        o_gus = BOX(s, L=ST * 3.5, W=gh * 0.55, H=ST).translate((0.0, sy * (gy + ST * 1.75), -(SH - ST - gh * 0.275)))
        o_main.uniteWith(o_gw); o_gw.erase()
        o_main.uniteWith(o_gus); o_gus.erase()
    # 3. 管底承重弧形滑板（O=0.0）
    o_arc = CYLINDER(s, R=R1 + ST, H=SL * 0.8, O=0.0).rotateY(90.0).translate((-(SL * 0.4), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL * 0.8 + 4.0, O=0.0).rotateY(90.0).translate((-(SL * 0.4 + 2.0), 0.0, 0.0))
    o_arc.subtractFrom(o_in); o_in.erase()
    o_top = BOX(s, L=(R1 + ST) * 2.5, W=(R1 + ST) * 1.6, H=SL).translate((0.0, 0.0, (R1 + ST) * 0.8))
    o_arc.subtractFrom(o_top); o_top.erase()
    o_web = BOX(s, L=ST, W=SH - R1, H=SL * 0.8).translate((0.0, 0.0, -(R1 + (SH - R1) / 2.0)))
    o_main.uniteWith(o_arc); o_arc.erase()
    o_main.uniteWith(o_web); o_web.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
