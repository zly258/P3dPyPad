# -*- coding: utf-8 -*-
# HG/T 21629-2021 ME1 立管用导向承重架（1/2"~24"，非金属管）（图 C.12-8）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="立管用导向承重架（1/2~24，", TooltipLong="HG/T 21629-2021 ME1 立管用导向承重架（1/2~24，非金属管） 图C.12-8", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至导向底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="导向长", TooltipLong="沿管道轴线导向座长度")
@param(SW=LENGTH, TooltipShort="导向宽", TooltipLong="导向底座总宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="导向翼板与底板厚度")
@param(GW=LENGTH, TooltipShort="导向间隙", TooltipLong="导向板与管托/管道单侧间隙")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_ME1(s, D=114.3, SH=142.2, SL=177.2, SW=171.4, ST=8.0, GW=3.0, ID=u"ME1", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); GW = float(GW)
    if D < 20.0: D = 114.3
    if ST < 5.0: ST = 8.0
    if SL < 80.0: SL = 180.0
    if SW < (D + 50.0): SW = D + 100.0
    R1 = D / 2.0
    if SH < (R1 + 60.0): SH = R1 + 140.0
    # 1. 竖直非金属立管段（沿 Z 轴，O=0.0）与上部粘接止推环、中部橡胶衬垫钢抱箍
    pipe_h = SL * 1.5
    o_main = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0)))
    o_collar = CYLINDER(s, R=R1 + ST * 2.5, H=SL * 0.28, O=0.0).translate((0.0, 0.0, SL * 0.12))
    o_clamp = CYLINDER(s, R=R1 + ST * 2.0, H=SL * 0.45, O=0.0).translate((0.0, 0.0, -(SL * 0.35)))
    o_ears = BOX(s, L=SW * 1.15, W=SL * 0.45, H=ST * 3.0).translate((0.0, 0.0, -(SL * 0.125)))
    for p in (o_collar, o_clamp, o_ears):
        o_main.uniteWith(p); p.erase()
    o_in = CYLINDER(s, R=max(8.0, R1 - ST), H=pipe_h + 6.0, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0 + 3.0)))
    o_main.subtractFrom(o_in); o_in.erase()
    # 2. 下部左右两侧平行布置的工字钢/H型钢承重横梁（见 hg_index_p024.png ME1 左右两侧工字钢截面）
    beam_h = max(60.0, SL * 0.45)
    beam_w = beam_h * 0.75
    z_bm = -(SL * 0.35 + beam_h / 2.0)
    for sy in (-(R1 + ST * 2.0 + beam_w * 0.55), (R1 + ST * 2.0 + beam_w * 0.55)):
        o_bw = BOX(s, L=ST * 1.2, W=beam_h, H=SW * 1.3).translate((0.0, sy, z_bm))
        o_bf1 = BOX(s, L=beam_w, W=ST * 1.3, H=SW * 1.3).translate((0.0, sy, z_bm + beam_h / 2.0 - ST * 0.65))
        o_bf2 = BOX(s, L=beam_w, W=ST * 1.3, H=SW * 1.3).translate((0.0, sy, z_bm - beam_h / 2.0 + ST * 0.65))
        for p in (o_bw, o_bf1, o_bf2):
            o_main.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
