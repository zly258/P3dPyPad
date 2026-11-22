# -*- coding: utf-8 -*-
# HG/T 21629-2021 N8 设备预焊件用连接板和螺栓（图 C.13-8）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="设备预焊件用连接板和螺栓", TooltipLong="HG/T 21629-2021 N8 设备预焊件用连接板和螺栓 图C.13-8", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_N8(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"N8", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 60.0: B = 180.0
    if T < 8.0: T = 14.0
    plate_w = max(160.0, B * 1.5)
    bolt_r = max(7.0, T * 0.65)
    # 1. 正面方形四孔连接钢板（位于 Y = 0）
    o1 = BOX(s, L=T, W=plate_w, H=plate_w).translate((0.0, 0.0, -(plate_w / 2.0)))
    # 2. 四角穿装 4 套六角连接螺栓与螺母
    off = plate_w * 0.34
    for sx in (-1.0, 1.0):
        for sz in (-(plate_w / 2.0 - off), -(plate_w / 2.0 + off)):
            o_b = CYLINDER(s, R=bolt_r, H=T * 4.5, O=0.0).rotateX(90.0).translate((sx * off, T * 2.0, sz))
            o_n = CYLINDER(s, R=bolt_r * 1.75, H=bolt_r * 1.4, O=0.0).rotateX(90.0).translate((sx * off, T * 1.9, sz))
            o1.uniteWith(o_b); o_b.erase()
            o1.uniteWith(o_n); o_n.erase()
        # 背部两条设备预焊连接耳板
        o_ear = BOX(s, L=plate_w * 0.45, W=plate_w * 0.9, H=T * 1.2).translate((sx * (off + T), -(plate_w * 0.25), -(plate_w / 2.0)))
        o1.uniteWith(o_ear); o_ear.erase()
    # 3. 贴合设备圆筒外壁的弧形预焊垫板（O=0.0）
    eq_r = max(350.0, plate_w * 1.8)
    o_pad = CYLINDER(s, R=eq_r + T * 1.4, H=plate_w * 1.15, O=0.0).translate((0.0, -(plate_w * 0.48 + eq_r), -(plate_w * 1.075)))
    o_pad_i = CYLINDER(s, R=eq_r, H=plate_w * 1.15 + 4.0, O=0.0).translate((0.0, -(plate_w * 0.48 + eq_r), -(plate_w * 1.075 + 2.0)))
    o_pad.subtractFrom(o_pad_i); o_pad_i.erase()
    o_pb = BOX(s, L=plate_w * 1.2, W=plate_w * 1.15, H=plate_w * 1.3).translate((0.0, -(plate_w * 0.48), -(plate_w / 2.0)))
    o_pad.intersectWith(o_pb); o_pb.erase()
    o1.uniteWith(o_pad); o_pad.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
