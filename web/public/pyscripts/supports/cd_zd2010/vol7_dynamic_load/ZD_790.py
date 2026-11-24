# -*- coding: utf-8 -*-
# CD-ZD2010 790 C形螺杆动载管夹（上半圈厚壁弧形鞍板 + 顶部高耸双耳吊板带梯形加劲肋与横销 + 两侧水平穿孔耳座 + 下半圈粗 U 形螺杆锁紧双螺母）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="790C形动载管夹", TooltipLong="CD-ZD2010 790 C形螺杆动载管夹", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径OD", TooltipLong="管道外径 OD")
@param(H=LENGTH, TooltipShort="销心高H", TooltipLong="管中心至铰销孔中心高度 H", Ask4Dist=True)
@param(B=LENGTH, TooltipShort="鞍板宽", TooltipLong="上半圈弧形鞍板宽度")
@param(T=LENGTH, TooltipShort="板厚K", TooltipLong="鞍板与耳板厚度 K")
@param(Pin_d=LENGTH, TooltipShort="销孔径d", TooltipLong="顶部铰接销孔直径 d")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="许用荷载", TooltipLong="许用荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_790(s, D=159.0, H=215.0, B=70.0, T=10.0, Pin_d=25.0, ID=u"ZD_790", Load_kN=51.0, Weight_kg=10.31, **kw):
    D = float(D); H = float(H); B = float(B); T = float(T); Pin_d = float(Pin_d)
    if D < 30.0: D = 30.0
    if T < 6.0: T = 6.0
    if B < 40.0: B = 40.0
    if Pin_d < 12.0: Pin_d = 12.0
    R1 = D / 2.0
    if H <= R1 + Pin_d * 2.0: H = R1 + Pin_d * 2.5

    # 对照图集 ZD_790_atlas.png (p.287)：
    # 1. 上半圈厚壁弧形管夹鞍板 (仅包覆管道上半圆 Z >= 0) + 两侧水平外伸的穿杆托板耳座
    R_saddle = R1 + T * 1.2
    o1 = CYLINDER(s, R=R_saddle, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o_cut_btm = BOX(s, L=R_saddle * 3.0, W=R_saddle * 1.5, H=B + 20.0).translate((0.0, 0.0, -(R_saddle * 0.75)))
    o1.subtractFrom(o_cut_btm); o_cut_btm.erase()

    # 两侧水平外伸穿杆托板与侧向肋板 (宽 A)
    rod_r = max(7.0, min(18.0, T * 0.95))
    y_ubolt = R1 + rod_r * 1.5 + T * 0.6
    span_A = (y_ubolt + rod_r * 2.2) * 2.0
    ledge_t = T * 1.5
    o_ledge = BOX(s, L=span_A, W=ledge_t, H=B).translate((0.0, 0.0, ledge_t / 2.0))
    o1.uniteWith(o_ledge); o_ledge.erase()

    # 2. 顶部高耸双耳吊板 (内净距 B_gap) + 前后及两侧梯形加劲肋板 + 横向穿销
    ear_gap = max(24.0, Pin_d * 1.15)
    ear_r = max(Pin_d * 1.15, B * 0.34)
    ear_h = H - R1 * 0.6
    for sy in (-1.0, 1.0):
        yc = sy * (ear_gap / 2.0 + T / 2.0)
        o_ear = BOX(s, L=T, W=ear_h, H=ear_r * 2.0).translate((0.0, yc, R1 * 0.6 + ear_h / 2.0))
        o_etop = CYLINDER(s, R=ear_r, H=T, O=0.0).rotateX(90.0).translate((0.0, yc + T / 2.0, H))
        o_ear.uniteWith(o_etop); o_etop.erase()
        # 侧面斜向加劲肋板 (连接双耳吊板外壁至两侧水平托板耳座)
        rib_y = max(16.0, y_ubolt - (ear_gap / 2.0 + T))
        rib_z = ear_h * 0.72
        o_rib = BOX(s, L=rib_y, W=rib_z, H=T).translate((0.0, sy * (ear_gap / 2.0 + T + rib_y / 2.0), ledge_t + rib_z / 2.0))
        o_ear.uniteWith(o_rib); o_rib.erase()
        o1.uniteWith(o_ear); o_ear.erase()

    # 顶部铰接销孔与横销
    pin_l = ear_gap + T * 4.0
    o_phole = CYLINDER(s, R=Pin_d / 2.0, H=pin_l, O=0.0).rotateX(90.0).translate((0.0, pin_l / 2.0, H))
    o1.subtractFrom(o_phole); o_phole.erase()
    o_pin = CYLINDER(s, R=Pin_d * 0.48, H=ear_gap + T * 3.2, O=0.0).rotateX(90.0).translate((0.0, (ear_gap + T * 3.2) / 2.0, H))
    o1.uniteWith(o_pin); o_pin.erase()
    for sy_c in (-1.0, 1.0):
        yc_col = sy_c * (ear_gap / 2.0 + T) + (Pin_d * 0.32 if sy_c > 0 else 0.0)
        o_pcol = CYLINDER(s, R=Pin_d * 0.68, H=Pin_d * 0.32, O=0.0).rotateX(90.0).translate((0.0, yc_col, H))
        o1.uniteWith(o_pcol); o_pcol.erase()

    # 3. 下半圈粗 U 形/C 形圓钢螺杆 (1 或 2 道圆弧螺杆兜住管道下半圆，两端向上穿过水平托板并配锁紧双螺母，与 ZD_791 钢带明显区分！)
    o_ubolt_arc = TORUS(s, R1=y_ubolt, R2=rod_r).rotateY(90.0)
    o_ucut = BOX(s, L=y_ubolt * 3.0, W=y_ubolt * 2.0, H=rod_r * 6.0).translate((0.0, 0.0, y_ubolt - 2.0))
    o_ubolt_arc.subtractFrom(o_ucut); o_ucut.erase()
    o1.uniteWith(o_ubolt_arc); o_ubolt_arc.erase()

    leg_h = ledge_t + rod_r * 4.2 + 3.0
    for sy in (-1.0, 1.0):
        yl = sy * y_ubolt
        o_leg = CYLINDER(s, R=rod_r, H=leg_h, O=0.0).translate((0.0, yl, -3.0))
        o_nut = CYLINDER(s, R=rod_r * 1.75, H=rod_r * 1.6, O=0.0).translate((0.0, yl, ledge_t))
        o1.uniteWith(o_leg); o_leg.erase()
        o1.uniteWith(o_nut); o_nut.erase()

    # 4. 切除中心管道通孔 ØD
    o_pipe = CYLINDER(s, R=R1, H=B * 2.0, O=0.0).rotateY(90.0).translate((-B, 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
