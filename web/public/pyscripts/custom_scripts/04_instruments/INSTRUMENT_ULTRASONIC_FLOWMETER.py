# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Instrument",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"四声道管段式超声波流量计",
    TooltipLong=u"化工贸易计量与大口径工艺管线四声道管段式超声波流量计 (USF / GB/T 34041，含厚壁精加工测量管段、两端高颈法兰、4对45°斜插式超声波换能器探头护套、顶部接线盒与双腔转换器表头)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"测量管段公称外径 (mm)")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"两端连接法兰面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(H_HEAD=LENGTH, TooltipShort=u"中心至表头高", TooltipLong=u"管道中心至顶部超声波转换器表头总高度 (mm)")
@param(W_HEAD=LENGTH, TooltipShort=u"表头宽度", TooltipLong=u"顶部双腔防爆转换器宽度 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧连接法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"超声波流量计型号编码")
def INSTRUMENT_ULTRASONIC_FLOWMETER(s, D=168.3, L=380.0, FL_OD=285.0, FL_T=26.0, H_HEAD=365.0, W_HEAD=155.0, NBOLTS=8, ID=u"FT-114-USF150", **kw):
    D = max(48.0, float(D))
    L = max(240.0, float(L))
    FL_OD = max(D + 65.0, float(FL_OD))
    FL_T = max(16.0, float(FL_T))
    H_HEAD = max(D * 0.5 + 165.0, float(H_HEAD))
    W_HEAD = max(110.0, float(W_HEAD))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.86
    r_fl = FL_OD / 2.0

    # 1. 加厚超声波测量管筒 + 两端连接法兰
    o_m = CYLINDER(s, R=r_pipe * 1.15, H=L - 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    o_m.uniteWith(fl_l); fl_l.erase()
    o_m.uniteWith(fl_r); fl_r.erase()

    # 2. 两侧对称 X 型交叉 8 个 45° 斜插超声波换能器探头护套座 (4对声道)
    dx_tr = (L - 2.0 * FL_T) * 0.24
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            for sz in (-0.52, 0.52):
                zc = sz * r_pipe
                yc = sy * r_pipe * 0.85
                tr_b = CYLINDER(s, R=18.0, H=65.0, O=0.0).rotateZ(45.0 * sx * sy).rotateX(-90.0 * sy).translate((sx * dx_tr, yc * 0.5, zc))
                o_m.uniteWith(tr_b); tr_b.erase()

    # 3. 顶部信号汇线盒 + 鹅颈立柱 + 双腔防爆数字转换器表头
    z_top_head = H_HEAD - 58.0
    o_jbox = BOX(s, L=95.0, W=36.0, H=140.0).translate((0.0, 0.0, r_pipe * 1.12 + 12.0))
    o_neck = CYLINDER(s, R=24.0, H=z_top_head - r_pipe, O=0.0).translate((0.0, 0.0, r_pipe))
    o_head = CYLINDER(s, R=58.0, H=W_HEAD, O=0.0).rotateX(90.0).translate((0.0, W_HEAD * 0.5, z_top_head))
    o_cap_f = CYLINDER(s, R=62.0, H=16.0, O=0.0).rotateX(90.0).translate((0.0, -W_HEAD * 0.5 + 16.0, z_top_head))
    for p in (o_jbox, o_neck, o_head, o_cap_f):
        o_m.uniteWith(p); p.erase()

    # 法兰螺栓孔与内流道切除
    r_bcd = (r_pipe + r_fl) * 0.54
    r_hole = max(6.0, (r_fl - r_pipe) * 0.16)
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
    s.setLinearDimension("H_HEAD", (0.0, 0.0, 0.0), (0.0, 0.0, H_HEAD))
    s.setLinearDimension("FL_OD", (-L / 2.0, -r_fl, 0.0), (-L / 2.0, r_fl, 0.0))
