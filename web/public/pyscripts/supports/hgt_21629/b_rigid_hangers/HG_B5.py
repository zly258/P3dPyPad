# -*- coding: utf-8 -*-
# HG/T 21629-2021 B5~B8 吊杆式刚性吊架（图 C.2-2）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="吊杆式刚性吊架", TooltipLong="HG/T 21629-2021 B5~B8 吊杆式刚性吊架 图C.2-2", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="吊杆长", TooltipLong="管心至吊杆上端总高", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="管夹/横担宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="管夹/横担板厚")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆公称直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_B5(s, D=114.3, H=485.8, B=38.4, T=8.0, d=12.0, ID=u"B5", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 25.0: D = 88.9
    if d < 8.0: d = 12.0
    if T < 6.0: T = 8.0
    if B < 35.0: B = 60.0
    R1 = D / 2.0
    if H < (R1 + 140.0): H = R1 + 300.0
    lug_h = max(55.0, (H - R1) * 0.25)
    o1 = BOX(s, L=B, W=lug_h + R1 * 0.3, H=T).translate((0.0, 0.0, R1 * 0.7 + lug_h / 2.0))
    o_pipe = CYLINDER(s, R=R1, H=T * 4.0, O=0.0).rotateY(90.0).translate((-(T * 2.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()
    o_clev = BOX(s, L=d * 2.4, W=d * 3.0, H=T * 2.6).translate((0.0, 0.0, R1 + lug_h))
    o_rod = CYLINDER(s, R=d / 2.0, H=H - (R1 + lug_h), O=0.0).translate((0.0, 0.0, R1 + lug_h))
    z_tb = R1 + lug_h + (H - R1 - lug_h) * 0.52
    o_tb = CYLINDER(s, R=d * 1.05, H=d * 4.2, O=0.0).translate((0.0, 0.0, z_tb - d * 2.1))
    o_top = BOX(s, L=B * 0.85, W=d * 2.5, H=T).translate((0.0, 0.0, H - d * 1.25))
    for p in (o_clev, o_rod, o_tb, o_top):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
