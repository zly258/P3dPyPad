# -*- coding: utf-8 -*-
# HG/T 21629-2021 X8 夹角可变的等长双弹簧减振器组合架（图 C.22-8）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="夹角可变的等长双弹簧减振器组合架", TooltipLong="HG/T 21629-2021 X8 夹角可变的等长双弹簧减振器组合架 图C.22-8", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="安装高", TooltipLong="管心至生根点/底面总高", Ask4Dist=True)
@param(CAN_D=LENGTH, TooltipShort="筒径", TooltipLong="弹簧筒/箱体外径或宽度")
@param(CAN_H=LENGTH, TooltipShort="筒高", TooltipLong="弹簧筒/箱体高度")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆/连接螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_X8(s, D=114.3, H=640.0, CAN_D=159.0, CAN_H=270.0, d=16.0, ID=u"X8", **kw):
    D = float(D); H = float(H); CAN_D = float(CAN_D); CAN_H = float(CAN_H); d = float(d)
    if D < 15.0: D = 15.0
    if d < 8.0: d = 12.0
    if CAN_D < 50.0: CAN_D = 90.0
    if CAN_H < 70.0: CAN_H = 160.0
    R1 = D / 2.0
    if H < (R1 + CAN_H + 40.0): H = R1 + CAN_H + 120.0
    wall = max(4.0, CAN_D * 0.05)
    R_can = CAN_D / 2.0
    # V形/90°正交双弹簧减振器组合架（X8~X11）
    bw = max(40.0, d * 2.8)
    o1 = CYLINDER(s, R=R1 + 8.0, H=bw, O=0.0).rotateY(90.0).translate((-(bw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=bw + 4.0, O=0.0).rotateY(90.0).translate((-(bw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    for sy in (-1.0, 1.0):
        ang = sy * 28.0
        o_arm = CYLINDER(s, R=d / 2.0, H=H - R1, O=0.0).translate((0.0, 0.0, R1))
        o_can = CYLINDER(s, R=R_can * 0.78, H=CAN_H * 0.85, O=0.0).translate((0.0, 0.0, R1 + (H - R1 - CAN_H) * 0.45))
        o_cin = CYLINDER(s, R=R_can * 0.78 - wall, H=CAN_H * 0.85 - wall * 2.0, O=0.0).translate((0.0, 0.0, R1 + (H - R1 - CAN_H) * 0.45 + wall))
        o_can.subtractFrom(o_cin); o_cin.erase()
        o_slot = BOX(s, L=max(10.0, d * 0.7), W=CAN_H * 0.5, H=CAN_D * 1.2).translate((0.0, 0.0, R1 + (H - R1 - CAN_H) * 0.45 + CAN_H * 0.42))
        o_can.subtractFrom(o_slot); o_slot.erase()
        o_clev = BOX(s, L=d * 2.6, W=d * 2.0, H=d * 1.5).translate((0.0, 0.0, H - d))
        o_arm.uniteWith(o_can); o_can.erase()
        o_arm.uniteWith(o_clev); o_clev.erase()
        o_arm.rotateX(ang)
        o1.uniteWith(o_arm); o_arm.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
