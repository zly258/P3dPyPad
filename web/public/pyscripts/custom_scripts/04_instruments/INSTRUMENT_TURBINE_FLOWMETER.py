# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Instrument",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"法兰式精密液体涡轮流量计",
    TooltipLong=u"化工洁净有机溶剂/轻烃/纯水计量用法兰式液体涡轮流量计 (LWGY / JB/T 9246，含不锈钢缩腰传感器壳体、两端连接法兰、内部导流器与涡轮叶轮、带散热片磁电感应接管颈与防爆积算仪)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"涡轮流量计连接管道外径 (mm)")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"两端连接法兰面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(H_HEAD=LENGTH, TooltipShort=u"中心至表头高", TooltipLong=u"管道中心至顶部防爆转换器总高 (mm)")
@param(D_HEAD=LENGTH, TooltipShort=u"表头直径", TooltipLong=u"顶部圆形防爆显示表头直径 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"液体涡轮流量计型号编码")
def INSTRUMENT_TURBINE_FLOWMETER(s, D=88.9, L=200.0, FL_OD=200.0, FL_T=22.0, H_HEAD=315.0, D_HEAD=118.0, NBOLTS=8, ID=u"FT-115-LWGY80", **kw):
    D = max(18.0, float(D))
    L = max(120.0, float(L))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    H_HEAD = max(D * 0.5 + 160.0, float(H_HEAD))
    D_HEAD = max(90.0, float(D_HEAD))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.84
    r_fl = FL_OD / 2.0
    r_head = D_HEAD / 2.0

    # 1. 不锈钢传感器管段 + 中部磁电检测环凸台 + 两端法兰
    o_m = CYLINDER(s, R=r_pipe * 1.04, H=L - 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    o_mid_ring = CYLINDER(s, R=r_pipe * 1.22, H=48.0, O=0.0).rotateY(90.0).translate((-24.0, 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    for p in (o_mid_ring, fl_l, fl_r):
        o_m.uniteWith(p); p.erase()

    # 2. 顶部六角锁母 + 带4片散热鳍片的磁电前置放大器立柱 + 圆形防爆显示表头
    z_head_c = H_HEAD - r_head
    o_hex = BOX(s, L=38.0, W=22.0, H=38.0).translate((0.0, 0.0, r_pipe * 1.2 + 8.0))
    o_neck = CYLINDER(s, R=16.0, H=z_head_c - r_pipe, O=0.0).translate((0.0, 0.0, r_pipe))
    o_head = CYLINDER(s, R=r_head, H=88.0, O=0.0).rotateX(90.0).translate((0.0, 44.0, z_head_c))
    o_bezel = CYLINDER(s, R=r_head * 1.06, H=16.0, O=0.0).rotateX(90.0).translate((0.0, -28.0, z_head_c))
    for p in (o_hex, o_neck, o_head, o_bezel):
        o_m.uniteWith(p); p.erase()

    for zf in (0.35, 0.52, 0.69):
        fin = CYLINDER(s, R=28.0, H=5.0, O=0.0).translate((0.0, 0.0, r_pipe + (z_head_c - r_pipe) * zf))
        o_m.uniteWith(fin); fin.erase()

    # 3. 法兰螺栓孔与内流道切除 + 内部中心导流锥与十字支撑翼片
    r_bcd = (r_pipe + r_fl) * 0.54
    r_hole = max(5.5, (r_fl - r_pipe) * 0.16)
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        for x_pos in (-L * 0.5 - 2.0, L * 0.5 - FL_T - 2.0):
            h_cyl = CYLINDER(s, R=r_hole, H=FL_T + 4.0, O=0.0).rotateY(90.0).translate((x_pos, r_bcd * math.cos(ang), r_bcd * math.sin(ang)))
            o_m.subtractFrom(h_cyl); h_cyl.erase()

    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_m.subtractFrom(o_bore); o_bore.erase()

    o_hub = CYLINDER(s, R=r_bore * 0.34, H=L * 0.55, O=0.0).rotateY(90.0).translate((-L * 0.275, 0.0, 0.0))
    o_vane1 = BOX(s, L=r_bore * 2.05, W=5.0, H=L * 0.45)
    o_vane2 = BOX(s, L=5.0, W=r_bore * 2.05, H=L * 0.45)
    for p in (o_hub, o_vane1, o_vane2):
        o_m.uniteWith(p); p.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_fl), (L / 2.0, 0.0, -r_fl))
    s.setLinearDimension("H_HEAD", (0.0, 0.0, 0.0), (0.0, 0.0, H_HEAD))
