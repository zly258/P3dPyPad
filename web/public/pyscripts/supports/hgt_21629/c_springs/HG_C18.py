# -*- coding: utf-8 -*-
# HG/T 21629-2021 C18 双簧对称式恒力吊架（图 C.3-10）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="双簧对称式恒力吊架", TooltipLong="HG/T 21629-2021 C18 双簧对称式恒力吊架 图C.3-10", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="安装高", TooltipLong="管心至生根点/底面总高", Ask4Dist=True)
@param(CAN_D=LENGTH, TooltipShort="筒径", TooltipLong="弹簧筒/箱体外径或宽度")
@param(CAN_H=LENGTH, TooltipShort="筒高", TooltipLong="弹簧筒/箱体高度")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆/连接螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_C18(s, D=114.3, H=640.0, CAN_D=159.0, CAN_H=270.0, d=16.0, ID=u"C18", **kw):
    D = float(D); H = float(H); CAN_D = float(CAN_D); CAN_H = float(CAN_H); d = float(d)
    if D < 15.0: D = 15.0
    if d < 8.0: d = 12.0
    if CAN_D < 50.0: CAN_D = 90.0
    if CAN_H < 70.0: CAN_H = 160.0
    R1 = D / 2.0
    if H < (R1 + CAN_H + 40.0): H = R1 + CAN_H + 120.0
    wall = max(4.0, CAN_D * 0.05)
    R_can = CAN_D / 2.0
    # 恒力弹簧吊架（C8 力矩平衡 / C12 主辅弹簧 / C14 多簧并联 / C18 双簧对称）
    z_box = R1 + (H - R1 - CAN_H) * 0.45
    bw = max(32.0, d * 2.5)
    o1 = CYLINDER(s, R=R1 + 6.0, H=bw, O=0.0).rotateY(90.0).translate((-(bw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=bw + 4.0, O=0.0).rotateY(90.0).translate((-(bw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_rod = CYLINDER(s, R=d / 2.0, H=H - R1, O=0.0).translate((0.0, 0.0, R1))
    o1.uniteWith(o_rod); o_rod.erase()
    o_cam = BOX(s, L=CAN_D * 0.9, W=CAN_H * 0.65, H=CAN_D * 0.65).translate((0.0, 0.0, z_box + CAN_H * 0.35))
    o1.uniteWith(o_cam); o_cam.erase()
    for sy in (-1.0, 1.0):
        o_sc = CYLINDER(s, R=R_can * 0.68, H=CAN_H * 0.78, O=0.0).rotateX(-90.0 * sy).translate((0.0, sy * (CAN_D * 0.35), z_box + CAN_H * 0.35))
        o_sci = CYLINDER(s, R=R_can * 0.68 - wall, H=CAN_H * 0.78 - wall * 2.0, O=0.0).rotateX(-90.0 * sy).translate((0.0, sy * (CAN_D * 0.35 + wall), z_box + CAN_H * 0.35))
        o_sc.subtractFrom(o_sci); o_sci.erase()
        o1.uniteWith(o_sc); o_sc.erase()
    o_top_lug = BOX(s, L=d * 3.2, W=d * 2.2, H=d * 1.6).translate((0.0, 0.0, H - d * 1.1))
    o1.uniteWith(o_top_lug); o_top_lug.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
