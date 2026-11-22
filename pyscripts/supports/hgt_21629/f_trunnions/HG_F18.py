# -*- coding: utf-8 -*-
# HG/T 21629-2021 F18 虾米弯支座（图 C.6-13）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="虾米弯支座", TooltipLong="HG/T 21629-2021 F18 虾米弯支座 图C.6-13", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_F18(s, D=114.3, SH=177.2, LEG_D=62.9, ST=8.0, ID=u"F18", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 25.0: D = 114.3
    if LEG_D < 25.0: LEG_D = max(50.0, D * 0.5)
    if ST < 6.0: ST = 10.0
    R1 = D / 2.0; R_elb = D * 1.5
    if SH < (R1 + 80.0): SH = R1 + 160.0
    off = 0.2929 * R_elb
    # 1. 上部 3 节斜接虾米弯头（使用原生 ARC3DS S=3）
    o1 = ARC3DS(s, D=R1, R=R_elb, A=90.0, S=3).rotateZ(90.0).rotateX(90.0).translate((off, 0.0, -off))
    # 2. 底部竖直主撑板（沿弯头平面 XZ 布置）与横向斜托板（贴合虾米弯外弧）
    web_h = SH
    base_b = max(LEG_D * 1.6, D * 0.85)
    base_e = max(60.0, base_b * 0.55)
    o_web = BOX(s, L=ST * 1.4, W=web_h, H=base_b * 1.15).translate((0.0, 0.0, -(SH / 2.0)))
    o_lhole = CYLINDER(s, R=max(10.0, ST * 1.2), H=ST * 5.0, O=0.0).rotateX(90.0).translate((-(base_b * 0.28), ST * 2.5, -(SH * 0.55)))
    o_web.subtractFrom(o_lhole); o_lhole.erase()
    o_tray = BOX(s, L=base_e * 1.6, W=web_h * 0.85, H=ST * 1.4).rotateY(-28.0).translate((0.0, 0.0, -(SH * 0.48)))
    # 3. 底部矩形承重底板
    o_base = BOX(s, L=base_e * 1.8, W=ST * 1.5, H=base_b * 1.2).translate((0.0, 0.0, -(SH - ST * 0.75)))
    for p in (o_web, o_tray, o_base):
        o1.uniteWith(p); p.erase()
    # 4. 切除虾米弯内腔（同时修剪伸入弯头内部的撑板）
    o_in = ARC3DS(s, D=max(5.0, R1 - ST), R=R_elb, A=90.0, S=3).rotateZ(90.0).rotateX(90.0).translate((off, 0.0, -off))
    o1.subtractFrom(o_in); o_in.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
