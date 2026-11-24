# -*- coding: utf-8 -*-
# HG/T 21629-2021 G7 连接板型管道支腿（1/2"~6")（图 C.7-7）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="连接板型管道支腿（1/2~6)", TooltipLong="HG/T 21629-2021 G7 连接板型管道支腿（1/2~6) 图C.7-7", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_G7(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"G7", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 15.0: D = 60.3
    if LEG_D < 30.0: LEG_D = 65.0
    if ST < 5.0: ST = 7.0
    R1 = D / 2.0
    if SH < (R1 + 80.0): SH = R1 + 180.0
    cw = max(36.0, LEG_D * 0.75)
    # 1. 上部管道抱箍（O=0.0 外圆减内圆）与侧向双螺栓连接耳板
    o1 = CYLINDER(s, R=R1 + ST, H=cw, O=0.0).rotateY(90.0).translate((-(cw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=cw + 4.0, O=0.0).rotateY(90.0).translate((-(cw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    ear_l = LEG_D * 1.15
    o_ear = BOX(s, L=ear_l, W=cw * 1.1, H=ST * 2.2).translate((0.0, -(R1 + ear_l * 0.45), 0.0))
    o1.uniteWith(o_ear); o_ear.erase()
    for zb in (cw * 0.25, -cw * 0.25):
        o_b = CYLINDER(s, R=ST * 0.85, H=ST * 5.0, O=0.0).rotateY(90.0).translate((-(ST * 2.5), -(R1 + ear_l * 0.55), zb))
        o1.uniteWith(o_b); o_b.erase()
    # 2. 单根竖直角钢支腿（L形截面两肢）+ 底部方形底板
    y_leg = -(R1 + ear_l * 0.55)
    o_l1 = BOX(s, L=LEG_D, W=SH, H=ST).translate((ST * 1.5, y_leg, -(SH / 2.0)))
    o_l2 = BOX(s, L=ST, W=SH, H=LEG_D).translate((ST * 1.5 + LEG_D / 2.0 - ST / 2.0, y_leg - LEG_D / 2.0 + ST / 2.0, -(SH / 2.0)))
    o_base = BOX(s, L=LEG_D * 2.2, W=ST * 1.5, H=LEG_D * 2.2).translate((ST * 1.5, y_leg, -(SH - ST * 0.75)))
    for p in (o_l1, o_l2, o_base):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
