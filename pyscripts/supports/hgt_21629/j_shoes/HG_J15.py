# -*- coding: utf-8 -*-
# HG/T 21629-2021 J15~J16 8"及以上立管用焊接式管托（图 C.9-9）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="8及以上立管用焊接式管托", TooltipLong="HG/T 21629-2021 J15~J16 8及以上立管用焊接式管托 图C.9-9", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="管托腹板/鞍板厚度")
@param(HH=LENGTH0, TooltipShort="滑板厚", TooltipLong="底部耐磨滑板厚，0=无")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_J15(s, D=508.0, SH=404.0, SL=562.6, SW=370.2, ST=12.0, HH=0.0, ID=u"J15", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 100.0: D = 219.1
    if ST < 6.0: ST = 10.0
    if SL < 80.0: SL = 220.0
    if SW < 60.0: SW = 120.0
    R1 = D / 2.0
    if SH < (R1 + 50.0): SH = R1 + 110.0
    # 1. 竖直立管段沿 Z 轴（O=0.0 空心圆管）与弧形补强板圈
    pipe_h = SL * 1.4
    o_main = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0)))
    o_in = CYLINDER(s, R=max(10.0, R1 - ST), H=pipe_h + 4.0, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0 + 2.0)))
    o_main.subtractFrom(o_in); o_in.erase()
    o_pad = CYLINDER(s, R=R1 + ST, H=SL, O=0.0).translate((0.0, 0.0, -(SL / 2.0)))
    o_pad_i = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).translate((0.0, 0.0, -(SL / 2.0 + 2.0)))
    o_pad.subtractFrom(o_pad_i); o_pad_i.erase()
    o_main.uniteWith(o_pad); o_pad.erase()
    # 2. 立管外壁四向对称焊接 4 组 H 形承重支座翼（每侧含腹板与外端承重翼板）
    wing_l = max(45.0, SH - R1)
    for ang in (0.0, 90.0, 180.0, 270.0):
        o_w = BOX(s, L=wing_l, W=SL * 0.78, H=ST * 1.2).translate((0.0, R1 + ST + wing_l / 2.0, 0.0)).rotateZ(ang)
        o_fl = BOX(s, L=ST * 1.4, W=SL * 0.78, H=SW * 0.65).translate((0.0, R1 + ST + wing_l, 0.0)).rotateZ(ang)
        o_bot = BOX(s, L=wing_l, W=ST * 1.4, H=SW * 0.65).translate((0.0, R1 + ST + wing_l / 2.0, -(SL * 0.39))).rotateZ(ang)
        for p in (o_w, o_fl, o_bot):
            o_main.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
