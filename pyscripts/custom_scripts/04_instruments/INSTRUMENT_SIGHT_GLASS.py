# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *


@activate(
    Group="Instrument",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"化工管道直通双面视镜",
    TooltipLong=u"化工凝结水/溶剂/观察管线用直通法兰式双面透光玻璃视镜 (SG-I / HG/T 21575，含十字球形观察腔、两端连接法兰、前后双面6螺栓压盖钢化硼硅玻璃视窗与顶部排气丝堵)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"视镜连接管道外径 (mm)")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"两端连接法兰密封面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"两端连接法兰厚度 (mm)")
@param(W_GLASS=LENGTH, TooltipShort=u"视窗总宽", TooltipLong=u"前后双面玻璃视窗压盖外端面间距 (mm)")
@param(D_WIN=LENGTH, TooltipShort=u"视窗外径", TooltipLong=u"玻璃压盖法兰外径 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧连接法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"管道视镜型号规格编码")
def INSTRUMENT_SIGHT_GLASS(s, D=88.9, L=240.0, FL_OD=200.0, FL_T=22.0, W_GLASS=210.0, D_WIN=155.0, NBOLTS=8, ID=u"SG-111-DN80", **kw):
    D = max(20.0, float(D))
    L = max(140.0, float(L))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    W_GLASS = max(D + 80.0, float(W_GLASS))
    D_WIN = max(D + 45.0, float(D_WIN))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.84
    r_fl = FL_OD / 2.0
    r_win = D_WIN / 2.0

    # 1. 直通管身 + 中央鼓形观察腔 + 两端连接法兰 + 顶部排气/底部排液六角丝堵
    o_m = CYLINDER(s, R=r_pipe * 1.12, H=L - 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    o_hub = SPHERE(s, R=r_pipe * 1.48)
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    o_top_plug = BOX(s, L=28.0, W=28.0, H=28.0).translate((0.0, 0.0, r_pipe * 1.45))
    o_bot_plug = BOX(s, L=28.0, W=28.0, H=28.0).translate((0.0, 0.0, -r_pipe * 1.45))
    for p in (o_hub, fl_l, fl_r, o_top_plug, o_bot_plug):
        o_m.uniteWith(p); p.erase()

    # 2. 前后对称双面玻璃视窗座 + 6螺栓压盖外环 + 凹入钢化玻璃窗凹槽
    o_win_bar = CYLINDER(s, R=r_win * 0.84, H=W_GLASS - 24.0, O=0.0).rotateX(-90.0).translate((0.0, -(W_GLASS * 0.5 - 12.0), 0.0))
    o_m.uniteWith(o_win_bar); o_win_bar.erase()

    for sy in (-1.0, 1.0):
        y_face = sy * (W_GLASS * 0.5)
        w_fl = CYLINDER(s, R=r_win, H=22.0, O=0.0).rotateX(-90.0).translate((0.0, y_face - (22.0 if sy > 0 else 0.0), 0.0))
        o_m.uniteWith(w_fl); w_fl.erase()
        for k in range(6):
            ang = math.radians(60.0 * k + 30.0)
            bt = CYLINDER(s, R=6.5, H=30.0, O=0.0).rotateX(-90.0).translate((r_win * 0.80 * math.cos(ang), y_face - (26.0 if sy > 0 else -4.0), r_win * 0.80 * math.sin(ang)))
            o_m.uniteWith(bt); bt.erase()
        rec = CYLINDER(s, R=r_win * 0.58, H=12.0, O=0.0).rotateX(-90.0).translate((0.0, y_face - (10.0 if sy > 0 else 2.0), 0.0))
        o_m.subtractFrom(rec); rec.erase()

    # 3. 法兰螺栓孔与内流道切除
    r_bcd = (r_pipe + r_fl) * 0.54
    r_hole = max(5.5, (r_fl - r_pipe) * 0.16)
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        for x_pos in (-L * 0.5 - 2.0, L * 0.5 - FL_T - 2.0):
            h_cyl = CYLINDER(s, R=r_hole, H=FL_T + 4.0, O=0.0).rotateY(90.0).translate((x_pos, r_bcd * math.cos(ang), r_bcd * math.sin(ang)))
            o_m.subtractFrom(h_cyl); h_cyl.erase()

    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_m.subtractFrom(o_bore); o_bore.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_fl), (L / 2.0, 0.0, -r_fl))
    s.setLinearDimension("W_GLASS", (0.0, -W_GLASS / 2.0, 0.0), (0.0, W_GLASS / 2.0, 0.0))
