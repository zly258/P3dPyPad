# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *


@activate(
    Group="Valve",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"气动薄膜单座调节阀 (ZJHP / IEC 60534)",
    TooltipLong=u"化工过程控制气动薄膜直通单座/套筒调节阀 (ZJHP / IEC 60534，含球形制御阀体、上阀盖散热鳍片、双立柱支架、智能电气阀门定位器、空气过滤减压阀与12螺栓气动薄膜执行机构)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"调节阀连接管道外径 (mm)")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"两端连接法兰密封面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(H_BON=LENGTH, TooltipShort=u"支架顶高", TooltipLong=u"流道中心至气动膜头底部的高度 (mm)")
@param(D_ACT=LENGTH, TooltipShort=u"膜头直径", TooltipLong=u"气动薄膜执行机构外径 (mm)")
@param(H_ACT=LENGTH, TooltipShort=u"膜头高度", TooltipLong=u"气动薄膜执行机构上下膜盖总高 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧连接法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"气动薄膜调节阀图集型号编码")
def VALVE_CONTROL_PNEUMATIC(s, D=88.9, L=292.0, FL_OD=200.0, FL_T=22.0, H_BON=420.0, D_ACT=320.0, H_ACT=124.0, NBOLTS=8, ID=u"ZJHP-DN80", **kw):
    D = max(20.0, float(D))
    L = max(150.0, float(L))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(14.0, float(FL_T))
    H_BON = max(240.0, float(H_BON))
    D_ACT = max(180.0, float(D_ACT))
    H_ACT = max(80.0, float(H_ACT))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.82
    r_fl = FL_OD / 2.0
    r_act = D_ACT / 2.0

    # 1. 球形单座阀体 + 直通流道颈 + 两端法兰
    o_m = SPHERE(s, R=r_pipe * 1.52)
    o_neck = CYLINDER(s, R=r_pipe * 1.12, H=L - 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    for p in (o_neck, fl_l, fl_r):
        o_m.uniteWith(p); p.erase()

    # 2. 上阀盖法兰 + 散热片阀盖 + 双立柱开窗支架 + 智能阀门定位器 + 空气过滤减压阀
    z_bon0 = r_pipe * 1.15
    z_yoke0 = z_bon0 + 115.0
    h_yoke = max(90.0, H_BON - z_yoke0)
    o_bfl = CYLINDER(s, R=r_pipe * 1.42, H=24.0, O=0.0).translate((0.0, 0.0, z_bon0))
    o_bon = CYLINDER(s, R=r_pipe * 0.85, H=120.0, O=0.0).translate((0.0, 0.0, z_bon0))
    o_stem = CYLINDER(s, R=12.0, H=H_BON - z_bon0 + 20.0, O=0.0).translate((0.0, 0.0, z_bon0))
    for p in (o_bfl, o_bon, o_stem):
        o_m.uniteWith(p); p.erase()

    for zf in (0.38, 0.62, 0.86):
        fin = CYLINDER(s, R=r_pipe * 1.18, H=8.0, O=0.0).translate((0.0, 0.0, z_bon0 + 115.0 * zf))
        o_m.uniteWith(fin); fin.erase()

    for sy in (-1.0, 1.0):
        leg = CYLINDER(s, R=17.0, H=h_yoke + 16.0, O=0.0).translate((0.0, sy * r_pipe * 0.92, z_yoke0 - 6.0))
        o_m.uniteWith(leg); leg.erase()

    o_ytop = CYLINDER(s, R=r_pipe * 1.28, H=22.0, O=0.0).translate((0.0, 0.0, H_BON - 18.0))
    o_pos = BOX(s, L=68.0, W=90.0, H=65.0).translate((42.0, -r_pipe * 1.32, z_yoke0 + h_yoke * 0.5))
    o_afr = CYLINDER(s, R=22.0, H=78.0, O=0.0).translate((-38.0, -r_pipe * 1.25, z_yoke0 + h_yoke * 0.35))
    for p in (o_ytop, o_pos, o_afr):
        o_m.uniteWith(p); p.erase()

    # 3. 顶部气动薄膜执行机构 + 12颗周向夹紧螺栓
    o_d_low = CONE(s, R1=r_pipe * 1.2, R2=r_act * 0.92, H=H_ACT * 0.44, E=0.0).translate((0.0, 0.0, H_BON))
    o_d_rim = CYLINDER(s, R=r_act, H=16.0, O=0.0).translate((0.0, 0.0, H_BON + H_ACT * 0.44 - 4.0))
    o_d_top = ELLIPSOIDHEAD(s, R=r_act * 0.92, H=H_ACT * 0.46).translate((0.0, 0.0, H_BON + H_ACT * 0.54))
    for p in (o_d_low, o_d_rim, o_d_top):
        o_m.uniteWith(p); p.erase()

    for k in range(12):
        ang = math.radians(30.0 * k)
        bt = CYLINDER(s, R=5.5, H=28.0, O=0.0).translate((r_act * 0.94 * math.cos(ang), r_act * 0.94 * math.sin(ang), H_BON + H_ACT * 0.44 - 10.0))
        o_m.uniteWith(bt); bt.erase()

    # 法兰螺栓孔与内流道切除
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
    s.setLinearDimension("H_BON", (0.0, 0.0, 0.0), (0.0, 0.0, H_BON + H_ACT))
    s.setLinearDimension("D_ACT", (-r_act, 0.0, H_BON + H_ACT * 0.5), (r_act, 0.0, H_BON + H_ACT * 0.5))
