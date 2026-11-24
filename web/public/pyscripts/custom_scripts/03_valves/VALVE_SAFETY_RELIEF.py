# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *


@activate(
    Group="Valve",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"弹簧全启式安全阀 (A42Y / API 526)",
    TooltipLong=u"化工压力容器与管道超压泄放保护用带扳手弹簧全启式安全阀 (A42Y / API 526，含下进侧出扩径角式阀体、8螺栓中腔连接法兰、带四向散热筋高耸弹簧罩筒、顶盖及手动起跳试验扳手)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D_IN=LENGTH, TooltipShort=u"进口管外径", TooltipLong=u"下部整定压力入口管外径 (mm)")
@param(D_OUT=LENGTH, TooltipShort=u"出口管外径", TooltipLong=u"侧向扩径泄放出口管外径 (mm)")
@param(FL_IN=LENGTH, TooltipShort=u"进口法兰径", TooltipLong=u"底部入口连接法兰外径 (mm)")
@param(FL_OUT=LENGTH, TooltipShort=u"出口法兰径", TooltipLong=u"侧向泄放出口连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(C_IN=LENGTH, TooltipShort=u"中心至底距", TooltipLong=u"出口中心至底部进口法兰面距离 (mm)")
@param(C_OUT=LENGTH, TooltipShort=u"中心至侧距", TooltipLong=u"进口中心至侧向出口法兰面距离 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"中心至顶高", TooltipLong=u"出口中心至顶部铅封帽与试验扳手的总高 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"弹簧全启式安全阀图集型号编码")
def VALVE_SAFETY_RELIEF(s, D_IN=88.9, D_OUT=114.3, FL_IN=200.0, FL_OUT=220.0, FL_T=24.0, C_IN=140.0, C_OUT=160.0, H_TOP=465.0, ID=u"A42Y-DN80x100", **kw):
    D_IN = max(25.0, float(D_IN))
    D_OUT = max(D_IN, float(D_OUT))
    FL_IN = max(D_IN + 55.0, float(FL_IN))
    FL_OUT = max(D_OUT + 55.0, float(FL_OUT))
    FL_T = max(14.0, float(FL_T))
    C_IN = max(90.0, float(C_IN))
    C_OUT = max(100.0, float(C_OUT))
    H_TOP = max(280.0, float(H_TOP))

    r_in = D_IN / 2.0
    r_out = D_OUT / 2.0
    r_fl_in = FL_IN / 2.0
    r_fl_out = FL_OUT / 2.0

    # 1. 角式扩径泄放阀体 + 下部入口接管与法兰 (-Z) + 侧向大口径泄放接管与法兰 (+X)
    o_m = SPHERE(s, R=r_out * 1.38)
    n_in = CYLINDER(s, R=r_in * 1.15, H=C_IN - FL_T, O=0.0).rotateY(180.0)
    fl_in = CYLINDER(s, R=r_fl_in, H=FL_T, O=0.0).translate((0.0, 0.0, -C_IN))
    n_out = CYLINDER(s, R=r_out * 1.12, H=C_OUT - FL_T, O=0.0).rotateY(90.0)
    fl_out = CYLINDER(s, R=r_fl_out, H=FL_T, O=0.0).rotateY(90.0).translate((C_OUT - FL_T, 0.0, 0.0))
    for p in (n_in, fl_in, n_out, fl_out):
        o_m.uniteWith(p); p.erase()

    # 2. 中腔连接双法兰 + 8颗螺柱 + 高耸弹簧腔钟罩与四向散热纵肋 + 顶部起跳试验扳手
    z_bfl = r_out * 1.05
    h_bon = (H_TOP - z_bfl) * 0.68
    o_bfl = CYLINDER(s, R=r_in * 1.58, H=34.0, O=0.0).translate((0.0, 0.0, z_bfl))
    o_bon = CONE(s, R1=r_in * 1.18, R2=r_in * 0.92, H=h_bon, E=0.0).translate((0.0, 0.0, z_bfl + 30.0))
    for p in (o_bfl, o_bon):
        o_m.uniteWith(p); p.erase()

    for k in range(8):
        ang = math.radians(45.0 * k)
        bt = CYLINDER(s, R=6.5, H=44.0, O=0.0).translate((r_in * 1.34 * math.cos(ang), r_in * 1.34 * math.sin(ang), z_bfl - 5.0))
        o_m.uniteWith(bt); bt.erase()

    for ang in (0.0, 90.0):
        rib = BOX(s, L=12.0, W=h_bon * 0.88, H=r_in * 2.38).rotateZ(ang).translate((0.0, 0.0, z_bfl + 30.0 + h_bon * 0.44))
        o_m.uniteWith(rib); rib.erase()

    # 顶部铅封帽与侧向手动起跳试验杠杆扳手
    z_cap0 = z_bfl + 28.0 + h_bon
    h_cap = H_TOP - z_cap0
    o_cap_fl = CYLINDER(s, R=r_in * 1.05, H=18.0, O=0.0).translate((0.0, 0.0, z_cap0))
    o_cap = CYLINDER(s, R=r_in * 0.68, H=h_cap, O=0.0).translate((0.0, 0.0, z_cap0))
    o_lever_fork = BOX(s, L=28.0, W=28.0, H=55.0).translate((-22.0, 0.0, H_TOP - 22.0))
    o_lever_arm = BOX(s, L=14.0, W=115.0, H=16.0).rotateY(-28.0).translate((-38.0, 0.0, H_TOP - 58.0))
    for p in (o_cap_fl, o_cap, o_lever_fork, o_lever_arm):
        o_m.uniteWith(p); p.erase()

    # 法兰螺栓孔与内流道切除
    for i in range(8):
        ang = (2.0 * math.pi * i) / 8.0 + math.pi / 8.0
        h1 = CYLINDER(s, R=8.0, H=FL_T + 4.0, O=0.0).translate(((r_in + r_fl_in) * 0.54 * math.cos(ang), (r_in + r_fl_in) * 0.54 * math.sin(ang), -C_IN - 2.0))
        h2 = CYLINDER(s, R=8.5, H=FL_T + 4.0, O=0.0).rotateY(90.0).translate((C_OUT - FL_T - 2.0, (r_out + r_fl_out) * 0.54 * math.cos(ang), (r_out + r_fl_out) * 0.54 * math.sin(ang)))
        o_m.subtractFrom(h1); h1.erase()
        o_m.subtractFrom(h2); h2.erase()

    b_in = CYLINDER(s, R=r_in * 0.80, H=C_IN + 5.0, O=0.0).rotateY(180.0)
    b_out = CYLINDER(s, R=r_out * 0.82, H=C_OUT + 5.0, O=0.0).rotateY(90.0)
    o_m.subtractFrom(b_in); b_in.erase()
    o_m.subtractFrom(b_out); b_out.erase()

    s.setPoint((0.0, 0.0, -C_IN), (0.0, 0.0, -1.0))
    s.setPoint((C_OUT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("C_IN", (0.0, 0.0, -C_IN), (0.0, 0.0, 0.0))
    s.setLinearDimension("C_OUT", (0.0, 0.0, -C_IN), (C_OUT, 0.0, -C_IN))
    s.setLinearDimension("H_TOP", (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
