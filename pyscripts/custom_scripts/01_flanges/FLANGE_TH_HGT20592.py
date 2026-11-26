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
          TooltipShort=u"螺纹法兰 (HG/T 20592 Th PN16 RF)",
          TooltipLong=u"HG/T 20592-2009 PN16 RF 螺纹法兰(Th)，含 RF 突面、法兰盘、加厚螺纹颈及后端螺纹导向沉口台阶",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"螺纹法兰主要几何尺寸参数")
@param(D=LENGTH, TooltipShort=u"配用管外径", TooltipLong=u"螺纹连接管外径 A (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰盘外径 D (mm)")
@param(C_THK=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度 C (mm)")
@param(H_TOT=LENGTH, TooltipShort=u"法兰总高", TooltipLong=u"螺纹法兰总高度 H (mm)", Ask4Dist=True)
@param(N_HUB=LENGTH, TooltipShort=u"颈根外径", TooltipLong=u"螺纹颈根部外径 N1 (mm)")
@param(N_TOP=LENGTH, TooltipShort=u"颈端外径", TooltipLong=u"螺纹颈端部外径 N2 (mm)")
@param(D_RF=LENGTH, TooltipShort=u"突面外径", TooltipLong=u"RF 突面外径 d (mm)")
@param(F_RF=LENGTH, TooltipShort=u"突面高度", TooltipLong=u"RF 突面高度 f1 (mm)")
@param(B_ID=LENGTH, TooltipShort=u"螺纹通孔径", TooltipLong=u"螺纹孔有效通径 B (mm)")
def FLANGE_TH_HGT20592(
    s,
    D=60.3,
    D_FL=165.0,
    C_THK=18.0,
    H_TOT=28.0,
    N_HUB=80.0,
    N_TOP=74.0,
    D_RF=102.0,
    F_RF=2.0,
    B_ID=56.0,
    ID=u"FLANGE_TH_HGT20592",
    **kw
):
    u"""HG/T 20592 PN16 RF 螺纹法兰 (Port 1 在 X=0 密封面, Port 2 在 X=H_TOT 螺纹端)。"""
    D = max(15.0, float(D))
    D_FL = max(D + 26.0, float(D_FL))
    F_RF = max(0.0, min(8.0, float(F_RF)))
    C_THK = max(F_RF + 6.0, float(C_THK))
    H_TOT = float(H_TOT)
    if H_TOT < 1.0:
        H_TOT = 1.0
    B_ID = max(6.0, min(D - 1.0, float(B_ID)))
    N_TOP = max(D + 6.0, min(D_FL - 12.0, float(N_TOP)))
    N_HUB = max(N_TOP + 2.0, min(D_FL - 10.0, float(N_HUB)))
    D_RF = max(D + 6.0, min(D_FL - 8.0, float(D_RF)))

    disc_len = max(4.0, C_THK - F_RF)

    if F_RF > 0.1:
        o_main = CYLINDER(s, R=D_RF / 2.0, H=F_RF + 0.2, O=0.0).rotateY(90.0)
        o_disc = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=0.0).rotateY(90.0).translate((F_RF, 0.0, 0.0))
        o_main.uniteWith(o_disc)
        o_disc.erase()
    else:
        o_main = CYLINDER(s, R=D_FL / 2.0, H=C_THK, O=0.0).rotateY(90.0)

    neck_h = max(4.0, H_TOT - C_THK)
    o_hub = CONE(s, R1=N_HUB / 2.0, R2=N_TOP / 2.0, H=neck_h + 0.2, E=0.0).rotateY(90.0).translate((C_THK - 0.2, 0.0, 0.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()

    # 贯通螺纹孔 + 后端螺纹导向沉口台阶 (深度 4mm)
    o_bore = CYLINDER(s, R=B_ID / 2.0, H=H_TOT + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    c_depth = min(4.0, neck_h * 0.4)
    c_rad = min(N_TOP / 2.0 - 2.0, D / 2.0 + 1.0)
    if c_rad > B_ID / 2.0 + 0.5:
        o_cb = CYLINDER(s, R=c_rad, H=c_depth + 3.0, O=0.0).rotateY(90.0).translate((H_TOT - c_depth, 0.0, 0.0))
        o_main.subtractFrom(o_cb)
        o_cb.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H_TOT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOT', (0.0, 0.0, 0.0), (H_TOT, 0.0, 0.0))
