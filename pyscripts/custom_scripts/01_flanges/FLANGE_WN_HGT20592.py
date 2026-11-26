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
          TooltipShort=u"国标带颈对焊法兰 (HG/T 20592 WN PN16 RF)",
          TooltipLong=u"HG/T 20592-2009 PN16 RF 突面带颈对焊法兰(WN)，LOD300 工业美学标准（清晰突面台阶、法兰盘外廓、锥形焊颈与贯通内孔）",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"带颈对焊法兰主要几何尺寸参数")
@param(D=LENGTH, TooltipShort=u"配用管外径", TooltipLong=u"对焊端管道外径 A (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰盘外径 D (mm)")
@param(C_THK=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度 C (mm，含突面高度)")
@param(H_TOT=LENGTH, TooltipShort=u"法兰总高", TooltipLong=u"法兰总高度 H (mm)", Ask4Dist=True)
@param(N_HUB=LENGTH, TooltipShort=u"颈根外径", TooltipLong=u"锥形焊颈根部外径 N (mm)")
@param(D_RF=LENGTH, TooltipShort=u"突面外径", TooltipLong=u"RF 突面密封面外径 d (mm)")
@param(F_RF=LENGTH, TooltipShort=u"突面高度", TooltipLong=u"RF 突面高度 f1 (mm)")
@param(B_ID=LENGTH, TooltipShort=u"通孔内径", TooltipLong=u"法兰贯通内孔直径 B (mm)")
def FLANGE_WN_HGT20592(
    s,
    D=114.3,
    D_FL=220.0,
    C_THK=20.0,
    H_TOT=52.0,
    N_HUB=131.0,
    D_RF=158.0,
    F_RF=2.0,
    B_ID=106.3,
    ID=u"FLANGE_WN_HGT20592",
    **kw
):
    u"""HG/T 20592 PN16 RF 带颈对焊法兰 (Port 1 在 X=0 密封面, Port 2 在 X=H_TOT 对焊端)。"""
    D = max(15.0, float(D))
    D_FL = max(D + 30.0, float(D_FL))
    F_RF = max(0.0, min(8.0, float(F_RF)))
    C_THK = max(F_RF + 6.0, float(C_THK))
    H_TOT = float(H_TOT)
    if H_TOT < 1.0:
        H_TOT = 1.0
    N_HUB = max(D + 4.0, min(D_FL - 12.0, float(N_HUB)))
    D_RF = max(D + 4.0, min(D_FL - 8.0, float(D_RF)))
    B_ID = max(4.0, min(D - 2.0, float(B_ID)))

    r_in = B_ID / 2.0
    disc_len = max(4.0, C_THK - F_RF)

    # 1. 突面台阶 + 法兰盘
    if F_RF > 0.1:
        o_main = CYLINDER(s, R=D_RF / 2.0, H=F_RF + 0.2, O=r_in).rotateY(90.0)
        o_disc = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=r_in).rotateY(90.0).translate((F_RF, 0.0, 0.0))
        o_main.uniteWith(o_disc)
        o_disc.erase()
    else:
        o_main = CYLINDER(s, R=D_FL / 2.0, H=C_THK, O=r_in).rotateY(90.0)

    # 2. 锥形焊颈 + 对焊端直唇
    neck_span = max(8.0, H_TOT - C_THK)
    weld_lip = min(6.0, neck_span * 0.22)
    cone_h = max(4.0, neck_span - weld_lip)
    o_cone = CONE(s, R1=N_HUB / 2.0, R2=D / 2.0, H=cone_h + 0.2, E=0.0).rotateY(90.0).translate((C_THK - 0.2, 0.0, 0.0))
    o_lip = CYLINDER(s, R=D / 2.0, H=weld_lip + 0.2, O=0.0).rotateY(90.0).translate((C_THK + cone_h - 0.2, 0.0, 0.0))
    o_cone.uniteWith(o_lip)
    o_lip.erase()

    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 3. 贯穿内通孔
    o_bore = CYLINDER(s, R=r_in, H=H_TOT + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H_TOT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOT', (0.0, 0.0, 0.0), (H_TOT, 0.0, 0.0))
