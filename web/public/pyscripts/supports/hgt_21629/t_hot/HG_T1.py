# -*- coding: utf-8 -*-
# HG/T 21629-2021 T1 双管夹式高温隔热管托（1/2"～48")（图 C.18-1）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="双管夹式高温隔热管托（1/2～48", TooltipLong="HG/T 21629-2021 T1 双管夹式高温隔热管托（1/2～48) 图C.18-1", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线隔热托长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="隔热厚", TooltipLong="管托耐高温隔热瓦层厚度")
@param(HH=LENGTH0, TooltipShort="滑板厚", TooltipLong="底部滑板厚度，0=无")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_T1(s, D=114.3, SH=192.2, SL=238.6, SW=140.6, ST=60.0, HH=0.0, ID=u"T1", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 15.0: D = 114.3
    if ST < 15.0: ST = 45.0
    if SL < 80.0: SL = 200.0
    if SW < 50.0: SW = 110.0
    R1 = D / 2.0; t_p = 8.0; R_hot = R1 + ST
    if SH < (R_hot + 35.0): SH = R_hot + 80.0
    # 1. 内层微孔硅酸钙耐高温隔热瓦层（O=0.0）
    o_main = CYLINDER(s, R=R_hot, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    # 2. 前后两道独立双螺栓外管夹（位于 X = ±SL*0.28）
    cw = max(32.0, SL * 0.22)
    for sx in (-(SL * 0.28), (SL * 0.28)):
        o_cl = CYLINDER(s, R=R_hot + t_p, H=cw, O=0.0).rotateY(90.0).translate((sx - cw / 2.0, 0.0, 0.0))
        o_ear = BOX(s, L=(R_hot + t_p * 5.0) * 2.0, W=t_p * 2.2, H=cw).translate((sx, 0.0, 0.0))
        o_main.uniteWith(o_cl); o_cl.erase()
        o_main.uniteWith(o_ear); o_ear.erase()
    o_in = CYLINDER(s, R=R1, H=SL + 6.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 3.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    # 3. 下部T形腹板与底板
    web_h = max(20.0, SH - R_hot - t_p)
    o_web = BOX(s, L=t_p * 1.2, W=web_h, H=SL * 0.85).translate((0.0, 0.0, -(R_hot + web_h / 2.0)))
    o_base = BOX(s, L=SW, W=t_p * 1.4, H=SL * 0.92).translate((0.0, 0.0, -(SH - t_p * 0.7)))
    o_main.uniteWith(o_web); o_web.erase()
    o_main.uniteWith(o_base); o_base.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
