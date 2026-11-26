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

@activate(Group="Flange",
          TooltipShort=u"美标带颈对焊法兰 (ASME B16.5 WN RF)",
          TooltipLong=u"ASME B16.5-2025 Class150/300/600 突面带颈对焊法兰(WN)，区分 1.6mm(含于厚度)与 6.4mm(另计)突面台阶，LOD300 工业美学标准",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"ASME B16.5 带颈对焊法兰主要几何尺寸参数")
@param(D=LENGTH, TooltipShort=u"配用管外径", TooltipLong=u"对焊端管道外径 A (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰盘外径 O (mm)")
@param(C_THK=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度 tf (mm)")
@param(H_TOT=LENGTH, TooltipShort=u"法兰总高", TooltipLong=u"法兰长度 Y (mm，Class600 不含 6.4mm 突面)", Ask4Dist=True)
@param(N_HUB=LENGTH, TooltipShort=u"颈根外径", TooltipLong=u"焊颈根部外径 X (mm)")
@param(D_RF=LENGTH, TooltipShort=u"突面外径", TooltipLong=u"RF 突面外径 R (mm)")
@param(F_RF=LENGTH, TooltipShort=u"突面高度", TooltipLong=u"突面高度 (Class150/300 为 1.6mm，Class600 为 6.4mm)")
@param(RF_IN_THK=INT, TooltipShort=u"突面计入厚度", TooltipLong=u"1=突面计入厚度与总高(Class150/300)，0=突面另计(Class600)")
@param(B_ID=LENGTH, TooltipShort=u"通孔内径", TooltipLong=u"法兰贯通内孔直径 B (mm)")
def FLANGE_WN_ASME_B165(
    s,
    D=114.3,
    D_FL=230.0,
    C_THK=23.9,
    H_TOT=76.6,
    N_HUB=135.0,
    D_RF=157.2,
    F_RF=1.6,
    RF_IN_THK=1,
    B_ID=102.3,
    ID=u"FLANGE_WN_ASME_B165",
    **kw
):
    u"""ASME B16.5 Class150/300/600 带颈对焊法兰 (Port 1 在 X=0 密封面, Port 2 在 X=l_all 对焊端)。"""
    D = max(15.0, float(D))
    D_FL = max(D + 30.0, float(D_FL))
    F_RF = max(0.0, min(10.0, float(F_RF)))
    RF_IN_THK = 1 if int(RF_IN_THK) != 0 else 0
    C_THK = max(8.0, float(C_THK))
    H_TOT = float(H_TOT)
    if H_TOT < 1.0:
        H_TOT = 1.0
    N_HUB = max(D + 4.0, min(D_FL - 12.0, float(N_HUB)))
    D_RF = max(D + 4.0, min(D_FL - 8.0, float(D_RF)))
    B_ID = max(4.0, min(D - 2.0, float(B_ID)))

    if RF_IN_THK == 1:
        disc_x0 = F_RF
        disc_len = max(4.0, C_THK - F_RF)
        hub_x0 = C_THK
        l_all = H_TOT
    else:
        disc_x0 = F_RF
        disc_len = C_THK
        hub_x0 = F_RF + C_THK
        l_all = F_RF + H_TOT

    r_in = B_ID / 2.0
    if F_RF > 0.1:
        o_main = CYLINDER(s, R=D_RF / 2.0, H=F_RF + 0.2, O=r_in).rotateY(90.0)
        o_disc = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=r_in).rotateY(90.0).translate((disc_x0, 0.0, 0.0))
        o_main.uniteWith(o_disc)
        o_disc.erase()
    else:
        o_main = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=r_in).rotateY(90.0)

    neck_span = max(8.0, l_all - hub_x0)
    weld_lip = min(6.0, neck_span * 0.22)
    cone_h = max(4.0, neck_span - weld_lip)
    o_cone = CONE(s, R1=N_HUB / 2.0, R2=D / 2.0, H=cone_h + 0.2, E=0.0).rotateY(90.0).translate((hub_x0 - 0.2, 0.0, 0.0))
    o_lip = CYLINDER(s, R=D / 2.0, H=weld_lip + 0.2, O=0.0).rotateY(90.0).translate((hub_x0 + cone_h - 0.2, 0.0, 0.0))
    o_cone.uniteWith(o_lip)
    o_lip.erase()

    o_main.uniteWith(o_cone)
    o_cone.erase()

    o_bore = CYLINDER(s, R=r_in, H=l_all + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((l_all, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOT', (0.0 if RF_IN_THK == 1 else F_RF, 0.0, 0.0), (l_all, 0.0, 0.0))
