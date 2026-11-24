# -*- coding: utf-8 -*-
# HG/T 21629-2021 V1 水平管用单粘滞阻尼器（图 C.20-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="水平管用单粘滞阻尼器", TooltipLong="HG/T 21629-2021 V1 水平管用单粘滞阻尼器 图C.20-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(L=LENGTH, TooltipShort="安装长", TooltipLong="两端铰接销轴中心间距", Ask4Dist=True)
@param(BODY_D=LENGTH, TooltipShort="缸筒径", TooltipLong="阻尼器缸筒外径")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="连接关节轴承销轴直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_V1(s, D=114.3, L=520.0, BODY_D=153.0, d=20.0, ID=u"V1", **kw):
    D = float(D); L = float(L); BODY_D = float(BODY_D); d = float(d)
    if D < 15.0: D = 15.0
    if BODY_D < 80.0: BODY_D = 180.0
    if d < 12.0: d = 24.0
    if L < 150.0: L = 320.0
    R1 = D / 2.0
    o1 = CYLINDER(s, R=R1 + 8.0, H=d * 3.5, O=0.0).rotateY(90.0).translate((-(d * 1.75), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=d * 3.5 + 4.0, O=0.0).rotateY(90.0).translate((-(d * 1.75 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    y_offs = (-(BODY_D * 0.68), (BODY_D * 0.68)) if False else (0.0,)
    pot_h = L * 0.58
    for yo in y_offs:
        o_pot = CYLINDER(s, R=BODY_D / 2.0, H=pot_h, O=0.0).translate((0.0, yo, -L))
        o_fl1 = CYLINDER(s, R=BODY_D * 0.58, H=14.0, O=0.0).translate((0.0, yo, -L))
        o_fl2 = CYLINDER(s, R=BODY_D * 0.56, H=12.0, O=0.0).translate((0.0, yo, -(L - pot_h)))
        o_pst = CYLINDER(s, R=d * 0.85, H=L - R1, O=0.0).translate((0.0, yo, -(L - pot_h * 0.5)))
        for p in (o_pot, o_fl1, o_fl2, o_pst):
            o1.uniteWith(p); p.erase()
    if len(y_offs) > 1:
        o_bar = BOX(s, L=BODY_D * 2.2, W=18.0, H=d * 3.2).translate((0.0, 0.0, -(R1 + 16.0)))
        o1.uniteWith(o_bar); o_bar.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
