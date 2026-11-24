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

@activate(Group="Instrument", Ports=1, TooltipShort=u"智能单法兰隔膜压力/液位变送器 (3051LT)", TooltipLong=u"化工标准 HG/T 20507 智能单法兰平膜片隔膜密封差压/液位变送器 (Flanged Diaphragm-Seal Pressure/Level Transmitter)，含底部安装法兰、共面传感器膜盒室与顶部双端盖防爆电子表头", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"法兰压力/液位变送器主要结构尺寸：法兰外径、总高与表头尺寸")
@param(D_FL=LENGTH, TooltipShort=u"安装法兰径", Ask4Dist=True, TooltipLong=u"底部隔膜安装法兰外径 (如 DN80 为 200mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"安装法兰盘总厚")
@param(H_TOTAL=LENGTH, TooltipShort=u"变送器总高 H", Ask4Dist=True, TooltipLong=u"法兰底面至变送器表头顶部总高 H")
@param(D_HOUSING=LENGTH, TooltipShort=u"表头外径", TooltipLong=u"顶部圆柱形电子仓表壳直径")
@param(L_HOUSING=LENGTH, TooltipShort=u"表头长度", TooltipLong=u"顶部双端盖电子仓前后长度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓数", TooltipLong=u"安装法兰螺栓孔数量")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"安装位号，如 LT/PT-101")
def INSTRUMENT_DIFF_PRESSURE_XMTR(s, D_FL=200.0, FL_T=22.0, H_TOTAL=285.0, D_HOUSING=115.0, L_HOUSING=145.0, NBOLTS=8, ID=u"LT-101-DN80", **kw):
    D_FL = max(115.0, float(D_FL))
    FL_T = max(14.0, float(FL_T))
    H_TOTAL = max(210.0, float(H_TOTAL))
    D_HOUSING = max(90.0, float(D_HOUSING))
    L_HOUSING = max(110.0, float(L_HOUSING))
    NBOLTS = max(4, int(NBOLTS))

    r_fl = D_FL / 2.0
    r_hs = D_HOUSING / 2.0

    # 1. 底部隔膜安装法兰 (底面在 z = 0) + 共面传感器膜盒方座
    o_m = CYLINDER(s, R=r_fl, H=FL_T, O=0.0)
    r_bcd = r_fl * 0.78
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        bh = CYLINDER(s, R=9.0, H=FL_T + 6.0, O=0.0).translate((r_bcd * math.cos(ang), r_bcd * math.sin(ang), -2.0))
        o_m.subtractFrom(bh); bh.erase()

    h_cell = (H_TOTAL - D_HOUSING) * 0.55
    o_cell = BOX(s, L=82.0, W=h_cell, H=96.0).translate((0.0, 0.0, FL_T + h_cell * 0.5 - 2.0))
    o_m.uniteWith(o_cell); o_cell.erase()

    # 2. 传感器连接颈 + 顶部水平双端盖防爆电子仓表头 + 观察窗凹槽与两侧导管口
    z_hc = H_TOTAL - r_hs
    o_neck = CYLINDER(s, R=24.0, H=z_hc - FL_T, O=0.0).translate((0.0, 0.0, FL_T))
    o_head = CYLINDER(s, R=r_hs, H=L_HOUSING, O=0.0).rotateX(90.0).translate((0.0, L_HOUSING * 0.5, z_hc))
    o_m.uniteWith(o_neck); o_neck.erase()
    o_m.uniteWith(o_head); o_head.erase()

    o_win = CYLINDER(s, R=r_hs * 0.68, H=8.0, O=0.0).rotateX(90.0).translate((0.0, -L_HOUSING * 0.5 + 6.0, z_hc))
    o_m.subtractFrom(o_win); o_win.erase()
    for sx in (-1.0, 1.0):
        cd = CYLINDER(s, R=15.0, H=r_hs + 26.0, O=0.0).rotateY(90.0 * sx).translate((0.0, 0.0, z_hc - 10.0))
        o_m.uniteWith(cd); cd.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H_TOTAL", (-r_fl, 0.0, 0.0), (-r_fl, 0.0, H_TOTAL))
    s.setLinearDimension("D_FL", (-r_fl, 0.0, 0.0), (r_fl, 0.0, 0.0))
    s.setLinearDimension("L_HOUSING", (r_hs, -L_HOUSING * 0.5, z_hc), (r_hs, L_HOUSING * 0.5, z_hc))
