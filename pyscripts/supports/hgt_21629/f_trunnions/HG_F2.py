# -*- coding: utf-8 -*-
# HG/T 21629-2021 F2 弯头的竖直耳轴（图 C.6-2）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="弯头的竖直耳轴", TooltipLong="HG/T 21629-2021 F2 弯头的竖直耳轴 图C.6-2", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_F2(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"F2", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 25.0: D = 114.3
    if LEG_D < 20.0: LEG_D = max(33.7, D * 0.55)
    if ST < 4.0: ST = 8.0
    R1 = D / 2.0; R_elb = D * 1.5
    if SH < (R1 + 80.0): SH = R1 + 180.0
    R_leg = LEG_D / 2.0; R_leg_in = max(5.0, R_leg - ST)
    off = 0.2929 * R_elb
    # 1. 上部 90° 弯头本体（使用 ARC3D，中心弧顶置于原点 (0,0,0)）
    o1 = ARC3D(s, D=R1, R=R_elb, A=90.0).rotateZ(90.0).rotateX(90.0).translate((off, 0.0, -off))
    # 2. 弯头外弧面马鞍形补强圈与下部竖直圆管耳轴支腿（先与弯头并集，再切弯头内腔形成真实马鞍面）
    o_pad = CYLINDER(s, R=R_leg + ST * 1.8, H=R1 + ST * 2.0, O=0.0).translate((0.0, 0.0, -(R1 + ST)))
    leg_h = max(35.0, SH - ST)
    o_leg = CYLINDER(s, R=R_leg, H=leg_h, O=0.0).translate((0.0, 0.0, -(SH - ST)))
    o_leg_i = CYLINDER(s, R=R_leg_in, H=leg_h, O=0.0).translate((0.0, 0.0, -(SH - ST)))
    o_leg.subtractFrom(o_leg_i); o_leg_i.erase()
    # 3. 底部方形底板
    o_base = BOX(s, L=LEG_D * 2.0, W=ST * 1.4, H=LEG_D * 2.0).translate((0.0, 0.0, -(SH - ST * 0.7)))
    for p in (o_pad, o_leg, o_base):
        o1.uniteWith(p); p.erase()
    # 4. 切除弯头内部流道（同时将伸入弯头内腔的支腿上端修剪成贴合马鞍面）
    o_elb_in = ARC3D(s, D=max(5.0, R1 - ST), R=R_elb, A=90.0).rotateZ(90.0).rotateX(90.0).translate((off, 0.0, -off))
    o1.subtractFrom(o_elb_in); o_elb_in.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
