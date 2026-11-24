# -*- coding: utf-8 -*-
# HG/T 21629-2021 R2 管夹型刚性拉撑杆（直管耳轴）（图 C.16-2）
# 严格遵循 plant3d-python-cad-generator 规范：全部 CYLINDER 使用 O=0.0 并显式差集挖孔。
from __future__ import division
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="管夹型刚性拉撑杆（直管耳轴）", TooltipLong="HG/T 21629-2021 R2 管夹型刚性拉撑杆（直管耳轴） 图C.16-2", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径")
@param(L=LENGTH, TooltipShort="安装长", TooltipLong="两端铰接销轴中心间距", Ask4Dist=True)
@param(BODY_D=LENGTH, TooltipShort="拉杆外径", TooltipLong="刚性拉撑杆主管外径")
@param(d=LENGTH, TooltipShort="销孔径", TooltipLong="连接销轴直径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def HG_R2(s, D=114.3, L=520.0, BODY_D=85.0, d=20.0, ID=u"R2", **kw):
    D = float(D); L = float(L); BODY_D = float(BODY_D); d = float(d)
    if D < 15.0: D = 88.9
    if BODY_D < 20.0: BODY_D = 50.0
    if d < 10.0: d = 16.0
    if L < 150.0: L = 450.0
    R1 = D / 2.0; bw = max(36.0, d * 2.4)
    # 1. 管道抱箍（O=0.0）与向单侧（+Y 侧）水平伸出的单根耳轴
    o1 = CYLINDER(s, R=R1 + 7.0, H=bw, O=0.0).rotateY(90.0).translate((-(bw / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=bw + 4.0, O=0.0).rotateY(90.0).translate((-(bw / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    y_tr = R1 + max(BODY_D * 0.85, d * 2.5)
    o_tr = CYLINDER(s, R=max(14.0, d * 1.05), H=y_tr, O=0.0).rotateX(-90.0)
    o1.uniteWith(o_tr); o_tr.erase()
    # 2. 位于单侧耳轴端（Y = +y_tr）的单根拉撑杆/液压阻尼器
    cyl_h = L * (0.55 if False else 0.72)
    o_body = CYLINDER(s, R=BODY_D / 2.0, H=cyl_h, O=0.0).translate((0.0, y_tr, -(L * 0.82)))
    o_rod = CYLINDER(s, R=d * 0.48, H=L, O=0.0).translate((0.0, y_tr, -L))
    o_clev = BOX(s, L=d * 3.0, W=d * 2.2, H=d * 1.8).translate((0.0, y_tr, -L))
    for p in (o_body, o_rod, o_clev):
        o1.uniteWith(p); p.erase()
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, 0.0, -L))
