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

@activate(Group="Valve", Ports=2, TooltipShort=u"高压锻钢法兰针型阀 (J43W / JB/T 7747)", TooltipLong=u"化工行业标准 JB/T 7747 高压锻钢法兰连接针型截止阀/仪表取样阀 (Forged Steel Flanged Needle Valve)，带锻造方体阀腔、六角锁紧填料螺母、细长阀杆与T字形横杆手柄", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"针型阀主要结构尺寸：结构长度、中心高与T形手柄宽")
@param(D=LENGTH, TooltipShort=u"管道外径 D", Ask4Dist=True, TooltipLong=u"连接管道公称外径 OD")
@param(L=LENGTH, TooltipShort=u"结构长度 L", Ask4Dist=True, TooltipLong=u"两端法兰密封面间距 L")
@param(H=LENGTH, TooltipShort=u"中心至手柄高 H", Ask4Dist=True, TooltipLong=u"管道中心至顶部T形手柄高度 H")
@param(W_BAR=LENGTH, TooltipShort=u"T柄宽度", TooltipLong=u"顶部T字横杆手柄长度")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"连接法兰外径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"单端法兰螺栓孔数")
@param(ID=STRING, TooltipShort=u"阀门位号", TooltipLong=u"安装位号，如 NV-101")
def VALVE_NEEDLE(s, D=33.7, L=160.0, H=175.0, W_BAR=110.0, FL_OD=115.0, FL_T=18.0, NBOLTS=4, ID=u"J43W-160P-DN25", **kw):
    D = max(14.0, float(D))
    L = max(100.0, float(L))
    H = max(110.0, float(H))
    W_BAR = max(70.0, float(W_BAR))
    FL_OD = max(D + 45.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.72
    r_fl = FL_OD / 2.0
    rf_r = r_pipe + (r_fl - r_pipe) * 0.38
    rf_t = 2.0

    # 1. 左右高颈管段与两端法兰
    o_v = CYLINDER(s, R=r_pipe * 1.15, H=L - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(L * 0.5 - rf_t), 0.0, 0.0))
    for sx in (-1.0, 1.0):
        x_rf = -L * 0.5 if sx < 0 else (L * 0.5 - rf_t - 1.0)
        c_rf = CYLINDER(s, R=rf_r, H=rf_t + 1.0, O=0.0).rotateY(90.0).translate((x_rf, 0.0, 0.0))
        o_v.uniteWith(c_rf); c_rf.erase()
        x_fl = (-L * 0.5 + rf_t) if sx < 0 else (L * 0.5 - rf_t - FL_T)
        c_fl = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_v.uniteWith(c_fl); c_fl.erase()

    # 2. 中部锻钢方形高强度阀体块 + 阶梯六角阀盖与填料压母
    w_blk = max(D * 1.65, 52.0)
    o_blk = BOX(s, L=w_blk, W=w_blk * 1.15, H=L * 0.44)
    o_v.uniteWith(o_blk); o_blk.erase()

    z_bon0 = w_blk * 0.55
    h_bon = (H - z_bon0) * 0.58
    o_bon = CYLINDER(s, R=w_blk * 0.36, H=h_bon, O=0.0).translate((0.0, 0.0, z_bon0))
    o_gnut = BOX(s, L=w_blk * 0.58, W=18.0, H=w_blk * 0.58).translate((0.0, 0.0, z_bon0 + h_bon * 0.72))
    o_v.uniteWith(o_bon); o_bon.erase()
    o_v.uniteWith(o_gnut); o_gnut.erase()

    # 3. 细长针阀杆 + 顶部 T 字形横杆手柄 (两端带防滑圆球锤头)
    r_stem = max(6.0, r_pipe * 0.25)
    o_stem = CYLINDER(s, R=r_stem, H=H - z_bon0, O=0.0).translate((0.0, 0.0, z_bon0))
    o_v.uniteWith(o_stem); o_stem.erase()

    r_bar = max(5.5, r_stem * 0.85)
    o_tbar = CYLINDER(s, R=r_bar, H=W_BAR, O=0.0).rotateX(90.0).translate((0.0, W_BAR * 0.5, H - r_bar * 1.2))
    o_v.uniteWith(o_tbar); o_tbar.erase()
    for sy in (-1.0, 1.0):
        kn = SPHERE(s, R=r_bar * 1.65).translate((0.0, sy * W_BAR * 0.5, H - r_bar * 1.2))
        o_v.uniteWith(kn); kn.erase()

    # 4. 贯通流道与两端法兰螺栓孔
    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_v.subtractFrom(o_bore); o_bore.erase()
    r_bcd = r_pipe + (r_fl - r_pipe) * 0.66
    r_hole = max(5.0, min(10.0, (r_fl - r_pipe) * 0.14))
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        by, bz = r_bcd * math.cos(ang), r_bcd * math.sin(ang)
        hl = CYLINDER(s, R=r_hole, H=FL_T + rf_t + 6.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 2.0), by, bz))
        o_v.subtractFrom(hl); hl.erase()
        hr = CYLINDER(s, R=r_hole, H=FL_T + rf_t + 6.0, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T - rf_t - 4.0, by, bz))
        o_v.subtractFrom(hr); hr.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_fl), (L / 2.0, 0.0, -r_fl))
    s.setLinearDimension("H", (-L / 2.0, 0.0, 0.0), (-L / 2.0, 0.0, H))
    s.setLinearDimension("W_BAR", (0.0, -W_BAR * 0.5, H), (0.0, W_BAR * 0.5, H))
