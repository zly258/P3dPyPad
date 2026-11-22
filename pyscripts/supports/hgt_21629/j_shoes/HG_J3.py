# -*- coding: utf-8 -*-
# HG/T 21629-2021 J3 大管焊接式管托（26"~160"）（图 C.9-3）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="大管焊接式管托（26~160）", TooltipLong="HG/T 21629-2021 J3 大管焊接式管托（26~160） 图C.9-3", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="管托腹板/鞍板厚度")
@param(HH=LENGTH0, TooltipShort="滑板厚", TooltipLong="底部耐磨滑板厚，0=无")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_J3(s, D=1016.0, SH=658.0, SL=600.0, SW=550.0, ST=16.0, HH=0.0, ID=u"J3", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 200.0: D = 711.0
    if ST < 8.0: ST = 12.0
    if SL < 120.0: SL = 350.0
    if SW < 150.0: SW = max(320.0, D * 0.58)
    R1 = D / 2.0
    if SH < (R1 + 80.0): SH = R1 + 150.0
    # 1. 大口径下部 120° 弧形焊接鞍板（O=0.0）
    o_main = CYLINDER(s, R=R1 + ST, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    o_top = BOX(s, L=(R1 + ST) * 2.4, W=(R1 + ST) * 1.4, H=SL + 10.0).translate((0.0, 0.0, (R1 + ST) * 0.55))
    o_main.subtractFrom(o_top); o_top.erase()
    # 2. 左右两侧对称斜向支承腹板与前中后 3 道横向加劲隔板
    web_h = max(40.0, SH - R1 * 0.72 - ST)
    for sy in (-1.0, 1.0):
        o_sw = BOX(s, L=ST * 1.2, W=web_h, H=SL).rotateX(sy * (-12.0)).translate((0.0, sy * (SW * 0.34), -(SH - ST - web_h / 2.0)))
        o_main.uniteWith(o_sw); o_sw.erase()
    for sx in (-(SL * 0.38), 0.0, (SL * 0.38)):
        o_dia = BOX(s, L=SW * 0.85, W=web_h * 0.85, H=ST).translate((sx, 0.0, -(SH - ST - web_h * 0.425)))
        o_main.uniteWith(o_dia); o_dia.erase()
    o_base = BOX(s, L=SW, W=ST * 1.3, H=SL).translate((0.0, 0.0, -(SH - ST * 0.65)))
    o_main.uniteWith(o_base); o_base.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
