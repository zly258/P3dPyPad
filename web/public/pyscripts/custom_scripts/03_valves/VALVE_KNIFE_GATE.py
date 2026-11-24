# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Valve",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"薄型浆液刀型闸阀",
    TooltipLong=u"化工矿浆/结晶母液/高固含渣浆管线用对夹式明杆刀型闸阀 (PZ73H / JB/T 8691，含U型薄体阀腔、侧向加强筋、矩形填料压盖、双侧扁钢支架、升降薄刀闸板与手轮)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"阀门连接管道外径 (mm)")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"薄型刀闸阀两端面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"阀体外圆径", TooltipLong=u"刀闸阀圆盘法兰外径 (mm)")
@param(H=LENGTH, TooltipShort=u"中心至顶高", TooltipLong=u"流道中心至升杆护管顶部高度 (mm)")
@param(W_DIA=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"顶部手轮外径 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧连接螺栓孔数量")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"刀型闸阀图集型号编码")
def VALVE_KNIFE_GATE(s, D=219.1, L=70.0, FL_OD=340.0, H=620.0, W_DIA=280.0, NBOLTS=12, ID=u"PZ73H-DN200", **kw):
    D = max(57.0, float(D))
    L = max(46.0, float(L))
    FL_OD = max(D + 80.0, float(FL_OD))
    H = max(FL_OD * 1.35, float(H))
    W_DIA = max(160.0, float(W_DIA))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.88
    r_fl = FL_OD / 2.0

    # 1. 下部圆盘对夹阀体 + 上部矩形扁平闸板胸腔 + 两侧排渣导向凸耳
    o_m = CYLINDER(s, R=r_fl, H=L, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    w_chest = r_pipe * 2.28
    z_chest_top = r_fl * 1.08
    o_chest = BOX(s, L=w_chest, W=z_chest_top, H=L * 0.88).translate((0.0, 0.0, z_chest_top * 0.5))
    o_ear_l = BOX(s, L=w_chest + 56.0, W=36.0, H=L * 0.92).translate((0.0, 0.0, z_chest_top * 0.42))
    o_m.uniteWith(o_chest); o_chest.erase()
    o_m.uniteWith(o_ear_l); o_ear_l.erase()

    # 填料函压盖法兰与4颗压紧螺柱
    t_gland = 26.0
    o_gland = BOX(s, L=w_chest * 1.22, W=t_gland, H=L * 1.35).translate((0.0, 0.0, z_chest_top + t_gland * 0.5))
    o_m.uniteWith(o_gland); o_gland.erase()
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            gs = CYLINDER(s, R=6.5, H=t_gland * 2.2, O=0.0).translate((sx * L * 0.48, sy * w_chest * 0.52, z_chest_top - 6.0))
            o_m.uniteWith(gs); gs.erase()

    # 2. 双侧钢板门型支架 (Open Plate Yoke) + 穿出填料函的矩形不锈钢刀闸板 + 顶丝杆护套
    z_yoke_bot = z_chest_top + t_gland
    z_wheel = H - 75.0
    h_yoke = max(90.0, z_wheel - z_yoke_bot)
    t_pl = 14.0
    w_pl = L * 0.82
    for sy in (-1.0, 1.0):
        yp = sy * (w_chest * 0.44)
        pl = BOX(s, L=t_pl, W=h_yoke, H=w_pl).translate((0.0, yp, z_yoke_bot + h_yoke * 0.5))
        o_m.uniteWith(pl); pl.erase()

    o_ymid = BOX(s, L=w_chest * 0.96, W=18.0, H=w_pl * 0.95).translate((0.0, 0.0, z_yoke_bot + h_yoke * 0.52))
    o_ytop = BOX(s, L=w_chest * 1.05, W=24.0, H=w_pl * 1.18).translate((0.0, 0.0, z_wheel - 12.0))
    o_blade = BOX(s, L=w_chest * 0.76, W=h_yoke * 0.50, H=12.0).translate((0.0, 0.0, z_yoke_bot + h_yoke * 0.24))
    o_stem = CYLINDER(s, R=max(12.0, D * 0.065), H=H - (z_yoke_bot + h_yoke * 0.45), O=0.0).translate((0.0, 0.0, z_yoke_bot + h_yoke * 0.45))
    o_hood = CYLINDER(s, R=max(18.0, D * 0.09), H=H - z_wheel, O=0.0).translate((0.0, 0.0, z_wheel))
    for p in (o_ymid, o_ytop, o_blade, o_stem, o_hood):
        o_m.uniteWith(p); p.erase()

    # 3. 顶部水平手轮
    r_w = W_DIA / 2.0
    w_thk = 16.0
    o_rim = TORUS(s, R1=r_w - w_thk * 0.5, R2=w_thk * 0.5).translate((0.0, 0.0, z_wheel + 10.0))
    o_hub = CYLINDER(s, R=26.0, H=22.0, O=0.0).translate((0.0, 0.0, z_wheel))
    o_m.uniteWith(o_rim); o_rim.erase()
    o_m.uniteWith(o_hub); o_hub.erase()
    for k in range(4):
        spk = BOX(s, L=14.0, W=12.0, H=r_w * 1.85).rotateZ(k * 45.0).translate((0.0, 0.0, z_wheel + 10.0))
        o_m.uniteWith(spk); spk.erase()

    # 螺栓孔与内流道切除
    r_bcd = (r_pipe + r_fl) * 0.55
    r_hole = max(6.0, (r_fl - r_pipe) * 0.14)
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        h_cyl = CYLINDER(s, R=r_hole, H=L + 6.0, O=0.0).rotateY(90.0).translate((-L * 0.5 - 3.0, r_bcd * math.cos(ang), r_bcd * math.sin(ang)))
        o_m.subtractFrom(h_cyl); h_cyl.erase()

    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_m.subtractFrom(o_bore); o_bore.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_fl), (L / 2.0, 0.0, -r_fl))
    s.setLinearDimension("H", (0.0, 0.0, 0.0), (0.0, 0.0, H))
    s.setLinearDimension("W_DIA", (-r_w, 0.0, z_wheel + 10.0), (r_w, 0.0, z_wheel + 10.0))
