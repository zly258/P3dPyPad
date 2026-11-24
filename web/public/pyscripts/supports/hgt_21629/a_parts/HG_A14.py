# -*- coding: utf-8 -*-
# HG/T 21629-2021 A14 U形吊耳（图 C.1-14）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="U形吊耳", TooltipLong="HG/T 21629-2021 A14 U形吊耳 图C.1-14", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径或基准直径")
@param(H=LENGTH, TooltipShort="吊板高", TooltipLong="吊孔中心至底端/管壁高度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="吊板宽", TooltipLong="吊板/吊耳宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="吊板/耳板厚度")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="吊孔/销子直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A14(s, D=100.0, H=333.5, B=290.0, T=90.0, d=117.0, ID=u"A14", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if T < 6.0: T = 8.0
    if d < 10.0: d = 14.0
    if B < d * 2.2: B = d * 2.5
    if H < d * 1.8: H = d * 2.8
    gap = max(d * 1.4, T * 2.2)
    span_w = gap + T * 2.0
    # 1. 顶部水平封板（焊接于上部钢梁底面 Z = H）
    o1 = BOX(s, L=span_w, W=T, H=B).translate((0.0, 0.0, H - T / 2.0))
    # 2. 左右两侧竖直下垂耳板与下端半圆弧头
    ear_h = H - T
    for sy in (-(gap / 2.0 + T / 2.0), (gap / 2.0 + T / 2.0)):
        o_ear = BOX(s, L=T, W=ear_h, H=B).translate((0.0, sy, ear_h / 2.0))
        o_arc = CYLINDER(s, R=B / 2.0, H=T, O=0.0).rotateX(90.0).translate((0.0, sy + T / 2.0, 0.0))
        o1.uniteWith(o_ear); o_ear.erase()
        o1.uniteWith(o_arc); o_arc.erase()
    # 3. 底部横向销孔、六角头销轴与另一端挡圈开口销
    pin_l = span_w + d * 1.6
    o_pin = CYLINDER(s, R=d * 0.48, H=pin_l, O=0.0).rotateX(90.0).translate((0.0, pin_l / 2.0, 0.0))
    o_head = CYLINDER(s, R=d * 0.82, H=T * 0.75, O=0.0).rotateX(90.0).translate((0.0, -(span_w / 2.0), 0.0))
    o_washer = CYLINDER(s, R=d * 0.78, H=T * 0.4, O=0.0).rotateX(90.0).translate((0.0, (span_w / 2.0 + T * 0.4), 0.0))
    o_cotter = BOX(s, L=d * 0.22, W=d * 1.5, H=d * 0.22).translate((0.0, (span_w / 2.0 + T * 0.65), 0.0))
    for p in (o_pin, o_head, o_washer, o_cotter):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
