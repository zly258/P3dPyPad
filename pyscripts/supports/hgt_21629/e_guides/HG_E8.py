# -*- coding: utf-8 -*-
# HG/T 21629-2021 E8 水平双耳轴的导向架（图 C.5-8）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="水平双耳轴的导向架", TooltipLong="HG/T 21629-2021 E8 水平双耳轴的导向架 图C.5-8", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至导向底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="导向长", TooltipLong="沿管道轴线导向座长度")
@param(SW=LENGTH, TooltipShort="导向宽", TooltipLong="导向底座总宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="导向翼板与底板厚度")
@param(GW=LENGTH, TooltipShort="导向间隙", TooltipLong="导向板与管托/管道单侧间隙")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_E8(s, D=114.3, SH=142.2, SL=177.2, SW=171.4, ST=8.0, GW=3.0, ID=u"E8", **kw):
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
    # E8 水平双耳轴 + 两侧导向支座
    for sy in (-1.0, 1.0):
        o_tr = CYLINDER(s, R=leg_r, H=SW * 0.45, O=0.0).rotateX(-90.0 * sy).translate((0.0, sy * R1 * 0.8, 0.0))
        o_tr_i = CYLINDER(s, R=leg_in, H=SW * 0.45 + 4.0, O=0.0).rotateX(-90.0 * sy).translate((0.0, sy * (R1 * 0.8 - 2.0), 0.0))
        o_tr.subtractFrom(o_tr_i); o_tr_i.erase()
        o_main.uniteWith(o_tr); o_tr.erase()
        yc = sy * (R1 + SW * 0.28)
        o_ped = BOX(s, L=ST * 3.5, W=SH, H=SL * 0.7).translate((0.0, yc, -(SH / 2.0)))
        o_slot = BOX(s, L=ST * 4.0, W=leg_r * 2.2, H=leg_r * 2.4).translate((0.0, yc, 0.0))
        o_ped.subtractFrom(o_slot); o_slot.erase()
        o_main.uniteWith(o_ped); o_ped.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
