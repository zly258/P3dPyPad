# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.divsub.divutil import *
from varmain.custom import *
from aqa.math import *
import math

@activate(Group="Instrument", Ports=1, TooltipShort=u"万向型双金属温度计配套管 (WSS / JB/T 8803)", TooltipLong=u"化工行业标准 JB/T 8803 / HG/T 20507 万向型工业双金属温度计配锥形保护套管总成 (Bimetallic Thermometer with Stepped Thermowell)，含下部锥形热电偶套管、六角安装头、不锈钢波纹万向节与大表盘", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"双金属温度计主要结构尺寸：表盘直径、插入套管长与外伸高")
@param(D_DIAL=LENGTH, TooltipShort=u"表盘外径", Ask4Dist=True, TooltipLong=u"圆形温度表盘外径 (如 100, 150 mm)")
@param(THK_DIAL=LENGTH, TooltipShort=u"表盘厚度", TooltipLong=u"表盘壳体前后厚度")
@param(L_STEM=LENGTH, TooltipShort=u"套管插深 L", Ask4Dist=True, TooltipLong=u"下部锥形热套管插入深度")
@param(H_EXT=LENGTH, TooltipShort=u"外伸颈高 H", Ask4Dist=True, TooltipLong=u"安装螺纹基准面至表盘底外伸高度")
@param(D_WELL=LENGTH, TooltipShort=u"套管根径", TooltipLong=u"锥形保护套管根部直径")
@param(HEX_S=LENGTH, TooltipShort=u"六角对边", TooltipLong=u"安装六角螺母对边宽度")
@param(ID=STRING, TooltipShort=u"仪表位号", TooltipLong=u"安装位号，如 TI-101")
def INSTRUMENT_BIMETAL_THERMOMETER(s, D_DIAL=100.0, THK_DIAL=42.0, L_STEM=160.0, H_EXT=85.0, D_WELL=22.0, HEX_S=32.0, ID=u"TI-101", **kw):
    D_DIAL = max(60.0, float(D_DIAL))
    THK_DIAL = max(25.0, float(THK_DIAL))
    L_STEM = max(80.0, float(L_STEM))
    H_EXT = max(50.0, float(H_EXT))
    D_WELL = max(14.0, float(D_WELL))
    HEX_S = max(D_WELL + 8.0, float(HEX_S))

    r_dial = D_DIAL / 2.0
    r_well = D_WELL / 2.0

    # 1. 下部锥形棒料热套管 (z in [-L_STEM, 0]，端口在 z=0 处) + 球头测温端
    o_m = CONE(s, R1=r_well * 0.62, R2=r_well, H=L_STEM, E=0.0).translate((0.0, 0.0, -L_STEM))
    o_tip = SPHERE(s, R=r_well * 0.62).translate((0.0, 0.0, -L_STEM))
    o_m.uniteWith(o_tip); o_tip.erase()

    # 2. 过程安装六角螺母头 + 波纹管可调万向连接颈 (z in [0, H_EXT])
    nut_h = 22.0
    o_nut = NUT_BOLT_HEAD_6_001(s, W=HEX_S, H=nut_h).rotateY(-90.0)
    o_neck = CYLINDER(s, R=r_well * 0.72, H=H_EXT + 12.0, O=0.0)
    o_m.uniteWith(o_nut); o_nut.erase()
    o_m.uniteWith(o_neck); o_neck.erase()
    for k in range(3):
        ring = CYLINDER(s, R=r_well * 0.96, H=5.0, O=0.0).translate((0.0, 0.0, nut_h + 12.0 + k * 12.0))
        o_m.uniteWith(ring); ring.erase()

    # 3. 上部圆形双金属温度计表壳 + 压盖表圈 + 凹陷刻度盘与温度指针 (朝向 -Y)
    z_c = H_EXT + r_dial
    y_back = THK_DIAL * 0.5
    y_front = -THK_DIAL * 0.5
    o_case = CYLINDER(s, R=r_dial, H=THK_DIAL, O=0.0).rotateX(90.0).translate((0.0, y_back, z_c))
    o_bezel = CYLINDER(s, R=r_dial * 1.05, H=THK_DIAL * 0.30, O=0.0).rotateX(90.0).translate((0.0, y_front + THK_DIAL * 0.30, z_c))
    o_m.uniteWith(o_case); o_case.erase()
    o_m.uniteWith(o_bezel); o_bezel.erase()

    rec_d = 8.0
    o_rec = CYLINDER(s, R=r_dial * 0.84, H=rec_d + 2.0, O=0.0).rotateX(90.0).translate((0.0, y_front + rec_d, z_c))
    o_m.subtractFrom(o_rec); o_rec.erase()

    o_ptr = BOX(s, L=5.0, W=r_dial * 0.68, H=4.0).translate((0.0, 0.0, r_dial * 0.25)).rotateY(35.0).translate((0.0, y_front + rec_d - 2.0, z_c))
    o_m.uniteWith(o_ptr); o_ptr.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("L_STEM", (-r_dial, 0.0, -L_STEM), (-r_dial, 0.0, 0.0))
    s.setLinearDimension("H_EXT", (-r_dial, 0.0, 0.0), (-r_dial, 0.0, H_EXT))
    s.setLinearDimension("D_DIAL", (-r_dial, y_front, z_c), (r_dial, y_front, z_c))
