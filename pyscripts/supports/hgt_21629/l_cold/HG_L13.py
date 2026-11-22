# -*- coding: utf-8 -*-
# HG/T 21629-2021 L13 耳轴管的保冷管托（图 C.11-13）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="耳轴管的保冷管托", TooltipLong="HG/T 21629-2021 L13 耳轴管的保冷管托 图C.11-13", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_L13(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"L13", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 25.0: D = 114.3
    if LEG_D < 20.0: LEG_D = max(48.3, D * 0.55)
    if ST < 4.0: ST = 8.0
    R1 = D / 2.0; R_leg = LEG_D / 2.0
    if SH < (R1 + 80.0): SH = R1 + 180.0
    # 1. 左侧竖直主管段与90°弯头（沿 Z 轴主管在 Y = -R1*1.8 处）
    y_main = -(R1 * 1.6)
    o1 = CYLINDER(s, R=R1, H=D * 2.2, O=0.0).translate((0.0, y_main, -(D * 1.1)))
    o_in = CYLINDER(s, R=max(6.0, R1 - ST), H=D * 2.2 + 4.0, O=0.0).translate((0.0, y_main, -(D * 1.1 + 2.0)))
    o1.subtractFrom(o_in); o_in.erase()
    # 2. 向右侧（+Y）水平伸出的耳轴管 + 耳轴外包保冷圆筒与下部T形支座
    tr_len = abs(y_main) + LEG_D * 1.8
    o_tr = CYLINDER(s, R=R_leg, H=tr_len, O=0.0).rotateX(-90.0).translate((0.0, y_main, 0.0))
    R_cold = R_leg * 1.85
    cold_l = LEG_D * 1.5
    o_cold = CYLINDER(s, R=R_cold, H=cold_l, O=0.0).rotateX(-90.0).translate((0.0, -(cold_l * 0.35), 0.0))
    ped_h = max(30.0, SH - R_cold - ST)
    o_web = BOX(s, L=LEG_D * 1.4, W=ped_h, H=ST * 1.4).translate((0.0, LEG_D * 0.4, -(R_cold + ped_h / 2.0)))
    o_base = BOX(s, L=LEG_D * 2.2, W=ST * 1.4, H=LEG_D * 2.0).translate((0.0, LEG_D * 0.4, -(SH - ST * 0.7)))
    for p in (o_tr, o_cold, o_web, o_base):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
