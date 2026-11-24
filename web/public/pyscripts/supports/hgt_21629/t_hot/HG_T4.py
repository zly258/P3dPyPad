# -*- coding: utf-8 -*-
# HG/T 21629-2021 T4 高温隔热限位管托（1/2"～48"）（图 C.18-4）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="高温隔热限位管托（1/2～48）", TooltipLong="HG/T 21629-2021 T4 高温隔热限位管托（1/2～48） 图C.18-4", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线隔热托长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="隔热厚", TooltipLong="管托耐高温隔热瓦层厚度")
@param(HH=LENGTH0, TooltipShort="滑板厚", TooltipLong="底部滑板厚度，0=无")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_T4(s, D=114.3, SH=192.2, SL=238.6, SW=140.6, ST=60.0, HH=0.0, ID=u"T4", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 15.0: D = 15.0
    if ST < 15.0: ST = 40.0
    if SL < 60.0: SL = 180.0
    if SW < 50.0: SW = 100.0
    R1 = D / 2.0
    if SH < (R1 + ST + 30.0): SH = R1 + ST + 80.0
    t_plate = 8.0
    R_hot = R1 + ST
    o_main = CYLINDER(s, R=R_hot, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    o_clp = CYLINDER(s, R=R_hot + t_plate, H=SL * 0.78, O=0.0).rotateY(90.0).translate((-(SL * 0.39), 0.0, 0.0))
    o_clp_i = CYLINDER(s, R=R_hot, H=SL * 0.78 + 4.0, O=0.0).rotateY(90.0).translate((-(SL * 0.39 + 2.0), 0.0, 0.0))
    o_clp.subtractFrom(o_clp_i); o_clp_i.erase()
    o_main.uniteWith(o_clp); o_clp.erase()
    for sy in (-1.0, 1.0):
        o_ear = BOX(s, L=t_plate * 4.5, W=t_plate * 2.2, H=SL * 0.78).translate((0.0, sy * (R_hot + t_plate * 2.2), 0.0))
        o_main.uniteWith(o_ear); o_ear.erase()
    web_h = max(20.0, SH - R_hot - t_plate)
    o_web = BOX(s, L=t_plate * 1.2, W=web_h, H=SL * 0.85).translate((0.0, 0.0, -(R_hot + web_h / 2.0)))
    o_base = BOX(s, L=SW, W=t_plate * 1.4, H=SL * 0.9).translate((0.0, 0.0, -(SH - t_plate * 0.7)))
    o_main.uniteWith(o_web); o_web.erase()
    o_main.uniteWith(o_base); o_base.erase()
    for sx in (-1.0, 1.0):
        o_st = BOX(s, L=SW * 1.05, W=web_h, H=t_plate * 1.6).translate((sx * (SL * 0.42), 0.0, -(SH - t_plate - web_h / 2.0)))
        o_main.uniteWith(o_st); o_st.erase()
    if HH > 0.1:
        o_sl = BOX(s, L=SW * 0.9, W=HH, H=SL * 0.85).translate((0.0, 0.0, -(SH + HH / 2.0)))
        o_main.uniteWith(o_sl); o_sl.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
