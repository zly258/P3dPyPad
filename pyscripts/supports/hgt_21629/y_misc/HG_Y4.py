# -*- coding: utf-8 -*-
# HG/T 21629-2021 Y4 格栅板夹板（图 C.23-4）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="格栅板夹板", TooltipLong="HG/T 21629-2021 Y4 格栅板夹板 图C.23-4", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="螺纹径", TooltipLong="配用吊杆公称螺纹直径")
@param(L=LENGTH, TooltipShort="总长度", TooltipLong="连接件轴向总长度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="外形宽", TooltipLong="连接件外径或最大外宽")
@param(d=LENGTH, TooltipShort="孔销径", TooltipLong="内螺纹孔径或销子直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_Y4(s, D=12.0, L=120.0, B=145.0, d=12.0, ID=u"Y4", **kw):
    D = float(D); L = float(L); B = float(B); d = float(d)
    if D < 10.0: D = 12.0
    if B < 60.0: B = 120.0
    if L < 50.0: L = 100.0
    if d < 8.0: d = 12.0
    plate_t = max(8.0, d * 0.65)
    # 1. 上部格栅承压夹板与下部锁紧夹板
    o1 = BOX(s, L=B, W=plate_t, H=B * 0.55).translate((0.0, 0.0, -(plate_t / 2.0)))
    o_bot = BOX(s, L=B, W=plate_t, H=B * 0.55).translate((0.0, 0.0, -(L * 0.55)))
    o1.uniteWith(o_bot); o_bot.erase()
    # 2. 左右双穿格栅紧固螺栓与六角螺母
    for sy in (-(B * 0.32), (B * 0.32)):
        o_b = CYLINDER(s, R=d / 2.0, H=L, O=0.0).translate((0.0, sy, -L))
        o_n1 = CYLINDER(s, R=d * 0.9, H=d * 0.75, O=0.0).translate((0.0, sy, 0.0))
        o_n2 = CYLINDER(s, R=d * 0.9, H=d * 0.75, O=0.0).translate((0.0, sy, -(L * 0.55 + plate_t / 2.0 + d * 0.75)))
        for p in (o_b, o_n1, o_n2):
            o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
