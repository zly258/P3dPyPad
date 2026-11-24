# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
from aqa.math import *
import math

@activate(Group="Instrument", Ports=1, TooltipShort=u"法兰防爆热电阻温度变送器 (WZP / IEC 60751)", TooltipLong=u"化工标准 IEC 60751 / HG/T 20507 法兰安装锥形保护套管防爆一体化热电阻/热电偶温度变送器 (Flanged Explosion-Proof Temperature Transmitter with Thermowell)，含过程安装法兰、下部锥形套管、上部散热延长颈与隔爆铝合金接线表头", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"温度变送器主要结构尺寸：安装法兰外径、套管插深与表头高度")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", Ask4Dist=True, TooltipLong=u"过程连接法兰外径 (如 DN40 为 150mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"过程连接法兰厚度")
@param(L_INSERT=LENGTH, TooltipShort=u"套管插深 L", Ask4Dist=True, TooltipLong=u"法兰密封面以下锥形护套管插入深度 L")
@param(H_NECK=LENGTH, TooltipShort=u"延长颈高 H", Ask4Dist=True, TooltipLong=u"法兰面至顶部防爆接线盒顶总高 H")
@param(D_HEAD=LENGTH, TooltipShort=u"接线盒外径", TooltipLong=u"顶部防爆变送接线表头外径")
@param(D_WELL=LENGTH, TooltipShort=u"套管根径", TooltipLong=u"锥形保护套管根部直径")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"安装位号，如 TT-101")
def INSTRUMENT_TEMP_TRANSMITTER(s, FL_OD=150.0, FL_T=18.0, L_INSERT=220.0, H_NECK=240.0, D_HEAD=115.0, D_WELL=26.0, ID=u"TT-101-DN40", **kw):
    FL_OD = max(95.0, float(FL_OD))
    FL_T = max(14.0, float(FL_T))
    L_INSERT = max(100.0, float(L_INSERT))
    H_NECK = max(150.0, float(H_NECK))
    D_HEAD = max(85.0, float(D_HEAD))
    D_WELL = max(16.0, float(D_WELL))

    r_fl = FL_OD / 2.0
    r_well = D_WELL / 2.0
    r_head = D_HEAD / 2.0

    # 1. 中部过程连接法兰 (底面在 z = 0) + 下部整体钻孔锥形热电偶套管 (z in [-L_INSERT, 0])
    o_m = CYLINDER(s, R=r_fl, H=FL_T, O=0.0)
    o_well = CONE(s, R1=r_well * 0.62, R2=r_well, H=L_INSERT, E=0.0).translate((0.0, 0.0, -L_INSERT))
    o_m.uniteWith(o_well); o_well.erase()

    r_bcd = r_fl * 0.73
    for i in range(4):
        ang = math.radians(i * 90.0 + 45.0)
        bh = CYLINDER(s, R=9.0, H=FL_T + 6.0, O=0.0).translate((r_bcd * math.cos(ang), r_bcd * math.sin(ang), -2.0))
        o_m.subtractFrom(bh); bh.erase()

    # 2. 上部六角压紧接头 + 散热延长颈管 + 顶部防爆接线盒表头与防爆填料函格兰头
    z_hc = H_NECK - r_head
    o_neck = CYLINDER(s, R=15.0, H=z_hc, O=0.0)
    o_hex = BOX(s, L=36.0, W=24.0, H=36.0).translate((0.0, 0.0, FL_T + 12.0))
    o_m.uniteWith(o_neck); o_neck.erase()
    o_m.uniteWith(o_hex); o_hex.erase()

    o_head = SPHERE(s, R=r_head * 0.92).translate((0.0, 0.0, z_hc))
    o_cap = CYLINDER(s, R=r_head, H=D_HEAD * 0.95, O=0.0).rotateX(90.0).translate((0.0, D_HEAD * 0.45, z_hc))
    o_gland = CYLINDER(s, R=16.0, H=r_head + 36.0, O=0.0).rotateY(90.0).translate((0.0, 0.0, z_hc - 12.0))
    for p in (o_head, o_cap, o_gland):
        o_m.uniteWith(p); p.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("L_INSERT", (-r_fl, 0.0, -L_INSERT), (-r_fl, 0.0, 0.0))
    s.setLinearDimension("H_NECK", (-r_fl, 0.0, 0.0), (-r_fl, 0.0, H_NECK))
    s.setLinearDimension("FL_OD", (-r_fl, 0.0, 0.0), (r_fl, 0.0, 0.0))
