# -*- coding: utf-8 -*-
# HG/T 21629-2021 A26 不锈钢隔离层（图 C.1-26）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="不锈钢隔离层", TooltipLong="HG/T 21629-2021 A26 不锈钢隔离层 图C.1-26", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(B=LENGTH, TooltipShort="沿管长", TooltipLong="垫板/隔离层/支架沿管宽度", Ask4Dist=True)
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="弧形垫板/支架钢板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A26(s, D=114.3, B=125.0, T=8.0, ID=u"A26", **kw):
    D = float(D); B = float(B); T = float(T)
    if D < 15.0: D = 15.0
    if B < 20.0: B = 40.0
    if T < 1.5: T = 2.0
    R1 = D / 2.0; R2 = R1 + T
    o1 = CYLINDER(s, R=R2, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=B + 4.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_cut = BOX(s, L=R2 * 2.5, W=R2 * 1.6, H=B + 10.0).translate((0.0, 0.0, R2 * 0.85))
    o1.subtractFrom(o_cut); o_cut.erase()
    lip_h = max(3.0, T * 1.8)
    for x_lip in (-(B / 2.0), (B / 2.0 - T)):
        o_lip = CYLINDER(s, R=R2 + lip_h, H=T, O=0.0).rotateY(90.0).translate((x_lip, 0.0, 0.0))
        o_lip_in = CYLINDER(s, R=R1, H=T + 2.0, O=0.0).rotateY(90.0).translate((x_lip - 1.0, 0.0, 0.0))
        o_lip.subtractFrom(o_lip_in); o_lip_in.erase()
        o_lip_cut = BOX(s, L=(R2 + lip_h) * 2.5, W=(R2 + lip_h) * 1.6, H=T + 4.0).translate((x_lip + T / 2.0, 0.0, (R2 + lip_h) * 0.85))
        o_lip.subtractFrom(o_lip_cut); o_lip_cut.erase()
        o1.uniteWith(o_lip); o_lip.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('B', (0.0, 0.0, 0.0), (B, 0.0, 0.0))
