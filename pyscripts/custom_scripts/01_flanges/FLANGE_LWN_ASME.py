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
          TooltipShort=u"长焊颈法兰 (ASME LWN Class150/300)",
          TooltipLong=u"ASME B16.5 设备接管专用长焊颈法兰(LWN)，加长厚壁直筒颈部、颈根过渡台阶与 RF 突面密封面",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"长焊颈法兰主要几何尺寸参数")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰盘外径 O (mm)")
@param(C_THK=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度 tf (mm)")
@param(L_TOT=LENGTH, TooltipShort=u"长颈总高", TooltipLong=u"长焊颈法兰总长度 L (mm)", Ask4Dist=True)
@param(N_HUB=LENGTH, TooltipShort=u"厚壁直颈外径", TooltipLong=u"长直焊颈外径 X (mm)")
@param(D_RF=LENGTH, TooltipShort=u"突面外径", TooltipLong=u"RF 突面外径 R (mm)")
@param(F_RF=LENGTH, TooltipShort=u"突面高度", TooltipLong=u"RF 突面高度 (mm)")
@param(B_ID=LENGTH, TooltipShort=u"通孔内径", TooltipLong=u"厚壁直颈贯通内径 B (mm)")
def FLANGE_LWN_ASME(
    s,
    D_FL=230.0,
    C_THK=23.9,
    L_TOT=305.0,
    N_HUB=135.0,
    D_RF=157.2,
    F_RF=1.6,
    B_ID=101.6,
    ID=u"FLANGE_LWN_ASME",
    **kw
):
    u"""ASME 长焊颈法兰 LWN (Port 1 在 X=0 密封面, Port 2 在 X=L_TOT 接管端)。"""
    B_ID = max(12.0, float(B_ID))
    N_HUB = max(B_ID + 16.0, float(N_HUB))
    D_FL = max(N_HUB + 40.0, float(D_FL))
    F_RF = max(0.0, min(8.0, float(F_RF)))
    C_THK = max(F_RF + 10.0, float(C_THK))
    L_TOT = float(L_TOT)
    if L_TOT < 1.0:
        L_TOT = 1.0
    D_RF = max(B_ID + 10.0, min(D_FL - 10.0, float(D_RF)))

    r_in = B_ID / 2.0
    disc_len = max(6.0, C_THK - F_RF)

    # 1. RF 突面 + 法兰盘
    if F_RF > 0.1:
        o_main = CYLINDER(s, R=D_RF / 2.0, H=F_RF + 0.2, O=r_in).rotateY(90.0)
        o_disc = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=r_in).rotateY(90.0).translate((F_RF, 0.0, 0.0))
        o_main.uniteWith(o_disc)
        o_disc.erase()
    else:
        o_main = CYLINDER(s, R=D_FL / 2.0, H=C_THK, O=r_in).rotateY(90.0)

    # 2. 颈根过渡倒角肩台 + 加长厚壁直颈
    fillet_h = min(14.0, (L_TOT - C_THK) * 0.12)
    r_fillet = min(D_FL / 2.0 - 6.0, N_HUB / 2.0 + 6.0)
    o_fil = CONE(s, R1=r_fillet, R2=N_HUB / 2.0, H=fillet_h + 0.2, E=0.0).rotateY(90.0).translate((C_THK - 0.2, 0.0, 0.0))
    o_main.uniteWith(o_fil)
    o_fil.erase()

    neck_h = max(20.0, L_TOT - C_THK)
    o_neck = CYLINDER(s, R=N_HUB / 2.0, H=neck_h + 0.2, O=r_in).rotateY(90.0).translate((C_THK - 0.2, 0.0, 0.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    # 3. 贯通内孔
    o_bore = CYLINDER(s, R=r_in, H=L_TOT + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L_TOT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_TOT', (0.0, 0.0, 0.0), (L_TOT, 0.0, 0.0))
