# -*- coding: utf-8 -*-
# HG/T 21629-2021 D1 筋板和垫板（图 C.4-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="筋板和垫板", TooltipLong="HG/T 21629-2021 D1 筋板和垫板 图C.4-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(B=LENGTH, TooltipShort="沿管长", TooltipLong="垫板/隔离层/支架沿管宽度", Ask4Dist=True)
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="弧形垫板/支架钢板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_D1(s, D=114.3, B=180.0, T=14.0, ID=u"D1", **kw):
    D = float(D); B = float(B); T = float(T)
    if B < 80.0: B = 180.0
    if T < 6.0: T = 10.0
    pad_l = B * 1.6
    pad_w = B
    rib_h = B * 0.85
    # 1. 顶部水平矩形垫板（Z = -T ~ 0）
    o1 = BOX(s, L=pad_l, W=T, H=pad_w).translate((0.0, 0.0, -(T / 2.0)))
    # 2. 垫板下方垂直焊接的 3 片平行加劲筋板（对照 hg_index_p018.png D1 示意图与 HG_D1_atlas.png 子项C）
    for sy in (-(pad_l * 0.36), 0.0, (pad_l * 0.36)):
        o_rib = BOX(s, L=T, W=rib_h, H=pad_w * 0.9).translate((0.0, sy, -(T + rib_h / 2.0)))
        # 内角 20x20 焊缝避让切角
        o_ch = BOX(s, L=T * 3.0, W=T * 2.2, H=T * 2.2).translate((pad_w * 0.45, sy, -T))
        o_rib.subtractFrom(o_ch); o_ch.erase()
        o1.uniteWith(o_rib); o_rib.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('B', (0.0, 0.0, 0.0), (B, 0.0, 0.0))
