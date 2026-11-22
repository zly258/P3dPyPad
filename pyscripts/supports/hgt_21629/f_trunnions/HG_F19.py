# -*- coding: utf-8 -*-
# HG/T 21629-2021 F19 斜管的竖直耳轴（图 C.6-14）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="斜管的竖直耳轴", TooltipLong="HG/T 21629-2021 F19 斜管的竖直耳轴 图C.6-14", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_F19(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"F19", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 25.0: D = 114.3
    if LEG_D < 20.0: LEG_D = max(33.7, D * 0.55)
    if ST < 4.0: ST = 8.0
    R1 = D / 2.0
    if SH < (R1 + 80.0): SH = R1 + 180.0
    R_leg = LEG_D / 2.0; R_leg_in = max(5.0, R_leg - ST)
    pipe_l = max(LEG_D * 2.8, D * 1.8)
    # 1. 倾斜 20° 的母管段（先沿 X 轴构造空心管，再绕 Y 轴旋转 -20°）
    o1 = CYLINDER(s, R=R1, H=pipe_l, O=0.0).rotateY(90.0).translate((-(pipe_l / 2.0), 0.0, 0.0)).rotateY(-20.0)
    o_in = CYLINDER(s, R=max(5.0, R1 - ST * 0.8), H=pipe_l + 6.0, O=0.0).rotateY(90.0).translate((-(pipe_l / 2.0 + 3.0), 0.0, 0.0)).rotateY(-20.0)
    o1.subtractFrom(o_in); o_in.erase()
    # 2. 斜管底部补强板与竖直圆管耳轴支腿（沿 -Z 轴竖直向下延伸至水平底板 Z = -SH）
    leg_h = max(35.0, SH - R1 * 0.75 - ST)
    o_leg = CYLINDER(s, R=R_leg, H=leg_h, O=0.0).translate((0.0, 0.0, -(SH - ST)))
    o_leg_i = CYLINDER(s, R=R_leg_in, H=leg_h + 4.0, O=0.0).translate((0.0, 0.0, -(SH - ST + 2.0)))
    o_leg.subtractFrom(o_leg_i); o_leg_i.erase()
    o_base = BOX(s, L=LEG_D * 2.2, W=ST * 1.4, H=LEG_D * 2.0).translate((0.0, 0.0, -(SH - ST * 0.7)))
    o1.uniteWith(o_leg); o_leg.erase()
    o1.uniteWith(o_base); o_base.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
