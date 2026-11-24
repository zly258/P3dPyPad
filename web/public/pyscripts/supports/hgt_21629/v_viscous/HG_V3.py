# -*- coding: utf-8 -*-
# HG/T 21629-2021 V3 立管用单粘滞阻尼器（图 C.20-3）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="立管用单粘滞阻尼器", TooltipLong="HG/T 21629-2021 V3 立管用单粘滞阻尼器 图C.20-3", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(L=LENGTH, TooltipShort="安装长", TooltipLong="两端铰接销轴中心间距", Ask4Dist=True)
@param(BODY_D=LENGTH, TooltipShort="缸筒径", TooltipLong="阻尼器缸筒外径")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="连接关节轴承销轴直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_V3(s, D=114.3, L=520.0, BODY_D=153.0, d=20.0, ID=u"V3", **kw):
    D = float(D); L = float(L); BODY_D = float(BODY_D); d = float(d)
    if D < 25.0: D = 114.3
    if BODY_D < 80.0: BODY_D = 180.0
    if d < 12.0: d = 24.0
    if L < 150.0: L = 320.0
    R1 = D / 2.0
    pipe_h = max(180.0, L * 0.85)
    # 1. 竖直立管沿 Z 轴（O=0.0）与上下双道立管抱箍
    o1 = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h * 0.45)))
    for z_c in (pipe_h * 0.25, 0.0):
        o_cl = CYLINDER(s, R=R1 + 10.0, H=d * 1.6, O=0.0).translate((0.0, 0.0, z_c))
        o1.uniteWith(o_cl); o_cl.erase()
    o_in = CYLINDER(s, R=max(8.0, R1 - 8.0), H=pipe_h + 6.0, O=0.0).translate((0.0, 0.0, -(pipe_h * 0.45 + 3.0)))
    o1.subtractFrom(o_in); o_in.erase()
    # 2. 向一侧（-Y 侧）伸出的悬臂牛腿托架 + 牛腿下方单个大直径粘滞阻尼锅筒
    yo = -(R1 + BODY_D * 0.65)
    o_arm = BOX(s, L=abs(yo), W=pipe_h * 0.42, H=d * 2.2).translate((0.0, yo / 2.0, pipe_h * 0.16))
    pot_h = L * 0.62
    o_pot = CYLINDER(s, R=BODY_D / 2.0, H=pot_h, O=0.0).translate((0.0, yo, -L))
    o_fl1 = CYLINDER(s, R=BODY_D * 0.58, H=14.0, O=0.0).translate((0.0, yo, -L))
    o_fl2 = CYLINDER(s, R=BODY_D * 0.56, H=12.0, O=0.0).translate((0.0, yo, -(L - pot_h)))
    o_pst = CYLINDER(s, R=d * 0.85, H=L - pot_h * 0.4, O=0.0).translate((0.0, yo, -(L - pot_h * 0.4)))
    for p in (o_arm, o_pot, o_fl1, o_fl2, o_pst):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
