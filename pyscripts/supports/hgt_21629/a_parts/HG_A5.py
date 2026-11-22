# -*- coding: utf-8 -*-
# HG/T 21629-2021 A5 减振用U形管夹（图 C.1-5）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="减振用U形管夹", TooltipLong="HG/T 21629-2021 A5 减振用U形管夹 图C.1-5", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="腿长", TooltipLong="U形螺栓直线段长度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="开档", TooltipLong="U形中心距/内宽")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="U形圆钢螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A5(s, D=114.3, H=120.7, B=140.3, d=12.0, ID=u"A5", **kw):
    D = float(D); H = float(H); B = float(B); d = float(d)
    if D < 15.0: D = 33.7
    if d < 6.0: d = 10.0
    if B < (D + d * 2.0): B = D + d * 2.4
    if H < (D / 2.0 + d * 2.5): H = D / 2.0 + d * 3.5
    R = B / 2.0; rod = d / 2.0
    o1 = TORUS(s, R1=R, R2=rod).rotateY(90.0)
    o_cut = BOX(s, L=(R + rod) * 3.0, W=(R + rod) * 2.2, H=d * 4.0).translate((0.0, 0.0, -(R + rod)))
    o1.subtractFrom(o_cut); o_cut.erase()
    z_base = -(D / 2.0 + d * 0.8)
    for sy in (-1.0, 1.0):
        o_leg = CYLINDER(s, R=rod, H=H, O=0.0).translate((0.0, sy * R, -H))
        o_gus = BOX(s, L=d * 3.2, W=d * 2.4, H=max(5.0, d * 0.5)).translate((0.0, sy * (R + d * 1.4), z_base + d * 1.2))
        o_nut = CYLINDER(s, R=d * 0.88, H=d * 0.8, O=0.0).translate((0.0, sy * R, -H))
        for p in (o_leg, o_gus, o_nut):
            o1.uniteWith(p); p.erase()
    lin_t = max(4.0, (R - D / 2.0 - rod * 0.5))
    if lin_t < 3.0: lin_t = 4.0
    lin_w = max(28.0, d * 2.8)
    o_lin = CYLINDER(s, R=D / 2.0 + lin_t, H=lin_w, O=0.0).rotateY(90.0).translate((-(lin_w / 2.0), 0.0, 0.0))
    o_lin_i = CYLINDER(s, R=D / 2.0, H=lin_w + 4.0, O=0.0).rotateY(90.0).translate((-(lin_w / 2.0 + 2.0), 0.0, 0.0))
    o_lin.subtractFrom(o_lin_i); o_lin_i.erase()
    o_base = BOX(s, L=B + d * 6.5, W=max(6.0, d * 0.6), H=lin_w).translate((0.0, 0.0, z_base))
    o1.uniteWith(o_lin); o_lin.erase()
    o1.uniteWith(o_base); o_base.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
