# -*- coding: utf-8 -*-
# HG/T 21629-2021 L11 温度低于-40℃的不保冷管管夹式管托(3"~40")（图 C.11-11）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="温度低于-40℃的不保冷管管夹式管托", TooltipLong="HG/T 21629-2021 L11 温度低于-40℃的不保冷管管夹式管托(3~40) 图C.11-11", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线保冷托长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="鞍板及底板钢板厚度")
@param(HH=LENGTH, TooltipShort="保冷厚", TooltipLong="高密度PIR/PUR保冷块厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_L11(s, D=114.3, SH=167.2, SL=222.9, SW=171.8, ST=8.0, HH=75.0, ID=u"L11", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 25.0: D = 114.3
    if ST < 5.0: ST = 8.0
    if HH < 25.0: HH = 50.0
    if SL < 60.0: SL = 160.0
    if SW < 50.0: SW = 110.0
    R1 = D / 2.0
    if SH < (R1 + HH + 40.0): SH = R1 + HH + 85.0
    # 1. 上部金属管夹直接抱紧低温裸管（O=0.0，带35°斜向双螺栓耳）
    o_main = CYLINDER(s, R=R1 + ST, H=SL * 0.8, O=0.0).rotateY(90.0).translate((-(SL * 0.4), 0.0, 0.0))
    o_ears = BOX(s, L=(R1 + ST * 4.5) * 2.0, W=ST * 2.2, H=SL * 0.8).rotateX(35.0)
    o_main.uniteWith(o_ears); o_ears.erase()
    o_in = CYLINDER(s, R=R1, H=SL + 6.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 3.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    # 2. 管夹下部钢腹板 + 底部厚层方形隔冷垫块（高 HH）+ 底板与双侧紧固螺栓
    web_h = max(20.0, SH - R1 - HH - ST * 2.0)
    o_web = BOX(s, L=ST * 1.3, W=web_h, H=SL * 0.8).translate((0.0, 0.0, -(R1 + web_h / 2.0)))
    o_mid_p = BOX(s, L=SW * 0.92, W=ST, H=SL * 0.88).translate((0.0, 0.0, -(R1 + web_h + ST / 2.0)))
    z_blk = -(SH - ST - HH / 2.0)
    o_blk = BOX(s, L=SW * 0.88, W=HH, H=SL * 0.88).translate((0.0, 0.0, z_blk))
    o_base = BOX(s, L=SW * 1.15, W=ST * 1.3, H=SL).translate((0.0, 0.0, -(SH - ST * 0.65)))
    for p in (o_web, o_mid_p, o_blk, o_base):
        o_main.uniteWith(p); p.erase()
    for sy in (-(SW * 0.36), (SW * 0.36)):
        o_b = CYLINDER(s, R=ST * 0.75, H=HH + ST * 3.5, O=0.0).translate((0.0, sy, -(SH + ST * 0.5)))
        o_main.uniteWith(o_b); o_b.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
