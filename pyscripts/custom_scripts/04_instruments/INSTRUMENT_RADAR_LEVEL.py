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

@activate(Group="Instrument", Ports=1, TooltipShort=u"高频喇叭口法兰雷达液位计 (80GHz / HG/T 20507)", TooltipLong=u"化工行业标准 HG/T 20507 罐顶法兰安装非接触式喇叭口天线雷达液位计 (Flanged Horn-Antenna Radar Level Transmitter)，含罐顶连接法兰、向下伸入罐内的不锈钢锥形喇叭口天线与上部双腔隔爆电子表头", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"雷达液位计主要结构尺寸：安装法兰外径、喇叭口天线尺寸与表头高度")
@param(FL_OD=LENGTH, TooltipShort=u"安装法兰径", Ask4Dist=True, TooltipLong=u"罐顶安装法兰外径 (如 DN100 为 220mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"安装法兰盘厚度")
@param(D_HORN=LENGTH, TooltipShort=u"喇叭口外径", Ask4Dist=True, TooltipLong=u"下部锥形发射喇叭天线口部直径")
@param(L_HORN=LENGTH, TooltipShort=u"天线伸入长 L", Ask4Dist=True, TooltipLong=u"法兰面以下喇叭口天线伸入长度 L")
@param(H_HEAD=LENGTH, TooltipShort=u"法兰至表头高", Ask4Dist=True, TooltipLong=u"法兰面至上部电子表头顶部总高 H")
@param(D_HEAD=LENGTH, TooltipShort=u"表头外径", TooltipLong=u"上部防爆雷达电子仓直径")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"安装法兰螺栓孔数量")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"安装位号，如 LT-201")
def INSTRUMENT_RADAR_LEVEL(s, FL_OD=220.0, FL_T=22.0, D_HORN=96.0, L_HORN=210.0, H_HEAD=225.0, D_HEAD=125.0, NBOLTS=8, ID=u"LT-201-DN100", **kw):
    FL_OD = max(150.0, float(FL_OD))
    FL_T = max(16.0, float(FL_T))
    D_HORN = max(55.0, min(FL_OD * 0.62, float(D_HORN)))
    L_HORN = max(120.0, float(L_HORN))
    H_HEAD = max(160.0, float(H_HEAD))
    D_HEAD = max(95.0, float(D_HEAD))
    NBOLTS = max(4, int(NBOLTS))

    r_fl = FL_OD / 2.0
    r_horn = D_HORN / 2.0
    r_head = D_HEAD / 2.0

    # 1. 中部罐顶安装法兰 (底面在 z = 0) + 下部伸入罐内的空心喇叭口锥形发射天线 (z in [-L_HORN, 0])
    o_m = CYLINDER(s, R=r_fl, H=FL_T, O=0.0)
    o_horn = CONE(s, R1=r_horn, R2=22.0, H=L_HORN, E=0.0).translate((0.0, 0.0, -L_HORN))
    o_horn_in = CONE(s, R1=r_horn - 3.5, R2=16.0, H=L_HORN * 0.92, E=0.0).translate((0.0, 0.0, -L_HORN - 1.0))
    o_horn.subtractFrom(o_horn_in); o_horn_in.erase()
    o_m.uniteWith(o_horn); o_horn.erase()

    r_bcd = r_fl * 0.78
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        bh = CYLINDER(s, R=10.0, H=FL_T + 6.0, O=0.0).translate((r_bcd * math.cos(ang), r_bcd * math.sin(ang), -2.0))
        o_m.subtractFrom(bh); bh.erase()

    # 2. 上部万向调角球铰颈座 + 双腔防爆雷达表头
    z_hc = H_HEAD - r_head
    o_neck = CYLINDER(s, R=28.0, H=z_hc, O=0.0)
    o_head = CYLINDER(s, R=r_head, H=D_HEAD * 1.15, O=0.0).rotateX(90.0).translate((0.0, D_HEAD * 0.55, z_hc))
    o_m.uniteWith(o_neck); o_neck.erase()
    o_m.uniteWith(o_head); o_head.erase()

    o_win = CYLINDER(s, R=r_head * 0.68, H=8.0, O=0.0).rotateX(90.0).translate((0.0, -D_HEAD * 0.6 + 6.0, z_hc))
    o_m.subtractFrom(o_win); o_win.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("L_HORN", (-r_fl, 0.0, -L_HORN), (-r_fl, 0.0, 0.0))
    s.setLinearDimension("H_HEAD", (-r_fl, 0.0, 0.0), (-r_fl, 0.0, H_HEAD))
    s.setLinearDimension("D_HORN", (-r_horn, 0.0, -L_HORN), (r_horn, 0.0, -L_HORN))
