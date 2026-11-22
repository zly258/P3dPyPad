# -*- coding: utf-8 -*-
# HG/T 21629-2021 S9 夹角为90°的等长或不等长双液压阻尼器组合架（图 C.17-9）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="夹角为90°的等长或不等长双液压阻尼", TooltipLong="HG/T 21629-2021 S9 夹角为90°的等长或不等长双液压阻尼器组合架 图C.17-9", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(L=LENGTH, TooltipShort="安装长", TooltipLong="两端铰接销轴中心间距", Ask4Dist=True)
@param(BODY_D=LENGTH, TooltipShort="缸筒径", TooltipLong="阻尼器缸筒外径")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="连接关节轴承销轴直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_S9(s, D=114.3, L=520.0, BODY_D=85.0, d=20.0, ID=u"S9", **kw):
    D = float(D); L = float(L); BODY_D = float(BODY_D); d = float(d)
    if D < 15.0: D = 88.9
    if BODY_D < 25.0: BODY_D = 60.0
    if d < 10.0: d = 20.0
    if L < 200.0: L = 500.0
    R1 = D / 2.0; bw = max(45.0, d * 2.8)
    o1 = CYLINDER(s, R=R1 + 8.0, H=bw, O=0.0).rotateY(90.0).translate((-(bw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=bw + 4.0, O=0.0).rotateY(90.0).translate((-(bw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    # 90°直角正交双杆：1根沿 -Z 竖直，1根绕 X 轴旋转 90° 沿 +Y 水平正交
    for ang in (0.0, 90.0):
        o_rod = CYLINDER(s, R=d * 0.48, H=L - R1, O=0.0).translate((0.0, 0.0, -L))
        o_cyl = CYLINDER(s, R=BODY_D / 2.0, H=L * 0.56, O=0.0).translate((0.0, 0.0, -(L * 0.75)))
        o_end = BOX(s, L=d * 2.6, W=d * 2.0, H=d * 1.6).translate((0.0, 0.0, -L))
        o_rod.uniteWith(o_cyl); o_cyl.erase()
        o_rod.uniteWith(o_end); o_end.erase()
        o_res = BOX(s, L=BODY_D * 0.65, W=L * 0.26, H=BODY_D * 0.55).translate((BODY_D * 0.55, 0.0, -(L * 0.58)))
        o_rod.uniteWith(o_res); o_res.erase()
        if ang > 0.1:
            o_rod.rotateX(ang)
        o1.uniteWith(o_rod); o_rod.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
