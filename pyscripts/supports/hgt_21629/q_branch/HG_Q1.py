# -*- coding: utf-8 -*-
# HG/T 21629-2021 Q1 大管用角钢支撑小管(1/2"~4" 不保温管）（图 C.15-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="大管用角钢支撑小管(1/2~4 ", TooltipLong="HG/T 21629-2021 Q1 大管用角钢支撑小管(1/2~4 不保温管） 图C.15-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="母管外径", TooltipLong="大管/主管外径")
@param(D2=LENGTH, TooltipShort="支管外径", TooltipLong="被支撑小支管外径")
@param(L=LENGTH, TooltipShort="支承跨度", TooltipLong="小管中心至母管中心/生根距", Ask4Dist=True)
@param(T=LENGTH, TooltipShort="型材厚", TooltipLong="角钢/加强板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_Q1(s, D=114.3, D2=33.7, L=194.0, T=8.0, ID=u"Q1", **kw):
    D = float(D); D2 = float(D2); L = float(L); T = float(T)
    if D < 40.0: D = 114.3
    if D2 < 15.0: D2 = 33.7
    if D2 > D: D2 = D * 0.45
    if T < 4.0: T = 6.0
    if L < (D / 2.0 + D2 / 2.0 + 30.0): L = D / 2.0 + D2 / 2.0 + 80.0
    R1 = D / 2.0; R2 = D2 / 2.0
    pipe_len = max(140.0, D * 1.4)
    # 1. 原点处下部水平大主管段（沿 X 轴，O=0.0）与上部 Z = +L 处平行小支管段
    o1 = CYLINDER(s, R=R1, H=pipe_len, O=0.0).rotateY(90.0).translate((-(pipe_len / 2.0), 0.0, 0.0))
    o1_i = CYLINDER(s, R=max(6.0, R1 - T), H=pipe_len + 4.0, O=0.0).rotateY(90.0).translate((-(pipe_len / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o1_i); o1_i.erase()
    o_sub = CYLINDER(s, R=R2, H=pipe_len, O=0.0).rotateY(90.0).translate((-(pipe_len / 2.0), 0.0, L))
    o_sub_i = CYLINDER(s, R=max(4.0, R2 - T * 0.7), H=pipe_len + 4.0, O=0.0).rotateY(90.0).translate((-(pipe_len / 2.0 + 2.0), 0.0, L))
    o_sub.subtractFrom(o_sub_i); o_sub_i.erase()
    o1.uniteWith(o_sub); o_sub.erase()
    # 2. 焊接在大主管上的 L 形角钢立柱与横托臂 + 抱持小支管的 U 形螺栓
    ang_w = max(40.0, D2 * 1.2)
    post_h = L - R1 * 0.75 - R2
    o_v1 = BOX(s, L=T, W=post_h, H=ang_w).translate((0.0, -(T / 2.0), R1 * 0.75 + post_h / 2.0))
    o_v2 = BOX(s, L=ang_w, W=post_h, H=T).translate((ang_w / 2.0 - T / 2.0, -(ang_w / 2.0), R1 * 0.75 + post_h / 2.0))
    o_seat = BOX(s, L=D2 * 2.2, W=T * 1.3, H=ang_w).translate((0.0, 0.0, L - R2 - T * 0.65))
    o_ub = TORUS(s, R1=R2 + T * 0.7, R2=T * 0.6).rotateY(90.0).translate((0.0, 0.0, L))
    for p in (o_v1, o_v2, o_seat, o_ub):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
