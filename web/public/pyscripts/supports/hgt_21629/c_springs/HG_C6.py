# -*- coding: utf-8 -*-
# HG/T 21629-2021 C6 可变弹簧支架（图 C.3-3）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="可变弹簧支架", TooltipLong="HG/T 21629-2021 C6 可变弹簧支架 图C.3-3", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="安装高", TooltipLong="管心至生根点/底面总高", Ask4Dist=True)
@param(CAN_D=LENGTH, TooltipShort="筒径", TooltipLong="弹簧筒/箱体外径或宽度")
@param(CAN_H=LENGTH, TooltipShort="筒高", TooltipLong="弹簧筒/箱体高度")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆/连接螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_C6(s, D=114.3, H=640.0, CAN_D=159.0, CAN_H=270.0, d=16.0, ID=u"C6", **kw):
    D = float(D); H = float(H); CAN_D = float(CAN_D); CAN_H = float(CAN_H); d = float(d)
    if D < 15.0: D = 15.0
    if d < 8.0: d = 12.0
    if CAN_D < 50.0: CAN_D = 90.0
    if CAN_H < 70.0: CAN_H = 160.0
    R1 = D / 2.0
    if H < (R1 + CAN_H + 40.0): H = R1 + CAN_H + 120.0
    wall = max(4.0, CAN_D * 0.05)
    R_can = CAN_D / 2.0
    # 1. 底部方形安装底座板（Z = -H）
    base_w = CAN_D * 1.45
    base_t = max(10.0, d * 0.7)
    o1 = BOX(s, L=base_w, W=base_t, H=base_w).translate((0.0, 0.0, -(H - base_t / 2.0)))
    # 2. 立式可变弹簧筒体（O=0.0 外筒减内筒 + 侧壁行程刻度槽）
    z_can_bot = -(H - base_t)
    o_can = CYLINDER(s, R=R_can, H=CAN_H, O=0.0).translate((0.0, 0.0, z_can_bot))
    o_can_in = CYLINDER(s, R=R_can - wall, H=CAN_H - wall * 2.0, O=0.0).translate((0.0, 0.0, z_can_bot + wall))
    o_can.subtractFrom(o_can_in); o_can_in.erase()
    o_slot = BOX(s, L=max(14.0, d * 0.9), W=CAN_H * 0.58, H=CAN_D * 1.3).translate((0.0, 0.0, z_can_bot + CAN_H * 0.5))
    o_can.subtractFrom(o_slot); o_slot.erase()
    o_cap = CYLINDER(s, R=R_can * 1.12, H=base_t * 0.85, O=0.0).translate((0.0, 0.0, z_can_bot + CAN_H - base_t * 0.85))
    o_can.uniteWith(o_cap); o_cap.erase()
    o1.uniteWith(o_can); o_can.erase()
    # 3. 顶部升降柱与圆形承重荷载盘（Load Flange）+ 管底鞍座
    col_h = max(20.0, H - R1 - base_t - CAN_H)
    o_col = CYLINDER(s, R=R_can * 0.42, H=col_h + 15.0, O=0.0).translate((0.0, 0.0, -(R1 + col_h + 10.0)))
    o_platen = CYLINDER(s, R=R_can * 0.88, H=base_t, O=0.0).translate((0.0, 0.0, -(R1 + base_t * 1.2)))
    o_sad = CYLINDER(s, R=R1 + 8.0, H=CAN_D * 0.8, O=0.0).rotateY(90.0).translate((-(CAN_D * 0.4), 0.0, 0.0))
    o_sad_in = CYLINDER(s, R=R1, H=CAN_D * 0.8 + 4.0, O=0.0).rotateY(90.0).translate((-(CAN_D * 0.4 + 2.0), 0.0, 0.0))
    o_sad.subtractFrom(o_sad_in); o_sad_in.erase()
    o_sad_cut = BOX(s, L=(R1 + 10.0) * 2.5, W=(R1 + 10.0) * 1.5, H=CAN_D).translate((0.0, 0.0, (R1 + 10.0) * 0.75))
    o_sad.subtractFrom(o_sad_cut); o_sad_cut.erase()
    for p in (o_col, o_platen, o_sad):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
