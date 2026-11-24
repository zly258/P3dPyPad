# -*- coding: utf-8 -*-
# HG/T 21629-2021 A13 90°弯头用吊板（图 C.1-13）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="90°弯头用吊板", TooltipLong="HG/T 21629-2021 A13 90°弯头用吊板 图C.1-13", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径或基准直径")
@param(H=LENGTH, TooltipShort="吊板高", TooltipLong="吊孔中心至底端/管壁高度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="吊板宽", TooltipLong="吊板/吊耳宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="吊板/耳板厚度")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="吊孔/销子直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A13(s, D=114.3, H=187.2, B=100.0, T=16.0, d=22.0, ID=u"A13", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 25.0: D = 60.3
    if T < 6.0: T = 10.0
    if B < 45.0: B = 85.0
    if d < 10.0: d = 18.0
    R1 = D / 2.0
    R_elb = D * 1.5
    if H < (R1 + d * 2.5): H = R1 + d * 3.8
    R_top = min(B * 0.36, max(d * 1.25, B * 0.3))
    plate_h = H + R1 * 0.55
    # 1. 不对称偏置立板毛坯与顶部圆弧耳头（左侧竖直齐平 Y = -R_top，右侧向外斜展至 Y = B - R_top）
    w_tot = R_top + B * 0.85
    yc_mid = (B * 0.85 - R_top) / 2.0
    o1 = BOX(s, L=w_tot, W=plate_h, H=T).translate((0.0, yc_mid, H - plate_h / 2.0))
    o_top = CYLINDER(s, R=R_top, H=T, O=0.0).rotateY(90.0).translate((-(T / 2.0), 0.0, H))
    o1.uniteWith(o_top); o_top.erase()
    # 2. 右上斜边裁切（形成上窄下宽单侧斜边）
    dx_r = B * 0.85 - R_top
    if dx_r > 2.0:
        ang_r = degrees(atan2(dx_r, plate_h * 0.72))
        o_rcut = BOX(s, L=B, W=plate_h * 1.5, H=T * 4.0).rotateX(ang_r).translate((0.0, R_top + dx_r * 0.5 + B * 0.46, H - plate_h * 0.32))
        o1.subtractFrom(o_rcut); o_rcut.erase()
    # 3. 底部用偏心 90° 弯头环体 TORUS 切除不对称斜弧底边
    o_elb = TORUS(s, R1=R_elb, R2=R1).rotateY(90.0).translate((0.0, R_elb * 0.42, -(R_elb * 0.88)))
    o1.subtractFrom(o_elb); o_elb.erase()
    # 4. 顶部吊孔切除
    o_hole = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateY(90.0).translate((-(T * 2.0), 0.0, H))
    o1.subtractFrom(o_hole); o_hole.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
