# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Instrument",
    FirstPortEndtypes="FL",
    Ports="1",
    TooltipShort=u"导波雷达液位变送器",
    TooltipLong=u"化工高压反应釜/界面测量与卧罐旁通管用导波雷达液位变送器 (GWR / HG/T 20507，含过程连接法兰、高温高频密封隔离脖颈、双腔智能雷达表头与下部同轴/单杆导波探头及配重锤)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(FL_OD=LENGTH, TooltipShort=u"过程法兰径", TooltipLong=u"导波雷达安装法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"过程连接法兰厚度 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"表头总高", TooltipLong=u"法兰底面至顶部雷达转换器顶面的高度 (mm)")
@param(L_PROBE=LENGTH, TooltipShort=u"导波杆长度", TooltipLong=u"法兰底面以下不锈钢导波探杆与配重端头的长度 (mm)")
@param(W_HEAD=LENGTH, TooltipShort=u"表头宽度", TooltipLong=u"双腔防爆雷达变送器表头宽度 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"过程连接法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"导波雷达液位计型号编码")
def INSTRUMENT_GUIDED_WAVE_RADAR(s, FL_OD=165.0, FL_T=20.0, H_TOP=255.0, L_PROBE=420.0, W_HEAD=148.0, NBOLTS=4, ID=u"LT-117-GWR", **kw):
    FL_OD = max(100.0, float(FL_OD))
    FL_T = max(14.0, float(FL_T))
    H_TOP = max(180.0, float(H_TOP))
    L_PROBE = max(200.0, float(L_PROBE))
    W_HEAD = max(110.0, float(W_HEAD))
    NBOLTS = max(4, int(NBOLTS))

    r_fl = FL_OD / 2.0

    # 1. 过程连接法兰 (底面 Z=0, Port 1 朝向 -Z) + 法兰螺栓孔
    o_m = CYLINDER(s, R=r_fl, H=FL_T, O=0.0)
    r_bcd = r_fl * 0.74
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        bh = CYLINDER(s, R=8.0, H=FL_T + 4.0, O=0.0).translate((r_bcd * math.cos(ang), r_bcd * math.sin(ang), -2.0))
        o_m.subtractFrom(bh); bh.erase()

    # 2. 高温散热隔离颈 + 顶部双腔雷达变送器表头 + 遮阳防护罩顶板
    z_head_c = H_TOP - 58.0
    o_hex = BOX(s, L=48.0, W=32.0, H=48.0).translate((0.0, 0.0, FL_T + 14.0))
    o_neck = CYLINDER(s, R=22.0, H=z_head_c - FL_T, O=0.0).translate((0.0, 0.0, FL_T))
    o_head = CYLINDER(s, R=54.0, H=W_HEAD, O=0.0).rotateX(90.0).translate((0.0, W_HEAD * 0.5, z_head_c))
    o_cap1 = CYLINDER(s, R=58.0, H=16.0, O=0.0).rotateX(90.0).translate((0.0, -W_HEAD * 0.5 + 16.0, z_head_c))
    o_cap2 = CYLINDER(s, R=58.0, H=16.0, O=0.0).rotateX(90.0).translate((0.0, W_HEAD * 0.5, z_head_c))
    for p in (o_hex, o_neck, o_head, o_cap1, o_cap2):
        o_m.uniteWith(p); p.erase()

    # 3. 法兰下方同轴导波护套 + 中心导波杆 + 底部重锤张紧配重块 (Z: [-L_PROBE, 0])
    o_coax = CYLINDER(s, R=24.0, H=L_PROBE * 0.35, O=0.0).translate((0.0, 0.0, -L_PROBE * 0.35 + 4.0))
    o_rod = CYLINDER(s, R=9.0, H=L_PROBE, O=0.0).translate((0.0, 0.0, -L_PROBE + 4.0))
    o_weight = CYLINDER(s, R=20.0, H=55.0, O=0.0).translate((0.0, 0.0, -L_PROBE))
    for p in (o_coax, o_rod, o_weight):
        o_m.uniteWith(p); p.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H_TOP", (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
    s.setLinearDimension("L_PROBE", (0.0, 0.0, -L_PROBE), (0.0, 0.0, 0.0))
    s.setLinearDimension("FL_OD", (-r_fl, 0.0, 0.0), (r_fl, 0.0, 0.0))
