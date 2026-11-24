# -*- coding: utf-8 -*-
# HG/T 21629-2021 A17 单孔吊板（图 C.1-17）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="单孔吊板", TooltipLong="HG/T 21629-2021 A17 单孔吊板 图C.1-17", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径或基准直径")
@param(H=LENGTH, TooltipShort="吊板高", TooltipLong="吊孔中心至底端/管壁高度", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="吊板宽", TooltipLong="吊板/吊耳宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="吊板/耳板厚度")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="吊孔/销子直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_A17(s, D=36.0, H=115.0, B=100.0, T=25.0, d=45.0, ID=u"A17", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if T < 6.0: T = 10.0
    if B < 35.0: B = 65.0
    if d < 10.0: d = 18.0
    if d > B * 0.55: d = B * 0.48
    if H < B * 0.8: H = B * 1.15
    h_tot = H + B * 0.45
    # 1. 方正矩形吊板本体（从 Z = -B*0.45 延伸至顶部焊接面 Z = H）
    o1 = BOX(s, L=B, W=h_tot, H=T).translate((0.0, 0.0, H - h_tot / 2.0))
    # 2. 顶部双侧角焊缝加强条
    o_weld = BOX(s, L=B, W=max(6.0, T * 0.5), H=T * 1.65).translate((0.0, 0.0, H - max(3.0, T * 0.25)))
    o1.uniteWith(o_weld); o_weld.erase()
    # 3. 中心圆吊孔（在 Z = 0 处沿 X 轴贯穿切除）
    o_hole = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateY(90.0).translate((-(T * 2.0), 0.0, 0.0))
    o1.subtractFrom(o_hole); o_hole.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
