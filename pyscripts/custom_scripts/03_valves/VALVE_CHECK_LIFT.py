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

@activate(Group="Valve", Ports=2, TooltipShort=u"直通升降式法兰止回阀 (H41H / GB/T 12235)", TooltipLong=u"化工标准 GB/T 12235 直通升降式钢制法兰止回阀 (Lift Check Valve)，带球形流道阀体、螺栓连接平顶阀盖与中心活塞导向筒帽", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"升降止回阀主要结构尺寸：结构长度、阀盖顶高与法兰规格")
@param(D=LENGTH, TooltipShort=u"管道外径 D", Ask4Dist=True, TooltipLong=u"连接管道公称外径 OD")
@param(L=LENGTH, TooltipShort=u"结构长度 L", Ask4Dist=True, TooltipLong=u"两端法兰密封面间距 L")
@param(H=LENGTH, TooltipShort=u"中心至阀盖高 H", Ask4Dist=True, TooltipLong=u"管道中心至阀盖导向帽顶部高度 H")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"连接法兰外圆直径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰盘厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"单端法兰螺栓孔数")
@param(ID=STRING, TooltipShort=u"阀门位号", TooltipLong=u"安装位号，如 CV-102")
def VALVE_CHECK_LIFT(s, D=114.3, L=300.0, H=215.0, FL_OD=220.0, FL_T=22.0, NBOLTS=8, ID=u"H41H-16C-DN100", **kw):
    D = max(20.0, float(D))
    L = max(130.0, float(L))
    H = max(100.0, float(H))
    FL_OD = max(D + 50.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.86
    r_fl = FL_OD / 2.0
    rf_r = r_pipe + (r_fl - r_pipe) * 0.36
    rf_t = 2.5

    # 1. 直通管段 + 两端 RF 法兰
    o_v = CYLINDER(s, R=r_pipe * 1.08, H=L - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(L * 0.5 - rf_t), 0.0, 0.0))
    for sx in (-1.0, 1.0):
        x_rf = -L * 0.5 if sx < 0 else (L * 0.5 - rf_t - 1.0)
        c_rf = CYLINDER(s, R=rf_r, H=rf_t + 1.0, O=0.0).rotateY(90.0).translate((x_rf, 0.0, 0.0))
        o_v.uniteWith(c_rf); c_rf.erase()
        x_fl = (-L * 0.5 + rf_t) if sx < 0 else (L * 0.5 - rf_t - FL_T)
        c_fl = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_v.uniteWith(c_fl); c_fl.erase()

    # 2. 中部球肚阀体 (与截止阀同源的 S 形球腔)
    r_globe = r_pipe * 1.52
    o_top_g = ELLIPSOIDHEAD(s, R=r_globe, H=r_globe * 0.90)
    o_bot_g = ELLIPSOIDHEAD(s, R=r_globe, H=r_globe * 0.85).rotateX(180.0)
    o_v.uniteWith(o_top_g); o_top_g.erase()
    o_v.uniteWith(o_bot_g); o_bot_g.erase()

    # 3. 顶部中法兰 + 螺栓圈 + 活塞导向筒帽（无手轮，区别于截止阀与旋启式止回阀）
    z_bfl = r_globe * 0.68
    r_bfl = r_globe * 1.08
    t_bfl = 32.0
    o_bfl = CYLINDER(s, R=r_bfl, H=t_bfl, O=0.0).translate((0.0, 0.0, z_bfl))
    o_v.uniteWith(o_bfl); o_bfl.erase()

    r_bbcd = r_bfl * 0.78
    for i in range(8):
        ang = math.radians(i * 45.0)
        bt = CYLINDER(s, R=max(5.5, r_pipe * 0.11), H=t_bfl + 14.0, O=0.0).translate((r_bbcd * math.cos(ang), r_bbcd * math.sin(ang), z_bfl - 4.0))
        o_v.uniteWith(bt); bt.erase()

    z_cap = z_bfl + t_bfl - 2.0
    h_cap = max(24.0, H - z_cap)
    o_cap = CYLINDER(s, R=r_globe * 0.48, H=h_cap, O=0.0).translate((0.0, 0.0, z_cap))
    o_hex = BOX(s, L=r_globe * 0.55, W=16.0, H=r_globe * 0.55).translate((0.0, 0.0, H - 8.0))
    o_v.uniteWith(o_cap); o_cap.erase()
    o_v.uniteWith(o_hex); o_hex.erase()

    # 4. 贯通流道与两端法兰螺栓孔
    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_v.subtractFrom(o_bore); o_bore.erase()
    r_bcd = r_pipe + (r_fl - r_pipe) * 0.66
    r_hole = max(5.0, min(13.0, (r_fl - r_pipe) * 0.14))
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        by, bz = r_bcd * math.cos(ang), r_bcd * math.sin(ang)
        hl = CYLINDER(s, R=r_hole, H=FL_T + rf_t + 6.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 2.0), by, bz))
        o_v.subtractFrom(hl); hl.erase()
        hr = CYLINDER(s, R=r_hole, H=FL_T + rf_t + 6.0, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T - rf_t - 4.0, by, bz))
        o_v.subtractFrom(hr); hr.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_fl), (L / 2.0, 0.0, -r_fl))
    s.setLinearDimension("H", (-L / 2.0, 0.0, 0.0), (-L / 2.0, 0.0, H))
