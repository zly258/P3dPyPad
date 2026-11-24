# -*- coding: utf-8 -*-
# HG/T 21629-2021 K2 绝热管的限位架（1/2"~24")（图 C.10-2）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="绝热管的限位架（1/2~24)", TooltipLong="HG/T 21629-2021 K2 绝热管的限位架（1/2~24) 图C.10-2", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至限位架底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="限位长", TooltipLong="沿管轴线限位座总长")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="限位座底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="止推挡板与腹板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_K2(s, D=114.3, SH=157.2, SL=188.6, SW=114.3, ST=8.0, ID=u"K2", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 6.0
    if SL < 60.0: SL = max(100.0, D * 0.9)
    if SW < 50.0: SW = max(80.0, D * 0.7)
    R1 = D / 2.0
    if SH < (R1 + ST * 2.0 + 20.0): SH = R1 + max(70.0, D * 0.5)
    # 1. 管托鞍板（O=0.0）与腹板、底板
    o_main = CYLINDER(s, R=R1 + ST, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    web_h = SH - R1 - ST
    if web_h < 20.0: web_h = 20.0
    o_web = BOX(s, L=ST * 1.4, W=web_h, H=SL).translate((0.0, 0.0, -(R1 + web_h / 2.0)))
    o_base = BOX(s, L=SW, W=ST * 1.2, H=SL).translate((0.0, 0.0, -(SH - ST * 0.6)))
    o_main.uniteWith(o_web); o_web.erase()
    o_main.uniteWith(o_base); o_base.erase()
    # 2. 前后轴向止推限位端板与侧向卡板
    for sx in (-1.0, 1.0):
        o_end = BOX(s, L=SW * 1.15, W=web_h * 0.85, H=ST * 1.5).translate((sx * (SL / 2.0 - ST * 0.75), 0.0, -(SH - web_h * 0.425)))
        o_main.uniteWith(o_end); o_end.erase()
    for sy in (-1.0, 1.0):
        o_lat = BOX(s, L=ST * 1.4, W=web_h * 0.65, H=SL * 0.5).translate((0.0, sy * (SW / 2.0 + ST * 0.7), -(SH - web_h * 0.325)))
        o_main.uniteWith(o_lat); o_lat.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
