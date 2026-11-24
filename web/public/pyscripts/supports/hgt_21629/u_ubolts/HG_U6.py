# -*- coding: utf-8 -*-
# HG/T 21629-2021 U6 法兰用U形管夹（1/2"~2"，-20℃~300℃）（图 C.19-6）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="法兰用U形管夹（1/2~2，-2", TooltipLong="HG/T 21629-2021 U6 法兰用U形管夹（1/2~2，-20℃~300℃） 图C.19-6", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="腿长", TooltipLong="U形螺栓直线段长度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="开档", TooltipLong="U形中心距/内宽")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="U形圆钢螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_U6(s, D=42.4, H=65.0, B=56.4, d=10.0, ID=u"U6", **kw):
    D = float(D); H = float(H); B = float(B); d = float(d)
    if D < 15.0: D = 33.7
    if d < 6.0: d = 8.0
    if B < (D + d): B = D + d
    if H < (D / 2.0 + d * 3.0): H = D / 2.0 + d * 4.5
    R = B / 2.0; rod = d / 2.0
    o1 = TORUS(s, R1=R, R2=rod).rotateY(90.0)
    o_cut = BOX(s, L=(R + rod) * 3.0, W=(R + rod) * 2.2, H=d * 4.0).translate((0.0, 0.0, -(R + rod)))
    o1.subtractFrom(o_cut); o_cut.erase()
    for sy in (-1.0, 1.0):
        o_leg = CYLINDER(s, R=rod, H=H, O=0.0).translate((0.0, sy * R, -H))
        o_nut = CYLINDER(s, R=d * 0.88, H=d * 0.8, O=0.0).translate((0.0, sy * R, -H))
        o1.uniteWith(o_leg); o_leg.erase()
        o1.uniteWith(o_nut); o_nut.erase()
    # 后侧多孔圆弧法兰连接立板 + 下部水平槽钢支承底座（见 hg_index_p028.png U6）
    fl_r = R * 1.65; fl_t = max(6.0, d * 0.65)
    o_fl = CYLINDER(s, R=fl_r, H=fl_t, O=0.0).rotateY(90.0).translate((d * 1.5, 0.0, 0.0))
    o_fl_i = CYLINDER(s, R=D / 2.0, H=fl_t + 4.0, O=0.0).rotateY(90.0).translate((d * 1.5 - 2.0, 0.0, 0.0))
    o_fl.subtractFrom(o_fl_i); o_fl_i.erase()
    o_ch = BOX(s, L=fl_r * 2.2, W=d * 2.8, H=d * 4.0).translate((0.0, 0.0, -(D / 2.0 + d * 1.6)))
    o1.uniteWith(o_fl); o_fl.erase()
    o1.uniteWith(o_ch); o_ch.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
