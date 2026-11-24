# -*- coding: utf-8 -*-
# HG/T 21629-2021 X1 管夹型弹簧减振器（图 C.22-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="管夹型弹簧减振器", TooltipLong="HG/T 21629-2021 X1 管夹型弹簧减振器 图C.22-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="安装高", TooltipLong="管心至生根点/底面总高", Ask4Dist=True)
@param(CAN_D=LENGTH, TooltipShort="筒径", TooltipLong="弹簧筒/箱体外径或宽度")
@param(CAN_H=LENGTH, TooltipShort="筒高", TooltipLong="弹簧筒/箱体高度")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆/连接螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_X1(s, D=114.3, H=640.0, CAN_D=159.0, CAN_H=270.0, d=16.0, ID=u"X1", **kw):
    D = float(D); H = float(H); CAN_D = float(CAN_D); CAN_H = float(CAN_H); d = float(d)
    if D < 15.0: D = 15.0
    if d < 8.0: d = 12.0
    if CAN_D < 50.0: CAN_D = 90.0
    if CAN_H < 70.0: CAN_H = 160.0
    R1 = D / 2.0
    if H < (R1 + CAN_H + 40.0): H = R1 + CAN_H + 120.0
    wall = max(4.0, CAN_D * 0.05)
    R_can = CAN_D / 2.0
    # 单双向弹簧减振器（X1~X3, X5~X6）：空心弹簧外筒（O=0.0）+ 中部双向隔环 + 双行程观察窗 + 铰接耳环
    bw = max(36.0, d * 2.5)
    o1 = CYLINDER(s, R=R1 + 7.0, H=bw, O=0.0).rotateY(90.0).translate((-(bw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=bw + 4.0, O=0.0).rotateY(90.0).translate((-(bw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    z_can = R1 + (H - R1 - CAN_H) * 0.45
    o_rod = CYLINDER(s, R=d / 2.0, H=H - R1, O=0.0).translate((0.0, 0.0, R1))
    o_can = CYLINDER(s, R=R_can, H=CAN_H, O=0.0).translate((0.0, 0.0, z_can))
    o_cin = CYLINDER(s, R=R_can - wall, H=CAN_H - wall * 2.0, O=0.0).translate((0.0, 0.0, z_can + wall))
    o_can.subtractFrom(o_cin); o_cin.erase()
    o_slot = BOX(s, L=max(12.0, d * 0.75), W=CAN_H * 0.62, H=CAN_D * 1.3).translate((0.0, 0.0, z_can + CAN_H * 0.5))
    o_can.subtractFrom(o_slot); o_slot.erase()
    o_mid_ring = CYLINDER(s, R=R_can * 1.12, H=wall * 2.5, O=0.0).translate((0.0, 0.0, z_can + CAN_H * 0.5 - wall * 1.25))
    o_top_lug = BOX(s, L=d * 2.8, W=d * 2.2, H=d * 1.5).translate((0.0, 0.0, H - d * 1.1))
    for p in (o_rod, o_can, o_mid_ring, o_top_lug):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
