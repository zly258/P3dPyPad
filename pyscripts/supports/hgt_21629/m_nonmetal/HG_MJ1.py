# -*- coding: utf-8 -*-
# HG/T 21629-2021 MJ1 管夹式管托(1/2"~24"，-20℃~120℃，非金属管）（图 C.12-14）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="管夹式管托(1/2~24，-20", TooltipLong="HG/T 21629-2021 MJ1 管夹式管托(1/2~24，-20℃~120℃，非金属管） 图C.12-14", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(SH=LENGTH, TooltipShort="支承高", TooltipLong="管心至底板底面高度", Ask4Dist=True)
@param(SL=LENGTH, TooltipShort="托长", TooltipLong="沿管道轴线长度")
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="管托底板宽度")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="管托腹板/鞍板厚度")
@param(HH=LENGTH0, TooltipShort="滑板厚", TooltipLong="底部耐磨滑板厚，0=无")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_MJ1(s, D=114.3, SH=157.2, SL=188.6, SW=114.3, ST=8.0, HH=0.0, ID=u"MJ1", **kw):
    D = float(D); SH = float(SH); SL = float(SL); SW = float(SW); ST = float(ST); HH = float(HH)
    if D < 15.0: D = 88.9
    if ST < 4.0: ST = 6.0
    if SL < 60.0: SL = 160.0
    if SW < 45.0: SW = 95.0
    R1 = D / 2.0; rub_t = max(5.0, ST * 0.85); R_rub = R1 + rub_t
    if SH < (R_rub + 35.0): SH = R_rub + 85.0
    # 1. 全长橡胶缓冲内衬套（长 SL*1.12，O=0.0）与外部前后两道钢抱箍
    o_main = CYLINDER(s, R=R_rub, H=SL * 1.12, O=0.0).rotateY(90.0).translate((-(SL * 0.56), 0.0, 0.0))
    cw = max(28.0, SL * 0.22)
    for sx in (-(SL * 0.32), (SL * 0.32)):
        o_cl = CYLINDER(s, R=R_rub + ST, H=cw, O=0.0).rotateY(90.0).translate((sx - cw / 2.0, 0.0, 0.0))
        o_ear = BOX(s, L=(R_rub + ST * 4.5) * 2.0, W=ST * 2.2, H=cw).translate((sx, 0.0, 0.0))
        o_main.uniteWith(o_cl); o_cl.erase()
        o_main.uniteWith(o_ear); o_ear.erase()
    o_in = CYLINDER(s, R=R1, H=SL * 1.2, O=0.0).rotateY(90.0).translate((-(SL * 0.6), 0.0, 0.0))
    o_main.subtractFrom(o_in); o_in.erase()
    # 2. 下部纵向腹板、前后端护板与宽底板
    web_h = max(18.0, SH - R_rub - ST)
    o_web = BOX(s, L=ST * 1.2, W=web_h, H=SL).translate((0.0, 0.0, -(R_rub + web_h / 2.0)))
    o_base = BOX(s, L=SW * 1.1, W=ST * 1.3, H=SL * 1.05).translate((0.0, 0.0, -(SH - ST * 0.65)))
    o_main.uniteWith(o_web); o_web.erase()
    o_main.uniteWith(o_base); o_base.erase()
    for sx_e in (-(SL * 0.48), (SL * 0.48)):
        o_ep = BOX(s, L=SW * 0.85, W=web_h * 0.8, H=ST).translate((sx_e, 0.0, -(SH - ST - web_h * 0.4)))
        o_main.uniteWith(o_ep); o_ep.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
