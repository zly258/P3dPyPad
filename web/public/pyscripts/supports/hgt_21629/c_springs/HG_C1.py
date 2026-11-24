# -*- coding: utf-8 -*-
# HG/T 21629-2021 C1 上螺纹连接式可变弹簧吊架（图 C.3-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="上螺纹连接式可变弹簧吊架", TooltipLong="HG/T 21629-2021 C1 上螺纹连接式可变弹簧吊架 图C.3-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="安装高", TooltipLong="管心至生根点/底面总高", Ask4Dist=True)
@param(CAN_D=LENGTH, TooltipShort="筒径", TooltipLong="弹簧筒/箱体外径或宽度")
@param(CAN_H=LENGTH, TooltipShort="筒高", TooltipLong="弹簧筒/箱体高度")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆/连接螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_C1(s, D=114.3, H=640.0, CAN_D=159.0, CAN_H=270.0, d=16.0, ID=u"C1", **kw):
    D = float(D); H = float(H); CAN_D = float(CAN_D); CAN_H = float(CAN_H); d = float(d)
    if D < 15.0: D = 15.0
    if d < 8.0: d = 12.0
    if CAN_D < 50.0: CAN_D = 90.0
    if CAN_H < 70.0: CAN_H = 160.0
    R1 = D / 2.0
    if H < (R1 + CAN_H + 40.0): H = R1 + CAN_H + 120.0
    wall = max(4.0, CAN_D * 0.05)
    R_can = CAN_D / 2.0
    # 1. 底部管夹抱箍（O=0.0 外圆减内圆）
    bw = max(30.0, d * 2.2)
    o1 = CYLINDER(s, R=R1 + 6.0, H=bw, O=0.0).rotateY(90.0).translate((-(bw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=bw + 4.0, O=0.0).rotateY(90.0).translate((-(bw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_cut = BOX(s, L=(R1 + 8.0) * 2.6, W=(R1 + 8.0) * 1.5, H=bw + 8.0).translate((0.0, 0.0, -(R1 + 8.0) * 0.75))
    o1.subtractFrom(o_cut); o_cut.erase()
    # 2. 弹簧保护圆筒（O=0.0 外圆减内圆 + 侧面载荷位移刻度窗 + 上下法兰端盖）
    z_can = R1 + (H - R1 - CAN_H) * (0.55 if True else 0.38)
    o_can = CYLINDER(s, R=R_can, H=CAN_H, O=0.0).translate((0.0, 0.0, z_can))
    o_cin = CYLINDER(s, R=R_can - wall, H=CAN_H - wall * 2.0, O=0.0).translate((0.0, 0.0, z_can + wall))
    o_can.subtractFrom(o_cin); o_cin.erase()
    o_slot = BOX(s, L=max(12.0, d * 0.8), W=CAN_H * 0.58, H=CAN_D * 1.3).translate((0.0, 0.0, z_can + CAN_H * 0.5))
    o_can.subtractFrom(o_slot); o_slot.erase()
    o_cap1 = CYLINDER(s, R=R_can * 1.08, H=wall * 1.8, O=0.0).translate((0.0, 0.0, z_can))
    o_cap2 = CYLINDER(s, R=R_can * 1.08, H=wall * 1.8, O=0.0).translate((0.0, 0.0, z_can + CAN_H - wall * 1.8))
    o_can.uniteWith(o_cap1); o_cap1.erase()
    o_can.uniteWith(o_cap2); o_cap2.erase()
    # 3. 贯穿拉杆与顶部连接结构
    o_rod = CYLINDER(s, R=d / 2.0, H=H - R1, O=0.0).translate((0.0, 0.0, R1))
    o1.uniteWith(o_can); o_can.erase()
    o1.uniteWith(o_rod); o_rod.erase()
    o_boss = CYLINDER(s, R=d * 1.25, H=d * 1.8, O=0.0).translate((0.0, 0.0, z_can + CAN_H))
    o1.uniteWith(o_boss); o_boss.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
