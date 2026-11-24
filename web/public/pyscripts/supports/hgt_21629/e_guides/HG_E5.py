# -*- coding: utf-8 -*-
# HG/T 21629-2021 E5 弹簧支架或可调支架的导向/限位架（图 C.5-5）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="弹簧支架或可调支架的导向/限位架", TooltipLong="HG/T 21629-2021 E5 弹簧支架或可调支架的导向/限位架 图C.5-5", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至导向底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="导向长", TooltipLong="沿管道轴线导向座长度")
@param(SW=LENGTH, TooltipShort="导向宽", TooltipLong="导向底座总宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="导向翼板与底板厚度")
@param(GW=LENGTH, TooltipShort="导向间隙", TooltipLong="导向板与管托/管道单侧间隙")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_E5(s, D=114.3, SH=142.2, SL=177.2, SW=171.4, ST=8.0, GW=3.0, ID=u"E5", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); GW = float(GW)
    if D < 15.0: D = 88.9
    if ST < 4.0: ST = 8.0
    if GW < 1.0: GW = 3.0
    if SL < 40.0: SL = max(100.0, D * 0.85)
    if SW < (D + 30.0): SW = D + 80.0
    R1 = D / 2.0
    if SH < (R1 + 120.0): SH = R1 + 180.0
    # 1. 上部管托鞍板（O=0.0）与向左右伸出的水平导向滑翼板
    o_main = CYLINDER(s, R=R1 + ST, H=SL * 0.85, O=0.0).rotateY(90.0).translate((-(SL * 0.425), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL * 0.85 + 4.0, O=0.0).rotateY(90.0).translate((-(SL * 0.425 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    o_top = BOX(s, L=(R1 + ST) * 2.5, W=(R1 + ST) * 1.5, H=SL).translate((0.0, 0.0, (R1 + ST) * 0.75))
    o_main.subtractFrom(o_top); o_top.erase()
    z_wing = -(R1 + (SH - R1) * 0.25)
    o_web = BOX(s, L=ST * 1.2, W=(z_wing + R1) * -1.0, H=SL * 0.8).translate((0.0, 0.0, -(R1 - (z_wing + R1) * 0.5)))
    o_wing = BOX(s, L=SW * 1.15, W=ST * 1.5, H=SL * 0.75).translate((0.0, 0.0, z_wing))
    o_main.uniteWith(o_web); o_web.erase()
    o_main.uniteWith(o_wing); o_wing.erase()
    # 2. 中央下方坐落式弹簧/可调支座圆筒与底板
    can_h = max(50.0, SH + z_wing - ST * 2.0)
    can_r = min(SW * 0.32, max(35.0, R1 * 0.7))
    o_can = CYLINDER(s, R=can_r, H=can_h, O=0.0).translate((0.0, 0.0, -(SH - ST * 1.4)))
    o_base = BOX(s, L=SW * 1.4, W=ST * 1.4, H=SL).translate((0.0, 0.0, -(SH - ST * 0.7)))
    o_main.uniteWith(o_can); o_can.erase()
    o_main.uniteWith(o_base); o_base.erase()
    # 3. 左右两侧竖直双槽钢导向立柱（夹住水平导向翼板两端）
    post_h = (SH + z_wing) + ST * 6.0
    for sy in (-1.0, 1.0):
        yc = sy * (SW * 0.575 + GW + ST)
        o_p1 = BOX(s, L=ST * 2.2, W=post_h, H=SL * 0.55).translate((0.0, yc, -(SH - post_h / 2.0)))
        o_p2 = BOX(s, L=ST * 3.5, W=ST * 1.2, H=SL * 0.55).translate((0.0, yc - sy * ST * 1.2, -(SH - post_h + ST * 0.6)))
        o_main.uniteWith(o_p1); o_p1.erase()
        o_main.uniteWith(o_p2); o_p2.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
