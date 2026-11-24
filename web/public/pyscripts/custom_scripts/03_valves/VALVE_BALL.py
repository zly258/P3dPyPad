# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *
import math

@activate(Group="Valve", Ports=2, TooltipShort=u"两片式法兰球阀 (Q41F / API 608)", TooltipLong=u"化工标准 GB/T 12237 / API 608 两片式分体连接法兰球阀 (Split-Body Flanged Ball Valve)，带球形阀腔、中体连接法兰、ISO 5211支架平台与折弯扳手手柄", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"阀门主要结构尺寸：结构长度、中心高与法兰规格")
@param(D=LENGTH, TooltipShort=u"管道外径 OD", Ask4Dist=True, TooltipLong=u"管道外径 OD")
@param(L=LENGTH, TooltipShort=u"结构长度 L (GB/T 12221)", Ask4Dist=True, TooltipLong=u"结构长度 L (GB/T 12221)")
@param(H=LENGTH, TooltipShort=u"中心至手柄高 H", Ask4Dist=True, TooltipLong=u"中心至手柄高 H")
@param(LEVER_L=LENGTH, TooltipShort=u"手柄总长", TooltipLong=u"手柄总长")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰密封面外圆直径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓孔数", TooltipLong=u"法兰螺栓孔总数，需与法兰外径/厚度配套")
@param(ID=STRING, TooltipShort=u"阀门位号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def VALVE_BALL(s, D=114.3, L=230.0, H=195.0, LEVER_L=280.0, FL_OD=220.0, FL_T=22.0, NBOLTS=8, ID="Q41F-16C", **kw):
    D = max(20.0, float(D))
    L = max(120.0, float(L))
    H = max(95.0, float(H))
    LEVER_L = max(120.0, float(LEVER_L))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.88
    r_fl = FL_OD / 2.0
    rf_r = r_pipe + (r_fl - r_pipe) * 0.36
    rf_t = 2.5

    # 1. 左右两片式流道筒节 + 两端 RF 法兰
    o_valve = CYLINDER(s, R=r_pipe * 1.12, H=L - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(L * 0.5 - rf_t), 0.0, 0.0))
    for sx in (-1.0, 1.0):
        x_rf = -L * 0.5 if sx < 0 else (L * 0.5 - rf_t - 1.0)
        c_rf = CYLINDER(s, R=rf_r, H=rf_t + 1.0, O=0.0).rotateY(90.0).translate((x_rf, 0.0, 0.0))
        o_valve.uniteWith(c_rf); c_rf.erase()
        x_fl = (-L * 0.5 + rf_t) if sx < 0 else (L * 0.5 - rf_t - FL_T)
        c_fl = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_valve.uniteWith(c_fl); c_fl.erase()

    # 2. 中部球体包容腔 + 两片式中体连接法兰盘 + 周向连接螺柱
    r_chamber = r_pipe * 1.48
    w_chamber = L * 0.46
    o_cham = CYLINDER(s, R=r_chamber, H=w_chamber, O=0.0).rotateY(90.0).translate((-w_chamber * 0.5, 0.0, 0.0))
    o_valve.uniteWith(o_cham); o_cham.erase()

    r_split_fl = min(r_fl * 0.94, r_chamber * 1.24)
    t_split = FL_T * 1.4
    o_split = CYLINDER(s, R=r_split_fl, H=t_split, O=0.0).rotateY(90.0).translate((-t_split * 0.35, 0.0, 0.0))
    o_valve.uniteWith(o_split); o_split.erase()

    r_sbcd = r_chamber + (r_split_fl - r_chamber) * 0.55
    for i in range(8):
        ang = math.radians(i * 45.0 + 22.5)
        st = CYLINDER(s, R=max(5.0, (r_split_fl - r_chamber) * 0.28), H=t_split * 1.45, O=0.0).rotateY(90.0).translate((-t_split * 0.55, r_sbcd * math.cos(ang), r_sbcd * math.sin(ang)))
        o_valve.uniteWith(st); st.erase()

    # 3. 顶部防吹出阀杆脖颈 + ISO 5211 方形安装平台 + 填料压盖
    z_pad = r_chamber + (H - r_chamber) * 0.45
    r_stem_boss = r_pipe * 0.38
    o_boss = CYLINDER(s, R=r_stem_boss, H=z_pad, O=0.0)
    o_valve.uniteWith(o_boss); o_boss.erase()

    pad_w = r_stem_boss * 2.35
    o_pad = BOX(s, L=pad_w, W=12.0, H=pad_w).translate((0.0, 0.0, z_pad - 6.0))
    o_valve.uniteWith(o_pad); o_pad.erase()

    r_stem = max(8.0, r_pipe * 0.18)
    o_stem = CYLINDER(s, R=r_stem, H=H - z_pad + 14.0, O=0.0).translate((0.0, 0.0, z_pad - 2.0))
    o_valve.uniteWith(o_stem); o_stem.erase()

    # 4. 折弯防干涉长柄扳手 (Cranked Lever Handle: 根部压板 + 斜升过渡段 + 水平握把套)
    h_bar_t = 9.0
    h_bar_w = max(22.0, r_stem * 2.4)
    l_root = LEVER_L * 0.20
    l_riser = LEVER_L * 0.14
    l_grip = LEVER_L * 0.68
    z_lever_base = H - 20.0

    o_root = BOX(s, L=h_bar_w, W=h_bar_t, H=l_root + r_stem * 1.5).translate(((l_root - r_stem * 1.5) * 0.5, 0.0, z_lever_base))
    o_valve.uniteWith(o_root); o_root.erase()

    # 斜升段连接 z_lever_base 到 H
    o_riser = BOX(s, L=h_bar_w, W=H - z_lever_base + h_bar_t, H=h_bar_t * 1.4).translate((l_root, 0.0, 0.5 * (H + z_lever_base)))
    o_valve.uniteWith(o_riser); o_riser.erase()

    # 水平加厚包塑手柄握把 (沿 +X 延伸)
    o_grip = BOX(s, L=h_bar_w * 1.15, W=h_bar_t * 1.45, H=l_grip).translate((l_root + l_grip * 0.5 - 2.0, 0.0, H))
    o_valve.uniteWith(o_grip); o_grip.erase()

    # 5. 贯通流道孔与法兰螺栓孔
    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_valve.subtractFrom(o_bore); o_bore.erase()
    r_bcd = r_pipe + (r_fl - r_pipe) * 0.66
    r_hole = max(5.0, min(13.0, (r_fl - r_pipe) * 0.14))
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        by, bz = r_bcd * math.cos(ang), r_bcd * math.sin(ang)
        hl = CYLINDER(s, R=r_hole, H=FL_T + rf_t + 6.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 2.0), by, bz))
        o_valve.subtractFrom(hl); hl.erase()
        hr = CYLINDER(s, R=r_hole, H=FL_T + rf_t + 6.0, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T - rf_t - 4.0, by, bz))
        o_valve.subtractFrom(hr); hr.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))

    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_fl), (L / 2.0, 0.0, -r_fl))
    s.setLinearDimension("H", (-L / 2.0, 0.0, 0.0), (-L / 2.0, 0.0, H))
    s.setLinearDimension("LEVER_L", (0.0, 0.0, H), (l_root + l_grip, 0.0, H))
