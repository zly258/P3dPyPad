# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Valve",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"堰式衬氟法兰隔膜阀",
    TooltipLong=u"化工强酸强碱及腐蚀性介质用堰式衬氟隔膜阀 (G41F46 / BS 5156，含鱼腹式弧形隔膜堰腔、四螺栓方形压盖法兰、阶梯式阀盖、行程指示环与手轮)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"阀门连接管道外径 (mm)")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"两端法兰密封面间距离 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(H=LENGTH, TooltipShort=u"中心至顶高", TooltipLong=u"流道中心至手轮顶面总高度 (mm)")
@param(W_BON=LENGTH, TooltipShort=u"隔膜盖宽度", TooltipLong=u"中部四螺栓隔膜压盖外径/边宽 (mm)")
@param(W_DIA=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"顶部操作手轮直径 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧连接法兰螺栓孔数量")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"隔膜阀图集型号编码")
def VALVE_DIAPHRAGM(s, D=114.3, L=310.0, FL_OD=220.0, FL_T=22.0, H=342.0, W_BON=195.0, W_DIA=220.0, NBOLTS=8, ID=u"G41F46-DN100", **kw):
    D = max(20.0, float(D))
    L = max(120.0, float(L))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    H = max(180.0, float(H))
    W_BON = max(D * 1.45, float(W_BON))
    W_DIA = max(120.0, float(W_DIA))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.84
    r_fl = FL_OD / 2.0

    # 1. 左右直通流道颈 + 两端连接法兰与密封面
    o_m = CYLINDER(s, R=r_pipe * 1.05, H=L - 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    o_m.uniteWith(fl_l); fl_l.erase()
    o_m.uniteWith(fl_r); fl_r.erase()

    # 2. 鱼腹式横向鞍桥堰腔 + 四螺栓圆角方形隔膜压盖法兰盘
    z_weir = r_pipe * 0.72
    o_saddle = CYLINDER(s, R=r_pipe * 1.18, H=W_BON * 1.02, O=0.0).rotateX(-90.0).translate((0.0, -W_BON * 0.51, z_weir * 0.25))
    o_weir_neck = CONE(s, R1=W_BON * 0.52, R2=W_BON * 0.55, H=z_weir * 0.85, E=0.0).translate((0.0, 0.0, z_weir * 0.2))
    t_bfl = max(16.0, FL_T * 0.8)
    o_bfl_disk = CYLINDER(s, R=W_BON * 0.56, H=t_bfl * 2.1, O=0.0).translate((0.0, 0.0, z_weir))
    o_bfl_sq = BOX(s, L=W_BON * 0.92, W=t_bfl * 2.1, H=W_BON * 0.86).translate((0.0, 0.0, z_weir + t_bfl * 1.05))
    for p in (o_saddle, o_weir_neck, o_bfl_disk, o_bfl_sq):
        o_m.uniteWith(p); p.erase()

    # 隔膜压盖四角紧固螺栓
    off_b = W_BON * 0.35
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bt = CYLINDER(s, R=8.5, H=t_bfl * 2.8, O=0.0).translate((sx * off_b * 0.92, sy * off_b, z_weir - 4.0))
            o_m.uniteWith(bt); bt.erase()

    # 3. 阶梯钟罩式隔膜阀盖 + 阀盖纵肋 + 行程限位指示套 + 顶手轮
    z_bon0 = z_weir + t_bfl * 2.1
    z_wheel = H - 24.0
    h_bon = max(50.0, z_wheel - z_bon0 - 38.0)
    r_stem = max(13.0, D * 0.13)
    o_bon_low = CONE(s, R1=W_BON * 0.44, R2=W_BON * 0.24, H=h_bon * 0.65, E=0.0).translate((0.0, 0.0, z_bon0 - 2.0))
    o_bon_up = CYLINDER(s, R=W_BON * 0.22, H=h_bon * 0.42, O=0.0).translate((0.0, 0.0, z_bon0 + h_bon * 0.58))
    o_ind = CYLINDER(s, R=r_stem * 1.75, H=16.0, O=0.0).translate((0.0, 0.0, z_bon0 + h_bon + 8.0))
    o_stem = CYLINDER(s, R=r_stem, H=H - z_bon0, O=0.0).translate((0.0, 0.0, z_bon0))
    for p in (o_bon_low, o_bon_up, o_ind, o_stem):
        o_m.uniteWith(p); p.erase()

    for ang in (0.0, 90.0):
        rib = BOX(s, L=10.0, W=h_bon * 0.62, H=W_BON * 0.84).rotateZ(ang).translate((0.0, 0.0, z_bon0 + h_bon * 0.31))
        o_m.uniteWith(rib); rib.erase()

    # 手轮圆环与四辐条
    r_w = W_DIA / 2.0
    w_thk = max(12.0, W_DIA * 0.065)
    o_rim = TORUS(s, R1=r_w - w_thk * 0.5, R2=w_thk * 0.5).translate((0.0, 0.0, z_wheel))
    o_hub = CYLINDER(s, R=r_stem * 1.9, H=w_thk * 1.3, O=0.0).translate((0.0, 0.0, z_wheel - w_thk * 0.65))
    o_m.uniteWith(o_rim); o_rim.erase()
    o_m.uniteWith(o_hub); o_hub.erase()
    for k in range(4):
        spk = BOX(s, L=w_thk * 0.7, W=w_thk * 0.65, H=r_w * 1.85).rotateZ(k * 45.0).translate((0.0, 0.0, z_wheel))
        o_m.uniteWith(spk); spk.erase()

    # 法兰螺栓孔与内流道切除
    r_bcd = (r_pipe + r_fl) * 0.54
    r_hole = max(6.0, (r_fl - r_pipe) * 0.16)
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
    s.setLinearDimension("H", (0.0, 0.0, 0.0), (0.0, 0.0, H))
    s.setLinearDimension("W_DIA", (-r_w, 0.0, z_wheel), (r_w, 0.0, z_wheel))
