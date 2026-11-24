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

@activate(Group="Instrument", Ports=2, TooltipShort=u"温压补偿法兰式涡街流量计 (LUGB / JB/T 9249)", TooltipLong=u"化工标准 JB/T 9249 一体化温压补偿法兰式涡街流量计 (Flanged Vortex Shedding Flowmeter)，含带旋涡发生体三角柱的法兰测量管、细长高温散热隔离立柱与顶部防爆变送表头", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"涡街流量计主要结构尺寸：结构长度、散热颈高与表头尺寸")
@param(D=LENGTH, TooltipShort=u"管道外径 D", Ask4Dist=True, TooltipLong=u"连接管道公称外径 OD")
@param(L=LENGTH, TooltipShort=u"结构长度 L", Ask4Dist=True, TooltipLong=u"两端法兰端面间距 L")
@param(H_NECK=LENGTH, TooltipShort=u"中心至表头高", Ask4Dist=True, TooltipLong=u"管道中心至顶部表头总高度 H")
@param(D_HEAD=LENGTH, TooltipShort=u"表头外径", TooltipLong=u"顶部防爆变送表头直径")
@param(L_HEAD=LENGTH, TooltipShort=u"表头深度", TooltipLong=u"顶部防爆表头前后总长")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"两端连接法兰厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"单端法兰螺栓孔数")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"安装位号，如 FT-102")
def INSTRUMENT_VORTEX_FLOWMETER(s, D=88.9, L=200.0, H_NECK=340.0, D_HEAD=125.0, L_HEAD=150.0, FL_OD=200.0, FL_T=20.0, NBOLTS=8, ID=u"FT-102-DN80", **kw):
    D = max(20.0, float(D))
    L = max(140.0, float(L))
    H_NECK = max(D * 2.2, float(H_NECK))
    D_HEAD = max(95.0, float(D_HEAD))
    L_HEAD = max(110.0, float(L_HEAD))
    FL_OD = max(D + 50.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.86
    r_head = D_HEAD / 2.0
    r_fl = FL_OD / 2.0
    rf_r = r_pipe + (r_fl - r_pipe) * 0.36
    rf_t = 2.5

    # 1. 测量管本体 + 两端连接法兰
    o_m = CYLINDER(s, R=r_pipe * 1.08, H=L - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(L * 0.5 - rf_t), 0.0, 0.0))
    for sx in (-1.0, 1.0):
        x_rf = -L * 0.5 if sx < 0 else (L * 0.5 - rf_t - 1.0)
        c_rf = CYLINDER(s, R=rf_r, H=rf_t + 1.0, O=0.0).rotateY(90.0).translate((x_rf, 0.0, 0.0))
        o_m.uniteWith(c_rf); c_rf.erase()
        x_fl = (-L * 0.5 + rf_t) if sx < 0 else (L * 0.5 - rf_t - FL_T)
        c_fl = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_m.uniteWith(c_fl); c_fl.erase()

    # 2. 压电传感器底座法兰 + 细长散热隔离立柱 + 侧向温压补偿探头凸台 + 顶部变送器表头
    z_hc = H_NECK - r_head
    o_sbase = CYLINDER(s, R=38.0, H=24.0, O=0.0).translate((0.0, 0.0, r_pipe * 0.9))
    o_stem = CYLINDER(s, R=16.0, H=z_hc, O=0.0)
    o_m.uniteWith(o_sbase); o_sbase.erase()
    o_m.uniteWith(o_stem); o_stem.erase()
    for k in range(3):
        fin = CYLINDER(s, R=28.0, H=5.0, O=0.0).translate((0.0, 0.0, r_pipe + 35.0 + k * 22.0))
        o_m.uniteWith(fin); fin.erase()

    o_head = CYLINDER(s, R=r_head, H=L_HEAD, O=0.0).rotateX(90.0).translate((0.0, L_HEAD * 0.5, z_hc))
    o_m.uniteWith(o_head); o_head.erase()
    o_win = CYLINDER(s, R=r_head * 0.72, H=8.0, O=0.0).rotateX(90.0).translate((0.0, -L_HEAD * 0.5 + 6.0, z_hc))
    o_m.subtractFrom(o_win); o_win.erase()

    # 3. 切除内流道后，在流道中央并入竖向梯形旋涡发生体柱 (Vortex Bluff Bar)
    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_m.subtractFrom(o_bore); o_bore.erase()

    o_bluff = BOX(s, L=r_bore * 0.52, W=2.0 * r_bore + 8.0, H=r_bore * 0.48)
    o_m.uniteWith(o_bluff); o_bluff.erase()

    r_bcd = r_pipe + (r_fl - r_pipe) * 0.66
    r_hole = max(5.0, min(12.0, (r_fl - r_pipe) * 0.14))
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        by, bz = r_bcd * math.cos(ang), r_bcd * math.sin(ang)
        hl = CYLINDER(s, R=r_hole, H=FL_T + rf_t + 6.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 2.0), by, bz))
        o_m.subtractFrom(hl); hl.erase()
        hr = CYLINDER(s, R=r_hole, H=FL_T + rf_t + 6.0, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T - rf_t - 4.0, by, bz))
        o_m.subtractFrom(hr); hr.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_fl), (L / 2.0, 0.0, -r_fl))
    s.setLinearDimension("H_NECK", (-L / 2.0, 0.0, 0.0), (-L / 2.0, 0.0, H_NECK))
