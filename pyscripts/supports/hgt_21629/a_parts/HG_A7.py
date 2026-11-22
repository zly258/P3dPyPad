# -*- coding: utf-8 -*-
# HG/T 21629-2021 A7 标准型3螺栓管夹（图 C.1-7）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="标准型3螺栓管夹", TooltipLong="HG/T 21629-2021 A7 标准型3螺栓管夹 图C.1-7", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="螺栓跨距", TooltipLong="管心至螺栓孔中心距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="管夹扁钢宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="管夹扁钢厚度")
@param(d=LENGTH, TooltipShort="螺栓径", TooltipLong="夹紧/悬吊螺栓直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A7(s, D=114.3, H=113.9, B=38.4, T=8.0, d=12.0, ID=u"A7", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 15.0: D = 33.7
    if T < 4.0: T = 6.0
    if B < 25.0: B = 40.0
    if d < 8.0: d = 12.0
    R1 = D / 2.0; R2 = R1 + T
    if H < (R1 + d * 3.2): H = R1 + d * 4.2
    gap = max(10.0, d * 1.1)
    # 1. 左右两瓣抱箍圆环（O=0.0 外圆减内圆，再切出中央竖直分缝 Y ∈ [-gap/2, +gap/2]）
    o1 = CYLINDER(s, R=R2, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=B + 4.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_vsplit = BOX(s, L=gap, W=R2 * 2.5, H=B + 6.0)
    o1.subtractFrom(o_vsplit); o_vsplit.erase()
    # 2. 上部加长竖直双耳板（含第1颗夹紧螺栓与顶部第2颗吊耳螺栓）与下部竖直双耳板（含第3颗底部夹紧螺栓）
    up_h = (H + d * 1.6) - R1
    low_h = d * 3.0
    for sy in (-(gap / 2.0 + T / 2.0), (gap / 2.0 + T / 2.0)):
        o_uear = BOX(s, L=T, W=up_h, H=B).translate((0.0, sy, R1 + up_h / 2.0 - 3.0))
        o_lear = BOX(s, L=T, W=low_h, H=B).translate((0.0, sy, -(R1 + low_h / 2.0 - 3.0)))
        o1.uniteWith(o_uear); o_uear.erase()
        o1.uniteWith(o_lear); o_lear.erase()
    blt_l = gap + T * 4.6
    for zb in (R1 + d * 1.5, H, -(R1 + d * 1.5)):
        o_b = CYLINDER(s, R=d / 2.0, H=blt_l, O=0.0).rotateX(90.0).translate((0.0, blt_l / 2.0, zb))
        o_n1 = CYLINDER(s, R=d * 0.88, H=d * 0.75, O=0.0).rotateX(90.0).translate((0.0, -(gap / 2.0 + T), zb))
        o_n2 = CYLINDER(s, R=d * 0.88, H=d * 0.75, O=0.0).rotateX(90.0).translate((0.0, (gap / 2.0 + T + d * 0.75), zb))
        for p in (o_b, o_n1, o_n2):
            o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
