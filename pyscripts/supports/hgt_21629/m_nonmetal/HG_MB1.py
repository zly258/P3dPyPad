# -*- coding: utf-8 -*-
# HG/T 21629-2021 MB1~MB4 管夹式刚性吊架（1/2"~36"，-20℃～120℃，非金属管）（图 C.12-6）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="管夹式刚性吊架（1/2~36，-", TooltipLong="HG/T 21629-2021 MB1~MB4 管夹式刚性吊架（1/2~36，-20℃～120℃，非金属管） 图C.12-6", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(H=LENGTH, TooltipShort="吊杆长", TooltipLong="管心至吊杆上端总高", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="管夹/横担宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="管夹/横担板厚")
@param(d=LENGTH, TooltipShort="杆径", TooltipLong="吊杆公称直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_MB1(s, D=114.3, H=485.8, B=38.4, T=8.0, d=12.0, ID=u"MB1", **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 15.0: D = 60.3
    if d < 8.0: d = 12.0
    if T < 4.0: T = 6.0
    if B < 30.0: B = 50.0
    R1 = D / 2.0; rub_t = max(5.0, T * 0.85); R_rub = R1 + rub_t; R2 = R_rub + T
    if H < (R2 + 120.0): H = R2 + 280.0
    # 1. 内层非金属管专用橡胶护套（宽 B*1.3）与外层钢抱箍（宽 B）
    o1 = CYLINDER(s, R=R_rub, H=B * 1.3, O=0.0).rotateY(90.0).translate((-(B * 0.65), 0.0, 0.0))
    o_cl = CYLINDER(s, R=R2, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o1.uniteWith(o_cl); o_cl.erase()
    o_in = CYLINDER(s, R=R1, H=B * 1.4 + 4.0, O=0.0).rotateY(90.0).translate((-(B * 0.7 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    # 2. 上下夹紧立耳 + 顶部U形螺母叉口 + 竖直吊杆与双槽钢横担顶座
    o_uear = BOX(s, L=T * 3.2, W=d * 3.5, H=B).translate((0.0, 0.0, R2 + d * 1.5))
    o_lear = BOX(s, L=T * 3.2, W=d * 2.5, H=B).translate((0.0, 0.0, -(R2 + d * 1.1)))
    o_rod = CYLINDER(s, R=d / 2.0, H=H - R2, O=0.0).translate((0.0, 0.0, R2))
    o_tb = CYLINDER(s, R=d * 1.1, H=d * 4.5, O=0.0).translate((0.0, 0.0, R2 + (H - R2) * 0.45))
    o_top = BOX(s, L=B * 1.4, W=d * 2.5, H=B * 1.1).translate((0.0, 0.0, H - d * 1.25))
    for p in (o_uear, o_lear, o_rod, o_tb, o_top):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
