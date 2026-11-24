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

@activate(Group="Instrument", Ports=2, TooltipShort=u"U型双管科氏力质量流量计 (CMF / GB/T 31130)", TooltipLong=u"化工标准 GB/T 31130 科里奥利力U型双弯管质量流量计 (Coriolis Mass Flowmeter)，含两端法兰分流歧管、下部标志性圆底不锈钢U型振动管密封防护箱壳与顶部智能变送表头", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"质量流量计主要结构尺寸：安装总长、U型传感器箱深与顶部表头高")
@param(D=LENGTH, TooltipShort=u"管道外径 D", Ask4Dist=True, TooltipLong=u"连接管道公称外径 OD")
@param(L=LENGTH, TooltipShort=u"安装总长 L", Ask4Dist=True, TooltipLong=u"两端法兰端面间距 L")
@param(H_BOX=LENGTH, TooltipShort=u"U型箱下深", Ask4Dist=True, TooltipLong=u"管道中心至下部U型传感器保护壳底深度")
@param(W_BOX=LENGTH, TooltipShort=u"U型箱厚度", TooltipLong=u"下部传感器保护壳横向厚度")
@param(H_HEAD=LENGTH, TooltipShort=u"中心至表头高", Ask4Dist=True, TooltipLong=u"管道中心至顶部转换器表头高度")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"两端连接法兰厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"单端法兰螺栓孔数")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"安装位号，如 FT-103")
def INSTRUMENT_CORIOLIS_FLOWMETER(s, D=60.3, L=460.0, H_BOX=360.0, W_BOX=135.0, H_HEAD=245.0, FL_OD=165.0, FL_T=18.0, NBOLTS=4, ID=u"CMF-DN50", **kw):
    D = max(18.0, float(D))
    L = max(260.0, float(L))
    H_BOX = max(200.0, float(H_BOX))
    W_BOX = max(80.0, float(W_BOX))
    H_HEAD = max(160.0, float(H_HEAD))
    FL_OD = max(D + 45.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.85
    r_fl = FL_OD / 2.0

    # 1. 水平分流歧管过渡管段 + 两端连接法兰
    o_m = CYLINDER(s, R=r_pipe * 1.15, H=L, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    o_m.uniteWith(fl_l); fl_l.erase()
    o_m.uniteWith(fl_r); fl_r.erase()

    # 2. 下部标志性 U 型圆底不锈钢全密封传感器防护盒壳
    l_case = L * 0.68
    r_bot = l_case * 0.5
    h_rect = max(40.0, H_BOX - r_bot + r_pipe * 0.8)
    z_rect_bot = -(H_BOX - r_bot)
    o_u_rect = BOX(s, L=W_BOX, W=h_rect, H=l_case).translate((0.0, 0.0, z_rect_bot + h_rect * 0.5))
    o_u_bot = CYLINDER(s, R=r_bot, H=W_BOX, O=0.0).rotateX(90.0).translate((0.0, W_BOX * 0.5, z_rect_bot))
    o_m.uniteWith(o_u_rect); o_u_rect.erase()
    o_m.uniteWith(o_u_bot); o_u_bot.erase()

    # 3. 顶部立柱与智能质量流量变送表头
    r_head = 65.0
    z_hc = H_HEAD - r_head
    o_neck = CYLINDER(s, R=22.0, H=z_hc, O=0.0)
    o_head = CYLINDER(s, R=r_head, H=140.0, O=0.0).rotateX(90.0).translate((0.0, 70.0, z_hc))
    o_m.uniteWith(o_neck); o_neck.erase()
    o_m.uniteWith(o_head); o_head.erase()

    # 4. 两端端口内孔与法兰螺栓孔
    for sx in (-1.0, 1.0):
        xb = -L * 0.5 - 2.0 if sx < 0 else (L * 0.5 - FL_T * 2.5)
        br = CYLINDER(s, R=r_bore, H=FL_T * 2.5 + 4.0, O=0.0).rotateY(90.0).translate((xb, 0.0, 0.0))
        o_m.subtractFrom(br); br.erase()
    r_bcd = r_pipe + (r_fl - r_pipe) * 0.66
    r_hole = max(5.0, min(11.0, (r_fl - r_pipe) * 0.14))
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        by, bz = r_bcd * math.cos(ang), r_bcd * math.sin(ang)
        hl = CYLINDER(s, R=r_hole, H=FL_T + 6.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 2.0), by, bz))
        o_m.subtractFrom(hl); hl.erase()
        hr = CYLINDER(s, R=r_hole, H=FL_T + 6.0, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T - 4.0, by, bz))
        o_m.subtractFrom(hr); hr.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, H_HEAD), (L / 2.0, 0.0, H_HEAD))
    s.setLinearDimension("H_BOX", (-L / 2.0, 0.0, 0.0), (-L / 2.0, 0.0, -H_BOX))
    s.setLinearDimension("H_HEAD", (L / 2.0, 0.0, 0.0), (L / 2.0, 0.0, H_HEAD))
