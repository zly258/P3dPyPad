# -*- coding: utf-8 -*-
# HG/T 21629-2021 Y3 法兰支架（3"~24")（图 C.23-3）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="法兰支架（3~24)", TooltipLong="HG/T 21629-2021 Y3 法兰支架（3~24) 图C.23-3", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(B=LENGTH, TooltipShort="沿管长", TooltipLong="垫板/隔离层/支架沿管宽度", Ask4Dist=True)
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="弧形垫板/支架钢板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_Y3(s, D=114.3, B=125.0, T=8.0, ID=u"Y3", **kw):
    D = float(D); B = float(B); T = float(T)
    if D < 20.0: D = 88.9
    if B < 60.0: B = 180.0
    if T < 6.0: T = 10.0
    R1 = D / 2.0
    fl_r = R1 + max(35.0, D * 0.28)
    o1 = CYLINDER(s, R=fl_r, H=T * 1.2, O=0.0).rotateY(90.0).translate((-(T * 0.6), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=T * 2.0, O=0.0).rotateY(90.0).translate((-T, 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_up = BOX(s, L=fl_r * 2.4, W=fl_r * 1.3, H=T * 3.0).translate((0.0, 0.0, fl_r * 0.65))
    o1.subtractFrom(o_up); o_up.erase()
    leg_h = max(80.0, B)
    o_web = BOX(s, L=fl_r * 1.1, W=leg_h, H=T).translate((0.0, 0.0, -(R1 + leg_h / 2.0)))
    o_rib = BOX(s, L=T, W=leg_h, H=fl_r * 0.9).translate((0.0, 0.0, -(R1 + leg_h / 2.0)))
    o_base = BOX(s, L=fl_r * 1.4, W=T * 1.4, H=fl_r * 1.2).translate((0.0, 0.0, -(R1 + leg_h)))
    for p in (o_web, o_rib, o_base):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('B', (0.0, 0.0, 0.0), (B, 0.0, 0.0))
