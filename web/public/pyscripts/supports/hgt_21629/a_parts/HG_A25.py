# -*- coding: utf-8 -*-
# HG/T 21629-2021 A25 保冷管用重载型管夹（图 C.1-25）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="保冷管用重载型管夹", TooltipLong="HG/T 21629-2021 A25 保冷管用重载型管夹 图C.1-25", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="螺栓跨距", TooltipLong="管心至螺栓孔中心距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="管夹扁钢宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="管夹扁钢厚度")
@param(d=LENGTH, TooltipShort="螺栓径", TooltipLong="夹紧/悬吊螺栓直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A25(s, D=194.3, H=151.6, B=48.0, T=10.0, d=16.0, ID=u"A25", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 60.0: D = 168.3
    if T < 6.0: T = 10.0
    if B < 60.0: B = 150.0
    if d < 12.0: d = 20.0
    R1 = D / 2.0; R2 = R1 + T
    if H < (R1 + 80.0): H = R1 + 140.0
    # 1. 下半圆宽幅 U 形扁钢托带（W=B, T=T）
    o1 = CYLINDER(s, R=R2, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=B + 4.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_up_cut = BOX(s, L=R2 * 2.4, W=R2 * 1.4, H=B + 8.0).translate((0.0, 0.0, R2 * 0.7))
    o1.subtractFrom(o_up_cut); o_up_cut.erase()
    # 2. U形托带两侧竖直向上延伸段（从 Z=0 延伸至管顶上方横担顶面 Z = H）
    for sy in (-1.0, 1.0):
        o_vstrap = BOX(s, L=T, W=H, H=B).translate((0.0, sy * (R1 + T / 2.0), H / 2.0))
        o1.uniteWith(o_vstrap); o_vstrap.erase()
    # 3. 顶部水平 H 型钢横担梁（构件 A，横跨 [-R1, +R1]）与两侧斜向三角形加劲板
    beam_h = max(60.0, (H - R1) * 0.65)
    z_beam = H - beam_h / 2.0
    o_web = BOX(s, L=D, W=beam_h, H=T).translate((0.0, 0.0, z_beam))
    o_fl1 = BOX(s, L=D, W=T, H=B * 0.85).translate((0.0, 0.0, H - T / 2.0))
    o_fl2 = BOX(s, L=D, W=T, H=B * 0.85).translate((0.0, 0.0, H - beam_h + T / 2.0))
    for p in (o_web, o_fl1, o_fl2):
        o1.uniteWith(p); p.erase()
    # 4. 横担中心向上伸出的竖直吊板与两侧斜撑肋
    lug_h = max(45.0, d * 2.5)
    o_lug = BOX(s, L=T * 1.2, W=beam_h + lug_h, H=B * 0.75).translate((0.0, 0.0, H - beam_h / 2.0 + lug_h / 2.0))
    o_hole = CYLINDER(s, R=d / 2.0, H=B, O=0.0).rotateX(90.0).translate((0.0, B / 2.0, H + lug_h * 0.55))
    o_lug.subtractFrom(o_hole); o_hole.erase()
    o1.uniteWith(o_lug); o_lug.erase()
    for sy in (-1.0, 1.0):
        o_diag = BOX(s, L=R1 * 0.85, W=T, H=B * 0.5).rotateX(sy * 25.0).translate((0.0, sy * (R1 * 0.45), z_beam))
        o1.uniteWith(o_diag); o_diag.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
