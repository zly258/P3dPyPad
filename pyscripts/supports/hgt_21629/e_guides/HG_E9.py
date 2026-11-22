# -*- coding: utf-8 -*-
# HG/T 21629-2021 E9 不保温管的管夹型导向架（6"~24")（图 C.5-9）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="不保温管的管夹型导向架（6~24", TooltipLong="HG/T 21629-2021 E9 不保温管的管夹型导向架（6~24) 图C.5-9", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至导向底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="导向长", TooltipLong="沿管道轴线导向座长度")
@param(SW=LENGTH, TooltipShort="导向宽", TooltipLong="导向底座总宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="导向翼板与底板厚度")
@param(GW=LENGTH, TooltipShort="导向间隙", TooltipLong="导向板与管托/管道单侧间隙")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_E9(s, D=406.4, SH=338.2, SL=425.4, SW=507.4, ST=10.0, GW=5.0, ID=u"E9", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); GW = float(GW)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 6.0
    if GW < 1.0: GW = 3.0
    if SL < 40.0: SL = max(80.0, D * 0.8)
    if SW < (D + 30.0): SW = D + 60.0
    R1 = D / 2.0
    if SH < (R1 + ST * 2.0 + 15.0): SH = R1 + max(60.0, D * 0.45)
    # 1. 管夹主体（O=0.0 外圆减内圆）
    o_main = CYLINDER(s, R=R1 + ST, H=SL * 0.75, O=0.0).rotateY(90.0).translate((-(SL * 0.375), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL * 0.75 + 4.0, O=0.0).rotateY(90.0).translate((-(SL * 0.375 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    # 2. 四向十字导向翼板与定距螺栓耳
    wing_h = max(45.0, SH - R1)
    for ang in (0.0, 90.0, 180.0, 270.0):
        o_w = BOX(s, L=ST * 1.5, W=wing_h, H=SL * 0.75).translate((0.0, 0.0, R1 + wing_h / 2.0)).rotateX(ang)
        o_main.uniteWith(o_w); o_w.erase()
    # 3. 下部双侧导向支座底板与导向挡块
    o_base = BOX(s, L=SW, W=ST * 1.3, H=SL).translate((0.0, 0.0, -(SH - ST * 0.65)))
    for sy in (-1.0, 1.0):
        o_g = BOX(s, L=ST * 1.4, W=wing_h * 0.85, H=SL * 0.85).translate((0.0, sy * (ST * 1.5 + GW + ST * 0.7), -(SH - wing_h * 0.425)))
        o_base.uniteWith(o_g); o_g.erase()
    o_main.uniteWith(o_base); o_base.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
