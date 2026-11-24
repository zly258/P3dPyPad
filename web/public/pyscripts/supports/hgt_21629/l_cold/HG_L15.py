# -*- coding: utf-8 -*-
# HG/T 21629-2021 L15 标准型保冷管的吊架组件（1/2"~36"）（图 C.11-15）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="标准型保冷管的吊架组件（1/2~3", TooltipLong="HG/T 21629-2021 L15 标准型保冷管的吊架组件（1/2~36） 图C.11-15", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线保冷托长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="鞍板及底板钢板厚度")
@param(HH=LENGTH, TooltipShort="保冷厚", TooltipLong="高密度PIR/PUR保冷块厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_L15(s, D=114.3, SH=167.2, SL=222.9, SW=171.8, ST=8.0, HH=75.0, ID=u"L15", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 15.0: D = 88.9
    if ST < 4.0: ST = 6.0
    if HH < 30.0: HH = 75.0
    if SL < 60.0: SL = 160.0
    R1 = D / 2.0; R_cold = R1 + HH
    if SH < (R_cold + 80.0): SH = R_cold + 160.0
    # 1. 圆筒形保冷瓦块（O=0.0）与外部三螺栓吊夹
    o_main = CYLINDER(s, R=R_cold, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    cw = max(40.0, SL * 0.42)
    o_cl = CYLINDER(s, R=R_cold + ST * 1.3, H=cw, O=0.0).rotateY(90.0).translate((-(cw / 2.0), 0.0, 0.0))
    o_main.uniteWith(o_cl); o_cl.erase()
    o_in = CYLINDER(s, R=R1, H=SL + 6.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 3.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    # 2. 顶部双耳夹紧座、底部锁紧耳与向上延伸的竖直吊杆组件
    o_top_ear = BOX(s, L=ST * 5.0, W=ST * 6.0, H=cw).translate((0.0, 0.0, R_cold + ST * 3.0))
    o_bot_ear = BOX(s, L=ST * 5.0, W=ST * 4.0, H=cw).translate((0.0, 0.0, -(R_cold + ST * 2.0)))
    rod_h = max(60.0, SH - R_cold)
    o_rod = CYLINDER(s, R=ST * 1.1, H=rod_h, O=0.0).translate((0.0, 0.0, R_cold))
    o_nut = CYLINDER(s, R=ST * 2.0, H=ST * 2.2, O=0.0).translate((0.0, 0.0, R_cold + rod_h * 0.65))
    for p in (o_top_ear, o_bot_ear, o_rod, o_nut):
        o_main.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
