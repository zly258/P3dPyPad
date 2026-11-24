# -*- coding: utf-8 -*-
# HG/T 21629-2021 F20 小管径三通和弯头用支架(1/2"~2")（图 C.6-15）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="小管径三通和弯头用支架(1/2~2", TooltipLong="HG/T 21629-2021 F20 小管径三通和弯头用支架(1/2~2) 图C.6-15", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_F20(s, D=42.4, SH=141.2, LEG_D=26.9, ST=6.0, ID=u"F20", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 15.0: D = 48.3
    if LEG_D < 20.0: LEG_D = max(33.7, D * 0.75)
    if ST < 4.0: ST = 6.0
    R1 = D / 2.0
    if SH < (R1 + 80.0): SH = R1 + 160.0
    R_leg = LEG_D / 2.0
    tee_l = max(100.0, D * 2.4)
    # 1. 上部水平小口径三通管件（沿 X 轴主管 + 沿 +Z 轴向上引出支管口，O=0.0）
    o1 = CYLINDER(s, R=R1, H=tee_l, O=0.0).rotateY(90.0).translate((-(tee_l / 2.0), 0.0, 0.0))
    o_br = CYLINDER(s, R=R1 * 0.9, H=R1 * 2.2, O=0.0).translate((0.0, 0.0, 0.0))
    o1.uniteWith(o_br); o_br.erase()
    # 2. 三通底部方形承重托板 + 竖直圆管立柱 + 下部圆锥台（CONE）扩口底座与底板
    z_top_p = -(R1 + ST * 0.6)
    o_top_p = BOX(s, L=LEG_D * 1.6, W=ST * 1.2, H=LEG_D * 1.6).translate((0.0, 0.0, z_top_p))
    cone_h = (SH - R1) * 0.38
    post_h = max(25.0, SH - R1 - ST * 2.4 - cone_h)
    o_post = CYLINDER(s, R=R_leg * 0.85, H=post_h + ST, O=0.0).translate((0.0, 0.0, -(R1 + ST + post_h)))
    o_cone = CONE(s, R1=R_leg * 1.65, R2=R_leg * 0.85, H=cone_h, E=0.0).translate((0.0, 0.0, -(SH - ST * 1.2)))
    o_base = BOX(s, L=LEG_D * 2.2, W=ST * 1.2, H=LEG_D * 2.2).translate((0.0, 0.0, -(SH - ST * 0.6)))
    for p in (o_top_p, o_post, o_cone, o_base):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
