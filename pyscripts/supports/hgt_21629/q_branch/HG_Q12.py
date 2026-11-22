# -*- coding: utf-8 -*-
# HG/T 21629-2021 Q12 小支管加强架（排净、放空和仪表，1/2"~2")（图 C.15-12）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="小支管加强架（排净、放空和仪表，1/", TooltipLong="HG/T 21629-2021 Q12 小支管加强架（排净、放空和仪表，1/2~2) 图C.15-12", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="母管外径", TooltipLong="大管/主管外径")
@param(D2=LENGTH, TooltipShort="支管外径", TooltipLong="被支撑小支管外径")
@param(L=LENGTH, TooltipShort="支承跨度", TooltipLong="小管中心至母管中心/生根距", Ask4Dist=True)
@param(T=LENGTH, TooltipShort="型材厚", TooltipLong="角钢/加强板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_Q12(s, D=93.3, D2=42.4, L=187.8, T=6.0, ID=u"Q12", **kw):
    D = float(D); D2 = float(D2); L = float(L); T = float(T)
    if D < 40.0: D = 114.3
    if D2 < 15.0: D2 = 26.9
    if T < 4.0: T = 6.0
    if L < (D / 2.0 + 60.0): L = D / 2.0 + 140.0
    R1 = D / 2.0; R2 = D2 / 2.0
    # 1. 上部水平主管抱箍（O=0.0）与向下引出的排净小支管及阀门体（双圆锥阀体 + 手轮杆）
    cw = max(40.0, D2 * 1.8)
    o1 = CYLINDER(s, R=R1 + T, H=cw, O=0.0).rotateY(90.0).translate((-(cw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=cw + 4.0, O=0.0).rotateY(90.0).translate((-(cw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    o_br_v = CYLINDER(s, R=R2, H=L, O=0.0).translate((0.0, 0.0, -L))
    z_vlv = -(R1 + (L - R1) * 0.48)
    o_vc1 = CONE(s, R1=R2 * 2.1, R2=R2 * 0.9, H=D2 * 0.9, E=0.0).translate((0.0, 0.0, z_vlv))
    o_vc2 = CONE(s, R1=R2 * 0.9, R2=R2 * 2.1, H=D2 * 0.9, E=0.0).translate((0.0, 0.0, z_vlv - D2 * 0.9))
    o_vstem = CYLINDER(s, R=R2 * 0.45, H=D2 * 2.2, O=0.0).rotateX(-90.0).translate((0.0, 0.0, z_vlv))
    # 2. 从主管一侧伸出的 L 形角钢加强框（竖直臂 + 底部水平横臂）与抱持小支管下端的 U 形卡
    y_frame = -(R1 * 0.75)
    frame_h = L - R1 * 0.5
    ang_w = max(36.0, D2 * 1.4)
    o_fv = BOX(s, L=T, W=frame_h, H=ang_w).translate((0.0, y_frame, -(R1 * 0.5 + frame_h / 2.0)))
    o_fh = BOX(s, L=abs(y_frame) + R2 * 2.5, W=T, H=ang_w).translate((0.0, y_frame / 2.0, -(L - R2 * 1.2)))
    o_ub = TORUS(s, R1=R2 + T * 0.6, R2=T * 0.5).translate((0.0, 0.0, -(L - R2 * 1.2)))
    for p in (o_br_v, o_vc1, o_vc2, o_vstem, o_fv, o_fh, o_ub):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
