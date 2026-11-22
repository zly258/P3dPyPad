# -*- coding: utf-8 -*-
# HG/T 21629-2021 G11 混凝土上生根的悬臂架（图 C.7-11）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="混凝土上生根的悬臂架", TooltipLong="HG/T 21629-2021 G11 混凝土上生根的悬臂架 图C.7-11", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(L=LENGTH, TooltipShort="悬臂长", TooltipLong="悬臂挑出总长度", Ask4Dist=True)
@param(SH=LENGTH, TooltipShort="截面高", TooltipLong="悬臂根部高度或立柱高")
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢腹板/翼缘厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_G11(s, D=114.3, L=750.0, SH=600.0, B=100.0, T=10.0, ID=u"G11", **kw):
    D = float(D); L = float(L); SH = float(SH); B = float(B); T = float(T)
    if D < 15.0: D = 15.0
    if B < 40.0: B = 80.0
    if T < 4.0: T = 8.0
    if L < 120.0: L = 300.0
    if SH < 80.0: SH = 200.0
    R1 = D / 2.0
    z_arm = -(R1 + B / 2.0)
    o1 = BOX(s, L=L, W=B, H=T).translate((0.0, -(L / 2.0), z_arm))
    o_f1 = BOX(s, L=L, W=T, H=B).translate((0.0, -(L / 2.0), z_arm + B / 2.0 - T / 2.0))
    o_f2 = BOX(s, L=L, W=T, H=B).translate((0.0, -(L / 2.0), z_arm - B / 2.0 + T / 2.0))
    o1.uniteWith(o_f1); o_f1.erase()
    o1.uniteWith(o_f2); o_f2.erase()
    o_root = BOX(s, L=T * 1.6, W=SH, H=B * 1.6).translate((0.0, -L, -(SH / 2.0)))
    o_brace = BOX(s, L=L * 0.45, W=B * 0.6, H=T).rotateX(-35.0).translate((0.0, -(L * 0.78), -(R1 + B + SH * 0.22)))
    o1.uniteWith(o_root); o_root.erase()
    o1.uniteWith(o_brace); o_brace.erase()
    for sz_b in (-(SH * 0.32), -(SH * 0.68)):
        for sx_b in (-(B * 0.55), (B * 0.55)):
            o_anc = CYLINDER(s, R=T * 0.8, H=B * 1.2, O=0.0).rotateX(90.0).translate((sx_b, -L, sz_b))
            o1.uniteWith(o_anc); o_anc.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
