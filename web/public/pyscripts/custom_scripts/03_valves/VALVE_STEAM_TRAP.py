# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Valve",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"倒吊桶浮球式蒸汽疏水阀",
    TooltipLong=u"化工伴热与换热器凝结水回收用机械型浮球/倒吊桶式法兰蒸汽疏水阀 (FT43H / GB/T 22654，含水平同轴法兰进出口、下部大容量储水浮球罐、多螺栓法兰顶盖与底部排污丝堵)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"疏水阀连接管道外径 (mm)")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"进出口法兰密封面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(D_POT=LENGTH, TooltipShort=u"阀体罐径", TooltipLong=u"下部倒吊桶/浮球腔圆筒外径 (mm)")
@param(H_BOT=LENGTH, TooltipShort=u"中心至底深", TooltipLong=u"流道中心至储水罐底排污口的垂直深度 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"中心至顶高", TooltipLong=u"流道中心至顶盖排气螺塞的总高度 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"蒸汽疏水阀图集型号编码")
def VALVE_STEAM_TRAP(s, D=60.3, L=230.0, FL_OD=165.0, FL_T=20.0, D_POT=168.0, H_BOT=215.0, H_TOP=95.0, NBOLTS=4, ID=u"FT43H-DN50", **kw):
    D = max(18.0, float(D))
    L = max(140.0, float(L))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    D_POT = max(D * 1.85, float(D_POT))
    H_BOT = max(120.0, float(H_BOT))
    H_TOP = max(65.0, float(H_TOP))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.80
    r_fl = FL_OD / 2.0
    r_pot = min(L * 0.36, D_POT / 2.0)

    # 1. 水平直通流道阀颈 + 左右连接法兰
    o_m = CYLINDER(s, R=r_pipe * 1.15, H=L - 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    o_m.uniteWith(fl_l); fl_l.erase()
    o_m.uniteWith(fl_r); fl_r.erase()

    # 2. 下部立式凝结水吊桶腔圆筒 + 底部椭球底 + 顶部 8 螺栓法兰盖
    z_pot_bot = -H_BOT + r_pot * 0.42
    z_cov_fl = H_TOP - 32.0
    o_pot = CYLINDER(s, R=r_pot, H=z_cov_fl - z_pot_bot, O=0.0).translate((0.0, 0.0, z_pot_bot))
    o_bot_dish = ELLIPSOIDHEAD(s, R=r_pot, H=r_pot * 0.38).rotateY(180.0).translate((0.0, 0.0, z_pot_bot))
    o_cov_fl = CYLINDER(s, R=r_pot * 1.18, H=28.0, O=0.0).translate((0.0, 0.0, z_cov_fl - 14.0))
    o_cov_dome = CONE(s, R1=r_pot * 0.92, R2=r_pot * 0.35, H=22.0, E=0.0).translate((0.0, 0.0, z_cov_fl + 14.0))
    o_tplug = BOX(s, L=24.0, W=22.0, H=24.0).translate((0.0, 0.0, H_TOP - 11.0))
    o_bplug = BOX(s, L=28.0, W=24.0, H=28.0).translate((0.0, 0.0, -H_BOT + 12.0))
    for p in (o_pot, o_bot_dish, o_cov_fl, o_cov_dome, o_tplug, o_bplug):
        o_m.uniteWith(p); p.erase()

    for k in range(8):
        ang = (2.0 * math.pi * k) / 8.0
        bt = CYLINDER(s, R=6.0, H=36.0, O=0.0).translate((r_pot * 1.05 * math.cos(ang), r_pot * 1.05 * math.sin(ang), z_cov_fl - 18.0))
        o_m.uniteWith(bt); bt.erase()

    # 3. 法兰螺栓孔与内流道切除
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
    s.setLinearDimension("H_BOT", (0.0, 0.0, -H_BOT), (0.0, 0.0, 0.0))
    s.setLinearDimension("H_TOP", (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
