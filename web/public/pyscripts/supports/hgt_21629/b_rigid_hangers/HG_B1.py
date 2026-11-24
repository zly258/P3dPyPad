# -*- coding: utf-8 -*-
# HG/T 21629-2021 B1~B4 管夹式刚性吊架（1/2"~36"）（图 C.2-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="管夹式刚性吊架（1/2~36）", TooltipLong="HG/T 21629-2021 B1~B4 管夹式刚性吊架（1/2~36） 图C.2-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="吊杆长", TooltipLong="管心至吊杆上端总高", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="管夹/横担宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="管夹/横担板厚")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆公称直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_B1(s, D=114.3, H=485.8, B=38.4, T=8.0, d=12.0, ID=u"B1", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 15.0: D = 60.3
    if d < 8.0: d = 12.0
    if T < 4.0: T = 6.0
    if B < 24.0: B = 40.0
    R1 = D / 2.0; R2 = R1 + T
    if H < (R1 + 120.0): H = R1 + 280.0
    o1 = CYLINDER(s, R=R2, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=B + 4.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    ear_h = d * 3.2
    for sy in (-(d * 0.6 + T / 2.0), (d * 0.6 + T / 2.0)):
        o_ear = BOX(s, L=T, W=ear_h, H=B).translate((0.0, sy, R1 + ear_h / 2.0 - 2.0))
        o1.uniteWith(o_ear); o_ear.erase()
    o_rod = CYLINDER(s, R=d / 2.0, H=H - R1, O=0.0).translate((0.0, 0.0, R1))
    z_tb = R1 + (H - R1) * 0.5
    o_tb = BOX(s, L=d * 2.2, W=d * 5.0, H=d * 1.4).translate((0.0, 0.0, z_tb))
    o_win = BOX(s, L=d * 1.0, W=d * 3.2, H=d * 3.0).translate((0.0, 0.0, z_tb))
    o_tb.subtractFrom(o_win); o_win.erase()
    o_top = BOX(s, L=d * 3.0, W=d * 2.2, H=B * 0.8).translate((0.0, 0.0, H - d * 1.1))
    for p in (o_rod, o_tb, o_top):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
