# -*- coding: utf-8 -*-
# HG/T 21629-2021 F4 竖直弯头的水平耳轴（图 C.6-4）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="竖直弯头的水平耳轴", TooltipLong="HG/T 21629-2021 F4 竖直弯头的水平耳轴 图C.6-4", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_F4(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"F4", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 25.0: D = 114.3
    if LEG_D < 20.0: LEG_D = max(33.7, D * 0.55)
    if ST < 4.0: ST = 8.0
    R1 = D / 2.0; R_elb = D * 1.5
    if SH < (R1 + 80.0): SH = R1 + 180.0
    R_leg = LEG_D / 2.0; R_leg_in = max(5.0, R_leg - ST)
    off = 0.2929 * R_elb
    # 1. 90° 弯头本体（ARC3D，中心弧顶置于原点 (0,0,0)）
    o1 = ARC3D(s, D=R1, R=R_elb, A=90.0).rotateZ(90.0).rotateX(90.0).translate((off, 0.0, -off))
    # 2. 弯头外弧面水平伸出的圆管耳轴（沿 +X 轴水平伸出至 SH）与补强环、端盖板
    o_pad = CYLINDER(s, R=R_leg + ST * 1.8, H=R1 + ST * 2.0, O=0.0).rotateY(90.0)
    o_tr = CYLINDER(s, R=R_leg, H=SH, O=0.0).rotateY(90.0)
    o_tr_i = CYLINDER(s, R=R_leg_in, H=SH, O=0.0).rotateY(90.0).translate((R1, 0.0, 0.0))
    o_tr.subtractFrom(o_tr_i); o_tr_i.erase()
    o_cap = BOX(s, L=LEG_D * 1.6, W=LEG_D * 1.6, H=ST * 1.4).translate((SH, 0.0, 0.0))
    for p in (o_pad, o_tr, o_cap):
        o1.uniteWith(p); p.erase()
    # 3. 切除弯头内部流道（同时修剪耳轴根部使其贴合弯头外壁）
    o_elb_i = ARC3D(s, D=max(5.0, R1 - ST), R=R_elb, A=90.0).rotateZ(90.0).rotateX(90.0).translate((off, 0.0, -off))
    o1.subtractFrom(o_elb_i); o_elb_i.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (SH, 0.0, 0.0))
