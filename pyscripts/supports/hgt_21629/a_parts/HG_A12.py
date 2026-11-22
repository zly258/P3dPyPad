# -*- coding: utf-8 -*-
# HG/T 21629-2021 A12 直管用吊板（图 C.1-12）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="直管用吊板", TooltipLong="HG/T 21629-2021 A12 直管用吊板 图C.1-12", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径或基准直径")
@param(H=LENGTH, TooltipShort="吊板高", TooltipLong="吊孔中心至底端/管壁高度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="吊板宽", TooltipLong="吊板/吊耳宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="吊板/耳板厚度")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="吊孔/销子直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A12(s, D=114.3, H=187.2, B=100.0, T=16.0, d=22.0, ID=u"A12", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 25.0: D = 60.3
    if T < 6.0: T = 10.0
    if B < 45.0: B = 85.0
    if d < 10.0: d = 18.0
    R1 = D / 2.0
    if H < (R1 + d * 2.2): H = R1 + d * 3.5
    R_top = min(B * 0.35, max(d * 1.25, B * 0.28))
    z_base = R1 * 0.35
    plate_h = H - z_base
    # 1. 梯形立板毛坯（宽 B，高 plate_h）+ 顶部圆弧头
    o1 = BOX(s, L=B, W=plate_h, H=T).translate((0.0, 0.0, z_base + plate_h / 2.0))
    o_top = CYLINDER(s, R=R_top, H=T, O=0.0).rotateY(90.0).translate((-(T / 2.0), 0.0, H))
    o1.uniteWith(o_top); o_top.erase()
    # 2. 左右两侧斜切刀切除上部多余角块，形成精准的上窄(2*R_top)下宽(B)梯形轮廓
    dx_taper = (B / 2.0) - R_top
    if dx_taper > 2.0:
        ang_t = degrees(atan2(dx_taper, plate_h))
        cut_l = sqrt(dx_taper * dx_taper + plate_h * plate_h) * 1.5
        for sy in (-1.0, 1.0):
            o_tcut = BOX(s, L=B, W=cut_l, H=T * 4.0).rotateX(sy * ang_t).translate((0.0, sy * (R_top + dx_taper / 2.0 + B * 0.48), z_base + plate_h / 2.0))
            o1.subtractFrom(o_tcut); o_tcut.erase()
    # 3. 底部减去直管外径圆柱（O=0.0），形成贴合直管外壁的圆弧马鞍口
    o_pipe = CYLINDER(s, R=R1, H=T * 4.0, O=0.0).rotateY(90.0).translate((-(T * 2.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()
    # 4. 顶部吊孔切除
    o_hole = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateY(90.0).translate((-(T * 2.0), 0.0, H))
    o1.subtractFrom(o_hole); o_hole.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
