# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Valve",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"化工密闭在线取样阀总成",
    TooltipLong=u"化工挥发性有机物(VOCs)/有毒介质管道密闭在线取样器总成 (符合 ISO 15848，含法兰直通取样管段、顶部弹簧复位取样旋塞阀与安全手柄、下部不锈钢取样瓶防爆保护套筒与观察视窗)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"主管外径", TooltipLong=u"被取样工艺管道外径 (mm)")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"两端连接法兰密封面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"上部阀高", TooltipLong=u"管道中心至顶部弹簧复位手柄的高度 (mm)")
@param(H_BOT=LENGTH, TooltipShort=u"取样瓶护罩深", TooltipLong=u"管道中心至下部不锈钢取样瓶保护罩底部的深度 (mm)")
@param(D_BOTTLE=LENGTH, TooltipShort=u"护罩外径", TooltipLong=u"下部取样瓶不锈钢防爆护套外径 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧连接法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"密闭在线取样阀图集型号编码")
def VALVE_SAMPLING(s, D=60.3, L=180.0, FL_OD=165.0, FL_T=20.0, H_TOP=210.0, H_BOT=245.0, D_BOTTLE=102.0, NBOLTS=4, ID=u"QYF-DN50", **kw):
    D = max(20.0, float(D))
    L = max(120.0, float(L))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    H_TOP = max(140.0, float(H_TOP))
    H_BOT = max(160.0, float(H_BOT))
    D_BOTTLE = max(68.0, float(D_BOTTLE))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.84
    r_fl = FL_OD / 2.0
    r_btl = D_BOTTLE / 2.0

    # 1. 直通取样阀体 + 两端连接法兰
    o_m = CYLINDER(s, R=r_pipe * 1.18, H=L - 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    o_m.uniteWith(fl_l); fl_l.erase()
    o_m.uniteWith(fl_r); fl_r.erase()

    # 2. 上部弹簧自动复位取样旋塞阀头 + 氮气吹扫针阀嘴 + 安全自闭长扳手
    o_vbon = CYLINDER(s, R=32.0, H=H_TOP - 28.0, O=0.0).translate((0.0, 0.0, r_pipe * 0.6))
    o_spr_can = CYLINDER(s, R=44.0, H=65.0, O=0.0).translate((0.0, 0.0, H_TOP - 105.0))
    o_lever = BOX(s, L=24.0, W=14.0, H=165.0).translate((68.0, 0.0, H_TOP - 15.0))
    o_purge = CYLINDER(s, R=12.0, H=55.0, O=0.0).rotateX(-90.0).translate((0.0, 0.0, r_pipe + 45.0))
    for p in (o_vbon, o_spr_can, o_lever, o_purge):
        o_m.uniteWith(p); p.erase()

    # 3. 下部快装卡口连接盘 + 不锈钢取样瓶防爆安全防护罩筒 (Z: [-H_BOT, -r_pipe*0.6])
    o_bayonet = CYLINDER(s, R=r_btl * 1.15, H=28.0, O=0.0).translate((0.0, 0.0, -(r_pipe + 32.0)))
    h_shroud = H_BOT - r_pipe - 18.0
    o_shroud = CYLINDER(s, R=r_btl, H=h_shroud, O=0.0).translate((0.0, 0.0, -H_BOT))
    o_bcap = CYLINDER(s, R=r_btl * 1.06, H=16.0, O=0.0).translate((0.0, 0.0, -H_BOT))
    for p in (o_bayonet, o_shroud, o_bcap):
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
    s.setLinearDimension("H_TOP", (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
    s.setLinearDimension("H_BOT", (0.0, 0.0, -H_BOT), (0.0, 0.0, 0.0))
