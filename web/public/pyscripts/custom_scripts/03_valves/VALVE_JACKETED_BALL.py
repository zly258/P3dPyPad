# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Valve",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"蒸汽保温夹套法兰球阀",
    TooltipLong=u"化工硫磺/沥青/高凝点聚合物管线用外包全夹套保温法兰球阀 (BQ41F，含外包大直径圆柱焊接蒸汽夹套筒、缩径加大连接法兰、底部进汽排凝伴热法兰管嘴、防吹出阀杆平台与长扳手)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"主管内通径", TooltipLong=u"球阀实际介质流道外径 (mm)")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"两端连接法兰密封面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"大法兰外径", TooltipLong=u"放大一档的保温夹套连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(D_JKT=LENGTH, TooltipShort=u"夹套筒外径", TooltipLong=u"外包蒸汽保温夹套圆筒外径 (mm)")
@param(H=LENGTH, TooltipShort=u"中心至顶高", TooltipLong=u"流道中心至操作手柄顶面高度 (mm)")
@param(LEVER_L=LENGTH, TooltipShort=u"手柄长度", TooltipLong=u"手动扳手手柄长度 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧大法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"保温夹套球阀图集型号编码")
def VALVE_JACKETED_BALL(s, D=88.9, L=240.0, FL_OD=250.0, FL_T=24.0, D_JKT=185.0, H=235.0, LEVER_L=280.0, NBOLTS=8, ID=u"BQ41F-DN80x125", **kw):
    D = max(25.0, float(D))
    L = max(140.0, float(L))
    D_JKT = max(D * 1.65, float(D_JKT))
    FL_OD = max(D_JKT + 45.0, float(FL_OD))
    FL_T = max(14.0, float(FL_T))
    H = max(D_JKT * 0.5 + 95.0, float(H))
    LEVER_L = max(160.0, float(LEVER_L))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.85
    r_jkt = D_JKT / 2.0
    r_fl = FL_OD / 2.0

    # 1. 外包全夹套焊接圆筒壳体 + 夹套两端环焊缝凸缘 + 两端放大连接法兰
    l_jkt = L - 2.0 * FL_T - 20.0
    o_m = CYLINDER(s, R=r_jkt, H=l_jkt, O=0.0).rotateY(90.0).translate((-l_jkt * 0.5, 0.0, 0.0))
    o_neck = CYLINDER(s, R=r_jkt * 0.84, H=L - 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    for p in (o_neck, fl_l, fl_r):
        o_m.uniteWith(p); p.erase()

    # 2. 侧向与底部蒸汽伴热进汽/排凝小法兰接管 (DN20, 位于 +Y 与 -Z)
    for sx in (-0.25, 0.25):
        st_n = CYLINDER(s, R=13.5, H=r_jkt + 52.0, O=0.0).rotateX(-90.0).translate((sx * l_jkt, 0.0, 0.0))
        st_f = CYLINDER(s, R=42.0, H=14.0, O=0.0).rotateX(-90.0).translate((sx * l_jkt, r_jkt + 38.0, 0.0))
        o_m.uniteWith(st_n); st_n.erase()
        o_m.uniteWith(st_f); st_f.erase()

    dr_n = CYLINDER(s, R=13.5, H=r_jkt + 48.0, O=0.0).translate((0.0, 0.0, -(r_jkt + 48.0)))
    dr_f = CYLINDER(s, R=42.0, H=14.0, O=0.0).translate((0.0, 0.0, -(r_jkt + 48.0)))
    o_m.uniteWith(dr_n); dr_n.erase()
    o_m.uniteWith(dr_f); dr_f.erase()

    # 3. 顶部加高保温填料函柱 + ISO 5211 方形安装平台 + 阀杆与扁钢长手柄
    o_pad = BOX(s, L=82.0, W=18.0, H=82.0).translate((0.0, 0.0, r_jkt + 32.0))
    o_stem_col = CYLINDER(s, R=28.0, H=H - r_jkt * 0.6, O=0.0).translate((0.0, 0.0, r_jkt * 0.6))
    o_lever = BOX(s, L=28.0, W=14.0, H=LEVER_L).translate((LEVER_L * 0.5 - 20.0, 0.0, H - 7.0))
    for p in (o_pad, o_stem_col, o_lever):
        o_m.uniteWith(p); p.erase()

    # 4. 法兰螺栓孔与内流道切除
    r_bcd = (r_jkt * 0.8 + r_fl) * 0.54
    r_hole = max(6.0, (r_fl - r_jkt * 0.8) * 0.16)
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
    s.setLinearDimension("FL_OD", (-L / 2.0, -r_fl, 0.0), (-L / 2.0, r_fl, 0.0))
