# -*- coding: utf-8 -*-
# HG/T 21629-2021 W3 保温/保冷管的碟簧减振架（1/2"~24"，无横向位移）（图 C.21-3）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="保温/保冷管的碟簧减振架（1/2~", TooltipLong="HG/T 21629-2021 W3 保温/保冷管的碟簧减振架（1/2~24，无横向位移） 图C.21-3", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="安装高", TooltipLong="管心至生根点/底面总高", Ask4Dist=True)
@param(CAN_D=LENGTH, TooltipShort="筒径", TooltipLong="弹簧筒/箱体外径或宽度")
@param(CAN_H=LENGTH, TooltipShort="筒高", TooltipLong="弹簧筒/箱体高度")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆/连接螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_W3(s, D=114.3, H=453.1, CAN_D=139.3, CAN_H=215.9, d=12.0, ID=u"W3", **kw):
    D = float(D); H = float(H); CAN_D = float(CAN_D); CAN_H = float(CAN_H); d = float(d)
    if D < 15.0: D = 15.0
    if d < 8.0: d = 12.0
    if CAN_D < 50.0: CAN_D = 90.0
    if CAN_H < 70.0: CAN_H = 160.0
    R1 = D / 2.0
    if H < (R1 + CAN_H + 40.0): H = R1 + CAN_H + 120.0
    wall = max(4.0, CAN_D * 0.05)
    R_can = CAN_D / 2.0
    # 1. 管道抱箍与承重鞍座（O=0.0）
    bw = max(40.0, d * 3.0)
    o1 = CYLINDER(s, R=R1 + 8.0, H=bw, O=0.0).rotateY(90.0).translate((-(bw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=bw + 4.0, O=0.0).rotateY(90.0).translate((-(bw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    span_y = D + CAN_D * 1.35
    o_cross = BOX(s, L=span_y + CAN_D, W=max(12.0, d * 0.8), H=bw).translate((0.0, 0.0, -(R1 + 10.0)))
    o1.uniteWith(o_cross); o_cross.erase()
    # 2. 左右两侧双螺杆与叠合碟簧柱（用多层交错圆台 CONE 呈现真实碟形弹簧组）
    disc_r = CAN_D * 0.48
    z_disc0 = -(R1 + CAN_H * 0.75)
    for sy in (-1.0, 1.0):
        yc = sy * (span_y / 2.0)
        o_rod = CYLINDER(s, R=d / 2.0, H=CAN_H * 1.35, O=0.0).translate((0.0, yc, z_disc0 - d * 2.0))
        o1.uniteWith(o_rod); o_rod.erase()
        n_disc = 6
        dh = (CAN_H * 0.65) / float(n_disc)
        for i in range(n_disc):
            zd = z_disc0 + i * dh
            r_bot = disc_r if (i % 2 == 0) else disc_r * 0.68
            r_top = disc_r * 0.68 if (i % 2 == 0) else disc_r
            o_d = CONE(s, R1=r_bot, R2=r_top, H=dh, E=0.0).translate((0.0, yc, zd))
            o1.uniteWith(o_d); o_d.erase()
        o_p1 = CYLINDER(s, R=disc_r * 1.1, H=d * 0.6, O=0.0).translate((0.0, yc, z_disc0 - d * 0.6))
        o_p2 = CYLINDER(s, R=disc_r * 1.1, H=d * 0.6, O=0.0).translate((0.0, yc, z_disc0 + CAN_H * 0.65))
        o1.uniteWith(o_p1); o_p1.erase()
        o1.uniteWith(o_p2); o_p2.erase()
    o_ins = BOX(s, L=D * 0.85, W=R1 * 0.6, H=bw * 1.5).translate((0.0, 0.0, -(R1 * 0.8)))
    o1.uniteWith(o_ins); o_ins.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
