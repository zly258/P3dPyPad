# -*- coding: utf-8 -*-
# HG/T 21629-2021 G9 罐的支腿（-20℃~300℃）（图 C.7-9）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="罐的支腿（-20℃~300℃）", TooltipLong="HG/T 21629-2021 G9 罐的支腿（-20℃~300℃） 图C.7-9", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_G9(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"G9", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 100.0: D = 400.0
    if LEG_D < 50.0: LEG_D = 120.0
    if ST < 6.0: ST = 10.0
    if SH < 180.0: SH = 350.0
    R_tank = max(250.0, D * 1.2)
    pad_h = SH * 0.65
    # 1. 贴合立式罐体外壁的竖直圆弧预焊垫板（O=0.0 外圆筒减内圆筒，再截取支腿宽度）
    o1 = CYLINDER(s, R=R_tank + ST, H=pad_h, O=0.0).translate((0.0, R_tank, -(pad_h)))
    o_in = CYLINDER(s, R=R_tank, H=pad_h + 4.0, O=0.0).translate((0.0, R_tank, -(pad_h + 2.0)))
    o1.subtractFrom(o_in); o_in.erase()
    o_bound = BOX(s, L=LEG_D * 1.5, W=pad_h + 10.0, H=LEG_D * 2.0).translate((0.0, 0.0, -(pad_h / 2.0)))
    o1.intersectWith(o_bound); o_bound.erase()
    # 2. 竖直双腹板/槽钢罐支腿（从 Z = 0 向下延伸至 Z = -SH）
    leg_w = LEG_D * 1.2
    for sx in (-(leg_w * 0.42), (leg_w * 0.42)):
        o_web = BOX(s, L=LEG_D, W=SH, H=ST).translate((sx, -(LEG_D / 2.0), -(SH / 2.0)))
        o1.uniteWith(o_web); o_web.erase()
    o_front = BOX(s, L=ST, W=SH, H=leg_w).translate((0.0, -LEG_D + ST / 2.0, -(SH / 2.0)))
    o_top_cap = BOX(s, L=LEG_D, W=ST * 1.2, H=leg_w).translate((0.0, -(LEG_D / 2.0), -(ST * 0.6)))
    # 3. 底部支腿底板与下部基础垫板
    o_base1 = BOX(s, L=LEG_D * 1.8, W=ST * 1.5, H=leg_w * 1.6).translate((0.0, -(LEG_D * 0.6), -(SH - ST * 1.8)))
    o_base2 = BOX(s, L=LEG_D * 2.0, W=ST * 1.2, H=leg_w * 1.8).translate((0.0, -(LEG_D * 0.6), -(SH - ST * 0.6)))
    for p in (o_front, o_top_cap, o_base1, o_base2):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
