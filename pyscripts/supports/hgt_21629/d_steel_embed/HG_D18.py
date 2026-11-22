# -*- coding: utf-8 -*-
# HG/T 21629-2021 D18 双角钢/槽钢悬臂架（图 C.4-18）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="双角钢/槽钢悬臂架", TooltipLong="HG/T 21629-2021 D18 双角钢/槽钢悬臂架 图C.4-18", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(L=LENGTH, TooltipShort="悬臂长", TooltipLong="悬臂挑出总长度", Ask4Dist=True)
@param(SH=LENGTH, TooltipShort="截面高", TooltipLong="悬臂根部高度或立柱高")
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢腹板/翼缘厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_D18(s, D=114.3, L=750.0, SH=600.0, B=100.0, T=10.0, ID=u"D18", **kw):
    D = float(D); L = float(L); SH = float(SH); B = float(B); T = float(T)
    if D < 15.0: D = 60.3
    if B < 40.0: B = 80.0
    if T < 5.0: T = 8.0
    if L < 150.0: L = 350.0
    if SH < 80.0: SH = 200.0
    R1 = D / 2.0; z_arm = -(R1 + B / 2.0); gap = T * 2.0
    o1 = BOX(s, L=L, W=B, H=T).translate((-(gap / 2.0 + T / 2.0), -(L / 2.0), z_arm))
    o_b2 = BOX(s, L=L, W=B, H=T).translate(((gap / 2.0 + T / 2.0), -(L / 2.0), z_arm))
    o_root = BOX(s, L=T * 1.6, W=SH, H=B * 1.8).translate((0.0, -L, z_arm))
    for yf in (-L * 0.15, -L * 0.5, -L * 0.85):
        o_bat = BOX(s, L=B * 0.6, W=B * 0.85, H=gap + T * 2.0).translate((0.0, yf, z_arm))
        o1.uniteWith(o_bat); o_bat.erase()
    o1.uniteWith(o_b2); o_b2.erase()
    o1.uniteWith(o_root); o_root.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
