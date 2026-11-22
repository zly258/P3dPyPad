# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Valve",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"气动偏心旋转调节阀",
    TooltipLong=u"化工高粘度/含颗粒介质大可调比气动偏心旋转调节阀 (凸轮挠曲阀 ZSLV / IEC 60534，含法兰连接阀体、长颈侧伸旋转阀杆轴套、曲柄连杆转换箱、立式弹簧气缸/薄膜执行机构与数字定位器)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"阀门连接管道外径 (mm)")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"两端法兰面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(H_ACT=LENGTH, TooltipShort=u"执行机构高", TooltipLong=u"流道中心至气动执行机构顶部高度 (mm)")
@param(D_ACT=LENGTH, TooltipShort=u"执行机构径", TooltipLong=u"气动薄膜/弹簧缸筒直径 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧连接法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"偏心旋转调节阀图集型号编码")
def VALVE_ECCENTRIC_ROTARY(s, D=114.3, L=230.0, FL_OD=220.0, FL_T=22.0, H_ACT=460.0, D_ACT=240.0, NBOLTS=8, ID=u"ZSLV-DN100", **kw):
    D = max(25.0, float(D))
    L = max(120.0, float(L))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(14.0, float(FL_T))
    H_ACT = max(280.0, float(H_ACT))
    D_ACT = max(150.0, float(D_ACT))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.85
    r_fl = FL_OD / 2.0
    r_act = D_ACT / 2.0

    # 1. 紧凑型法兰阀体 + 偏心球面阀芯凸肚 + 两端连接法兰
    o_m = CYLINDER(s, R=r_pipe * 1.25, H=L - 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    o_m.uniteWith(fl_l); fl_l.erase()
    o_m.uniteWith(fl_r); fl_r.erase()

    # 2. 侧向 (+Y) 水平旋转主轴长颈轴套 + 曲柄连杆转换箱 + 智能阀门定位器
    y_box = r_fl * 0.85 + 75.0
    o_shaft_neck = CYLINDER(s, R=r_pipe * 0.52, H=y_box, O=0.0).rotateX(-90.0)
    o_crank_box = BOX(s, L=125.0, W=135.0, H=115.0).translate((0.0, y_box, 15.0))
    o_pos = BOX(s, L=75.0, W=95.0, H=85.0).translate((0.0, y_box + 85.0, 15.0))
    for p in (o_shaft_neck, o_crank_box, o_pos):
        o_m.uniteWith(p); p.erase()

    # 3. 曲柄箱上方立式弹簧活塞/薄膜气动执行机构筒体
    z_cyl_bot = 82.0
    h_cyl = H_ACT - z_cyl_bot - 55.0
    o_cyl = CYLINDER(s, R=r_act * 0.65, H=h_cyl, O=0.0).translate((0.0, y_box, z_cyl_bot))
    o_dome = CYLINDER(s, R=r_act, H=32.0, O=0.0).translate((0.0, y_box, H_ACT - 55.0))
    o_cap = ELLIPSOIDHEAD(s, R=r_act, H=35.0).translate((0.0, y_box, H_ACT - 23.0))
    for p in (o_cyl, o_dome, o_cap):
        o_m.uniteWith(p); p.erase()

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
    s.setLinearDimension("H_ACT", (0.0, y_box, 0.0), (0.0, y_box, H_ACT))
