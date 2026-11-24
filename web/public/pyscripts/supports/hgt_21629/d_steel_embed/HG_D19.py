# -*- coding: utf-8 -*-
# HG/T 21629-2021 D19 双槽钢三角架（图 C.4-19）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="双槽钢三角架", TooltipLong="HG/T 21629-2021 D19 双槽钢三角架 图C.4-19", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_D19(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"D19", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 45.0: B = 100.0
    if T < 6.0: T = 8.0
    if SPAN < 200.0: SPAN = 450.0
    if SH < 180.0: SH = 400.0
    R1 = D / 2.0; z_top = -(R1 + B / 2.0)
    # 1. 中央夹持节点钢板（位于 X = 0 平面，在顶角、前端与底角延伸为节点连接板）
    o1 = BOX(s, L=B * 1.8, W=B * 1.8, H=T * 1.4).translate((0.0, -(B * 0.9), z_top - B * 0.4))
    o_g2 = BOX(s, L=B * 1.8, W=SH, H=T * 1.4).translate((0.0, -(SPAN - B * 0.5), z_top - SH / 2.0 + B / 2.0))
    o1.uniteWith(o_g2); o_g2.erase()
    # 2. 节点板两侧对称背靠背双槽钢杆件（X = ±(T*0.7 + B*0.3)）
    diag_l = sqrt(SPAN * SPAN + SH * SH)
    ang = degrees(atan2(SH - B, SPAN))
    for sx in (-1.0, 1.0):
        xo = sx * (T * 0.55 + B * 0.20)
        o_arm = BOX(s, L=SPAN, W=B, H=B * 0.45).translate((xo, -(SPAN / 2.0), z_top))
        o_post = BOX(s, L=B * 0.85, W=SH, H=B * 0.45).translate((xo, -SPAN + B * 0.42, z_top - SH / 2.0 + B / 2.0))
        o_diag = BOX(s, L=diag_l * 0.9, W=B * 0.85, H=B * 0.45).rotateX(-ang).translate((xo, -(SPAN * 0.5), z_top - SH * 0.45))
        for p in (o_arm, o_post, o_diag):
            o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
