# -*- coding: utf-8 -*-
# HG/T 21629-2021 R8 夹角可变的等长双刚性拉撑杆组合架（图 C.16-8）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="夹角可变的等长双刚性拉撑杆组合架", TooltipLong="HG/T 21629-2021 R8 夹角可变的等长双刚性拉撑杆组合架 图C.16-8", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(L=LENGTH, TooltipShort="安装长", TooltipLong="两端铰接销轴中心间距", Ask4Dist=True)
@param(BODY_D=LENGTH, TooltipShort="拉杆外径", TooltipLong="刚性拉撑杆主管外径")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="连接销轴直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_R8(s, D=114.3, L=520.0, BODY_D=85.0, d=20.0, ID=u"R8", **kw):
    D = float(D); L = float(L); BODY_D = float(BODY_D); d = float(d)
    if D < 15.0: D = 88.9
    if BODY_D < 25.0: BODY_D = 60.0
    if d < 10.0: d = 20.0
    if L < 200.0: L = 500.0
    R1 = D / 2.0; bw = max(45.0, d * 2.8)
    o1 = CYLINDER(s, R=R1 + 8.0, H=bw, O=0.0).rotateY(90.0).translate((-(bw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=bw + 4.0, O=0.0).rotateY(90.0).translate((-(bw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    for sy in (-1.0, 1.0):
        o_rod = CYLINDER(s, R=d * 0.48, H=L - R1, O=0.0).translate((0.0, 0.0, -L))
        o_cyl = CYLINDER(s, R=BODY_D / 2.0, H=L * 0.56, O=0.0).translate((0.0, 0.0, -(L * 0.75)))
        o_end = BOX(s, L=d * 2.6, W=d * 2.0, H=d * 1.6).translate((0.0, 0.0, -L))
        o_rod.uniteWith(o_cyl); o_cyl.erase()
        o_rod.uniteWith(o_end); o_end.erase()
        o_nut = CYLINDER(s, R=BODY_D * 0.62, H=d * 1.2, O=0.0).translate((0.0, 0.0, -(L * 0.22)))
        o_rod.uniteWith(o_nut); o_nut.erase()
        o_rod.rotateX(sy * 35.0)
        o1.uniteWith(o_rod); o_rod.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
