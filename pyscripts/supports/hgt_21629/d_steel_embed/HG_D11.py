# -*- coding: utf-8 -*-
# HG/T 21629-2021 D11 辅助柱（图 C.4-11）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="辅助柱", TooltipLong="HG/T 21629-2021 D11 辅助柱 图C.4-11", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_D11(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"D11", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 50.0: B = 125.0
    if T < 6.0: T = 9.0
    if SH < 200.0: SH = 600.0
    # 1. 竖直 H 型钢立柱（腹板与前后翼缘沿 Z 轴从 -SH 延伸至 0）
    o1 = BOX(s, L=T, W=SH, H=B).translate((0.0, 0.0, -(SH / 2.0)))
    for sy in (-(B / 2.0 - T / 2.0), (B / 2.0 - T / 2.0)):
        o_fl = BOX(s, L=T, W=SH, H=B).rotateZ(90.0).translate((0.0, sy, -(SH / 2.0)))
        o1.uniteWith(o_fl); o_fl.erase()
    # 2. 柱顶（Z=0）与柱底（Z=-SH）水平连接端板及侧向三角形加劲肋板
    for z_end, s_dir in ((0.0, -1.0), (-SH, 1.0)):
        o_cap = BOX(s, L=B * 1.6, W=T * 1.5, H=B * 1.6).translate((0.0, 0.0, z_end + s_dir * (T * 0.75)))
        o_rib = BOX(s, L=B * 1.4, W=B * 0.65, H=T).translate((0.0, 0.0, z_end + s_dir * (T * 1.5 + B * 0.325)))
        o1.uniteWith(o_cap); o_cap.erase()
        o1.uniteWith(o_rib); o_rib.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
