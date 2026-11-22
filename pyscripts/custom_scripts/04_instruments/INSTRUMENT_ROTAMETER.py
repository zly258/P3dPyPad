# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Instrument",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"立式金属管浮子流量计",
    TooltipLong=u"化工小流量及氮封吹扫管线立式金属管浮子/转子流量计 (LZ 系列，符合 JB/T 6844，含下进上出立式锥形测量管、上下连接法兰与前向磁耦合指针式转换器方圆表箱)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"流量计连接管道外径 (mm)")
@param(H=LENGTH, TooltipShort=u"安装高度", TooltipLong=u"上下法兰密封面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"上下连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(W_BOX=LENGTH, TooltipShort=u"指示器宽", TooltipLong=u"前侧机械/智能指针度盘表箱宽度 (mm)")
@param(H_BOX=LENGTH, TooltipShort=u"指示器高", TooltipLong=u"前侧指示器表箱高度 (mm)")
@param(D_BOX=LENGTH, TooltipShort=u"指示器厚", TooltipLong=u"前侧指示器表箱前后厚度 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"金属管转子流量计型号编码")
def INSTRUMENT_ROTAMETER(s, D=60.3, H=250.0, FL_OD=165.0, FL_T=20.0, W_BOX=118.0, H_BOX=140.0, D_BOX=68.0, NBOLTS=4, ID=u"FI-104-DN50", **kw):
    D = max(18.0, float(D))
    H = max(200.0, float(H))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    W_BOX = max(90.0, float(W_BOX))
    H_BOX = min(H - 2.0 * FL_T - 24.0, max(100.0, float(H_BOX)))
    D_BOX = max(50.0, float(D_BOX))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.84
    r_fl = FL_OD / 2.0

    # 1. 下进上出立式锥形金属测量管 + 上下法兰与加强颈
    o_m = CONE(s, R1=r_pipe * 0.96, R2=r_pipe * 1.24, H=H - 2.0 * FL_T, E=0.0).translate((0.0, 0.0, FL_T))
    fl_bot = CYLINDER(s, R=r_fl, H=FL_T, O=0.0)
    fl_top = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).translate((0.0, 0.0, H - FL_T))
    o_m.uniteWith(fl_bot); fl_bot.erase()
    o_m.uniteWith(fl_top); fl_top.erase()

    # 2. 前侧 (-Y 方向) 磁耦合指针刻度指示器方箱 + 前表面大圆弧刻度窗圈 + 电缆格兰头
    y_box_c = -(r_pipe * 1.15 + D_BOX * 0.5)
    o_neck = BOX(s, L=D_BOX * 0.65, W=H_BOX * 0.52, H=r_pipe * 1.1).translate((0.0, -r_pipe * 0.95, H * 0.5))
    o_box = BOX(s, L=D_BOX, W=H_BOX, H=W_BOX).translate((0.0, y_box_c, H * 0.5))
    r_win = min(W_BOX, H_BOX) * 0.42
    o_win = CYLINDER(s, R=r_win, H=16.0, O=r_win * 0.82).rotateX(90.0).translate((0.0, y_box_c - D_BOX * 0.5 + 2.0, H * 0.5))
    o_gland = CYLINDER(s, R=12.0, H=28.0, O=0.0).rotateY(-90.0).translate((-W_BOX * 0.5, y_box_c, H * 0.5 - H_BOX * 0.28))
    for p in (o_neck, o_box, o_win, o_gland):
        o_m.uniteWith(p); p.erase()

    # 3. 法兰螺栓孔与内通孔 + 内部锥形转子浮子芯
    r_bcd = (r_pipe + r_fl) * 0.54
    r_hole = max(5.5, (r_fl - r_pipe) * 0.16)
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        for z_pos in (-2.0, H - FL_T - 2.0):
            h_cyl = CYLINDER(s, R=r_hole, H=FL_T + 4.0, O=0.0).translate((r_bcd * math.cos(ang), r_bcd * math.sin(ang), z_pos))
            o_m.subtractFrom(h_cyl); h_cyl.erase()

    o_bore = CYLINDER(s, R=r_bore, H=H + 10.0, O=0.0).translate((0.0, 0.0, -5.0))
    o_m.subtractFrom(o_bore); o_bore.erase()

    o_float = CONE(s, R1=r_bore * 0.35, R2=r_bore * 0.72, H=38.0, E=0.0).translate((0.0, 0.0, H * 0.45))
    o_f_str = BOX(s, L=6.0, W=10.0, H=r_bore * 2.05).translate((0.0, 0.0, H * 0.45 + 15.0))
    o_m.uniteWith(o_float); o_float.erase()
    o_m.uniteWith(o_f_str); o_f_str.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setPoint((0.0, 0.0, H), (0.0, 0.0, 1.0))
    s.setLinearDimension("H", (r_fl, 0.0, 0.0), (r_fl, 0.0, H))
    s.setLinearDimension("FL_OD", (-r_fl, 0.0, 0.0), (r_fl, 0.0, 0.0))
