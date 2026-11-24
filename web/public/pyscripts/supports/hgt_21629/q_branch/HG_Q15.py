# -*- coding: utf-8 -*-
# HG/T 21629-2021 Q15 小支管加强架（钢管撑，1/2"~2")（图 C.15-15）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="小支管加强架（钢管撑，1/2~2", TooltipLong="HG/T 21629-2021 Q15 小支管加强架（钢管撑，1/2~2) 图C.15-15", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="母管外径", TooltipLong="大管/主管外径")
@param(D2=LENGTH, TooltipShort="支管外径", TooltipLong="被支撑小支管外径")
@param(L=LENGTH, TooltipShort="支承跨度", TooltipLong="小管中心至母管中心/生根距", Ask4Dist=True)
@param(T=LENGTH, TooltipShort="型材厚", TooltipLong="角钢/加强板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_Q15(s, D=93.3, D2=42.4, L=187.8, T=6.0, ID=u"Q15", **kw):
    D = float(D); D2 = float(D2); L = float(L); T = float(T)
    if D < 40.0: D = 114.3
    if D2 < 15.0: D2 = 33.7
    if T < 4.0: T = 6.0
    if L < (D / 2.0 + 70.0): L = D / 2.0 + 160.0
    R1 = D / 2.0; R2 = D2 / 2.0
    cw = max(38.0, D2 * 1.6)
    # 1. 上部水平主管管夹抱箍（O=0.0）与向下引出的支管及阀门
    o1 = CYLINDER(s, R=R1 + T, H=cw, O=0.0).rotateY(90.0).translate((-(cw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=cw + 4.0, O=0.0).rotateY(90.0).translate((-(cw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_sub_v = CYLINDER(s, R=R2, H=L, O=0.0).translate((0.0, -(R1 * 0.85), -L))
    o_sub_h = CYLINDER(s, R=R2, H=R1 * 1.8, O=0.0).rotateX(90.0).translate((0.0, 0.0, -(L * 0.25)))
    # 2. 斜向圆钢管撑杆（连接主管底部与支管下端管夹，区别于角钢支架 Q1/Q9/Q12）
    r_strut = max(10.0, R2 * 0.85)
    strut_l = sqrt((R1 * 0.85) * (R1 * 0.85) + (L * 0.72) * (L * 0.72))
    ang_s = degrees(atan2(R1 * 0.85, L * 0.72))
    o_pipe_brace = CYLINDER(s, R=r_strut, H=strut_l, O=0.0).rotateX(ang_s).translate((0.0, -(R1 * 0.85), -(L * 0.92)))
    o_bot_cl = CYLINDER(s, R=R2 + T, H=cw * 0.8, O=0.0).translate((0.0, -(R1 * 0.85), -(L * 0.95)))
    for p in (o_sub_v, o_sub_h, o_pipe_brace, o_bot_cl):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
