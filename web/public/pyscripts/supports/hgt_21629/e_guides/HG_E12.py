# -*- coding: utf-8 -*-
# HG/T 21629-2021 E12 立管的四方向导向架（图 C.5-12）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="立管的四方向导向架", TooltipLong="HG/T 21629-2021 E12 立管的四方向导向架 图C.5-12", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至导向底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="导向长", TooltipLong="沿管道轴线导向座长度")
@param(SW=LENGTH, TooltipShort="导向宽", TooltipLong="导向底座总宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="导向翼板与底板厚度")
@param(GW=LENGTH, TooltipShort="导向间隙", TooltipLong="导向板与管托/管道单侧间隙")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_E12(s, D=114.3, SH=142.2, SL=177.2, SW=171.4, ST=8.0, GW=3.0, ID=u"E12", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); GW = float(GW)
    if D < 25.0: D = 114.3
    if ST < 5.0: ST = 8.0
    if GW < 1.0: GW = 4.0
    if SL < 80.0: SL = 160.0
    if SW < (D + 60.0): SW = D + 120.0
    R1 = D / 2.0
    if SH < (R1 + 80.0): SH = R1 + 180.0
    # 1. 竖直立管段（沿 Z 轴，O=0.0）与四向放射状焊接导向翼块
    pipe_h = SL * 1.6
    o_main = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0)))
    o_in = CYLINDER(s, R=max(8.0, R1 - ST), H=pipe_h + 4.0, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0 + 2.0)))
    o_main.subtractFrom(o_in); o_in.erase()
    lug_r = R1 + ST * 4.5
    for ang in (0.0, 90.0):
        o_w = BOX(s, L=lug_r * 2.0, W=SL * 0.65, H=ST * 1.5).rotateZ(ang)
        o_main.uniteWith(o_w); o_w.erase()
    # 2. 外部水平面内正交四梁 # 字形井字槽钢导向框架（2根X向梁 + 2根Y向梁）
    grid_off = lug_r + ST * 1.2
    beam_len = max(SW * 1.5, grid_off * 2.8)
    ch_h = max(60.0, SL * 0.48)
    for s_pos in (-1.0, 1.0):
        o_bx = BOX(s, L=ST * 3.5, W=ch_h, H=beam_len).translate((0.0, s_pos * grid_off, 0.0))
        o_by = BOX(s, L=beam_len, W=ch_h, H=ST * 3.5).translate((s_pos * grid_off, 0.0, 0.0))
        o_main.uniteWith(o_bx); o_bx.erase()
        o_main.uniteWith(o_by); o_by.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
