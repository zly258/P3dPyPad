# -*- coding: utf-8 -*-
# HG/T 21629-2021 E11 立管的两方向导向架（图 C.5-11）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="立管的两方向导向架", TooltipLong="HG/T 21629-2021 E11 立管的两方向导向架 图C.5-11", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至导向底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="导向长", TooltipLong="沿管道轴线导向座长度")
@param(SW=LENGTH, TooltipShort="导向宽", TooltipLong="导向底座总宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="导向翼板与底板厚度")
@param(GW=LENGTH, TooltipShort="导向间隙", TooltipLong="导向板与管托/管道单侧间隙")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_E11(s, D=114.3, SH=142.2, SL=177.2, SW=171.4, ST=8.0, GW=3.0, ID=u"E11", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); GW = float(GW)
    if D < 15.0: D = 15.0
    if ST < 4.0: ST = 6.0
    if GW < 1.0: GW = 3.0
    if SL < 40.0: SL = max(80.0, D * 0.8)
    if SW < (D + 30.0): SW = D + 60.0
    R1 = D / 2.0
    if SH < (R1 + ST * 2.0 + 15.0): SH = R1 + max(60.0, D * 0.45)
    # 1. 立管外抱箍/护筒（O=0.0）
    o_main = CYLINDER(s, R=R1 + ST * 1.5, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    # 2. 外部两向/四向井字形槽钢导向框与导向挡块
    frame_r = R1 + ST * 1.5 + GW + ST
    beam_len = max(SW * 1.3, frame_r * 2.6)
    for sz in (-1.0, 1.0):
        o_bx = BOX(s, L=beam_len, W=ST * 1.6, H=ST * 4.5).translate((0.0, 0.0, sz * frame_r))
        o_main.uniteWith(o_bx); o_bx.erase()
    leg_top = frame_r + ST * 0.8
    leg_bot = -(SH - ST * 0.75)
    leg_h = max(20.0, leg_top - leg_bot)
    leg_zc = 0.5 * (leg_top + leg_bot)
    for sy in (-1.0, 1.0):
        o_lug = BOX(s, L=ST * 2.0, W=leg_h, H=SL * 0.55).translate((0.0, sy * (R1 + ST * 1.5), leg_zc))
        o_main.uniteWith(o_lug); o_lug.erase()
    # 底部生根支承转换座
    o_sup = BOX(s, L=beam_len, W=ST * 1.5, H=SL * 0.65).translate((0.0, 0.0, -(SH - ST * 0.75)))
    o_main.uniteWith(o_sup); o_sup.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
