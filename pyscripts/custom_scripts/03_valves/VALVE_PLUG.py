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

@activate(Group="Valve", Ports=2, TooltipShort=u"油封衬氟法兰旋塞阀 (X41W / API 599)", TooltipLong=u"化工标准 GB/T 22130 / API 599 法兰连接倒锥形旋塞阀 (Lubricated / Sleeved Plug Valve)，带倒锥形塞体腔、四螺栓三角压盖、防吹出阀杆与折弯手柄", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"旋塞阀主要结构尺寸：结构长度、中心高与法兰规格")
@param(D=LENGTH, TooltipShort=u"管道外径 D", Ask4Dist=True, TooltipLong=u"连接管道公称外径 OD")
@param(L=LENGTH, TooltipShort=u"结构长度 L", Ask4Dist=True, TooltipLong=u"两端法兰密封面间距 L")
@param(H=LENGTH, TooltipShort=u"中心至手柄高 H", Ask4Dist=True, TooltipLong=u"管道中心至顶部手柄高度 H")
@param(LEVER_L=LENGTH, TooltipShort=u"扳手手柄长", TooltipLong=u"顶部操作扳手总长度")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"连接法兰外圆直径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰盘厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"单端法兰螺栓孔数量")
@param(ID=STRING, TooltipShort=u"阀门位号", TooltipLong=u"安装位号，如 PV-101")
def VALVE_PLUG(s, D=114.3, L=229.0, H=210.0, LEVER_L=280.0, FL_OD=220.0, FL_T=22.0, NBOLTS=8, ID=u"X43F-16C-DN100", **kw):
    D = max(20.0, float(D))
    L = max(120.0, float(L))
    H = max(100.0, float(H))
    LEVER_L = max(120.0, float(LEVER_L))
    FL_OD = max(D + 50.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.86
    r_fl = FL_OD / 2.0
    rf_r = r_pipe + (r_fl - r_pipe) * 0.36
    rf_t = 2.5

    # 1. 左右流道圆筒与两端 RF 法兰
    o_v = CYLINDER(s, R=r_pipe * 1.10, H=L - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(L * 0.5 - rf_t), 0.0, 0.0))
    for sx in (-1.0, 1.0):
        x_rf = -L * 0.5 if sx < 0 else (L * 0.5 - rf_t - 1.0)
        c_rf = CYLINDER(s, R=rf_r, H=rf_t + 1.0, O=0.0).rotateY(90.0).translate((x_rf, 0.0, 0.0))
        o_v.uniteWith(c_rf); c_rf.erase()
        x_fl = (-L * 0.5 + rf_t) if sx < 0 else (L * 0.5 - rf_t - FL_T)
        c_fl = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_v.uniteWith(c_fl); c_fl.erase()

    # 2. 中部特征锥形旋塞体腔 (上宽下窄正锥台 + 底部调节螺塞凸台)
    z_plug_bot = -r_pipe * 1.25
    z_plug_top = r_pipe * 1.35
    r_plug_bot = r_pipe * 1.12
    r_plug_top = r_pipe * 1.42
    o_plug = CONE(s, R1=r_plug_bot, R2=r_plug_top, H=z_plug_top - z_plug_bot, E=0.0).translate((0.0, 0.0, z_plug_bot))
    o_v.uniteWith(o_plug); o_plug.erase()

    o_bot_cap = CYLINDER(s, R=r_plug_bot * 0.92, H=16.0, O=0.0).translate((0.0, 0.0, z_plug_bot - 14.0))
    o_v.uniteWith(o_bot_cap); o_bot_cap.erase()

    # 3. 顶部方形/菱形四螺栓压盖法兰与调节填料函
    w_cov = r_plug_top * 2.15
    t_cov = 18.0
    o_cov = BOX(s, L=w_cov, W=t_cov, H=w_cov).translate((0.0, 0.0, z_plug_top + t_cov * 0.4))
    o_v.uniteWith(o_cov); o_cov.erase()
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bt = CYLINDER(s, R=max(5.0, r_pipe * 0.11), H=t_cov + 12.0, O=0.0).translate((sx * w_cov * 0.36, sy * w_cov * 0.36, z_plug_top - 2.0))
            o_v.uniteWith(bt); bt.erase()

    # 4. 旋塞阀杆颈 + 四方驱动头 + 折弯手柄
    z_stem_base = z_plug_top + t_cov * 0.8
    r_stem = max(10.0, r_pipe * 0.24)
    o_stem = CYLINDER(s, R=r_stem, H=H - z_stem_base, O=0.0).translate((0.0, 0.0, z_stem_base))
    o_v.uniteWith(o_stem); o_stem.erase()

    sq_w = r_stem * 2.2
    o_sq = BOX(s, L=sq_w, W=22.0, H=sq_w).translate((0.0, 0.0, H - 11.0))
    o_v.uniteWith(o_sq); o_sq.erase()

    bar_w = max(22.0, r_stem * 1.8)
    bar_t = 10.0
    o_lever = BOX(s, L=bar_w, W=bar_t, H=LEVER_L).translate((LEVER_L * 0.5 - r_stem, 0.0, H - bar_t * 0.5))
    o_v.uniteWith(o_lever); o_lever.erase()

    # 5. 贯通流道与两端法兰螺栓孔
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
    s.setLinearDimension("LEVER_L", (0.0, 0.0, H), (LEVER_L - r_stem, 0.0, H))
