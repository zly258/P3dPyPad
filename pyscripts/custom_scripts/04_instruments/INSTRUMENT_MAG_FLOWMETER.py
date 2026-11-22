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

@activate(Group="Instrument", Ports=2, TooltipShort=u"法兰式智能电磁流量计 (EMF / JB/T 9248)", TooltipLong=u"化工标准 JB/T 9248 / HG/T 20507 一体化法兰式智能电磁流量计 (Flanged Electromagnetic Flowmeter)，含PTFE内衬测量直管、两端连接法兰、中部励磁线圈金属外壳、连接立柱与双腔防爆转换器表头", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"电磁流量计主要结构尺寸：结构长度、线圈腔径与表头高")
@param(D=LENGTH, TooltipShort=u"管道外径 D", Ask4Dist=True, TooltipLong=u"连接管道公称外径 OD")
@param(L=LENGTH, TooltipShort=u"结构长度 L", Ask4Dist=True, TooltipLong=u"两端法兰安装间距 L (JB/T 9248)")
@param(D_COIL=LENGTH, TooltipShort=u"励磁腔外径", Ask4Dist=True, TooltipLong=u"中部励磁线圈屏蔽筒外径")
@param(H_HEAD=LENGTH, TooltipShort=u"中心至表头高", Ask4Dist=True, TooltipLong=u"管道中心至顶部转换器表头高度")
@param(D_HEAD=LENGTH, TooltipShort=u"转换器外径", TooltipLong=u"顶部防爆转换器圆形表壳外径")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"两端连接法兰厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"单端法兰螺栓孔数")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"安装位号，如 FE/FIT-101")
def INSTRUMENT_MAG_FLOWMETER(s, D=114.3, L=250.0, D_COIL=168.0, H_HEAD=310.0, D_HEAD=145.0, FL_OD=220.0, FL_T=22.0, NBOLTS=8, ID=u"FIT-101-DN100", **kw):
    D = max(20.0, float(D))
    L = max(150.0, float(L))
    D_COIL = max(D * 1.32, float(D_COIL))
    H_HEAD = max(D * 1.8, float(H_HEAD))
    D_HEAD = max(110.0, float(D_HEAD))
    FL_OD = max(D + 50.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.86
    r_coil = D_COIL / 2.0
    r_head = D_HEAD / 2.0
    r_fl = FL_OD / 2.0
    rf_r = r_pipe + (r_fl - r_pipe) * 0.36
    rf_t = 2.5

    # 1. 测量直管段 + 两端法兰 + 中部加粗励磁线圈屏蔽腔
    o_m = CYLINDER(s, R=r_pipe * 1.06, H=L - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(L * 0.5 - rf_t), 0.0, 0.0))
    for sx in (-1.0, 1.0):
        x_rf = -L * 0.5 if sx < 0 else (L * 0.5 - rf_t - 1.0)
        c_rf = CYLINDER(s, R=rf_r, H=rf_t + 1.0, O=0.0).rotateY(90.0).translate((x_rf, 0.0, 0.0))
        o_m.uniteWith(c_rf); c_rf.erase()
        x_fl = (-L * 0.5 + rf_t) if sx < 0 else (L * 0.5 - rf_t - FL_T)
        c_fl = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_m.uniteWith(c_fl); c_fl.erase()

    w_coil = L * 0.54
    o_coil = CYLINDER(s, R=r_coil, H=w_coil, O=0.0).rotateY(90.0).translate((-w_coil * 0.5, 0.0, 0.0))
    o_m.uniteWith(o_coil); o_coil.erase()

    # 2. 顶部转换器支承颈柱 + 横向双腔防爆转换器表头 + 观察窗凹槽 + 电缆防爆格兰头
    z_head_c = H_HEAD - r_head
    o_neck = CYLINDER(s, R=26.0, H=z_head_c, O=0.0)
    o_nbase = BOX(s, L=68.0, W=22.0, H=68.0).translate((0.0, 0.0, r_coil))
    o_m.uniteWith(o_neck); o_neck.erase()
    o_m.uniteWith(o_nbase); o_nbase.erase()

    len_head = D_HEAD * 1.18
    o_head = CYLINDER(s, R=r_head, H=len_head, O=0.0).rotateX(90.0).translate((0.0, len_head * 0.5, z_head_c))
    o_bezel = CYLINDER(s, R=r_head * 1.05, H=22.0, O=0.0).rotateX(90.0).translate((0.0, -len_head * 0.5 + 22.0, z_head_c))
    o_m.uniteWith(o_head); o_head.erase()
    o_m.uniteWith(o_bezel); o_bezel.erase()

    o_win = CYLINDER(s, R=r_head * 0.72, H=10.0, O=0.0).rotateX(90.0).translate((0.0, -len_head * 0.5 + 8.0, z_head_c))
    o_m.subtractFrom(o_win); o_win.erase()

    for sx in (-1.0, 1.0):
        gl = CYLINDER(s, R=14.0, H=r_head + 28.0, O=0.0).rotateY(90.0 * sx).translate((0.0, 0.0, z_head_c - 15.0))
        o_m.uniteWith(gl); gl.erase()

    # 3. 贯通测量内流道与法兰螺栓孔
    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_m.subtractFrom(o_bore); o_bore.erase()
    r_bcd = r_pipe + (r_fl - r_pipe) * 0.66
    r_hole = max(5.0, min(13.0, (r_fl - r_pipe) * 0.14))
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
    s.setLinearDimension("H_HEAD", (-L / 2.0, 0.0, 0.0), (-L / 2.0, 0.0, H_HEAD))
    s.setLinearDimension("D_COIL", (0.0, -r_coil, -r_coil), (0.0, r_coil, -r_coil))
