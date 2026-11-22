# -*- coding: utf-8 -*-
# HG/T 21629-2021 L9 地面上生根的保冷管固定架（1/2"~2")（图 C.11-9）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="地面上生根的保冷管固定架（1/2~", TooltipLong="HG/T 21629-2021 L9 地面上生根的保冷管固定架（1/2~2) 图C.11-9", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线保冷托长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="鞍板及底板钢板厚度")
@param(HH=LENGTH, TooltipShort="保冷厚", TooltipLong="高密度PIR/PUR保冷块厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_L9(s, D=42.4, SH=106.2, SL=160.0, SW=92.6, ST=6.0, HH=50.0, ID=u"L9", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 15.0: D = 33.7
    if ST < 4.0: ST = 6.0
    if HH < 25.0: HH = 50.0
    if SL < 80.0: SL = 180.0
    if SW < 50.0: SW = 90.0
    R1 = D / 2.0; R_cold = R1 + HH
    if SH < (R_cold + 50.0): SH = R_cold + 110.0
    # 1. 竖直保冷立管筒体（沿 Z 轴，O=0.0）与上下两道外抱箍
    o_main = CYLINDER(s, R=R_cold, H=SL, O=0.0).translate((0.0, 0.0, -(SL / 2.0)))
    for z_c in (SL * 0.22, -(SL * 0.22)):
        o_cl = CYLINDER(s, R=R_cold + ST * 1.5, H=ST * 4.0, O=0.0).translate((0.0, 0.0, z_c - ST * 2.0))
        o_ear = BOX(s, L=R_cold * 2.5, W=ST * 4.0, H=ST * 2.5).translate((0.0, 0.0, z_c))
        o_main.uniteWith(o_cl); o_cl.erase()
        o_main.uniteWith(o_ear); o_ear.erase()
    o_in = CYLINDER(s, R=R1, H=SL + 6.0, O=0.0).translate((0.0, 0.0, -(SL / 2.0 + 3.0)))
    o_main.subtractFrom(o_in); o_in.erase()
    # 2. 一侧（-Y 侧）竖直落地角钢固定支腿与接地底板（见 hg_index_p023.png L9 左下角接地支座）
    y_leg = -(R_cold + ST * 4.5)
    leg_h = SL * 0.65
    o_link = BOX(s, L=ST * 8.0, W=SL * 0.55, H=ST * 1.5).translate((0.0, -(R_cold + ST * 2.5), -(SL * 0.1)))
    o_leg = BOX(s, L=SW * 0.6, W=leg_h, H=SW * 0.6).translate((0.0, y_leg, -(SL * 0.5 - leg_h / 2.0)))
    o_base = BOX(s, L=SW * 1.2, W=ST * 1.5, H=SW * 1.2).translate((0.0, y_leg, -(SL * 0.5 - ST * 0.75)))
    for p in (o_link, o_leg, o_base):
        o_main.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
