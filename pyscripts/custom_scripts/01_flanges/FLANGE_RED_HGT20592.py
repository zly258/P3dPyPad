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
          TooltipShort=u"异径带颈法兰 (HG/T 20592 Reducing RF)",
          TooltipLong=u"异径带颈法兰(Reducing Flange)，大规格法兰盘配小口径通孔与小锥颈，直接实现法兰端变径连接",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"异径法兰主要几何尺寸参数")
@param(D_SMALL=LENGTH, TooltipShort=u"小端管外径", TooltipLong=u"变径后小口径管道外径 (mm)")
@param(D_FL=LENGTH, TooltipShort=u"大法兰外径", TooltipLong=u"大规格法兰盘外径 D (mm)")
@param(C_THK=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"大法兰盘厚度 C (mm)")
@param(H_TOT=LENGTH, TooltipShort=u"法兰总高", TooltipLong=u"异径法兰总高度 H (mm)", Ask4Dist=True)
@param(N_HUB=LENGTH, TooltipShort=u"小颈根径", TooltipLong=u"小口径锥颈根部外径 N (mm)")
@param(D_RF=LENGTH, TooltipShort=u"突面外径", TooltipLong=u"大规格 RF 突面外径 d (mm)")
@param(F_RF=LENGTH, TooltipShort=u"突面高度", TooltipLong=u"RF 突面高度 f1 (mm)")
@param(B_ID=LENGTH, TooltipShort=u"小端通孔径", TooltipLong=u"小口径贯通内孔直径 B (mm)")
def FLANGE_RED_HGT20592(
    s,
    D_SMALL=60.3,
    D_FL=220.0,
    C_THK=22.0,
    H_TOT=52.0,
    N_HUB=84.0,
    D_RF=158.0,
    F_RF=2.0,
    B_ID=52.5,
    ID=u"FLANGE_RED_HGT20592",
    **kw
):
    u"""异径法兰 Reducing Flange (Port 1 在 X=0 大法兰密封面, Port 2 在 X=H_TOT 小口径焊端)。"""
    D_SMALL = max(15.0, float(D_SMALL))
    D_FL = max(D_SMALL + 50.0, float(D_FL))
    F_RF = max(0.0, min(8.0, float(F_RF)))
    C_THK = max(F_RF + 8.0, float(C_THK))
    H_TOT = float(H_TOT)
    if H_TOT < 1.0:
        H_TOT = 1.0
    N_HUB = max(D_SMALL + 8.0, min(D_FL - 20.0, float(N_HUB)))
    D_RF = max(N_HUB + 10.0, min(D_FL - 10.0, float(D_RF)))
    B_ID = max(4.0, min(D_SMALL - 2.0, float(B_ID)))

    r_in = B_ID / 2.0
    disc_len = max(6.0, C_THK - F_RF)

    if F_RF > 0.1:
        o_main = CYLINDER(s, R=D_RF / 2.0, H=F_RF + 0.2, O=r_in).rotateY(90.0)
        o_disc = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=r_in).rotateY(90.0).translate((F_RF, 0.0, 0.0))
        o_main.uniteWith(o_disc)
        o_disc.erase()
    else:
        o_main = CYLINDER(s, R=D_FL / 2.0, H=C_THK, O=r_in).rotateY(90.0)

    neck_span = max(10.0, H_TOT - C_THK)
    weld_lip = min(6.0, neck_span * 0.25)
    cone_h = max(4.0, neck_span - weld_lip)
    o_cone = CONE(s, R1=N_HUB / 2.0, R2=D_SMALL / 2.0, H=cone_h + 0.2, E=0.0).rotateY(90.0).translate((C_THK - 0.2, 0.0, 0.0))
    o_lip = CYLINDER(s, R=D_SMALL / 2.0, H=weld_lip + 0.2, O=0.0).rotateY(90.0).translate((C_THK + cone_h - 0.2, 0.0, 0.0))
    o_cone.uniteWith(o_lip)
    o_lip.erase()

    o_main.uniteWith(o_cone)
    o_cone.erase()

    o_bore = CYLINDER(s, R=r_in, H=H_TOT + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H_TOT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOT', (0.0, 0.0, 0.0), (H_TOT, 0.0, 0.0))
