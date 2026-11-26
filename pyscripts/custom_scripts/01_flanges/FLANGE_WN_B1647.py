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
          TooltipShort=u"大直径带颈对焊法兰 (ASME B16.47 Series A/B)",
          TooltipLong=u"ASME B16.47 Series A/B 大口径带颈对焊法兰 (DN700~DN1200 Class150/300)，厚重法兰盘、大锥颈与清晰突面台阶",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"ASME B16.47 大直径对焊法兰主要尺寸参数")
@param(D=LENGTH, TooltipShort=u"配用管外径", TooltipLong=u"大口径管外径 A (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰外径 O (mm)")
@param(C_THK=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度 tf (mm)")
@param(H_TOT=LENGTH, TooltipShort=u"法兰总高", TooltipLong=u"法兰总高 Y (mm)", Ask4Dist=True)
@param(N_HUB=LENGTH, TooltipShort=u"颈根外径", TooltipLong=u"锥颈大端外径 X (mm)")
@param(D_RF=LENGTH, TooltipShort=u"突面外径", TooltipLong=u"RF 突面外径 R (mm)")
@param(F_RF=LENGTH, TooltipShort=u"突面高度", TooltipLong=u"RF 突面高度 (mm)")
@param(B_ID=LENGTH, TooltipShort=u"通孔内径", TooltipLong=u"大口径法兰通孔内径 B (mm)")
def FLANGE_WN_B1647(
    s,
    D=711.2,
    D_FL=925.0,
    C_THK=71.5,
    H_TOT=125.6,
    N_HUB=727.0,
    D_RF=800.0,
    F_RF=1.6,
    B_ID=692.2,
    ID=u"FLANGE_WN_B1647",
    **kw
):
    u"""ASME B16.47 大直径带颈对焊法兰 (Port 1 在 X=0 密封面, Port 2 在 X=H_TOT 对焊端)。"""
    D = max(500.0, float(D))
    D_FL = max(D + 80.0, float(D_FL))
    F_RF = max(0.0, min(10.0, float(F_RF)))
    C_THK = max(F_RF + 20.0, float(C_THK))
    H_TOT = float(H_TOT)
    if H_TOT < 1.0:
        H_TOT = 1.0
    N_HUB = max(D + 12.0, min(D_FL - 30.0, float(N_HUB)))
    D_RF = max(D + 12.0, min(D_FL - 20.0, float(D_RF)))
    B_ID = max(400.0, min(D - 8.0, float(B_ID)))

    r_in = B_ID / 2.0
    disc_len = max(10.0, C_THK - F_RF)

    if F_RF > 0.1:
        o_main = CYLINDER(s, R=D_RF / 2.0, H=F_RF + 0.3, O=r_in).rotateY(90.0)
        o_disc = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=r_in).rotateY(90.0).translate((F_RF, 0.0, 0.0))
        o_main.uniteWith(o_disc)
        o_disc.erase()
    else:
        o_main = CYLINDER(s, R=D_FL / 2.0, H=C_THK, O=r_in).rotateY(90.0)

    neck_span = max(16.0, H_TOT - C_THK)
    weld_lip = min(12.0, neck_span * 0.22)
    cone_h = max(8.0, neck_span - weld_lip)
    o_cone = CONE(s, R1=N_HUB / 2.0, R2=D / 2.0, H=cone_h + 0.3, E=0.0).rotateY(90.0).translate((C_THK - 0.3, 0.0, 0.0))
    o_lip = CYLINDER(s, R=D / 2.0, H=weld_lip + 0.3, O=0.0).rotateY(90.0).translate((C_THK + cone_h - 0.3, 0.0, 0.0))
    o_cone.uniteWith(o_lip)
    o_lip.erase()

    o_main.uniteWith(o_cone)
    o_cone.erase()

    o_bore = CYLINDER(s, R=r_in, H=H_TOT + 20.0, O=0.0).rotateY(90.0).translate((-10.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H_TOT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOT', (0.0, 0.0, 0.0), (H_TOT, 0.0, 0.0))
