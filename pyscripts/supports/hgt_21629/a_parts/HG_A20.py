# -*- coding: utf-8 -*-
# HG/T 21629-2021 A20 不保温立管用3螺栓管夹（图 C.1-20）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="不保温立管用3螺栓管夹", TooltipLong="HG/T 21629-2021 A20 不保温立管用3螺栓管夹 图C.1-20", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="螺栓跨距", TooltipLong="管心至螺栓孔中心距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="管夹扁钢宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="管夹扁钢厚度")
@param(d=LENGTH, TooltipShort="螺栓径", TooltipLong="夹紧/悬吊螺栓直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A20(s, D=114.3, H=113.9, B=38.4, T=8.0, d=12.0, ID=u"A20", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 15.0: D = 15.0
    if T < 4.0: T = 6.0
    if B < 30.0: B = 45.0
    if d < 8.0: d = 12.0
    R1 = D / 2.0; R2 = R1 + T
    if H < (R1 + d * 3.2): H = R1 + d * 4.2
    gap = 6.0
    o1 = CYLINDER(s, R=R2, H=B, O=0.0).translate((0.0, 0.0, -(B / 2.0)))
    o_in = CYLINDER(s, R=R1, H=B + 4.0, O=0.0).translate((0.0, 0.0, -(B / 2.0 + 2.0)))
    o1.subtractFrom(o_in); o_in.erase()
    o_slot = BOX(s, L=gap, W=B + 4.0, H=R2 * 2.4)
    o1.subtractFrom(o_slot); o_slot.erase()
    ear_len = (H - R1) + d * 2.0
    for sx in (-1.0, 1.0):
        for sy in (-(gap / 2.0 + T / 2.0), (gap / 2.0 + T / 2.0)):
            o_ear = BOX(s, L=T, W=B, H=ear_len).translate((sx * (R1 + ear_len / 2.0 - 2.0), sy, 0.0))
            o1.uniteWith(o_ear); o_ear.erase()
        for bx in (R1 + d * 1.4, H):
            bh = gap + T * 4.5
            o_blt = CYLINDER(s, R=d / 2.0, H=bh, O=0.0).rotateX(90.0).translate((sx * bx, bh / 2.0, 0.0))
            o_n1 = CYLINDER(s, R=d * 0.88, H=d * 0.75, O=0.0).rotateX(90.0).translate((sx * bx, -(gap / 2.0 + T), 0.0))
            o_n2 = CYLINDER(s, R=d * 0.88, H=d * 0.75, O=0.0).rotateX(90.0).translate((sx * bx, (gap / 2.0 + T + d * 0.75), 0.0))
            for p in (o_blt, o_n1, o_n2):
                o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
