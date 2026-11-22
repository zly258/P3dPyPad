# -*- coding: utf-8 -*-
# HG/T 21629-2021 C8~C11 力矩平衡式恒力吊架（图 C.3-5）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="力矩平衡式恒力吊架", TooltipLong="HG/T 21629-2021 C8~C11 力矩平衡式恒力吊架 图C.3-5", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="安装高", TooltipLong="管心至生根点/底面总高", Ask4Dist=True)
@param(CAN_D=LENGTH, TooltipShort="筒径", TooltipLong="弹簧筒/箱体外径或宽度")
@param(CAN_H=LENGTH, TooltipShort="筒高", TooltipLong="弹簧筒/箱体高度")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆/连接螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_C8(s, D=114.3, H=640.0, CAN_D=159.0, CAN_H=270.0, d=16.0, ID=u"C8", **kw):
    D = float(D); H = float(H); CAN_D = float(CAN_D); CAN_H = float(CAN_H); d = float(d)
    if D < 15.0: D = 60.3
    if d < 8.0: d = 14.0
    if CAN_D < 60.0: CAN_D = 120.0
    if CAN_H < 90.0: CAN_H = 200.0
    R1 = D / 2.0; R_can = CAN_D / 2.0; wall = max(4.0, CAN_D * 0.05)
    if H < (R1 + CAN_H + 80.0): H = R1 + CAN_H + 160.0
    bw = max(35.0, d * 2.5)
    # 1. 下部管道抱箍与主吊杆（沿 Z 轴位于 Y = 0）
    o1 = CYLINDER(s, R=R1 + 6.0, H=bw, O=0.0).rotateY(90.0).translate((-(bw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=bw + 4.0, O=0.0).rotateY(90.0).translate((-(bw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_rod = CYLINDER(s, R=d / 2.0, H=H - R1, O=0.0).translate((0.0, 0.0, R1))
    o1.uniteWith(o_rod); o_rod.erase()
    # 2. 上部水平力矩平衡摇臂壳体（从 Y = 0 向 Y = -CAN_D*1.15 悬挑）与偏置立式弹簧筒
    z_top_arm = H - CAN_H * 0.28
    arm_len = CAN_D * 1.25
    o_arm = BOX(s, L=arm_len, W=CAN_H * 0.36, H=CAN_D * 0.58).translate((0.0, -(arm_len * 0.35), z_top_arm))
    o_pivot = CYLINDER(s, R=d * 1.1, H=CAN_D * 0.72, O=0.0).rotateY(90.0).translate((-(CAN_D * 0.36), 0.0, z_top_arm))
    z_can = z_top_arm - CAN_H * 0.85
    o_can = CYLINDER(s, R=R_can * 0.88, H=CAN_H * 0.82, O=0.0).translate((0.0, -(arm_len * 0.72), z_can))
    o_cin = CYLINDER(s, R=R_can * 0.88 - wall, H=CAN_H * 0.82 - wall * 2.0, O=0.0).translate((0.0, -(arm_len * 0.72), z_can + wall))
    o_can.subtractFrom(o_cin); o_cin.erase()
    o_top_lug = BOX(s, L=d * 3.0, W=d * 2.4, H=d * 2.0).translate((0.0, 0.0, H - d * 1.2))
    for p in (o_arm, o_pivot, o_can, o_top_lug):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
