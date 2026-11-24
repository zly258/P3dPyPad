# -*- coding: utf-8 -*-
# HG/T 21629-2021 E3 管托的压扣型导向架（图 C.5-3）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="管托的压扣型导向架", TooltipLong="HG/T 21629-2021 E3 管托的压扣型导向架 图C.5-3", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至导向底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="导向长", TooltipLong="沿管道轴线导向座长度")
@param(SW=LENGTH, TooltipShort="导向宽", TooltipLong="导向底座总宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="导向翼板与底板厚度")
@param(GW=LENGTH, TooltipShort="导向间隙", TooltipLong="导向板与管托/管道单侧间隙")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_E3(s, D=114.3, SH=142.2, SL=177.2, SW=171.4, ST=8.0, GW=3.0, ID=u"E3", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); GW = float(GW)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 6.0
    if GW < 1.0: GW = 3.0
    if SL < 40.0: SL = max(80.0, D * 0.8)
    if SW < (D + 30.0): SW = D + 60.0
    R1 = D / 2.0
    if SH < (R1 + ST * 2.0 + 15.0): SH = R1 + max(60.0, D * 0.45)
    # 1. T型焊接管托本体（弧形鞍板 O=0.0 + 腹板 + 管托底板）
    o_main = CYLINDER(s, R=R1 + ST, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    o_top = BOX(s, L=(R1 + ST) * 2.5, W=(R1 + ST) * 1.6, H=SL + 10.0).translate((0.0, 0.0, (R1 + ST) * 0.8))
    o_main.subtractFrom(o_top); o_top.erase()
    web_h = SH - R1 - ST
    if web_h < 15.0: web_h = 15.0
    o_web = BOX(s, L=ST, W=web_h, H=SL).translate((0.0, 0.0, -(R1 + web_h / 2.0)))
    o_base = BOX(s, L=SW, W=ST, H=SL).translate((0.0, 0.0, -(SH - ST / 2.0)))
    o_main.uniteWith(o_web); o_web.erase()
    o_main.uniteWith(o_base); o_base.erase()
    # 2. 双侧导向型钢卡板（夹在管托底板两侧 Y = ±(SW/2 + GW)）
    guide_h = max(50.0, (SH - R1) * 0.65)
    for sy in (-1.0, 1.0):
        gy = SW / 2.0 + GW + ST / 2.0
        o_gcol = BOX(s, L=ST * 1.2, W=guide_h, H=SL * 0.65).translate((0.0, sy * gy, -(SH - guide_h / 2.0)))
        o_gfoot = BOX(s, L=ST * 3.5, W=ST, H=SL * 0.65).translate((0.0, sy * (gy + ST * 1.2), -(SH - ST / 2.0)))
        o_main.uniteWith(o_gcol); o_gcol.erase()
        o_main.uniteWith(o_gfoot); o_gfoot.erase()
        # E3 压扣型向内折边抗拔压板（扣住管托底板上表面）
        o_lip = BOX(s, L=ST * 3.2, W=ST, H=SL * 0.65).translate((0.0, sy * (SW / 2.0 - ST * 0.8), -(SH - ST * 2.2)))
        o_gus = BOX(s, L=ST * 2.5, W=guide_h * 0.7, H=ST).translate((0.0, sy * (gy + ST * 1.2), -(SH - guide_h * 0.45)))
        o_main.uniteWith(o_lip); o_lip.erase()
        o_main.uniteWith(o_gus); o_gus.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
