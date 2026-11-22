# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *
import math

@activate(Group="Valve", Ports=2, TooltipShort=u"化工提篮式法兰过滤器 (SBL / HG/T 21637)", TooltipLong=u"化工行业标准 HG/T 21637 直通高低接管提篮式（蓝式）管道过滤器 (Simplex Basket Strainer)，含立式大口径滤筒、椭圆封底、快开螺栓盲板顶盖、提手弓架与底部排污口", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"提篮过滤器主要结构尺寸：结构长度、滤筒直径与顶底高度")
@param(D=LENGTH, TooltipShort=u"接管外径 D", Ask4Dist=True, TooltipLong=u"进出口管道外径 OD")
@param(L=LENGTH, TooltipShort=u"结构长度 L", Ask4Dist=True, TooltipLong=u"进出口法兰端面间距 L")
@param(D_BODY=LENGTH, TooltipShort=u"滤筒外径", Ask4Dist=True, TooltipLong=u"立式提篮过滤筒体外径")
@param(H_TOP=LENGTH, TooltipShort=u"中心至顶高", TooltipLong=u"管中心线至顶盖提手高度")
@param(H_BOT=LENGTH, TooltipShort=u"中心至底深", TooltipLong=u"管中心线至底部排污口深度")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"进出口连接法兰外径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"进出口法兰厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"单端法兰螺栓孔数")
@param(ID=STRING, TooltipShort=u"过滤器位号", TooltipLong=u"安装位号，如 SBL-101")
def VALVE_STRAINER_BASKET(s, D=114.3, L=420.0, D_BODY=219.1, H_TOP=240.0, H_BOT=340.0, FL_OD=220.0, FL_T=22.0, NBOLTS=8, ID=u"SBL-DN100", **kw):
    D = max(25.0, float(D))
    L = max(220.0, float(L))
    D_BODY = max(D * 1.55, float(D_BODY))
    H_TOP = max(D * 1.3, float(H_TOP))
    H_BOT = max(D * 1.8, float(H_BOT))
    FL_OD = max(D + 50.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.86
    r_body = D_BODY / 2.0
    r_fl = FL_OD / 2.0
    rf_r = r_pipe + (r_fl - r_pipe) * 0.36
    rf_t = 2.5

    # 1. 水平进出接管与两端法兰
    o_v = CYLINDER(s, R=r_pipe, H=L - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(L * 0.5 - rf_t), 0.0, 0.0))
    for sx in (-1.0, 1.0):
        x_rf = -L * 0.5 if sx < 0 else (L * 0.5 - rf_t - 1.0)
        c_rf = CYLINDER(s, R=rf_r, H=rf_t + 1.0, O=0.0).rotateY(90.0).translate((x_rf, 0.0, 0.0))
        o_v.uniteWith(c_rf); c_rf.erase()
        x_fl = (-L * 0.5 + rf_t) if sx < 0 else (L * 0.5 - rf_t - FL_T)
        c_fl = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_v.uniteWith(c_fl); c_fl.erase()

    # 2. 立式大口径提篮滤筒 + 底部椭圆封头与排污管嘴
    z_cyl_bot = -(H_BOT - r_body * 0.55)
    z_cyl_top = H_TOP - 45.0
    o_cyl = CYLINDER(s, R=r_body, H=z_cyl_top - z_cyl_bot, O=0.0).translate((0.0, 0.0, z_cyl_bot))
    o_bot_h = ELLIPSOIDHEAD(s, R=r_body, H=r_body * 0.5).rotateX(180.0).translate((0.0, 0.0, z_cyl_bot))
    o_drain = CYLINDER(s, R=max(16.0, r_pipe * 0.35), H=r_body * 0.65, O=0.0).translate((0.0, 0.0, -H_BOT))
    o_v.uniteWith(o_cyl); o_cyl.erase()
    o_v.uniteWith(o_bot_h); o_bot_h.erase()
    o_v.uniteWith(o_drain); o_drain.erase()

    # 3. 顶部大法兰 + 盲板盖 + 周向快开吊环螺栓 + 顶部排气阀与提手弓架
    r_tfl = r_body * 1.28
    t_tfl = 34.0
    o_tfl = CYLINDER(s, R=r_tfl, H=t_tfl, O=0.0).translate((0.0, 0.0, z_cyl_top - 10.0))
    o_v.uniteWith(o_tfl); o_tfl.erase()

    r_tbcd = r_body + (r_tfl - r_body) * 0.55
    for i in range(8):
        ang = math.radians(i * 45.0)
        bt = CYLINDER(s, R=max(6.0, r_pipe * 0.12), H=t_tfl + 16.0, O=0.0).translate((r_tbcd * math.cos(ang), r_tbcd * math.sin(ang), z_cyl_top - 16.0))
        o_v.uniteWith(bt); bt.erase()

    z_cap_top = z_cyl_top + t_tfl - 10.0
    h_arch = max(20.0, H_TOP - z_cap_top)
    o_arch = BOX(s, L=24.0, W=h_arch, H=r_body * 1.1).translate((0.0, 0.0, z_cap_top + h_arch * 0.5 - 2.0))
    o_v.uniteWith(o_arch); o_arch.erase()

    # 4. 贯通流道与两端法兰螺栓孔
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
    s.setLinearDimension("L", (-L / 2.0, 0.0, H_TOP), (L / 2.0, 0.0, H_TOP))
    s.setLinearDimension("H_BOT", (-L / 2.0, 0.0, 0.0), (-L / 2.0, 0.0, -H_BOT))
    s.setLinearDimension("D_BODY", (-r_body, 0.0, -H_BOT * 0.5), (r_body, 0.0, -H_BOT * 0.5))
