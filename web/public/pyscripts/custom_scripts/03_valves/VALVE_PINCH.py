# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Valve",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"化工耐磨胶管夹管阀",
    TooltipLong=u"化工脱硫石膏浆液/矿浆/固液两相流全通径无阻流夹管阀 (J41X，含上下对开带散热加强筋铸造全封闭外壳、橡胶内衬管法兰、侧向椭圆观察视窗、双导柱挤压横梁与顶部手轮)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"夹管阀连接管道外径 (mm)")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"两端法兰面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(W_BODY=LENGTH, TooltipShort=u"阀壳横向宽", TooltipLong=u"夹管阀扁平铸造壳体横向总宽度 (mm)")
@param(H=LENGTH, TooltipShort=u"中心至顶高", TooltipLong=u"流道中心至顶部手轮高度 (mm)")
@param(W_DIA=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"顶部手轮外径 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧连接法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"耐磨夹管阀图集型号编码")
def VALVE_PINCH(s, D=114.3, L=280.0, FL_OD=220.0, FL_T=22.0, W_BODY=260.0, H=350.0, W_DIA=240.0, NBOLTS=8, ID=u"J41X-DN100", **kw):
    D = max(25.0, float(D))
    L = max(160.0, float(L))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(14.0, float(FL_T))
    W_BODY = max(D * 1.85, float(W_BODY))
    H = max(220.0, float(H))
    W_DIA = max(140.0, float(W_DIA))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.85
    r_fl = FL_OD / 2.0

    # 1. 内部耐磨橡胶套管 + 两端连接法兰 + 上下对开扁宽铸铁护壳与中分面螺栓边
    o_m = CYLINDER(s, R=r_pipe * 1.12, H=L - 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    o_m.uniteWith(fl_l); fl_l.erase()
    o_m.uniteWith(fl_r); fl_r.erase()

    l_shell = (L - 2.0 * FL_T) * 0.78
    o_casing = BOX(s, L=W_BODY * 0.88, W=r_pipe * 2.45, H=l_shell).translate((0.0, 0.0, 0.0))
    o_split_fl = BOX(s, L=W_BODY, W=26.0, H=l_shell * 1.06).translate((0.0, 0.0, 0.0))
    o_m.uniteWith(o_casing); o_casing.erase()
    o_m.uniteWith(o_split_fl); o_split_fl.erase()

    # 壳体纵向与横向加强筋
    for sx in (-0.32, 0.0, 0.32):
        rib = BOX(s, L=W_BODY * 0.94, W=r_pipe * 2.65, H=12.0).translate((sx * l_shell, 0.0, 0.0))
        o_m.uniteWith(rib); rib.erase()

    # 2. 上部挤压机构导柱座 + 中央升降螺杆 + 顶部手轮
    z_top_box = r_pipe * 1.25
    z_wheel = H - 22.0
    o_bon = CYLINDER(s, R=r_pipe * 0.65, H=z_wheel - z_top_box, O=0.0).translate((0.0, 0.0, z_top_box))
    o_m.uniteWith(o_bon); o_bon.erase()
    for sy in (-1.0, 1.0):
        grod = CYLINDER(s, R=14.0, H=(z_wheel - z_top_box) * 0.72, O=0.0).translate((0.0, sy * W_BODY * 0.28, z_top_box))
        o_m.uniteWith(grod); grod.erase()

    o_ybar = BOX(s, L=W_BODY * 0.68, W=22.0, H=48.0).translate((0.0, 0.0, z_top_box + (z_wheel - z_top_box) * 0.68))
    o_m.uniteWith(o_ybar); o_ybar.erase()

    r_w = W_DIA / 2.0
    w_thk = 16.0
    o_rim = TORUS(s, R1=r_w - w_thk * 0.5, R2=w_thk * 0.5).translate((0.0, 0.0, z_wheel))
    o_m.uniteWith(o_rim); o_rim.erase()
    for k in range(4):
        spk = BOX(s, L=14.0, W=12.0, H=r_w * 1.85).rotateZ(k * 45.0).translate((0.0, 0.0, z_wheel))
        o_m.uniteWith(spk); spk.erase()

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
    s.setLinearDimension("H", (0.0, 0.0, 0.0), (0.0, 0.0, H))
    s.setLinearDimension("W_BODY", (0.0, -W_BODY / 2.0, 0.0), (0.0, W_BODY / 2.0, 0.0))
