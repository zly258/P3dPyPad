# -*- coding: utf-8 -*-
# HG/T 21629-2021 B9~B12 秋千式刚性吊架（图 C.2-3）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="秋千式刚性吊架", TooltipLong="HG/T 21629-2021 B9~B12 秋千式刚性吊架 图C.2-3", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="吊杆长", TooltipLong="管心至吊杆上端总高", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="管夹/横担宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="管夹/横担板厚")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆公称直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_B9(s, D=306.0, H=1008.0, B=115.2, T=13.8, d=36.0, ID=u"B9", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 25.0: D = 88.9
    if d < 10.0: d = 14.0
    if T < 6.0: T = 8.0
    if B < 40.0: B = 60.0
    R1 = D / 2.0
    if H < (R1 + 150.0): H = R1 + 320.0
    span_y = D + B * 2.4
    z_beam = -(R1 + B * 0.55)
    o1 = BOX(s, L=span_y + B * 1.4, W=B, H=B * 0.85).translate((0.0, 0.0, z_beam))
    o_sad = CYLINDER(s, R=R1 + T, H=B * 0.85, O=0.0).rotateY(90.0).translate((-(B * 0.425), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=B * 0.85 + 4.0, O=0.0).rotateY(90.0).translate((-(B * 0.425 + 2.0), 0.0, 0.0))
    o_sad.subtractFrom(o_in); o_in.erase()
    o_up = BOX(s, L=(R1 + T) * 2.4, W=(R1 + T) * 1.4, H=B).translate((0.0, 0.0, (R1 + T) * 0.7))
    o_sad.subtractFrom(o_up); o_up.erase()
    o1.uniteWith(o_sad); o_sad.erase()
    for sy in (-1.0, 1.0):
        yc = sy * (span_y / 2.0)
        o_r = CYLINDER(s, R=d / 2.0, H=H - z_beam + B * 0.6, O=0.0).translate((0.0, yc, z_beam - B * 0.6))
        o_tb = BOX(s, L=d * 2.1, W=d * 4.5, H=d * 1.4).translate((0.0, yc, H * 0.48))
        o_lug = BOX(s, L=d * 2.8, W=d * 2.2, H=d * 1.8).translate((0.0, yc, H - d * 1.1))
        for p in (o_r, o_tb, o_lug):
            o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
