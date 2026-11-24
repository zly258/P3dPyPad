# -*- coding: utf-8 -*-
# HG/T 21629-2021 T9~T12 双管夹式多向高温隔热管托（1/2"～48"）（图 C.18-9）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="双管夹式多向高温隔热管托（1/2～", TooltipLong="HG/T 21629-2021 T9~T12 双管夹式多向高温隔热管托（1/2～48） 图C.18-9", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线隔热托长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="隔热厚", TooltipLong="管托耐高温隔热瓦层厚度")
@param(HH=LENGTH0, TooltipShort="滑板厚", TooltipLong="底部滑板厚度，0=无")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_T9(s, D=114.3, SH=192.2, SL=238.6, SW=140.6, ST=60.0, HH=6.0, ID=u"T9", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 15.0: D = 114.3
    if ST < 15.0: ST = 45.0
    if SL < 80.0: SL = 200.0
    if SW < 50.0: SW = 110.0
    R1 = D / 2.0; t_p = 8.0; R_hot = R1 + ST
    if SH < (R_hot + 35.0): SH = R_hot + 75.0
    o_main = CYLINDER(s, R=R_hot + t_p, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 6.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 3.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    leg_h = max(18.0, SH - R_hot - t_p)
    for ang in (0.0, 90.0, 180.0, 270.0):
        o_w = BOX(s, L=t_p * 1.4, W=leg_h, H=SL * 0.85).translate((0.0, 0.0, -(R_hot + leg_h / 2.0))).rotateX(ang)
        o_b = BOX(s, L=SW * 0.82, W=t_p * 1.3, H=SL * 0.9).translate((0.0, 0.0, -(SH - t_p * 0.65))).rotateX(ang)
        o_main.uniteWith(o_w); o_w.erase()
        o_main.uniteWith(o_b); o_b.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
