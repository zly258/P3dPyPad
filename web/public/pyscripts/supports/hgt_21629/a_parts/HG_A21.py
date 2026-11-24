# -*- coding: utf-8 -*-
# HG/T 21629-2021 A21 防振型4螺栓管夹（图 C.1-21）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="防振型4螺栓管夹", TooltipLong="HG/T 21629-2021 A21 防振型4螺栓管夹 图C.1-21", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="螺栓跨距", TooltipLong="管心至螺栓孔中心距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="管夹扁钢宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="管夹扁钢厚度")
@param(d=LENGTH, TooltipShort="螺栓径", TooltipLong="夹紧/悬吊螺栓直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A21(s, D=114.3, H=101.9, B=100.0, T=8.0, d=12.0, ID=u"A21", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 15.0: D = 15.0
    if T < 4.0: T = 6.0
    if d < 8.0: d = 12.0
    if B < d * 5.0: B = d * 5.5
    R1 = D / 2.0; R2 = R1 + T
    if H < (R1 + d * 1.6): H = R1 + d * 2.2
    gap = 6.0; L_ear = (H - R1) + d * 1.8
    o1 = CYLINDER(s, R=R2, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=B + 4.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_split = BOX(s, L=R2 * 2.4, W=gap, H=B + 6.0)
    o1.subtractFrom(o_split); o_split.erase()
    for sy in (-1.0, 1.0):
        for sz in (gap / 2.0 + T / 2.0, -(gap / 2.0 + T / 2.0)):
            o_ear = BOX(s, L=L_ear, W=T, H=B).translate((0.0, sy * (R1 + L_ear / 2.0 - 2.0), sz))
            o1.uniteWith(o_ear); o_ear.erase()
        o_rib = BOX(s, L=L_ear * 0.75, W=R2 * 0.42, H=T).translate((0.0, sy * (R1 + L_ear * 0.35), (gap / 2.0 + T + R2 * 0.21)))
        o1.uniteWith(o_rib); o_rib.erase()
        for bx in (-(B * 0.28), (B * 0.28)):
            bh = gap + T * 4.5
            o_b = CYLINDER(s, R=d / 2.0, H=bh, O=0.0).translate((bx, sy * H, -(bh / 2.0)))
            o_nh = CYLINDER(s, R=d * 0.9, H=d * 0.75, O=0.0).translate((bx, sy * H, (gap / 2.0 + T)))
            o1.uniteWith(o_b); o_b.erase()
            o1.uniteWith(o_nh); o_nh.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
