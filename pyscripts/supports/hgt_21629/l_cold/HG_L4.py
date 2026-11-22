# -*- coding: utf-8 -*-
# HG/T 21629-2021 L4 保冷立管的导向管托（1/2"～6")（图 C.11-4）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="保冷立管的导向管托（1/2～6)", TooltipLong="HG/T 21629-2021 L4 保冷立管的导向管托（1/2～6) 图C.11-4", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线保冷托长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="鞍板及底板钢板厚度")
@param(HH=LENGTH, TooltipShort="保冷厚", TooltipLong="高密度PIR/PUR保冷块厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_L4(s, D=114.3, SH=167.2, SL=222.9, SW=171.8, ST=8.0, HH=75.0, ID=u"L4", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 15.0: D = 60.3
    if ST < 4.0: ST = 6.0
    if HH < 30.0: HH = 65.0
    if SL < 80.0: SL = 200.0
    if SW < 60.0: SW = 120.0
    R1 = D / 2.0; R_cold = R1 + HH
    if SH < (R_cold + 40.0): SH = R_cold + 85.0
    # 1. 竖直立管段沿 Z 轴与外包分瓣保冷圆筒（O=0.0）
    pipe_h = SL * 1.4
    o_main = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0)))
    o_cold = CYLINDER(s, R=R_cold + ST, H=SL, O=0.0).translate((0.0, 0.0, -(SL / 2.0)))
    o_main.uniteWith(o_cold); o_cold.erase()
    o_in = CYLINDER(s, R=max(5.0, R1 - ST * 0.8), H=pipe_h + 6.0, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0 + 3.0)))
    o_main.subtractFrom(o_in); o_in.erase()
    # 2. 上下两道环向緊固抱箍与侧向结构生根工字形导向支座
    for z_ring in (SL * 0.32, -(SL * 0.32)):
        o_rg = CYLINDER(s, R=R_cold + ST * 2.2, H=ST * 3.5, O=0.0).translate((0.0, 0.0, z_ring - ST * 1.75))
        o_rgi = CYLINDER(s, R=R1, H=ST * 4.0, O=0.0).translate((0.0, 0.0, z_ring - ST * 2.0))
        o_rg.subtractFrom(o_rgi); o_rgi.erase()
        o_main.uniteWith(o_rg); o_rg.erase()
    arm_l = max(40.0, SH - R_cold)
    o_br = BOX(s, L=arm_l, W=SL * 0.55, H=SW * 0.75).translate((0.0, -(R_cold + arm_l / 2.0), 0.0))
    o_fl = BOX(s, L=ST * 1.6, W=SL * 0.75, H=SW * 1.1).translate((0.0, -SH, 0.0))
    o_main.uniteWith(o_br); o_br.erase()
    o_main.uniteWith(o_fl); o_fl.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
