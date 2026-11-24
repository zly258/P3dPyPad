# -*- coding: utf-8 -*-
# HG/T 21629-2021 J4 大管管夹式管托（26"~72")（图 C.9-4）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="大管管夹式管托（26~72)", TooltipLong="HG/T 21629-2021 J4 大管管夹式管托（26~72) 图C.9-4", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="管托腹板/鞍板厚度")
@param(HH=LENGTH0, TooltipShort="滑板厚", TooltipLong="底部耐磨滑板厚，0=无")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_J4(s, D=1016.0, SH=658.0, SL=600.0, SW=550.0, ST=16.0, HH=0.0, ID=u"J4", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 200.0: D = 711.0
    if ST < 8.0: ST = 12.0
    if SL < 120.0: SL = 320.0
    if SW < 150.0: SW = max(300.0, D * 0.55)
    R1 = D / 2.0
    if SH < (R1 + 80.0): SH = R1 + 150.0
    # 1. 全周重型宽管夹 + 斜向双侧夹紧法兰耳板（对照 hg_index_p021.png J4 示意图）
    o_main = CYLINDER(s, R=R1 + ST * 1.2, H=SL * 0.8, O=0.0).rotateY(90.0).translate((-(SL * 0.4), 0.0, 0.0))
    ear_span = D + ST * 14.0
    o_ears = BOX(s, L=ear_span, W=ST * 3.2, H=SL * 0.8).rotateX(25.0)
    o_main.uniteWith(o_ears); o_ears.erase()
    o_in = CYLINDER(s, R=R1, H=SL + 6.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 3.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    # 2. 下部双腹板承重鞍座与底板
    web_h = max(40.0, SH - R1 * 0.78 - ST)
    for sy in (-(SW * 0.32), (SW * 0.32)):
        o_w = BOX(s, L=ST * 1.2, W=web_h, H=SL * 0.85).translate((0.0, sy, -(SH - ST - web_h / 2.0)))
        o_main.uniteWith(o_w); o_w.erase()
    o_base = BOX(s, L=SW, W=ST * 1.3, H=SL).translate((0.0, 0.0, -(SH - ST * 0.65)))
    o_main.uniteWith(o_base); o_base.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
