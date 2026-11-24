# -*- coding: utf-8 -*-
# HG/T 21629-2021 E6 竖管耳轴的导向/限位架（图 C.5-6）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="竖管耳轴的导向/限位架", TooltipLong="HG/T 21629-2021 E6 竖管耳轴的导向/限位架 图C.5-6", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至导向底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="导向长", TooltipLong="沿管道轴线导向座长度")
@param(SW=LENGTH, TooltipShort="导向宽", TooltipLong="导向底座总宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="导向翼板与底板厚度")
@param(GW=LENGTH, TooltipShort="导向间隙", TooltipLong="导向板与管托/管道单侧间隙")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_E6(s, D=114.3, SH=142.2, SL=177.2, SW=171.4, ST=8.0, GW=3.0, ID=u"E6", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); GW = float(GW)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 6.0
    if GW < 1.0: GW = 3.0
    if SL < 40.0: SL = max(80.0, D * 0.8)
    if SW < (D + 30.0): SW = D + 60.0
    R1 = D / 2.0
    if SH < (R1 + ST * 2.0 + 15.0): SH = R1 + max(60.0, D * 0.45)
    # 1. 耳轴圆管支腿（O=0.0 外圆减内圆）与母管鞍座垫板
    leg_r = max(16.0, R1 * 0.42)
    leg_in = max(8.0, leg_r - ST)
    o_main = CYLINDER(s, R=R1 + ST, H=SL * 0.85, O=0.0).rotateY(90.0).translate((-(SL * 0.425), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL * 0.85 + 4.0, O=0.0).rotateY(90.0).translate((-(SL * 0.425 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    o_top = BOX(s, L=(R1 + ST) * 2.5, W=(R1 + ST) * 1.5, H=SL).translate((0.0, 0.0, (R1 + ST) * 0.75))
    o_main.subtractFrom(o_top); o_top.erase()
    # E6/E7 竖直耳轴支腿 + 底部耳轴滑板 + 两侧压扣型导向滑槽导轨
    leg_h = SH - R1 - ST
    if leg_h < 25.0: leg_h = 25.0
    o_leg = CYLINDER(s, R=leg_r, H=leg_h, O=0.0).translate((0.0, 0.0, -(SH - ST)))
    o_leg_i = CYLINDER(s, R=leg_in, H=leg_h + 4.0, O=0.0).translate((0.0, 0.0, -(SH - ST + 2.0)))
    o_leg.subtractFrom(o_leg_i); o_leg_i.erase()
    o_tbase = BOX(s, L=SW * 0.8, W=ST, H=SL * 0.75).translate((0.0, 0.0, -(SH - ST / 2.0)))
    o_main.uniteWith(o_leg); o_leg.erase()
    o_main.uniteWith(o_tbase); o_tbase.erase()
    rail_h = ST * 3.2
    for sy in (-1.0, 1.0):
        gy = SW * 0.4 + GW + ST / 2.0
        o_r1 = BOX(s, L=ST * 1.4, W=rail_h, H=SL).translate((0.0, sy * gy, -(SH - rail_h / 2.0)))
        o_r2 = BOX(s, L=ST * 3.0, W=ST, H=SL).translate((0.0, sy * (SW * 0.4 - ST * 0.6), -(SH - rail_h + ST / 2.0)))
        o_main.uniteWith(o_r1); o_r1.erase()
        o_main.uniteWith(o_r2); o_r2.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
