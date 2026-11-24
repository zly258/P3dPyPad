# -*- coding: utf-8 -*-
# HG/T 21629-2021 L6 保冷管道的耳轴型限位架（3"～72"，大荷载，非首选）（图 C.11-6）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="保冷管道的耳轴型限位架（3～72", TooltipLong="HG/T 21629-2021 L6 保冷管道的耳轴型限位架（3～72，大荷载，非首选） 图C.11-6", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_L6(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"L6", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 60.0: D = 114.3
    if LEG_D < 25.0: LEG_D = max(48.3, D * 0.5)
    if ST < 5.0: ST = 8.0
    R1 = D / 2.0; R_leg = LEG_D / 2.0
    if SH < (R1 + 60.0): SH = R1 + 130.0
    pipe_l = max(180.0, D * 1.5)
    # 1. 中央水平母管段（沿 X 轴，O=0.0）
    o1 = CYLINDER(s, R=R1, H=pipe_l, O=0.0).rotateY(90.0).translate((-(pipe_l / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=max(8.0, R1 - ST), H=pipe_l + 4.0, O=0.0).rotateY(90.0).translate((-(pipe_l / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    # 2. 左右两侧水平伸出耳轴 + 耳轴外包保冷圆筒 + 左右两座 H 型限位支座
    tr_span = R1 + LEG_D * 1.8
    for sy in (-1.0, 1.0):
        o_tr = CYLINDER(s, R=R_leg, H=tr_span, O=0.0).rotateX(-90.0 * sy).translate((0.0, sy * R1 * 0.7, 0.0))
        o_cold = CYLINDER(s, R=R_leg * 1.65, H=LEG_D * 1.3, O=0.0).rotateX(-90.0 * sy).translate((0.0, sy * (R1 + LEG_D * 0.45), 0.0))
        yc_ped = sy * (R1 + LEG_D * 1.1)
        ped_h = SH - R_leg * 1.2
        o_ped = BOX(s, L=LEG_D * 1.5, W=ped_h, H=LEG_D * 1.6).translate((0.0, yc_ped, -(SH - ped_h / 2.0)))
        o_bp = BOX(s, L=LEG_D * 2.1, W=ST * 1.5, H=LEG_D * 2.1).translate((0.0, yc_ped, -(SH - ST * 0.75)))
        for p in (o_tr, o_cold, o_ped, o_bp):
            o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
