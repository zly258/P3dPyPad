# -*- coding: utf-8 -*-
# HG/T 21629-2021 J5~J8 多向管夹式管托（1/2"~24"）（图 C.9-5）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="多向管夹式管托（1/2~24）", TooltipLong="HG/T 21629-2021 J5~J8 多向管夹式管托（1/2~24） 图C.9-5", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="管托腹板/鞍板厚度")
@param(HH=LENGTH0, TooltipShort="滑板厚", TooltipLong="底部耐磨滑板厚，0=无")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_J5(s, D=114.3, SH=157.2, SL=188.6, SW=114.3, ST=8.0, HH=6.0, ID=u"J5", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 6.0
    if SL < 40.0: SL = 100.0
    if SW < 40.0: SW = 80.0
    R1 = D / 2.0
    if SH < (R1 + ST * 2.0 + 15.0): SH = R1 + 80.0
    o_main = CYLINDER(s, R=R1 + ST, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    ear_w = ST * 4.0
    for sx in (-(SL * 0.35), (SL * 0.35)):
        o_ce = BOX(s, L=D + ear_w * 2.0, W=ST * 2.2, H=ST * 3.5).translate((sx, 0.0, 0.0))
        o_ce_i = CYLINDER(s, R=R1, H=ST * 4.0, O=0.0).rotateY(90.0).translate((sx - ST * 2.0, 0.0, 0.0))
        o_ce.subtractFrom(o_ce_i); o_ce_i.erase()
        o_main.uniteWith(o_ce); o_ce.erase()
    web_h = SH - R1 - ST
    if web_h < 15.0: web_h = 15.0
    o_web = BOX(s, L=ST, W=web_h, H=SL).translate((0.0, 0.0, -(R1 + web_h / 2.0)))
    o_base = BOX(s, L=SW, W=ST, H=SL).translate((0.0, 0.0, -(SH - ST / 2.0)))
    o_main.uniteWith(o_web); o_web.erase()
    o_main.uniteWith(o_base); o_base.erase()
    for ang in (90.0, -90.0):
        o_mw = BOX(s, L=ST, W=web_h, H=SL * 0.85).translate((0.0, 0.0, -(R1 + web_h / 2.0))).rotateX(ang)
        o_mb = BOX(s, L=SW * 0.75, W=ST, H=SL * 0.85).translate((0.0, 0.0, -(SH - ST / 2.0))).rotateX(ang)
        o_main.uniteWith(o_mw); o_mw.erase()
        o_main.uniteWith(o_mb); o_mb.erase()
    if HH > 0.1:
        o_slide = BOX(s, L=SW * 0.9, W=HH, H=SL * 0.9).translate((0.0, 0.0, -(SH + HH / 2.0)))
        o_main.uniteWith(o_slide); o_slide.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
