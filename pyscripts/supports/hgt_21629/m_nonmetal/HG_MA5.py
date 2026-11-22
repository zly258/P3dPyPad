# -*- coding: utf-8 -*-
# HG/T 21629-2021 MA5 法兰用U形管夹（1/2"~2"，-20°℃~120℃，非金属管）（图 C.12-5）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="法兰用U形管夹（1/2~2，-2", TooltipLong="HG/T 21629-2021 MA5 法兰用U形管夹（1/2~2，-20°℃~120℃，非金属管） 图C.12-5", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="腿长", TooltipLong="U形螺栓直线段长度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="开档", TooltipLong="U形中心距/内宽")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="U形圆钢螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_MA5(s, D=42.4, H=65.0, B=56.4, d=10.0, ID=u"MA5", **kw):
    D = float(D); H = float(H); B = float(B); d = float(d)
    if D < 15.0: D = 33.7
    if d < 6.0: d = 8.0
    if B < (D + d * 1.5): B = D + d * 2.0
    if H < (D / 2.0 + d * 3.0): H = D / 2.0 + d * 4.5
    R = B / 2.0; rod = d / 2.0; slv_r = rod * 1.45
    # 1. U形圆钢与顶部非金属保护套管（TORUS 双层环）
    o1 = TORUS(s, R1=R, R2=slv_r).rotateY(90.0)
    o_cut = BOX(s, L=(R + slv_r) * 3.0, W=(R + slv_r) * 2.2, H=slv_r * 4.0).translate((0.0, 0.0, -(R + slv_r)))
    o1.subtractFrom(o_cut); o_cut.erase()
    for sy in (-1.0, 1.0):
        o_leg = CYLINDER(s, R=rod, H=H, O=0.0).translate((0.0, sy * R, -H))
        o_slv = CYLINDER(s, R=slv_r, H=H * 0.55, O=0.0).translate((0.0, sy * R, -(H * 0.55)))
        o_nut = CYLINDER(s, R=d * 0.88, H=d * 0.8, O=0.0).translate((0.0, sy * R, -H))
        for p in (o_leg, o_slv, o_nut):
            o1.uniteWith(p); p.erase()
    # 2. 通长法兰安装扁钢底座 + 侧向法兰耳板与橡胶缓冲垫
    z_fl = -(H * 0.65)
    fl_w = max(36.0, d * 3.6); fl_t = max(6.0, d * 0.65)
    o_bar = BOX(s, L=B + d * 5.5, W=fl_t * 1.8, H=fl_w).translate((0.0, 0.0, z_fl))
    o_ear = BOX(s, L=B * 0.7, W=H * 0.42, H=fl_t).translate((fl_w * 0.5, 0.0, z_fl + H * 0.21))
    o1.uniteWith(o_bar); o_bar.erase()
    o1.uniteWith(o_ear); o_ear.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
