# -*- coding: utf-8 -*-
# HG/T 21629-2021 Y1 用于不锈钢裸管的垫板（图 C.23-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="用于不锈钢裸管的垫板", TooltipLong="HG/T 21629-2021 Y1 用于不锈钢裸管的垫板 图C.23-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(B=LENGTH, TooltipShort="沿管长", TooltipLong="垫板/隔离层/支架沿管宽度", Ask4Dist=True)
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="弧形垫板/支架钢板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_Y1(s, D=114.3, B=125.0, T=8.0, ID=u"Y1", **kw):
    D = float(D); B = float(B); T = float(T)
    if D < 15.0: D = 88.9
    if B < 40.0: B = 100.0
    if T < 2.0: T = 4.0
    R1 = D / 2.0
    pad_w = max(80.0, B * 1.25)
    pad_l = B
    z_pad = -(R1 + T / 2.0)
    # 1. 位于裸管底部与支承钢梁之间的水平矩形不锈钢平垫板
    o1 = BOX(s, L=pad_w, W=T, H=pad_l).translate((0.0, 0.0, z_pad))
    # 2. 前后两侧折弯卡爪（向下折边 + 向内回折钩爪，见 hg_index_p029.png Y1 示意图）
    claw_w = pad_w * 0.32
    claw_d = max(12.0, T * 3.5)
    for sx in (-1.0, 1.0):
        xc = sx * (pad_l / 2.0 - T / 2.0)
        o_drop = BOX(s, L=claw_w, W=claw_d, H=T).translate((xc, 0.0, z_pad - claw_d / 2.0))
        o_hook = BOX(s, L=claw_w, W=T, H=claw_d * 0.85).translate((xc - sx * (claw_d * 0.4), 0.0, z_pad - claw_d))
        o1.uniteWith(o_drop); o_drop.erase()
        o1.uniteWith(o_hook); o_hook.erase()
    for sy in (-1.0, 1.0):
        yc = sy * (pad_w / 2.0 - T / 2.0)
        o_sdrop = BOX(s, L=T, W=claw_d * 0.8, H=pad_l * 0.35).translate((0.0, yc, z_pad - claw_d * 0.4))
        o1.uniteWith(o_sdrop); o_sdrop.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('B', (0.0, 0.0, 0.0), (B, 0.0, 0.0))
