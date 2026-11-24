# -*- coding: utf-8 -*-
# HG/T 21629-2021 T3 大管焊接式高温隔热管托（26"~160"）（图 C.18-3）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="大管焊接式高温隔热管托（26~16", TooltipLong="HG/T 21629-2021 T3 大管焊接式高温隔热管托（26~160） 图C.18-3", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线隔热托长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="隔热厚", TooltipLong="管托耐高温隔热瓦层厚度")
@param(HH=LENGTH0, TooltipShort="滑板厚", TooltipLong="底部滑板厚度，0=无")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_T3(s, D=1016.0, SH=683.0, SL=680.0, SW=600.0, ST=100.0, HH=0.0, ID=u"T3", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 200.0: D = 711.0
    if ST < 20.0: ST = 50.0
    if SL < 120.0: SL = 340.0
    if SW < 150.0: SW = max(320.0, D * 0.58)
    R1 = D / 2.0; t_p = 12.0
    if SH < (R1 + ST + 60.0): SH = R1 + ST + 130.0
    # 1. 大管下部 120° 弧形焊接钢鞍板（O=0.0）
    o_main = CYLINDER(s, R=R1 + t_p, H=SL, O=0.0).rotateY(90.0).translate((-(SL / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=SL + 4.0, O=0.0).rotateY(90.0).translate((-(SL / 2.0 + 2.0), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    o_top = BOX(s, L=(R1 + t_p) * 2.4, W=(R1 + t_p) * 1.4, H=SL + 10.0).translate((0.0, 0.0, (R1 + t_p) * 0.55))
    o_main.subtractFrom(o_top); o_top.erase()
    # 2. 左右两侧双斜腹板 + 底部平板匣式耐高温隔热层（厚 ST）与底板
    ins_h = min(ST, (SH - R1) * 0.45)
    z_top_web = -(R1 * 0.68)
    z_bot_web = -(SH - t_p - ins_h * 0.5)
    web_h = max(40.0, z_top_web - z_bot_web)
    for sy in (-1.0, 1.0):
        o_sw = BOX(s, L=t_p * 1.4, W=web_h, H=SL * 0.9).rotateX(sy * (-10.0)).translate((0.0, sy * (SW * 0.30), 0.5 * (z_top_web + z_bot_web)))
        o_main.uniteWith(o_sw); o_sw.erase()
    z_box = -(SH - t_p - ins_h / 2.0)
    o_ibox = BOX(s, L=SW * 0.96, W=ins_h + t_p, H=SL * 0.94).translate((0.0, 0.0, z_box))
    o_base = BOX(s, L=SW * 1.12, W=t_p * 1.3, H=SL).translate((0.0, 0.0, -(SH - t_p * 0.65)))
    o_main.uniteWith(o_ibox); o_ibox.erase()
    o_main.uniteWith(o_base); o_base.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
