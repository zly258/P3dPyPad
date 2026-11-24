# -*- coding: utf-8 -*-
# HG/T 21629-2021 MF1 弯头的竖直耳轴（非金属管）（图 C.12-9）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="弯头的竖直耳轴（非金属管）", TooltipLong="HG/T 21629-2021 MF1 弯头的竖直耳轴（非金属管） 图C.12-9", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_MF1(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"MF1", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 25.0: D = 114.3
    if LEG_D < 20.0: LEG_D = max(42.4, D * 0.58)
    if ST < 5.0: ST = 9.0
    R1 = D / 2.0; R_elb = D * 1.5
    if SH < (R1 + 80.0): SH = R1 + 180.0
    R_leg = LEG_D / 2.0; R_leg_in = max(6.0, R_leg - ST)
    off = 0.2929 * R_elb
    # 1. 上部非金属 90° 弯头（ARC3D，中心弧顶置于原点 (0,0,0)）与两端承插环
    o1 = ARC3D(s, D=R1, R=R_elb, A=90.0).rotateZ(90.0).rotateX(90.0).translate((off, 0.0, -off))
    o_hub1 = CYLINDER(s, R=R1 + ST * 1.1, H=D * 0.28, O=0.0).rotateY(90.0).translate((-(R_elb - off + D * 0.14), 0.0, -off))
    o_hub2 = CYLINDER(s, R=R1 + ST * 1.1, H=D * 0.28, O=0.0).translate((off, 0.0, R_elb - off - D * 0.14))
    o1.uniteWith(o_hub1); o_hub1.erase()
    o1.uniteWith(o_hub2); o_hub2.erase()
    # 2. 弯头底部加厚包覆糊制圆台过渡领（CONE）+ 竖直耳轴支腿 + 圆形底板
    o_cone = CONE(s, R1=R_leg * 1.35, R2=R1 * 0.95, H=R1 * 1.1, E=0.0).translate((0.0, 0.0, -(R1 * 1.05)))
    leg_h = max(35.0, SH - ST)
    o_leg = CYLINDER(s, R=R_leg, H=leg_h, O=0.0).translate((0.0, 0.0, -(SH - ST)))
    o_leg_i = CYLINDER(s, R=R_leg_in, H=leg_h, O=0.0).translate((0.0, 0.0, -(SH - ST)))
    o_leg.subtractFrom(o_leg_i); o_leg_i.erase()
    o_base = CYLINDER(s, R=LEG_D * 1.15, H=ST * 1.6, O=0.0).translate((0.0, 0.0, -SH))
    for p in (o_cone, o_leg, o_base):
        o1.uniteWith(p); p.erase()
    # 3. 切除弯头内部流道与两端承插口内孔
    r_in = max(6.0, R1 - ST)
    o_elb_i = ARC3D(s, D=r_in, R=R_elb, A=90.0).rotateZ(90.0).rotateX(90.0).translate((off, 0.0, -off))
    o1.subtractFrom(o_elb_i); o_elb_i.erase()
    o_h1_i = CYLINDER(s, R=r_in, H=D * 0.4, O=0.0).rotateY(90.0).translate((-(R_elb - off + D * 0.2), 0.0, -off))
    o1.subtractFrom(o_h1_i); o_h1_i.erase()
    o_h2_i = CYLINDER(s, R=r_in, H=D * 0.4, O=0.0).translate((off, 0.0, R_elb - off - D * 0.2))
    o1.subtractFrom(o_h2_i); o_h2_i.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
