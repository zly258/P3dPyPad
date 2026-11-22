# -*- coding: utf-8 -*-
# HG/T 21629-2021 Q5 在大管的管托或耳轴上支撑小管（1/2"~6")（图 C.15-5）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="在大管的管托或耳轴上支撑小管（1/2", TooltipLong="HG/T 21629-2021 Q5 在大管的管托或耳轴上支撑小管（1/2~6) 图C.15-5", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_Q5(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"Q5", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 40.0: D = 114.3
    if LEG_D < 15.0: LEG_D = max(33.7, D * 0.35)
    if ST < 5.0: ST = 8.0
    R1 = D / 2.0; R_sub = min(R1 * 0.55, max(13.5, LEG_D * 0.45))
    if SH < (R1 + 60.0): SH = R1 + 130.0
    pipe_l = max(140.0, D * 1.4)
    # 1. 中央大主管弧形鞍板（O=0.0）与下部竖直支承腹板/耳轴
    o1 = CYLINDER(s, R=R1 + ST, H=pipe_l, O=0.0).rotateY(90.0).translate((-(pipe_l / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=pipe_l + 4.0, O=0.0).rotateY(90.0).translate((-(pipe_l / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_up = BOX(s, L=(R1 + ST) * 2.4, W=(R1 + ST) * 1.4, H=pipe_l + 8.0).translate((0.0, 0.0, (R1 + ST) * 0.65))
    o1.subtractFrom(o_up); o_up.erase()
    web_h = max(25.0, SH - R1 - ST * 1.5)
    o_web = BOX(s, L=ST * 1.4, W=web_h, H=pipe_l * 0.85).translate((0.0, 0.0, -(R1 + web_h / 2.0)))
    # 2. 向一侧（+Y 侧）加长挑出的水平横担底板梁 + 侧向平行小支管与 U 形螺栓抱卡
    ext_y = R1 + R_sub * 3.2
    beam_w = R1 * 1.4 + ext_y
    yc_beam = (ext_y - R1 * 0.8) / 2.0
    z_base = -(SH - ST * 0.75)
    o_base = BOX(s, L=beam_w, W=ST * 1.5, H=pipe_l * 0.85).translate((0.0, yc_beam, z_base))
    z_sub = z_base + ST * 0.75 + R_sub
    o_sub = CYLINDER(s, R=R_sub, H=pipe_l, O=0.0).rotateY(90.0).translate((-(pipe_l / 2.0), ext_y * 0.82, z_sub))
    o_sub_i = CYLINDER(s, R=max(4.0, R_sub - ST * 0.6), H=pipe_l + 4.0, O=0.0).rotateY(90.0).translate((-(pipe_l / 2.0 + 2.0), ext_y * 0.82, z_sub))
    o_sub.subtractFrom(o_sub_i); o_sub_i.erase()
    o_ub = TORUS(s, R1=R_sub + ST * 0.6, R2=ST * 0.5).rotateY(90.0).translate((0.0, ext_y * 0.82, z_sub))
    for p in (o_web, o_base, o_sub, o_ub):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
