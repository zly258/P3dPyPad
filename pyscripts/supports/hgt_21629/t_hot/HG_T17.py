# -*- coding: utf-8 -*-
# HG/T 21629-2021 T17~T18 8"及以上立管用焊接式高温隔热管托（图 C.18-11）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="8及以上立管用焊接式高温隔热管托", TooltipLong="HG/T 21629-2021 T17~T18 8及以上立管用焊接式高温隔热管托 图C.18-11", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线隔热托长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="隔热厚", TooltipLong="管托耐高温隔热瓦层厚度")
@param(HH=LENGTH0, TooltipShort="滑板厚", TooltipLong="底部滑板厚度，0=无")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_T17(s, D=508.0, SH=409.0, SL=612.6, SW=400.8, ST=80.0, HH=0.0, ID=u"T17", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 100.0: D = 219.1
    if ST < 15.0: ST = 40.0
    if SL < 80.0: SL = 220.0
    if SW < 60.0: SW = 120.0
    R1 = D / 2.0; t_p = 10.0
    if SH < (R1 + 70.0): SH = R1 + 140.0
    pipe_h = SL * 1.4
    # 1. 竖直立管沿 Z 轴（O=0.0）与环向补强板
    o_main = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0)))
    o_in = CYLINDER(s, R=max(10.0, R1 - t_p), H=pipe_h + 4.0, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0 + 2.0)))
    o_main.subtractFrom(o_in); o_in.erase()
    # 2. 立管外壁四向对称焊接 H 形承重支座 + 底部嵌装耐高温平板隔热块
    wing_l = max(55.0, SH - R1)
    ins_t = min(ST * 0.7, SL * 0.25)
    for ang in (0.0, 90.0, 180.0, 270.0):
        yc = R1 + wing_l / 2.0
        o_w = BOX(s, L=wing_l, W=SL * 0.7, H=t_p).translate((0.0, yc, 0.0)).rotateZ(ang)
        o_fl = BOX(s, L=t_p * 1.4, W=SL * 0.7, H=SW * 0.7).translate((0.0, R1 + wing_l, 0.0)).rotateZ(ang)
        o_ins = BOX(s, L=wing_l * 0.9, W=ins_t, H=SW * 0.75).translate((0.0, yc, -(SL * 0.35 + ins_t / 2.0))).rotateZ(ang)
        o_bp = BOX(s, L=wing_l * 1.05, W=t_p * 1.3, H=SW * 0.85).translate((0.0, yc, -(SL * 0.35 + ins_t + t_p * 0.65))).rotateZ(ang)
        for p in (o_w, o_fl, o_ins, o_bp):
            o_main.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
