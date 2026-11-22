# -*- coding: utf-8 -*-
# HG/T 21629-2021 K4 焊接型固定架（图 C.10-4）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="焊接型固定架", TooltipLong="HG/T 21629-2021 K4 焊接型固定架 图C.10-4", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至固定座底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="固定长", TooltipLong="沿管轴线固定座长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="固定座底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="固定座主筋板与底板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_K4(s, D=114.3, SH=157.2, SL=188.6, SW=114.3, ST=8.0, ID=u"K4", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST)
    if D < 25.0: D = 114.3
    if ST < 6.0: ST = 10.0
    if SL < 80.0: SL = 200.0
    if SW < 80.0: SW = 180.0
    R1 = D / 2.0
    if SH < (R1 + 50.0): SH = R1 + 110.0
    o_main = CYLINDER(s, R=R1 + ST, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    o_top = BOX(s, L=(R1 + ST) * 2.4, W=(R1 + ST) * 1.4, H=SL + 10.0).translate((0.0, 0.0, (R1 + ST) * 0.7))
    o_main.subtractFrom(o_top); o_top.erase()
    web_h = max(25.0, SH - R1 - ST)
    o_web = BOX(s, L=ST * 1.4, W=web_h + R1 * 0.25, H=SL).translate((0.0, 0.0, -(SH - ST - (web_h + R1 * 0.25) / 2.0)))
    o_base = BOX(s, L=SW * 1.35, W=ST * 1.5, H=SL * 1.05).translate((0.0, 0.0, -(SH - ST * 0.75)))
    o_main.uniteWith(o_web); o_web.erase()
    o_main.uniteWith(o_base); o_base.erase()
    # 左右两侧斜撑三角形主肋板（连接管底鞍板与宽底板两端）
    for sy in (-1.0, 1.0):
        for sx in (-(SL * 0.35), (SL * 0.35)):
            o_rib = BOX(s, L=SW * 0.55, W=web_h * 1.1, H=ST * 1.3).rotateX(sy * 28.0).translate((sx, sy * (SW * 0.28), -(SH - ST - web_h * 0.48)))
            o_main.uniteWith(o_rib); o_rib.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
