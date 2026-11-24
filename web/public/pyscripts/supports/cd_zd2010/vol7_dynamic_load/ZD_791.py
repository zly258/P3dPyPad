# -*- coding: utf-8 -*-
# CD-ZD2010 791 C形钢带动载管夹（上下两半全圆宽厚扁钢带抱箍 + 两侧水平法兰耳与对穿紧固螺栓 + 顶部双耳销座带加劲肋）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="791钢带动载管夹", TooltipLong="CD-ZD2010 791 C形钢带动载管夹", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径OD", TooltipLong="管道外径 OD")
@param(H=LENGTH, TooltipShort="耳孔高H", TooltipLong="管心至吊孔中心高度 H", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="钢带宽", TooltipLong="宽扁钢带宽度")
@param(T=LENGTH, TooltipShort="钢带厚K", TooltipLong="扁钢带厚度 K")
@param(Pin_d=LENGTH, TooltipShort="销孔径d", TooltipLong="穿销孔径 d")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="许用荷载", TooltipLong="许用荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_791(s, D=273.0, H=330.0, B=90.0, T=14.0, Pin_d=35.0, ID=u"ZD_791", Load_kN=106.0, Weight_kg=35.8, **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); Pin_d = float(Pin_d)
    if D < 50.0: D = 50.0
    if T < 8.0: T = 8.0
    if B < 50.0: B = 50.0
    if Pin_d < 15.0: Pin_d = 15.0
    R1 = D / 2.0
    R2 = R1 + T
    if H <= R2 + Pin_d * 1.8: H = R2 + Pin_d * 2.4

    # 对照图集 ZD_791_atlas.png (p.296)：与 790 的圆钢 U 形螺杆截然不同，791 上下两半均为宽厚扁钢带 (宽 B，厚 T)，水平分缝处带外挑螺栓法兰耳与紧固螺栓组！
    gap = max(6.0, T * 0.45)

    # 1. 上下两半全圆厚钢带管夹主体
    o1 = CYLINDER(s, R=R2, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))

    # 2. 左右两侧上下分体水平紧固螺栓耳板 + 竖向加劲肋 + 对穿紧固螺栓与螺母 (图集 791 核心特征)
    flange_ext = max(48.0, T * 3.6)
    span_A = (R2 + flange_ext) * 2.0
    for sz in (-1.0, 1.0):
        zf = sz * (gap / 2.0 + T / 2.0)
        o_fl = BOX(s, L=span_A, W=T, H=B).translate((0.0, 0.0, zf))
        o1.uniteWith(o_fl); o_fl.erase()

    # 切除水平分缝间隙 gap 及中心管道内孔 R1
    o_seam = BOX(s, L=span_A + 20.0, W=gap, H=B + 20.0)
    o_pipe = CYLINDER(s, R=R1, H=B + 20.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 10.0), 0.0, 0.0))
    o1.subtractFrom(o_seam); o_seam.erase()
    o1.subtractFrom(o_pipe); o_pipe.erase()

    # 两侧紧固螺栓群 (每侧前后 2 颗竖向穿栓 + 下半钢带耳板下方三角形托肋)
    bolt_r = max(6.0, T * 0.42)
    bolt_h = gap + T * 4.2
    for sy in (-1.0, 1.0):
        yb = sy * (R2 + flange_ext * 0.52)
        for sx in (-1.0, 1.0):
            xb = sx * (B * 0.26)
            o_bolt = CYLINDER(s, R=bolt_r, H=bolt_h, O=0.0).translate((xb, yb, -(bolt_h / 2.0)))
            o_nut = CYLINDER(s, R=bolt_r * 1.65, H=bolt_r * 1.4, O=0.0).translate((xb, yb, gap / 2.0 + T))
            o1.uniteWith(o_bolt); o_bolt.erase()
            o1.uniteWith(o_nut); o_nut.erase()
        # 下半部钢带耳座下方三角形加劲肋
        o_brib = BOX(s, L=flange_ext * 0.75, W=T * 2.2, H=T * 0.8).translate((0.0, sy * (R2 + flange_ext * 0.35), -(gap / 2.0 + T + T * 1.1)))
        o1.uniteWith(o_brib); o_brib.erase()

    # 3. 顶部重型双耳铰接销座 + 两侧斜向大加劲肋 + 横向穿销 (对照 p.296 791)
    ear_gap = max(28.0, Pin_d * 1.15)
    ear_r = max(Pin_d * 1.15, B * 0.36)
    ear_h = H - R1 * 0.65
    for sy in (-1.0, 1.0):
        yc = sy * (ear_gap / 2.0 + T / 2.0)
        o_ear = BOX(s, L=T, W=ear_h, H=ear_r * 2.0).translate((0.0, yc, R1 * 0.65 + ear_h / 2.0))
        o_etop = CYLINDER(s, R=ear_r, H=T, O=0.0).rotateX(90.0).translate((0.0, yc + T / 2.0, H))
        o_ear.uniteWith(o_etop); o_etop.erase()
        # 连接双耳外侧与上半圈钢带及侧法兰耳的斜向加强大肋板
        rib_w = max(24.0, (R2 + flange_ext * 0.6) - (ear_gap / 2.0 + T))
        rib_h = (H - gap / 2.0 - T) * 0.78
        o_rib = BOX(s, L=rib_w, W=rib_h, H=T).translate((0.0, sy * (ear_gap / 2.0 + T + rib_w / 2.0), gap / 2.0 + T + rib_h / 2.0))
        o_ear.uniteWith(o_rib); o_rib.erase()
        o1.uniteWith(o_ear); o_ear.erase()

    # 再次清空管道内孔并装入顶部横销
    o_pipe2 = CYLINDER(s, R=R1, H=B + 20.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 10.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe2); o_pipe2.erase()

    pin_l = ear_gap + T * 3.4
    o_pin = CYLINDER(s, R=Pin_d / 2.0, H=pin_l, O=0.0).rotateX(90.0).translate((0.0, pin_l / 2.0, H))
    o1.uniteWith(o_pin); o_pin.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
