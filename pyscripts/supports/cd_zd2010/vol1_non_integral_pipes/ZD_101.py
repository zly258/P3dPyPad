# -*- coding: utf-8 -*-
# CD-ZD2010 101 双孔管夹（水平管 X 轴抱箍 + 上下夹耳 + 横向穿孔螺栓 + 螺母）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="101双孔管夹", TooltipLong="CD-ZD2010 101 双孔管夹（水平管无保温双孔抱箍）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(H=LENGTH, TooltipShort="中心高", TooltipLong="管道中心至上下螺栓孔中心跨距", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="管夹扁钢板宽")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="管夹扁钢板厚")
@param(d=LENGTH, TooltipShort="螺栓径", TooltipLong="穿螺栓孔径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_101(s, D=108.0, H=90.0, B=50.0, T=6.0, d=16.0, ID=u"ZD_101", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 15.0: D = 15.0
    if T < 3.0: T = 3.0
    if B < 20.0: B = 20.0
    if d < 8.0: d = 8.0
    if d > B * 0.65: d = B * 0.5
    R1 = D / 2.0
    R2 = R1 + T
    if H <= R1 + d * 1.1: H = R1 + d * 1.4 + 10.0
    if H > R1 * 4.5 + 120.0: H = R1 * 1.6 + d * 1.8
    gap = max(6.0, T * 1.2)
    ear_h = (H + d * 1.4) - R1

    # 1. 左右两瓣圆弧抱箍 (沿 X 轴宽 B)
    o1 = CYLINDER(s, R=R2, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=B + 4.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_slot = BOX(s, L=gap, W=R2 * 3.0, H=B + 6.0)
    o1.subtractFrom(o_slot); o_slot.erase()

    # 2. 上下直立夹耳板 (位于 Y = ±(gap/2 + T/2)，向 ±Z 延伸至 ±(H + 1.4*d))
    tot_z = (H + d * 1.4) * 2.0
    for sy in (-1.0, 1.0):
        yc = sy * (gap / 2.0 + T / 2.0)
        o_ear = BOX(s, L=T, W=tot_z, H=B).translate((0.0, yc, 0.0))
        o1.uniteWith(o_ear); o_ear.erase()
    o_in2 = CYLINDER(s, R=R1, H=B + 6.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 3.0), 0.0, 0.0))
    o1.subtractFrom(o_in2); o_in2.erase()

    # 3. 上下夹耳横向穿孔 + 紧固螺栓与六角螺母 (Z = ±H，沿 Y 轴穿过双耳)
    bolt_r = (d / 2.0) * 0.85
    span_y = gap + T * 2.0
    bolt_len = span_y + d * 2.2
    hex_s = d * 1.5
    nut_h = d * 0.75
    for sz in (-1.0, 1.0):
        zc = sz * H
        o_hole = CYLINDER(s, R=d / 2.0, H=span_y + 10.0, O=0.0).rotateX(90.0).translate((0.0, (span_y + 10.0) / 2.0, zc))
        o1.subtractFrom(o_hole); o_hole.erase()
        # 横向螺栓杆 + 两侧六角头/螺母
        o_sh = CYLINDER(s, R=bolt_r, H=bolt_len, O=0.0).rotateX(90.0).translate((0.0, bolt_len / 2.0, zc))
        o1.uniteWith(o_sh); o_sh.erase()
        for sy_n in (-1.0, 1.0):
            yn = sy_n * (span_y / 2.0 + nut_h / 2.0)
            o_n1 = BOX(s, L=nut_h, W=hex_s, H=hex_s * 2.0).translate((0.0, yn, zc))
            o_n2 = BOX(s, L=nut_h, W=hex_s, H=hex_s * 2.0).rotateY(60.0).translate((0.0, yn, zc))
            o_n3 = BOX(s, L=nut_h, W=hex_s, H=hex_s * 2.0).rotateY(120.0).translate((0.0, yn, zc))
            o_n1.intersectWith(o_n2); o_n2.erase()
            o_n1.intersectWith(o_n3); o_n3.erase()
            o1.uniteWith(o_n1); o_n1.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
