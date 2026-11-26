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
          TooltipShort=u"带颈平焊法兰 (HG/T 20592 SO PN16 RF)",
          TooltipLong=u"HG/T 20592-2009 PN16 RF 带颈平焊法兰(SO)，含清晰 RF 突面、法兰盘外廓与短锥形加强颈",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"带颈平焊法兰主要几何尺寸参数")
@param(D=LENGTH, TooltipShort=u"配用管外径", TooltipLong=u"配用钢管外径 A (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰盘外径 D (mm)")
@param(C_THK=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度 C (mm)")
@param(H_TOT=LENGTH, TooltipShort=u"法兰总高", TooltipLong=u"带短锥颈总高度 H (mm)", Ask4Dist=True)
@param(N_HUB=LENGTH, TooltipShort=u"颈根外径", TooltipLong=u"短锥颈根部外径 N1 (mm)")
@param(N_TOP=LENGTH, TooltipShort=u"颈端外径", TooltipLong=u"短锥颈端部外径 N2 (mm)")
@param(D_RF=LENGTH, TooltipShort=u"突面外径", TooltipLong=u"RF 突面外径 d (mm)")
@param(F_RF=LENGTH, TooltipShort=u"突面高度", TooltipLong=u"RF 突面高度 f1 (mm)")
@param(B_ID=LENGTH, TooltipShort=u"通孔内径", TooltipLong=u"平焊贯通内径 B1 (mm)")
def FLANGE_SO_HGT20592(
    s,
    D=114.3,
    D_FL=220.0,
    C_THK=20.0,
    H_TOT=40.0,
    N_HUB=140.0,
    N_TOP=128.0,
    D_RF=158.0,
    F_RF=2.0,
    B_ID=116.0,
    ID=u"FLANGE_SO_HGT20592",
    **kw
):
    u"""HG/T 20592 PN16 RF 带颈平焊法兰 (Port 1 在 X=0 密封面, Port 2 在 X=H_TOT 颈端)。"""
    D = max(15.0, float(D))
    D_FL = max(D + 30.0, float(D_FL))
    F_RF = max(0.0, min(8.0, float(F_RF)))
    C_THK = max(F_RF + 6.0, float(C_THK))
    H_TOT = float(H_TOT)
    if H_TOT < 1.0:
        H_TOT = 1.0
    B_ID = max(6.0, min(D_FL - 20.0, float(B_ID)))
    N_TOP = max(B_ID + 6.0, min(D_FL - 14.0, float(N_TOP)))
    N_HUB = max(N_TOP + 2.0, min(D_FL - 10.0, float(N_HUB)))
    D_RF = max(B_ID + 6.0, min(D_FL - 8.0, float(D_RF)))

    r_in = B_ID / 2.0
    disc_len = max(4.0, C_THK - F_RF)

    if F_RF > 0.1:
        o_main = CYLINDER(s, R=D_RF / 2.0, H=F_RF + 0.2, O=r_in).rotateY(90.0)
        o_disc = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=r_in).rotateY(90.0).translate((F_RF, 0.0, 0.0))
        o_main.uniteWith(o_disc)
        o_disc.erase()
    else:
        o_main = CYLINDER(s, R=D_FL / 2.0, H=C_THK, O=r_in).rotateY(90.0)

    # 短锥颈
    neck_h = max(4.0, H_TOT - C_THK)
    o_hub = CONE(s, R1=N_HUB / 2.0, R2=N_TOP / 2.0, H=neck_h + 0.2, E=0.0).rotateY(90.0).translate((C_THK - 0.2, 0.0, 0.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()

    # 贯穿内通孔
    o_bore = CYLINDER(s, R=r_in, H=H_TOT + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H_TOT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOT', (0.0, 0.0, 0.0), (H_TOT, 0.0, 0.0))
