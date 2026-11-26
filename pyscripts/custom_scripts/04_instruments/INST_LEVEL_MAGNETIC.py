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
          TooltipShort=u"侧装双法兰磁翻板液位计 (HG/T 21584)",
          TooltipLong=u"化工侧装双法兰磁翻板液位计，含比例饱满的主浮筒、前侧磁翻柱指示面板、上下侧向连接法兰及顶部放空/底部排污口",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"磁翻板液位计中心距、浮筒直径、接管伸出及法兰尺寸")
@param(L_C2C=LENGTH, TooltipShort=u"法兰中心距", TooltipLong=u"上下侧向过程法兰中心距 C-C (mm)", Ask4Dist=True)
@param(D_CHAMBER=LENGTH, TooltipShort=u"主浮筒外径", TooltipLong=u"磁性浮子主测量筒外径 (mm)")
@param(L_NOZ=LENGTH, TooltipShort=u"接管伸出距", TooltipLong=u"主浮筒中心至侧向法兰密封面距离 (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"侧向过程连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"过程连接法兰厚度 (mm)")
def INST_LEVEL_MAGNETIC(
    s,
    L_C2C=800.0,
    D_CHAMBER=96.0,
    L_NOZ=140.0,
    D_FL=115.0,
    C_FL=18.0,
    ID=u"INST_LEVEL_MAGNETIC",
    **kw
):
    u"""侧装双法兰磁翻板液位计 (Port 1 在 (-L_NOZ, 0, -L_C2C/2), Port 2 在 (-L_NOZ, 0, +L_C2C/2))。"""
    L_C2C = float(L_C2C)
    if L_C2C < 1.0:
        L_C2C = 1.0
    D_CHAMBER = max(76.0, float(D_CHAMBER))
    L_NOZ = float(L_NOZ)
    if L_NOZ < 1.0:
        L_NOZ = 1.0
    D_FL = max(95.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))

    half_c = L_C2C / 2.0
    r_ch = D_CHAMBER / 2.0
    r_fl = D_FL / 2.0
    ext_top = 115.0
    ext_bot = 145.0
    h_body = L_C2C + ext_top + ext_bot

    # 1. 比例饱满的主浮筒 (Z=[-half_c - ext_bot, +half_c + ext_top])
    o_main = CYLINDER(s, R=r_ch, H=h_body, O=0.0).translate((0.0, 0.0, -half_c - ext_bot))

    # 2. 顶部检修盲法兰+放空丝堵，底部排污法兰+排污阀嘴
    o_tfl = CYLINDER(s, R=r_ch + 24.0, H=24.0, O=0.0).translate((0.0, 0.0, half_c + ext_top - 12.0))
    o_main.uniteWith(o_tfl)
    o_tfl.erase()
    o_vent = CYLINDER(s, R=16.0, H=38.0, O=0.0).translate((0.0, 0.0, half_c + ext_top + 10.0))
    o_main.uniteWith(o_vent)
    o_vent.erase()

    o_bfl = CYLINDER(s, R=r_ch + 24.0, H=26.0, O=0.0).translate((0.0, 0.0, -half_c - ext_bot - 14.0))
    o_main.uniteWith(o_bfl)
    o_bfl.erase()
    o_drain = CYLINDER(s, R=18.0, H=54.0, O=0.0).translate((0.0, 0.0, -half_c - ext_bot - 64.0))
    o_main.uniteWith(o_drain)
    o_drain.erase()
    o_dfl = CYLINDER(s, R=32.0, H=14.0, O=0.0).translate((0.0, 0.0, -half_c - ext_bot - 68.0))
    o_main.uniteWith(o_dfl)
    o_dfl.erase()

    # 3. 上下侧向连接短管与法兰 (-X)
    for sz in (-1.0, 1.0):
        zz = sz * half_c
        o_noz = CYLINDER(s, R=24.0, H=L_NOZ, O=0.0).rotateY(90.0).translate((-L_NOZ, 0.0, zz))
        o_main.uniteWith(o_noz)
        o_noz.erase()
        o_fl = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-L_NOZ, 0.0, zz))
        o_main.uniteWith(o_fl)
        o_fl.erase()

    # 4. 前侧磁翻柱指示面板 (-Y) + 上下抱箍 + 远传变送器表头 (+X 侧)
    w_panel = 52.0
    d_panel = 34.0
    h_panel = L_C2C + 70.0
    o_panel = CORNERBOX(s, L=w_panel, W=d_panel, H=h_panel).translate((-w_panel / 2.0, -(r_ch + d_panel - 4.0), -h_panel / 2.0))
    o_main.uniteWith(o_panel)
    o_panel.erase()
    # 标尺面板前框凸沿
    o_rail = CORNERBOX(s, L=w_panel + 12.0, W=12.0, H=h_panel - 20.0).translate((-(w_panel + 12.0) / 2.0, -(r_ch + d_panel + 4.0), -(h_panel - 20.0) / 2.0))
    o_main.uniteWith(o_rail)
    o_rail.erase()
    # 3道紧固抱箍环
    for zc in (-half_c * 0.65, 0.0, half_c * 0.65):
        o_clamp = CYLINDER(s, R=r_ch + 9.0, H=20.0, O=0.0).translate((0.0, 0.0, zc - 10.0))
        o_main.uniteWith(o_clamp)
        o_clamp.erase()
    # 侧装干簧管远传变送器表头 (+X 顶部附近)
    o_txarm = CYLINDER(s, R=14.0, H=48.0, O=0.0).rotateY(90.0).translate((r_ch - 8.0, 0.0, half_c - 60.0))
    o_main.uniteWith(o_txarm)
    o_txarm.erase()
    o_txhead = CYLINDER(s, R=44.0, H=82.0, O=0.0).translate((r_ch + 36.0, 0.0, half_c - 100.0))
    o_main.uniteWith(o_txhead)
    o_txhead.erase()

    s.setPoint((-L_NOZ, 0.0, -half_c), (-1.0, 0.0, 0.0))
    s.setPoint((-L_NOZ, 0.0, half_c), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_C2C', (-L_NOZ, 0.0, -half_c), (-L_NOZ, 0.0, half_c))
    s.setLinearDimension('L_NOZ', (-L_NOZ, 0.0, 0.0), (0.0, 0.0, 0.0))
