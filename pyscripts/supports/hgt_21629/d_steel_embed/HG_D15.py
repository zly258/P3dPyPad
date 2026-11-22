# -*- coding: utf-8 -*-
# HG/T 21629-2021 D15 水平T形架（图 C.4-15）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="水平T形架", TooltipLong="HG/T 21629-2021 D15 水平T形架 图C.4-15", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(SPAN=LENGTH, TooltipShort="跨距", TooltipLong="门形/三角/横担跨距或宽度")
@param(SH=LENGTH, TooltipShort="架高", TooltipLong="立柱高度或生根距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面高度/翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢壁厚/连接板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_D15(s, D=114.3, SPAN=750.0, SH=600.0, B=100.0, T=10.0, ID=u"D15", **kw):
    D = float(D); SPAN = float(SPAN); SH = float(SH); B = float(B); T = float(T)
    if B < 40.0: B = 100.0
    if T < 5.0: T = 8.0
    if SPAN < 180.0: SPAN = 450.0
    if SH < 150.0: SH = 350.0
    R1 = D / 2.0; z_plane = -(R1 + B / 2.0)
    # 1. 沿 Y 轴悬挑的水平 H 型钢主干梁（从根部 Y = -SH 延伸至前端 Y = 0）
    o1 = BOX(s, L=SH, W=B, H=T).translate((0.0, -(SH / 2.0), z_plane))
    o_mf1 = BOX(s, L=SH, W=T, H=B).translate((0.0, -(SH / 2.0), z_plane + B / 2.0 - T / 2.0))
    o_mf2 = BOX(s, L=SH, W=T, H=B).translate((0.0, -(SH / 2.0), z_plane - B / 2.0 + T / 2.0))
    # 2. 前端（Y = 0）沿 X 轴正交水平布置的 H 型钢横担梁（长 SPAN）
    o_cross = BOX(s, L=B, W=B, H=SPAN).translate((0.0, B / 2.0, z_plane))
    # 3. 根部（Y = -SH）焊接于钢柱侧面的竖直安装端板与水平腋角板
    o_root = BOX(s, L=T * 1.5, W=B * 1.8, H=B * 1.8).translate((0.0, -SH, z_plane))
    for sx in (-1.0, 1.0):
        o_hgus = BOX(s, L=B * 1.2, W=T, H=B * 1.2).translate((sx * (B * 0.9), -(B * 0.4), z_plane))
        o1.uniteWith(o_hgus); o_hgus.erase()
    for p in (o_mf1, o_mf2, o_cross, o_root):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
