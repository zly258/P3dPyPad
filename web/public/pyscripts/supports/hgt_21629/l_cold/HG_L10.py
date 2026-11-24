# -*- coding: utf-8 -*-
# HG/T 21629-2021 L10 地面上生根的保冷管架（1/2"~36"）（图 C.11-10）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="地面上生根的保冷管架（1/2~36", TooltipLong="HG/T 21629-2021 L10 地面上生根的保冷管架（1/2~36） 图C.11-10", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线保冷托长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="鞍板及底板钢板厚度")
@param(HH=LENGTH, TooltipShort="保冷厚", TooltipLong="高密度PIR/PUR保冷块厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_L10(s, D=114.3, SH=167.2, SL=222.9, SW=171.8, ST=8.0, HH=75.0, ID=u"L10", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 15.0: D = 88.9
    if ST < 4.0: ST = 6.0
    if HH < 30.0: HH = 75.0
    if SL < 60.0: SL = 160.0
    if SW < 60.0: SW = 120.0
    R1 = D / 2.0; R_cold = R1 + HH
    if SH < (R_cold + 100.0): SH = R_cold + 220.0
    # 1. 上部水平保冷层（O=0.0）与双螺栓水平抱箍
    o_main = CYLINDER(s, R=R_cold + ST, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_ears = BOX(s, L=(R_cold + ST * 5.0) * 2.0, W=ST * 2.2, H=SL * 0.75)
    o_main.uniteWith(o_ears); o_ears.erase()
    o_in = CYLINDER(s, R=R1, H=SL + 6.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 3.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    # 2. 下部左右对称双立柱高支腿架与底部接地底板
    leg_h = max(60.0, SH - R_cold * 0.85 - ST * 1.5)
    for sy in (-(R_cold * 0.55), (R_cold * 0.55)):
        o_col = BOX(s, L=ST * 1.6, W=leg_h, H=SL * 0.55).translate((0.0, sy, -(SH - ST * 1.5 - leg_h / 2.0)))
        o_main.uniteWith(o_col); o_col.erase()
    o_base = BOX(s, L=R_cold * 1.8, W=ST * 1.5, H=SL * 0.9).translate((0.0, 0.0, -(SH - ST * 0.75)))
    o_main.uniteWith(o_base); o_base.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
