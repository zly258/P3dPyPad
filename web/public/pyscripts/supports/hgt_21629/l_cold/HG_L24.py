# -*- coding: utf-8 -*-
# HG/T 21629-2021 L24 设备预焊件的保冷块（图 C.11-20）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="设备预焊件的保冷块", TooltipLong="HG/T 21629-2021 L24 设备预焊件的保冷块 图C.11-20", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线保冷托长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="鞍板及底板钢板厚度")
@param(HH=LENGTH, TooltipShort="保冷厚", TooltipLong="高密度PIR/PUR保冷块厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_L24(s, D=114.3, SH=167.2, SL=222.9, SW=171.8, ST=8.0, HH=75.0, ID=u"L24", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 15.0: D = 88.9
    if ST < 3.0: ST = 5.0
    if HH < 30.0: HH = 75.0
    if SL < 60.0: SL = 160.0
    R1 = D / 2.0; R_cold = R1 + HH
    # 1. 无鞍座纯圆筒分瓣高密度保冷块（O=0.0 外圆减内圆）
    o_main = CYLINDER(s, R=R_cold, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    # 2. 外表面前后两道金属紧固箍带与 45° 斜向拉紧螺栓耳
    for sx in (-(SL * 0.28), (SL * 0.28)):
        o_band = CYLINDER(s, R=R_cold + ST, H=ST * 4.0, O=0.0).rotateY(90.0).translate((sx - ST * 2.0, 0.0, 0.0))
        o_ear = BOX(s, L=(R_cold + ST * 4.2) * 2.0, W=ST * 2.2, H=ST * 4.0).rotateX(40.0).translate((sx, 0.0, 0.0))
        o_main.uniteWith(o_band); o_band.erase()
        o_main.uniteWith(o_ear); o_ear.erase()
    o_in = CYLINDER(s, R=R1, H=SL + 6.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 3.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
