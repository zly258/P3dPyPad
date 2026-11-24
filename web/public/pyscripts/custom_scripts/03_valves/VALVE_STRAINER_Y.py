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

@activate(Group="Valve", Ports=2, TooltipShort=u"化工Y型法兰过滤器 (GL41H / HG/T 21637)", TooltipLong=u"化工行业标准 HG/T 21637 Y型法兰管道过滤器 (Y-Pattern Flanged Strainer)，含水平直通阀体、45度斜向下排污滤网腔、盲板法兰端盖与排污螺塞", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"Y型过滤器主要结构尺寸：结构长度、斜滤筒高与法兰规格")
@param(D=LENGTH, TooltipShort=u"管道外径 D", Ask4Dist=True, TooltipLong=u"连接管道公称外径 OD")
@param(L=LENGTH, TooltipShort=u"结构长度 L", Ask4Dist=True, TooltipLong=u"两端法兰密封面间距 L")
@param(H_BRANCH=LENGTH, TooltipShort=u"滤筒下伸高 H", Ask4Dist=True, TooltipLong=u"管道中心至斜置滤筒底部总深 H")
@param(D_BRANCH=LENGTH, TooltipShort=u"滤筒外径", TooltipLong=u"45度斜置滤网筒体外径")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端法兰外圆直径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"两端法兰盘厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"单端法兰螺栓孔数")
@param(ID=STRING, TooltipShort=u"过滤器位号", TooltipLong=u"安装位号，如 SR-101")
def VALVE_STRAINER_Y(s, D=114.3, L=350.0, H_BRANCH=245.0, D_BRANCH=133.0, FL_OD=220.0, FL_T=22.0, NBOLTS=8, ID=u"GL41H-16C-DN100", **kw):
    D = max(20.0, float(D))
    L = max(140.0, float(L))
    H_BRANCH = max(D * 1.35, float(H_BRANCH))
    D_BRANCH = max(D * 0.95, float(D_BRANCH))
    FL_OD = max(D + 50.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.86
    r_fl = FL_OD / 2.0
    rf_r = r_pipe + (r_fl - r_pipe) * 0.36
    rf_t = 2.5

    # 1. 水平主管筒体 + 两端法兰
    o_v = CYLINDER(s, R=r_pipe * 1.12, H=L - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(L * 0.5 - rf_t), 0.0, 0.0))
    for sx in (-1.0, 1.0):
        x_rf = -L * 0.5 if sx < 0 else (L * 0.5 - rf_t - 1.0)
        c_rf = CYLINDER(s, R=rf_r, H=rf_t + 1.0, O=0.0).rotateY(90.0).translate((x_rf, 0.0, 0.0))
        o_v.uniteWith(c_rf); c_rf.erase()
        x_fl = (-L * 0.5 + rf_t) if sx < 0 else (L * 0.5 - rf_t - FL_T)
        c_fl = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_v.uniteWith(c_fl); c_fl.erase()

    # 2. 中部加粗相贯过渡球肚 + 45° 斜向下 (+X, -Z) 排污滤筒 + 盲板端盖与排污丝堵
    r_br = D_BRANCH / 2.0
    o_hub = SPHERE(s, R=max(r_pipe * 1.32, r_br * 1.12)).translate((-L * 0.08, 0.0, 0.0))
    o_v.uniteWith(o_hub); o_hub.erase()

    # rotateY(135) 将 +Z 旋转至 (+cos45, 0, -sin45)
    len_br = (H_BRANCH - r_br * 0.65) * 1.4142
    c45 = 0.70710678
    x_root = -L * 0.08
    o_br = CYLINDER(s, R=r_br, H=len_br, O=0.0).rotateY(135.0).translate((x_root, 0.0, 0.0))
    o_v.uniteWith(o_br); o_br.erase()

    r_bfl = r_br * 1.42
    t_bfl = FL_T * 1.55
    x_end = x_root + (len_br - t_bfl * 0.8) * c45
    z_end = -(len_br - t_bfl * 0.8) * c45
    o_bfl = CYLINDER(s, R=r_bfl, H=t_bfl, O=0.0).rotateY(135.0).translate((x_end, 0.0, z_end))
    o_v.uniteWith(o_bfl); o_bfl.erase()

    # 盲板端盖中心六角排污丝堵
    x_plug = x_end + (t_bfl - 2.0) * c45
    z_plug = z_end - (t_bfl - 2.0) * c45
    o_plug = CYLINDER(s, R=max(10.0, r_br * 0.28), H=24.0, O=0.0).rotateY(135.0).translate((x_plug, 0.0, z_plug))
    o_v.uniteWith(o_plug); o_plug.erase()

    # 3. 贯通流道与两端法兰螺栓孔
    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_v.subtractFrom(o_bore); o_bore.erase()
    r_bcd = r_pipe + (r_fl - r_pipe) * 0.66
    r_hole = max(5.0, min(13.0, (r_fl - r_pipe) * 0.14))
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        by, bz = r_bcd * math.cos(ang), r_bcd * math.sin(ang)
        hl = CYLINDER(s, R=r_hole, H=FL_T + rf_t + 6.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 2.0), by, bz))
        o_v.subtractFrom(hl); hl.erase()
        hr = CYLINDER(s, R=r_hole, H=FL_T + rf_t + 6.0, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T - rf_t - 4.0, by, bz))
        o_v.subtractFrom(hr); hr.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, r_fl), (L / 2.0, 0.0, r_fl))
    s.setLinearDimension("H_BRANCH", (L / 2.0, 0.0, 0.0), (L / 2.0, 0.0, -H_BRANCH))
