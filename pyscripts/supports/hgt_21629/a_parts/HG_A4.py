# -*- coding: utf-8 -*-
# HG/T 21629-2021 A4 法兰用U形管夹（1/2"~2"）（图 C.1-4）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="法兰用U形管夹（1/2~2）", TooltipLong="HG/T 21629-2021 A4 法兰用U形管夹（1/2~2） 图C.1-4", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="腿长", TooltipLong="U形螺栓直线段长度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="开档", TooltipLong="U形中心距/内宽")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="U形圆钢螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A4(s, D=42.4, H=65.0, B=56.4, d=10.0, ID=u"A4", **kw):
    D = float(D); H = float(H); B = float(B); d = float(d)
    if D < 10.0: D = 21.3
    if d < 6.0: d = 8.0
    if B < (D + d): B = D + d
    if H < (D / 2.0 + d * 3.0): H = D / 2.0 + d * 4.5
    R = B / 2.0; rod = d / 2.0
    o1 = TORUS(s, R1=R, R2=rod).rotateY(90.0)
    o_cut = BOX(s, L=(R + rod) * 3.0, W=(R + rod) * 2.2, H=d * 4.0).translate((0.0, 0.0, -(R + rod)))
    o1.subtractFrom(o_cut); o_cut.erase()
    fl_t = max(6.0, d * 0.65); fl_w = max(28.0, d * 2.8); fl_l = max(32.0, d * 3.2)
    z_fl = -(H * 0.68)
    for sy in (-1.0, 1.0):
        o_leg = CYLINDER(s, R=rod, H=H, O=0.0).translate((0.0, sy * R, -H))
        o_seat = BOX(s, L=fl_l, W=fl_t, H=fl_w).translate((0.0, sy * (R + fl_l * 0.28), z_fl))
        o_web = BOX(s, L=fl_t, W=H * 0.35, H=fl_w).translate((0.0, sy * (R + fl_t * 0.8), z_fl + H * 0.175))
        o_fb = CYLINDER(s, R=rod * 0.95, H=fl_t * 4.0, O=0.0).translate((0.0, sy * (R + fl_l * 0.45), z_fl - fl_t * 2.0))
        o_fn = CYLINDER(s, R=d * 0.85, H=d * 0.7, O=0.0).translate((0.0, sy * (R + fl_l * 0.45), z_fl + fl_t * 0.5))
        o_ln = CYLINDER(s, R=d * 0.85, H=d * 0.8, O=0.0).translate((0.0, sy * R, -H))
        for p in (o_leg, o_seat, o_web, o_fb, o_fn, o_ln):
            o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
