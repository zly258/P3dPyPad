# -*- coding: utf-8 -*-
# HG/T 21629-2021 C17 主辅弹簧式双簧并联恒力吊架（图 C.3-9）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="主辅弹簧式双簧并联恒力吊架", TooltipLong="HG/T 21629-2021 C17 主辅弹簧式双簧并联恒力吊架 图C.3-9", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="安装高", TooltipLong="管心至生根点/底面总高", Ask4Dist=True)
@param(CAN_D=LENGTH, TooltipShort="筒径", TooltipLong="弹簧筒/箱体外径或宽度")
@param(CAN_H=LENGTH, TooltipShort="筒高", TooltipLong="弹簧筒/箱体高度")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆/连接螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_C17(s, D=114.3, H=640.0, CAN_D=159.0, CAN_H=270.0, d=16.0, ID=u"C17", **kw):
    D = float(D); H = float(H); CAN_D = float(CAN_D); CAN_H = float(CAN_H); d = float(d)
    if D < 15.0: D = 15.0
    if d < 8.0: d = 12.0
    if CAN_D < 50.0: CAN_D = 90.0
    if CAN_H < 70.0: CAN_H = 160.0
    R1 = D / 2.0
    if H < (R1 + CAN_H + 40.0): H = R1 + CAN_H + 120.0
    wall = max(4.0, CAN_D * 0.05)
    R_can = CAN_D / 2.0
    # 1. 管道下方槽钢横担梁与管底鞍块
    span_y = max(D + CAN_D * 1.5, CAN_D * 2.4)
    beam_h = max(45.0, d * 3.0)
    z_beam = -(R1 + beam_h / 2.0 + 8.0)
    o1 = BOX(s, L=span_y + CAN_D * 0.8, W=beam_h, H=beam_h * 0.85).translate((0.0, 0.0, z_beam))
    o_sad = CYLINDER(s, R=R1 + 8.0, H=beam_h * 0.85, O=0.0).rotateY(90.0).translate((-(beam_h * 0.425), 0.0, 0.0))
    o_sad_i = CYLINDER(s, R=R1, H=beam_h * 0.85 + 4.0, O=0.0).rotateY(90.0).translate((-(beam_h * 0.425 + 2.0), 0.0, 0.0))
    o_sad.subtractFrom(o_sad_i); o_sad_i.erase()
    o1.uniteWith(o_sad); o_sad.erase()
    # 2. 左右对称双吊杆与双弹簧筒并联（Y = ±span_y/2）
    z_can = H - CAN_H - d * 2.5
    for sy in (-1.0, 1.0):
        yc = sy * (span_y / 2.0)
        o_rod = CYLINDER(s, R=d / 2.0, H=H - z_beam + d, O=0.0).translate((0.0, yc, z_beam - d * 0.5))
        o_can = CYLINDER(s, R=R_can, H=CAN_H, O=0.0).translate((0.0, yc, z_can))
        o_cin = CYLINDER(s, R=R_can - wall, H=CAN_H - wall * 2.0, O=0.0).translate((0.0, yc, z_can + wall))
        o_can.subtractFrom(o_cin); o_cin.erase()
        o_slot = BOX(s, L=max(12.0, d * 0.8), W=CAN_H * 0.55, H=CAN_D * 1.3).translate((0.0, yc, z_can + CAN_H * 0.5))
        o_can.subtractFrom(o_slot); o_slot.erase()
        o_aux = CYLINDER(s, R=R_can * 0.58, H=CAN_H * 0.65, O=0.0).translate((R_can * 0.85, yc, z_can + CAN_H * 0.2))
        o_can.uniteWith(o_aux); o_aux.erase()
        o1.uniteWith(o_rod); o_rod.erase()
        o1.uniteWith(o_can); o_can.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
