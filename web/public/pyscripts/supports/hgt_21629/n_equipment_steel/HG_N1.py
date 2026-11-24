# -*- coding: utf-8 -*-
# HG/T 21629-2021 N1 设备上生根的单悬臂架（图 C.13-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="设备上生根的单悬臂架", TooltipLong="HG/T 21629-2021 N1 设备上生根的单悬臂架 图C.13-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="支承管道外径")
@param(L=LENGTH, TooltipShort="悬臂长", TooltipLong="悬臂挑出总长度", Ask4Dist=True)
@param(SH=LENGTH, TooltipShort="截面高", TooltipLong="悬臂根部高度或立柱高")
@param(B=LENGTH, TooltipShort="截面宽", TooltipLong="型钢截面宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="型钢腹板/翼缘厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_N1(s, D=114.3, L=750.0, SH=600.0, B=100.0, T=10.0, ID=u"N1", **kw):
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
    eq_r = max(400.0, L * 1.2)
    o_eq = CYLINDER(s, R=eq_r + T * 1.5, H=SH * 1.1, O=0.0).translate((0.0, -(L + eq_r), -(SH * 1.05)))
    o_eq_i = CYLINDER(s, R=eq_r, H=SH * 1.1 + 4.0, O=0.0).translate((0.0, -(L + eq_r), -(SH * 1.05 + 2.0)))
    o_eq.subtractFrom(o_eq_i); o_eq_i.erase()
    o_eq_b = BOX(s, L=B * 2.2, W=SH * 1.1, H=B * 2.5).translate((0.0, -L, -(SH * 0.5)))
    o_eq.intersectWith(o_eq_b); o_eq_b.erase()
    o1.uniteWith(o_eq); o_eq.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
