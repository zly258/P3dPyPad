# -*- coding: utf-8 -*-
# HG/T 21629-2021 MA4 管夹用橡胶套（非金属管）（图 C.12-4）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="管夹用橡胶套（非金属管）", TooltipLong="HG/T 21629-2021 MA4 管夹用橡胶套（非金属管） 图C.12-4", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="螺栓跨距", TooltipLong="管心至螺栓孔中心距离", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="管夹扁钢宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="管夹扁钢厚度")
@param(d=LENGTH, TooltipShort="螺栓径", TooltipLong="夹紧/悬吊螺栓直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_MA4(s, D=114.3, H=101.9, B=38.4, T=8.0, d=12.0, ID=u"MA4", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 15.0: D = 60.3
    if T < 4.0: T = 6.0
    if B < 25.0: B = 45.0
    if d < 8.0: d = 12.0
    R1 = D / 2.0; rub_t = max(5.0, T * 0.9); R_rub = R1 + rub_t; R2 = R_rub + T
    if H < (R2 + d * 2.2): H = R2 + d * 3.0
    # 1. 内层成型橡胶护套（两端带防滑凸缘环，总宽 B*1.35，O=0.0）
    o1 = CYLINDER(s, R=R_rub, H=B * 1.35, O=0.0).rotateY(90.0).translate((-(B * 0.675), 0.0, 0.0))
    for sx in (-(B * 0.675), (B * 0.675 - rub_t)):
        o_fl = CYLINDER(s, R=R2 + rub_t * 0.6, H=rub_t, O=0.0).rotateY(90.0).translate((sx, 0.0, 0.0))
        o1.uniteWith(o_fl); o_fl.erase()
    # 2. 外层金属抱箍与上下立耳
    o_cl = CYLINDER(s, R=R2, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o_uear = BOX(s, L=T * 3.5, W=(H - R_rub) + d * 1.5, H=B).translate((0.0, 0.0, R_rub + ((H - R_rub) + d * 1.5) / 2.0))
    o_lear = BOX(s, L=T * 3.5, W=d * 3.0, H=B).translate((0.0, 0.0, -(R_rub + d * 1.5)))
    for p in (o_cl, o_uear, o_lear):
        o1.uniteWith(p); p.erase()
    o_in = CYLINDER(s, R=R1, H=B * 1.5, O=0.0).rotateY(90.0).translate((-(B * 0.75), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
