# -*- coding: utf-8 -*-
# HG/T 21629-2021 S1 管夹型液压阻尼器（图 C.17-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="管夹型液压阻尼器", TooltipLong="HG/T 21629-2021 S1 管夹型液压阻尼器 图C.17-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(L=LENGTH, TooltipShort="安装长", TooltipLong="两端铰接销轴中心间距", Ask4Dist=True)
@param(BODY_D=LENGTH, TooltipShort="缸筒径", TooltipLong="阻尼器缸筒外径")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="连接关节轴承销轴直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_S1(s, D=114.3, L=520.0, BODY_D=85.0, d=20.0, ID=u"S1", **kw):
    D = float(D); L = float(L); BODY_D = float(BODY_D); d = float(d)
    if D < 15.0: D = 15.0
    if BODY_D < 20.0: BODY_D = 50.0
    if d < 10.0: d = 16.0
    if L < 150.0: L = 450.0
    R1 = D / 2.0
    bw = max(36.0, d * 2.4)
    o1 = CYLINDER(s, R=R1 + 7.0, H=bw, O=0.0).rotateY(90.0).translate((-(bw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=bw + 4.0, O=0.0).rotateY(90.0).translate((-(bw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    cyl_h = L * (0.55 if True else 0.72)
    o_body = CYLINDER(s, R=BODY_D / 2.0, H=cyl_h, O=0.0).translate((0.0, 0.0, -(L * 0.82)))
    o_rod = CYLINDER(s, R=d * 0.48, H=L - R1, O=0.0).translate((0.0, 0.0, -L))
    o_base_clev = BOX(s, L=d * 3.0, W=d * 2.2, H=d * 1.8).translate((0.0, 0.0, -L))
    o1.uniteWith(o_body); o_body.erase()
    o1.uniteWith(o_rod); o_rod.erase()
    o1.uniteWith(o_base_clev); o_base_clev.erase()
    o_res = BOX(s, L=BODY_D * 0.65, W=cyl_h * 0.45, H=BODY_D * 0.55).translate((BODY_D * 0.55, 0.0, -(L * 0.62)))
    o1.uniteWith(o_res); o_res.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
