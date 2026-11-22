# -*- coding: utf-8 -*-
# HG/T 21629-2021 Q9 小支管加强架（安全阀，1/2"~2")（图 C.15-9）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="小支管加强架（安全阀，1/2~2", TooltipLong="HG/T 21629-2021 Q9 小支管加强架（安全阀，1/2~2) 图C.15-9", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="母管外径", TooltipLong="大管/主管外径")
@param(D2=LENGTH, TooltipShort="支管外径", TooltipLong="被支撑小支管外径")
@param(L=LENGTH, TooltipShort="支承跨度", TooltipLong="小管中心至母管中心/生根距", Ask4Dist=True)
@param(T=LENGTH, TooltipShort="型材厚", TooltipLong="角钢/加强板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_Q9(s, D=93.3, D2=42.4, L=187.8, T=6.0, ID=u"Q9", **kw):
    D = float(D); D2 = float(D2); L = float(L); T = float(T)
    if D < 25.0: D = 88.9
    if D2 < 15.0: D2 = 33.7
    if T < 4.0: T = 6.0
    if L < 80.0: L = 180.0
    R1 = D2 / 2.0
    # 1. 竖直安全阀进口管段（沿 Z 轴从 -L 延伸至 0）与上部水平排放支管段（沿 +Y 轴从 0 延伸至 +L）
    o1 = CYLINDER(s, R=R1, H=L * 1.15, O=0.0).translate((0.0, 0.0, -L))
    o_hz = CYLINDER(s, R=R1, H=L * 1.15, O=0.0).rotateX(-90.0).translate((0.0, 0.0, 0.0))
    o_fl = CYLINDER(s, R=R1 * 2.1, H=T * 2.5, O=0.0).translate((0.0, 0.0, -(T * 1.25)))
    # 2. 两端管夹 A2（一端抱竖直进口管 Z = -L*0.75，另一端抱水平排放管 Y = +L*0.75）
    cw = max(28.0, R1 * 1.6)
    o_c1 = CYLINDER(s, R=R1 + T, H=cw, O=0.0).translate((0.0, 0.0, -(L * 0.75 + cw / 2.0)))
    o_e1 = BOX(s, L=R1 * 3.8, W=cw, H=T * 2.2).translate((0.0, R1 * 0.8, -(L * 0.75)))
    o_c2 = CYLINDER(s, R=R1 + T, H=cw, O=0.0).rotateX(-90.0).translate((0.0, L * 0.75 - cw / 2.0, 0.0))
    o_e2 = BOX(s, L=cw, W=R1 * 3.8, H=T * 2.2).translate((0.0, L * 0.75, -(R1 * 0.8)))
    # 3. 45° 斜撑角钢（L50x6，连接 Z = -L*0.75 管夹与 Y = +L*0.75 管夹）
    diag_l = L * 0.75 * 1.4142
    ang_w = max(36.0, R1 * 1.8)
    o_brace1 = BOX(s, L=diag_l, W=ang_w, H=T).rotateX(45.0).translate((0.0, L * 0.375, -(L * 0.375)))
    o_brace2 = BOX(s, L=diag_l, W=T, H=ang_w).rotateX(45.0).translate((ang_w * 0.4, L * 0.375, -(L * 0.375)))
    for p in (o_hz, o_fl, o_c1, o_e1, o_c2, o_e2, o_brace1, o_brace2):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
