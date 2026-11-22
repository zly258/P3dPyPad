# -*- coding: utf-8 -*-
# HG/T 21629-2021 F10 小管径立管的耳板（1/2"～2")（图 C.6-8）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="小管径立管的耳板（1/2～2)", TooltipLong="HG/T 21629-2021 F10 小管径立管的耳板（1/2～2) 图C.6-8", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_F10(s, D=42.4, SH=141.2, LEG_D=26.9, ST=6.0, ID=u"F10", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 15.0: D = 48.3
    if LEG_D < 25.0: LEG_D = 50.0
    if ST < 5.0: ST = 8.0
    R1 = D / 2.0
    if SH < (R1 + 45.0): SH = R1 + 95.0
    pipe_h = max(120.0, LEG_D * 2.5)
    # 1. 竖直立管沿 Z 轴（O=0.0 空心圆管）
    o1 = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0)))
    o_in = CYLINDER(s, R=max(4.0, R1 - ST * 0.6), H=pipe_h + 4.0, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0 + 2.0)))
    o1.subtractFrom(o_in); o_in.erase()
    # 2. 左右两侧（±Y 轴）对称焊接的竖直矩形承重耳板（沿立管轴向高 LEG_D，外伸至 ±SH，厚 ST）
    span_y = SH * 2.0
    o_ears = BOX(s, L=span_y, W=LEG_D, H=ST).translate((0.0, 0.0, 0.0))
    o_pcut = CYLINDER(s, R=R1, H=LEG_D + 10.0, O=0.0).translate((0.0, 0.0, -(LEG_D / 2.0 + 5.0)))
    o_ears.subtractFrom(o_pcut); o_pcut.erase()
    o1.uniteWith(o_ears); o_ears.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
