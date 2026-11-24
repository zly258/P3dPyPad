# -*- coding: utf-8 -*-
# HG/T 21629-2021 F15~F16 16"及以上立管用导向耳轴（图 C.6-11）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="16及以上立管用导向耳轴", TooltipLong="HG/T 21629-2021 F15~F16 16及以上立管用导向耳轴 图C.6-11", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="母管外径")
@param(SH=LENGTH, TooltipShort="支腿高", TooltipLong="母管中心至底板/耳轴端距离", Ask4Dist=True)
@param(LEG_D=LENGTH, TooltipShort="耳轴外径", TooltipLong="耳轴/支腿圆管外径")
@param(ST=LENGTH, TooltipShort="板厚", TooltipLong="底板/补强板/耳座板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_F15(s, D=762.0, SH=876.3, LEG_D=406.4, ST=16.0, ID=u"F15", **kw):
    D = float(D); SH = float(SH); LEG_D = float(LEG_D); ST = float(ST)
    if D < 100.0: D = 406.4
    if LEG_D < 40.0: LEG_D = max(88.9, D * 0.35)
    if ST < 6.0: ST = 10.0
    R1 = D / 2.0
    if SH < (R1 + 80.0): SH = R1 + 180.0
    R_leg = LEG_D / 2.0; R_leg_in = max(8.0, R_leg - ST)
    pipe_h = max(LEG_D * 2.5, D * 0.85)
    o1 = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0)))
    o_in = CYLINDER(s, R=max(10.0, R1 - ST), H=pipe_h + 4.0, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0 + 2.0)))
    o1.subtractFrom(o_in); o_in.erase()
    tr_l = max(60.0, SH - R1 * 0.85)
    for sy in (-1.0, 1.0):
        o_tr = CYLINDER(s, R=R_leg, H=tr_l, O=0.0).rotateX(-90.0 * sy).translate((0.0, sy * R1 * 0.85, 0.0))
        o_tri = CYLINDER(s, R=R_leg_in, H=tr_l + 4.0, O=0.0).rotateX(-90.0 * sy).translate((0.0, sy * (R1 * 0.85 - 2.0), 0.0))
        o_tr.subtractFrom(o_tri); o_tri.erase()
        o1.uniteWith(o_tr); o_tr.erase()
        # 耳轴外端上下对称焊接的方形导向滑块翼板（见 hg_index_p020.png F15 截面图）
        yg = sy * (R1 + tr_l * 0.55)
        for sz in (-1.0, 1.0):
            o_gblk = BOX(s, L=tr_l * 0.65, W=ST * 2.2, H=LEG_D * 0.85).translate((0.0, yg, sz * (R_leg + ST * 0.9)))
            o1.uniteWith(o_gblk); o_gblk.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (0.0, 0.0, 0.0), (0.0, 0.0, -SH))
