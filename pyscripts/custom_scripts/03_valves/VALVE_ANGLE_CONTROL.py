# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *


@activate(
    Group="Valve",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"气动薄膜高压角式调节阀",
    TooltipLong=u"化工高压差防空化/防冲刷閃蒸工段 90° 气动薄膜高压角式调节阀 (ZJHQ / IEC 60534，含锻造球形角式阀体、上阀盖散热片、双柱开窗支架、行程刻度尺、12螺栓气动薄膜头与电气阀门定位器)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"阀门连接管道外径 (mm)")
@param(C=LENGTH, TooltipShort=u"中心至法兰距", TooltipLong=u"阀体中心至侧进/底出法兰密封面距离 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"进出口连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(H=LENGTH, TooltipShort=u"中心至顶高", TooltipLong=u"流道中心至气动薄膜执行机构顶部总高 (mm)")
@param(D_ACT=LENGTH, TooltipShort=u"膜头直径", TooltipLong=u"顶部气动薄膜执行机构外壳直径 (mm)")
@param(H_ACT=LENGTH, TooltipShort=u"膜头厚度", TooltipLong=u"气动薄膜执行机构上下膜盖总高 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧连接法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"气动角式调节阀图集型号编码")
def VALVE_ANGLE_CONTROL(s, D=88.9, C=155.0, FL_OD=200.0, FL_T=22.0, H=519.0, D_ACT=320.0, H_ACT=115.0, NBOLTS=8, ID=u"ZJHQ-DN80", **kw):
    D = max(25.0, float(D))
    C = max(100.0, float(C))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(14.0, float(FL_T))
    H = max(320.0, float(H))
    D_ACT = max(180.0, float(D_ACT))
    H_ACT = max(75.0, float(H_ACT))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.82
    r_fl = FL_OD / 2.0
    r_act = D_ACT / 2.0

    # 1. 90° 锻造球形角式阀腔 + 侧向进口 (-X) + 底部出口 (-Z)
    o_m = SPHERE(s, R=r_pipe * 1.48)
    n_in = CYLINDER(s, R=r_pipe * 1.12, H=C - FL_T, O=0.0).rotateY(-90.0)
    fl_in = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(-90.0).translate((-(C - FL_T), 0.0, 0.0))
    n_out = CYLINDER(s, R=r_pipe * 1.12, H=C - FL_T, O=0.0).rotateY(180.0)
    fl_out = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).translate((0.0, 0.0, -C))
    for p in (n_in, fl_in, n_out, fl_out):
        o_m.uniteWith(p); p.erase()

    # 2. 带散热片的加长上阀盖 + 双立柱支架 + 行程刻度牌 + 侧向智能定位器与空气过滤减压阀
    z_bon0 = r_pipe * 1.12
    z_yoke0 = z_bon0 + 105.0
    z_dome_bot = H - H_ACT
    h_yoke = max(85.0, z_dome_bot - z_yoke0)

    o_bfl = CYLINDER(s, R=r_pipe * 1.45, H=24.0, O=0.0).translate((0.0, 0.0, z_bon0))
    o_bon = CYLINDER(s, R=r_pipe * 0.86, H=110.0, O=0.0).translate((0.0, 0.0, z_bon0))
    o_stem = CYLINDER(s, R=12.0, H=z_dome_bot - z_bon0 + 20.0, O=0.0).translate((0.0, 0.0, z_bon0))
    for p in (o_bfl, o_bon, o_stem):
        o_m.uniteWith(p); p.erase()

    for zf in (0.38, 0.62, 0.86):
        fin = CYLINDER(s, R=r_pipe * 1.18, H=8.0, O=0.0).translate((0.0, 0.0, z_bon0 + 105.0 * zf))
        o_m.uniteWith(fin); fin.erase()

    for sy in (-1.0, 1.0):
        leg = CYLINDER(s, R=17.0, H=h_yoke + 16.0, O=0.0).translate((0.0, sy * r_pipe * 0.92, z_yoke0 - 6.0))
        o_m.uniteWith(leg); leg.erase()

    o_ytop = CYLINDER(s, R=r_pipe * 1.28, H=22.0, O=0.0).translate((0.0, 0.0, z_dome_bot - 18.0))
    o_pos = BOX(s, L=68.0, W=88.0, H=65.0).translate((42.0, -r_pipe * 1.32, z_yoke0 + h_yoke * 0.5))
    o_afr = CYLINDER(s, R=22.0, H=78.0, O=0.0).translate((-38.0, -r_pipe * 1.25, z_yoke0 + h_yoke * 0.35))
    for p in (o_ytop, o_pos, o_afr):
        o_m.uniteWith(p); p.erase()

    # 3. 顶部气动薄膜执行机构 (上下压铸皿形膜盖 + 中部夹紧外翻边 + 12颗周向夹紧螺栓)
    o_d_low = CONE(s, R1=r_pipe * 1.2, R2=r_act * 0.92, H=H_ACT * 0.44, E=0.0).translate((0.0, 0.0, z_dome_bot))
    o_d_rim = CYLINDER(s, R=r_act, H=16.0, O=0.0).translate((0.0, 0.0, z_dome_bot + H_ACT * 0.44 - 4.0))
    o_d_top = ELLIPSOIDHEAD(s, R=r_act * 0.92, H=H_ACT * 0.46).translate((0.0, 0.0, z_dome_bot + H_ACT * 0.54))
    for p in (o_d_low, o_d_rim, o_d_top):
        o_m.uniteWith(p); p.erase()

    for k in range(12):
        ang = math.radians(30.0 * k)
        bt = CYLINDER(s, R=5.5, H=28.0, O=0.0).translate((r_act * 0.94 * math.cos(ang), r_act * 0.94 * math.sin(ang), z_dome_bot + H_ACT * 0.44 - 10.0))
        o_m.uniteWith(bt); bt.erase()

    # 4. 法兰螺栓孔与直角流道切除
    r_bcd = (r_pipe + r_fl) * 0.54
    r_hole = max(5.5, (r_fl - r_pipe) * 0.16)
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        h1 = CYLINDER(s, R=r_hole, H=FL_T + 4.0, O=0.0).rotateY(90.0).translate((-C - 2.0, r_bcd * math.cos(ang), r_bcd * math.sin(ang)))
        h2 = CYLINDER(s, R=r_hole, H=FL_T + 4.0, O=0.0).translate((r_bcd * math.cos(ang), r_bcd * math.sin(ang), -C - 2.0))
        o_m.subtractFrom(h1); h1.erase()
        o_m.subtractFrom(h2); h2.erase()

    b_in = CYLINDER(s, R=r_bore, H=C + 5.0, O=0.0).rotateY(-90.0)
    b_out = CYLINDER(s, R=r_bore, H=C + 5.0, O=0.0).rotateY(180.0)
    o_m.subtractFrom(b_in); b_in.erase()
    o_m.subtractFrom(b_out); b_out.erase()

    s.setPoint((-C, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, -C), (0.0, 0.0, -1.0))
    s.setLinearDimension("C", (-C, 0.0, -C), (0.0, 0.0, -C))
    s.setLinearDimension("H", (0.0, 0.0, 0.0), (0.0, 0.0, H))
    s.setLinearDimension("D_ACT", (-r_act, 0.0, H - H_ACT * 0.5), (r_act, 0.0, H - H_ACT * 0.5))
