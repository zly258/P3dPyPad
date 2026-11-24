# -*- coding: utf-8 -*-
# HG/T 21629-2021 U4 角钢和U形螺栓/管卡组成的托吊架（1/2"~10"）（图 C.19-4）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="角钢和U形螺栓/管卡组成的托吊架（1", TooltipLong="HG/T 21629-2021 U4 角钢和U形螺栓/管卡组成的托吊架（1/2~10） 图C.19-4", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="腿长", TooltipLong="U形螺栓直线段长度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="开档", TooltipLong="U形中心距/内宽")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="U形圆钢螺杆直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_U4(s, D=114.3, H=120.7, B=130.3, d=12.0, ID=u"U4", **kw):
    D = float(D); H = float(H); B = float(B); d = float(d)
    if D < 10.0: D = 10.0
    if d < 6.0: d = 6.0
    if B < (D + d): B = D + d
    if H < (D / 2.0 + d * 3.0): H = D / 2.0 + d * 4.0
    R = B / 2.0
    rod = d / 2.0
    # 1. 顶部圆钢弯曲半环：TORUS(s, R1=R, R2=d/2.0).rotateY(90.0) 切去下半圆
    o1 = TORUS(s, R1=R, R2=d / 2.0).rotateY(90.0)
    o_cut = BOX(s, L=(R + rod) * 3.0, W=(R + rod) * 2.2, H=d * 4.0).translate((0.0, 0.0, -(R + rod)))
    o1.subtractFrom(o_cut); o_cut.erase()
    # 2. 两侧圆钢直腿
    o_leg1 = CYLINDER(s, R=d / 2.0, H=H, O=0.0).translate((0.0, -R, -H))
    o_leg2 = CYLINDER(s, R=d / 2.0, H=H, O=0.0).translate((0.0, R, -H))
    o1.uniteWith(o_leg1); o_leg1.erase()
    o1.uniteWith(o_leg2); o_leg2.erase()
    # 3. 下端垫圈与双六角螺母（正六棱柱并集）
    nut_w = d * 1.65
    nut_a = nut_w * 0.57735
    nut_h = d * 0.8
    z_nut1 = -(H - nut_h * 0.2)
    z_nut2 = z_nut1 + nut_h * 1.15
    for y_leg in (-R, R):
        o_wash = CYLINDER(s, R=d * 1.15, H=max(2.5, d * 0.2), O=0.0).translate((0.0, y_leg, z_nut2 + nut_h))
        o1.uniteWith(o_wash); o_wash.erase()
        for zn in (z_nut1, z_nut2):
            n1 = BOX(s, L=nut_w, W=nut_h, H=nut_a)
            n2 = BOX(s, L=nut_w, W=nut_h, H=nut_a).rotateZ(60.0)
            n3 = BOX(s, L=nut_w, W=nut_h, H=nut_a).rotateZ(-60.0)
            n1.uniteWith(n2); n2.erase()
            n1.uniteWith(n3); n3.erase()
            n1.translate((0.0, y_leg, zn + nut_h / 2.0))
            o1.uniteWith(n1); n1.erase()
    # 塑料/橡胶衬垫护套与底部槽钢/角钢导向托座
    slv_r = rod * 1.32
    o_slv = TORUS(s, R1=R, R2=slv_r).rotateY(90.0)
    o_scut = BOX(s, L=(R + slv_r) * 3.0, W=(R + slv_r) * 2.2, H=slv_r * 4.0).translate((0.0, 0.0, -(R + slv_r)))
    o_slv.subtractFrom(o_scut); o_scut.erase()
    o1.uniteWith(o_slv); o_slv.erase()
    ch_w = max(50.0, d * 4.0)
    ch_h = max(36.0, d * 2.8)
    ch_t = max(6.0, d * 0.5)
    z_ch = -(D / 2.0 + ch_h / 2.0)
    o_ch = BOX(s, L=B + d * 5.0, W=ch_h, H=ch_w).translate((0.0, 0.0, z_ch))
    o_ch_in = BOX(s, L=B + d * 5.0 + 10.0, W=ch_h - ch_t, H=ch_w - ch_t * 2.0).translate((0.0, 0.0, z_ch - ch_t / 2.0))
    o_ch.subtractFrom(o_ch_in); o_ch_in.erase()
    o1.uniteWith(o_ch); o_ch.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
