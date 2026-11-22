# -*- coding: utf-8 -*-
# HG/T 21629-2021 MD1 连续梁（非金属管）（图 C.12-7）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="连续梁（非金属管）", TooltipLong="HG/T 21629-2021 MD1 连续梁（非金属管） 图C.12-7", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_MD1(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"MD1", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if D < 20.0: D = 88.9
    if B < 45.0: B = max(80.0, D * 0.9)
    if T < 5.0: T = 8.0
    if SPAN < 250.0: SPAN = 600.0
    if SH < (D / 2.0 + 60.0): SH = D / 2.0 + 140.0
    R1 = D / 2.0
    # 1. 沿管道轴线 X 轴通长布置的 U 形/V 形连续承托槽梁（长 SPAN，兜住非金属管下半部）
    trough_w = max(D + T * 4.0, B * 1.2)
    trough_h = max(R1 * 0.85, B * 0.65)
    z_tr = -(R1 + T * 1.5 - trough_h * 0.35)
    o1 = BOX(s, L=trough_w, W=trough_h, H=SPAN).translate((0.0, 0.0, z_tr))
    o_p_cut = CYLINDER(s, R=R1 + T * 0.5, H=SPAN + 10.0, O=0.0).rotateY(90.0).translate((-(SPAN / 2.0 + 5.0), 0.0, 0.0))
    o1.subtractFrom(o_p_cut); o_p_cut.erase()
    # 2. 连续托槽梁下方前后对称布置的 2 座 T 形支承立柱与底板（位于 X = ±SPAN*0.32）
    leg_h = max(30.0, SH - R1 - T * 2.0)
    for sx in (-(SPAN * 0.32), (SPAN * 0.32)):
        o_col = BOX(s, L=trough_w * 0.75, W=leg_h, H=T * 2.5).translate((sx, 0.0, -(SH - T * 1.2 - leg_h / 2.0)))
        o_rib = BOX(s, L=T * 1.5, W=leg_h, H=B * 0.9).translate((sx, 0.0, -(SH - T * 1.2 - leg_h / 2.0)))
        o_bp = BOX(s, L=trough_w * 1.15, W=T * 1.4, H=B * 1.3).translate((sx, 0.0, -(SH - T * 0.7)))
        for p in (o_col, o_rib, o_bp):
            o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
