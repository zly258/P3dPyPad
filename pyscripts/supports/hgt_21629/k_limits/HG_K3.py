# -*- coding: utf-8 -*-
# HG/T 21629-2021 K3 大管的限位架（图 C.10-3）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="大管的限位架", TooltipLong="HG/T 21629-2021 K3 大管的限位架 图C.10-3", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至限位架底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="限位长", TooltipLong="沿管轴线限位座总长")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="限位座底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="止推挡板与腹板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_K3(s, D=711.0, SH=505.5, SL=600.0, SW=502.2, ST=12.0, ID=u"K3", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST)
    if D < 100.0: D = 406.4
    if ST < 6.0: ST = 10.0
    if SL < 100.0: SL = 260.0
    if SW < 100.0: SW = 240.0
    R1 = D / 2.0
    if SH < (R1 + 80.0): SH = R1 + 150.0
    o_main = CYLINDER(s, R=R1 + ST * 1.2, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    o_top = BOX(s, L=(R1 + ST * 2.0) * 2.4, W=(R1 + ST * 2.0) * 1.3, H=SL + 10.0).translate((0.0, 0.0, (R1 + ST * 2.0) * 0.65))
    o_main.subtractFrom(o_top); o_top.erase()
    web_h = max(30.0, SH - R1 * 0.75 - ST)
    for sy in (-(SW * 0.32), (SW * 0.32)):
        o_w = BOX(s, L=ST * 1.3, W=web_h, H=SL * 0.9).translate((0.0, sy, -(SH - ST - web_h / 2.0)))
        o_main.uniteWith(o_w); o_w.erase()
    o_base = BOX(s, L=SW * 1.15, W=ST * 1.4, H=SL).translate((0.0, 0.0, -(SH - ST * 0.7)))
    o_main.uniteWith(o_base); o_base.erase()
    # 底板下方前后成对向下卡持支撑钢梁翼缘的轴向限位挡爪
    lug_h = ST * 4.5
    for sx in (-(SL * 0.28), (SL * 0.28)):
        o_stop = BOX(s, L=SW * 0.85, W=lug_h, H=ST * 1.6).translate((sx, 0.0, -(SH + lug_h / 2.0)))
        o_gus = BOX(s, L=SW * 0.5, W=lug_h * 0.8, H=ST * 1.4).translate((sx * 1.32, 0.0, -(SH + lug_h * 0.4)))
        o_main.uniteWith(o_stop); o_stop.erase()
        o_main.uniteWith(o_gus); o_gus.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
