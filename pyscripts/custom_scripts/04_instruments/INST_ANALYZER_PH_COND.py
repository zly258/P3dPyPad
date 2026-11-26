# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except (NameError, AttributeError):
    pass

from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *

@activate(Group="Instrument",
          TooltipShort=u"在线 pH/电导率过程分析仪总成 (HG/T 20592)",
          TooltipLong=u"化工在线水质/过程分析仪 pH/电导率传感器总成，含过程法兰、浸入式长探杆、底部电极保护罩、上部延长颈管及防爆变送接线表头",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"过程法兰、浸入探深、探杆外径、上部外伸高度及变送表头直径")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"过程连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"过程连接法兰厚度 (mm)")
@param(L_IMM=LENGTH, TooltipShort=u"浸入深度", TooltipLong=u"法兰密封面至探头底端浸入长度 (mm)", Ask4Dist=True)
@param(D_PROBE=LENGTH, TooltipShort=u"探杆外径", TooltipLong=u"浸入式保护管/探杆外径 (mm)")
@param(H_EXT=LENGTH, TooltipShort=u"表头高度", TooltipLong=u"法兰密封面至变送表头顶面高度 (mm)", Ask4Dist=True)
@param(D_HEAD=LENGTH, TooltipShort=u"表头外径", TooltipLong=u"接线变送表头壳体外径 (mm)")
def INST_ANALYZER_PH_COND(
    s,
    D_FL=165.0,
    C_FL=18.0,
    L_IMM=600.0,
    D_PROBE=32.0,
    H_EXT=320.0,
    D_HEAD=118.0,
    ID=u"INST_ANALYZER_PH_COND",
    **kw
):
    u"""在线 pH/电导率分析仪总成 (Port 1 在 Z=0 法兰密封面中心，探杆沿 -Z 浸入，表头在 +Z)。"""
    D_FL = max(95.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    L_IMM = float(L_IMM)
    if L_IMM < 1.0:
        L_IMM = 1.0
    D_PROBE = max(20.0, float(D_PROBE))
    H_EXT = float(H_EXT)
    if H_EXT < 1.0:
        H_EXT = 1.0
    D_HEAD = max(88.0, float(D_HEAD))

    r_fl = D_FL / 2.0
    r_probe = D_PROBE / 2.0
    r_head = D_HEAD / 2.0

    # 1. 过程连接法兰 (Port 1 落在 Z=0 底面中心) + 法兰上方压紧六角螺母座
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).translate((0.0, 0.0, 0.0))
    o_gland = CYLINDER(s, R=r_probe * 1.45, H=28.0, O=0.0).translate((0.0, 0.0, C_FL - 2.0))
    o_main.uniteWith(o_gland)
    o_gland.erase()

    # 2. 浸入式长探杆 (-Z) + 电极护套环 + 底部传感玻璃/电导池端头
    h_guard = max(56.0, D_PROBE * 1.8)
    o_shaft = CYLINDER(s, R=r_probe, H=L_IMM - h_guard + 12.0, O=0.0).translate((0.0, 0.0, -(L_IMM - h_guard)))
    o_main.uniteWith(o_shaft)
    o_shaft.erase()

    o_collar = CYLINDER(s, R=r_probe * 1.25, H=18.0, O=0.0).translate((0.0, 0.0, -(L_IMM - h_guard)))
    o_main.uniteWith(o_collar)
    o_collar.erase()

    o_cage = CYLINDER(s, R=r_probe * 1.15, H=h_guard * 0.72, O=0.0).translate((0.0, 0.0, -(L_IMM - h_guard * 0.28)))
    o_main.uniteWith(o_cage)
    o_cage.erase()

    o_tip = HALFSPHERE(s, R=r_probe * 0.88).rotateX(180.0).translate((0.0, 0.0, -(L_IMM - r_probe * 0.88)))
    o_main.uniteWith(o_tip)
    o_tip.erase()

    # 3. 上部延长颈管 (+Z) + 双腔防爆变送接线表头 + 前视窗盖环 + 电缆格兰
    z_head_c = H_EXT - r_head
    h_neck = max(60.0, z_head_c - C_FL)
    o_neck = CYLINDER(s, R=max(16.0, r_probe * 0.82), H=h_neck + 20.0, O=0.0).translate((0.0, 0.0, C_FL + 18.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    o_hneck = CYLINDER(s, R=24.0, H=28.0, O=0.0).translate((0.0, 0.0, z_head_c - r_head * 0.85 - 12.0))
    o_main.uniteWith(o_hneck)
    o_hneck.erase()

    # 主表头圆筒 (沿 Y 轴贯通，前端 -Y 带数显表盖)
    len_head = D_HEAD * 1.22
    o_head = CYLINDER(s, R=r_head, H=len_head, O=0.0).rotateX(-90.0).translate((0.0, -len_head * 0.52, z_head_c))
    o_main.uniteWith(o_head)
    o_head.erase()

    o_bezel = CYLINDER(s, R=r_head + 6.0, H=18.0, O=0.0).rotateX(-90.0).translate((0.0, -len_head * 0.52 - 12.0, z_head_c))
    o_main.uniteWith(o_bezel)
    o_bezel.erase()

    # 顶部小铭牌凸台与两侧 M20 电缆格兰
    o_topcap = CYLINDER(s, R=r_head * 0.52, H=16.0, O=0.0).translate((0.0, 0.0, H_EXT - 16.0))
    o_main.uniteWith(o_topcap)
    o_topcap.erase()

    for sx in (-1.0, 1.0):
        o_gl = CYLINDER(s, R=14.0, H=30.0, O=0.0).rotateY(sx * 90.0).translate((sx * (r_head - 4.0), 10.0, z_head_c))
        o_main.uniteWith(o_gl)
        o_gl.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L_IMM', (0.0, 0.0, 0.0), (0.0, 0.0, -L_IMM))
    s.setLinearDimension('H_EXT', (0.0, 0.0, 0.0), (0.0, 0.0, H_EXT))
