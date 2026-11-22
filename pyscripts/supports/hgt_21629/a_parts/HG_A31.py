# -*- coding: utf-8 -*-
# HG/T 21629-2021 A31 单孔长吊板（图 C.1-31）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="单孔长吊板", TooltipLong="HG/T 21629-2021 A31 单孔长吊板 图C.1-31", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径或基准直径")
@param(H=LENGTH, TooltipShort="吊板高", TooltipLong="吊孔中心至底端/管壁高度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="吊板宽", TooltipLong="吊板/吊耳宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="吊板/耳板厚度")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="吊孔/销子直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A31(s, D=114.3, H=142.2, B=97.9, T=8.0, d=16.0, ID=u"A31", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if T < 6.0: T = 8.0
    if d < 10.0: d = 16.0
    if B < d * 2.6: B = d * 3.4
    if H < B * 1.2: H = B * 1.6
    R_bot = B / 2.0
    R_top = max(d * 1.05, R_bot * 0.52)
    # 1. 下部大圆弧底盘（圆心在 Z = R_bot）与上部小圆弧耳头（圆心在 Z = H）
    o1 = CYLINDER(s, R=R_bot, H=T, O=0.0).rotateY(90.0).translate((-(T / 2.0), 0.0, R_bot))
    o_top = CYLINDER(s, R=R_top, H=T, O=0.0).rotateY(90.0).translate((-(T / 2.0), 0.0, H))
    o1.uniteWith(o_top); o_top.erase()
    # 2. 中间梯形连接板（上窄 2*R_top，下宽 2*R_bot）
    mid_h = max(10.0, H - R_bot)
    o_mid = BOX(s, L=B, W=mid_h, H=T).translate((0.0, 0.0, R_bot + mid_h / 2.0))
    dx_t = R_bot - R_top
    if dx_t > 1.5:
        ang_t = degrees(atan2(dx_t, mid_h))
        cut_l = sqrt(dx_t * dx_t + mid_h * mid_h) * 1.5
        for sy in (-1.0, 1.0):
            o_tc = BOX(s, L=B, W=cut_l, H=T * 4.0).rotateX(sy * ang_t).translate((0.0, sy * (R_top + dx_t / 2.0 + B * 0.48), R_bot + mid_h / 2.0))
            o_mid.subtractFrom(o_tc); o_tc.erase()
    o1.uniteWith(o_mid); o_mid.erase()
    # 3. 上部小圆头中心吊孔（在 Z = H 处沿 X 轴贯穿切除）
    o_hole = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateY(90.0).translate((-(T * 2.0), 0.0, H))
    o1.subtractFrom(o_hole); o_hole.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
