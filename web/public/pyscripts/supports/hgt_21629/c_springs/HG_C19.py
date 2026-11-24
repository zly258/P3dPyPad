# -*- coding: utf-8 -*-
# HG/T 21629-2021 C19 双簧对称式恒力支架（图 C.3-11）
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="双簧对称式恒力支架", TooltipLong="HG/T 21629-2021 C19 双簧对称式恒力支架 图C.3-11", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="安装高", TooltipLong="管心至生根点/底面总高", Ask4Dist=True)
@param(CAN_D=LENGTH, TooltipShort="筒径", TooltipLong="弹簧筒/箱体外径或宽度")
@param(CAN_H=LENGTH, TooltipShort="筒高", TooltipLong="弹簧筒/箱体高度")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆/连接螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_C19(s, D=114.3, H=640.0, CAN_D=159.0, CAN_H=270.0, d=16.0, ID=u"C19", **kw):
    D = float(D); H = float(H); CAN_D = float(CAN_D); CAN_H = float(CAN_H); d = float(d)
    if D < 15.0: D = 15.0
    if d < 8.0: d = 12.0
    if CAN_D < 50.0: CAN_D = 90.0
    if CAN_H < 70.0: CAN_H = 160.0
    R1 = D / 2.0
    if H < (R1 + CAN_H + 80.0): H = R1 + CAN_H + 120.0
    R_can = CAN_D / 2.0
    base_w = CAN_D * 1.75
    base_t = max(12.0, d * 0.8)
    # 底部底座板
    o1 = BOX(s, L=base_w, W=base_t, H=base_w * 0.85).translate((0.0, 0.0, -(H - base_t / 2.0)))
    z_box = -(H - base_t)
    # 中部箱体与对称双弹簧筒
    o_frame = BOX(s, L=CAN_D * 1.15, W=CAN_H * 0.9, H=CAN_D * 0.75).translate((0.0, 0.0, z_box + CAN_H * 0.45))
    o1.uniteWith(o_frame); o_frame.erase()
    for sy in (-1.0, 1.0):
        o_sc = CYLINDER(s, R=R_can * 0.65, H=CAN_H * 0.8, O=0.0).rotateX(90.0 * sy).translate((0.0, sy * (CAN_D * 0.4), z_box + CAN_H * 0.45))
        o1.uniteWith(o_sc); o_sc.erase()
    # 竖向承重立柱导向柱
    col_h = (H - base_t - CAN_H * 0.9) - R1
    o_col = CYLINDER(s, R=max(18.0, d * 1.2), H=col_h, O=0.0).translate((0.0, 0.0, z_box + CAN_H * 0.9))
    o1.uniteWith(o_col); o_col.erase()
    # 顶部活动承重圆盘托板
    o_plat = CYLINDER(s, R=R_can * 0.9, H=base_t, O=0.0).translate((0.0, 0.0, -(R1 + base_t)))
    # 顶部弧形鞍座
    o_sad = CYLINDER(s, R=R1 + 8.0, H=CAN_D * 0.8, O=0.0).rotateY(90.0).translate((-(CAN_D * 0.4), 0.0, 0.0))
    o_sad_i = CYLINDER(s, R=R1, H=CAN_D * 0.8 + 4.0, O=0.0).rotateY(90.0).translate((-(CAN_D * 0.4 + 2.0), 0.0, 0.0))
    o_sad.subtractFrom(o_sad_i); o_sad_i.erase()
    o1.uniteWith(o_plat); o_plat.erase()
    o1.uniteWith(o_sad); o_sad.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
