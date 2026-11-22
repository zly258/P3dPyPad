# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
import math

@activate(Group="Valve", Ports=3, TooltipShort=u"气动活塞式三通法兰球阀 (Q644F / Q645F)", TooltipLong=u"化工标准 GB/T 12237 气动双缸齿轮齿条执行机构T形/L形三通法兰球阀 (Pneumatic Actuated 3-Way Flanged Ball Valve)，含三向法兰球体腔、ISO支架、双作用气动活塞缸与顶部开度指示球", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"气动三通球阀主要结构尺寸：主管长、支管长与气动头尺寸")
@param(D=LENGTH, TooltipShort=u"管道外径 D", Ask4Dist=True, TooltipLong=u"三端口连接管道公称外径 OD")
@param(L=LENGTH, TooltipShort=u"主管结构长 L", Ask4Dist=True, TooltipLong=u"直通两端法兰密封面间距 L")
@param(L_BR=LENGTH, TooltipShort=u"支管中心距", Ask4Dist=True, TooltipLong=u"阀中心至侧向第3端口法兰面距离")
@param(H=LENGTH, TooltipShort=u"中心至顶高 H", Ask4Dist=True, TooltipLong=u"管道中心至气动头顶部指示器总高 H")
@param(L_ACT=LENGTH, TooltipShort=u"气缸总长", TooltipLong=u"顶部齿轮齿条双活塞气动执行机构总长")
@param(D_ACT=LENGTH, TooltipShort=u"气缸高度", TooltipLong=u"气动执行机构缸体外高/外径")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"三端法兰盘外径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"三端法兰盘厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"单端法兰螺栓孔数")
@param(ID=STRING, TooltipShort=u"阀门位号", TooltipLong=u"安装位号，如 XV-301")
def VALVE_BALL_3WAY(s, D=114.3, L=320.0, L_BR=160.0, H=380.0, L_ACT=290.0, D_ACT=135.0, FL_OD=220.0, FL_T=22.0, NBOLTS=8, ID=u"Q644F-16C-DN100", **kw):
    D = max(25.0, float(D))
    L = max(180.0, float(L))
    L_BR = max(L * 0.45, float(L_BR))
    H = max(220.0, float(H))
    L_ACT = max(180.0, float(L_ACT))
    D_ACT = max(85.0, float(D_ACT))
    FL_OD = max(D + 50.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.85
    r_fl = FL_OD / 2.0

    # 1. 主管筒体 (沿 X [-L/2, L/2]) + 正交支管筒体 (沿 +Y [0, L_BR]) + 中心球体包容腔
    o_v = CYLINDER(s, R=r_pipe * 1.12, H=L, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    o_br = CYLINDER(s, R=r_pipe * 1.12, H=L_BR, O=0.0).rotateX(-90.0)
    o_sph = SPHERE(s, R=r_pipe * 1.56)
    o_v.uniteWith(o_br); o_br.erase()
    o_v.uniteWith(o_sph); o_sph.erase()

    # 三端连接法兰
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    fl_b = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateX(-90.0).translate((0.0, L_BR - FL_T, 0.0))
    for f in (fl_l, fl_r, fl_b):
        o_v.uniteWith(f); f.erase()

    # 2. ISO 5211 连接支架 + 顶部齿轮齿条双活塞气动执行机构缸体 + 端盖 + NAMUR电磁阀块 + 顶置黄蓝开度指示器
    z_act_bot = H - D_ACT - 28.0
    o_brk = CYLINDER(s, R=r_pipe * 0.48, H=z_act_bot, O=0.0)
    o_v.uniteWith(o_brk); o_brk.erase()

    o_act_box = BOX(s, L=D_ACT * 0.92, W=D_ACT, H=L_ACT * 0.82).translate((0.0, 0.0, z_act_bot + D_ACT * 0.5))
    o_v.uniteWith(o_act_box); o_act_box.erase()
    for sx in (-1.0, 1.0):
        cap = CYLINDER(s, R=D_ACT * 0.48, H=L_ACT * 0.12, O=0.0).rotateY(90.0).translate((sx * L_ACT * 0.41 - (L_ACT * 0.12 if sx < 0 else 0.0), 0.0, z_act_bot + D_ACT * 0.5))
        o_v.uniteWith(cap); cap.erase()

    # 侧向 NAMUR 电磁阀盒与顶部球形开度指示器
    o_sol = BOX(s, L=42.0, W=55.0, H=85.0).translate((0.0, -D_ACT * 0.55, z_act_bot + D_ACT * 0.5))
    o_ind = CYLINDER(s, R=32.0, H=32.0, O=0.0).translate((0.0, 0.0, z_act_bot + D_ACT - 4.0))
    o_v.uniteWith(o_sol); o_sol.erase()
    o_v.uniteWith(o_ind); o_ind.erase()

    # 3. 贯通 T 形流道
    b1 = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    b2 = CYLINDER(s, R=r_bore, H=L_BR + 5.0, O=0.0).rotateX(-90.0)
    o_v.subtractFrom(b1); b1.erase()
    o_v.subtractFrom(b2); b2.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((0.0, L_BR, 0.0), (0.0, 1.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_fl), (L / 2.0, 0.0, -r_fl))
    s.setLinearDimension("H", (-L / 2.0, 0.0, 0.0), (-L / 2.0, 0.0, H))
    s.setLinearDimension("L_ACT", (-L_ACT / 2.0, 0.0, H), (L_ACT / 2.0, 0.0, H))
