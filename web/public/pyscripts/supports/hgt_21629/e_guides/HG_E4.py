# -*- coding: utf-8 -*-
# HG/T 21629-2021 E4 结构型导向/限位架（图 C.5-4）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="结构型导向/限位架", TooltipLong="HG/T 21629-2021 E4 结构型导向/限位架 图C.5-4", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至导向底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="导向长", TooltipLong="沿管道轴线导向座长度")
@param(SW=LENGTH, TooltipShort="导向宽", TooltipLong="导向底座总宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="导向翼板与底板厚度")
@param(GW=LENGTH, TooltipShort="导向间隙", TooltipLong="导向板与管托/管道单侧间隙")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_E4(s, D=114.3, SH=142.2, SL=177.2, SW=171.4, ST=8.0, GW=3.0, ID=u"E4", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); GW = float(GW)
    if D < 15.0: D = 88.9
    if ST < 4.0: ST = 8.0
    if GW < 1.0: GW = 3.0
    if SL < 40.0: SL = max(100.0, D * 0.85)
    if SW < (D + 30.0): SW = D + 60.0
    R1 = D / 2.0
    if SH < (R1 + ST * 2.0 + 20.0): SH = R1 + max(75.0, D * 0.5)
    # 1. 中央管道承重鞍板（O=0.0）与 T 形管托
    o_main = CYLINDER(s, R=R1 + ST, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    o_top = BOX(s, L=(R1 + ST) * 2.5, W=(R1 + ST) * 1.5, H=SL + 10.0).translate((0.0, 0.0, (R1 + ST) * 0.75))
    o_main.subtractFrom(o_top); o_top.erase()
    o_web = BOX(s, L=ST, W=SH - R1, H=SL * 0.85).translate((0.0, 0.0, -(R1 + (SH - R1) / 2.0)))
    o_shoe_b = BOX(s, L=SW * 0.78, W=ST, H=SL * 0.85).translate((0.0, 0.0, -(SH - ST * 1.5)))
    o_main.uniteWith(o_web); o_web.erase()
    o_main.uniteWith(o_shoe_b); o_shoe_b.erase()
    # 2. 左右两侧高耸竖直 H 型钢导向立柱（高出管顶 Z = +R1*0.95，底部无顶盖横梁，呈敞口高立柱夹持）
    col_h = SH + R1 * 0.95
    col_w = max(45.0, SL * 0.45)
    frame_w = max(D + GW * 2.0 + ST * 4.0, SW + GW * 2.0)
    o_bot_beam = BOX(s, L=frame_w + col_w * 1.5, W=ST * 1.5, H=col_w * 1.2).translate((0.0, 0.0, -(SH - ST * 0.75)))
    o_main.uniteWith(o_bot_beam); o_bot_beam.erase()
    for sy in (-1.0, 1.0):
        yc = sy * (max(R1, SW * 0.39) + GW + col_w * 0.45)
        o_cw = BOX(s, L=col_w * 0.9, W=col_h, H=ST).translate((0.0, yc, -(SH - col_h / 2.0)))
        o_cf1 = BOX(s, L=ST * 1.3, W=col_h, H=col_w).translate((0.0, yc - sy * (col_w * 0.45 - ST * 0.65), -(SH - col_h / 2.0)))
        o_cf2 = BOX(s, L=ST * 1.3, W=col_h, H=col_w).translate((0.0, yc + sy * (col_w * 0.45 - ST * 0.65), -(SH - col_h / 2.0)))
        for p in (o_cw, o_cf1, o_cf2):
            o_main.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
