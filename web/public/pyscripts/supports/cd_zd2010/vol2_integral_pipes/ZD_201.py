# -*- coding: utf-8 -*-
# CD-ZD2010 201 焊接吊板（单块直立吊板底部弧形切口直接焊于水平管顶，上部半圆弧顶带吊孔）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="201焊接吊板", TooltipLong="CD-ZD2010 201 焊接吊板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(L=LENGTH, TooltipShort="板宽A", TooltipLong="吊板底部沿管轴方向宽度 A")
@param(H=LENGTH, TooltipShort="中心高", TooltipLong="管心至吊孔中心高度 H", Ask4Dist=True)
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="吊板厚度")
@param(d=LENGTH, TooltipShort="孔径", TooltipLong="吊杆销轴孔径 D")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_201(s, D=159.0, L=170.0, H=258.0, T=16.0, d=17.5, ID=u"ZD_201", **kw):
    D = float(D); L = float(L); H = float(H); T = float(T); d = float(d)
    if D < 20.0: D = 20.0
    if T < 6.0: T = 6.0
    if T > 36.0: T = 20.0
    if d < 10.0: d = 10.0
    if d > L * 0.55: d = L * 0.32
    R1 = D / 2.0
    if L < d * 2.5: L = d * 3.2
    if H <= R1 + d * 1.8: H = R1 + d * 2.5 + 35.0
    r_top = max(d * 1.25, L * 0.28)
    if r_top > L * 0.48: r_top = L * 0.45

    # 1. 直立梯形主吊板 (底部宽 L 沿 X，厚 T 沿 Y，高 H 沿 Z) + 顶部半圆弧耳头
    o1 = BOX(s, L=T, W=H, H=L).translate((0.0, 0.0, H / 2.0))
    cut_dx = (L - r_top * 2.0) / 2.0
    if cut_dx > 4.0 and (H - R1) > 20.0:
        ang = degrees(atan2(cut_dx, H - R1 * 0.7))
        for sx in (-1.0, 1.0):
            mid_x = sx * (r_top + L / 2.0) * 0.5
            mid_z = (R1 * 0.7 + H) * 0.5
            o_cut = BOX(s, L=T * 4.0, W=H * 2.0, H=L).translate((sx * (L / 2.0), 0.0, 0.0)).rotateY(sx * ang).translate((mid_x, 0.0, mid_z))
            o1.subtractFrom(o_cut); o_cut.erase()
    o_head = CYLINDER(s, R=r_top, H=T, O=0.0).rotateX(90.0).translate((0.0, T / 2.0, H))
    o1.uniteWith(o_head); o_head.erase()

    # 2. 底部水平管道圆弧马鞍切口 (沿 X 轴切除 R1)
    o_pipe = CYLINDER(s, R=R1, H=L + 40.0, O=0.0).rotateY(90.0).translate((-(L / 2.0 + 20.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    # 3. 顶部半圆头中心吊孔 (Z = H，沿 Y 轴穿透板厚 T)
    o_hole = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateX(90.0).translate((0.0, T * 2.0, H))
    o1.subtractFrom(o_hole); o_hole.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
