# -*- coding: utf-8 -*-
import math
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
          TooltipShort=u"孔板法兰单件 (ASME B16.36 Class300/600 RF)",
          TooltipLong=u"ASME B16.36 孔板法兰单件，采用加厚法兰盘、标准锥形焊颈、RF 突面与侧向对称双取压短节(含取压通孔)",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"ASME B16.36 孔板法兰主要几何尺寸参数")
@param(D=LENGTH, TooltipShort=u"配用管外径", TooltipLong=u"对焊端管道外径 A (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"孔板法兰盘外径 O (mm)")
@param(C_THK=LENGTH, TooltipShort=u"加厚盘厚度", TooltipLong=u"加厚孔板法兰盘厚度 tf (mm，满足取压孔布置)")
@param(H_TOT=LENGTH, TooltipShort=u"法兰总高", TooltipLong=u"孔板法兰总高 Y (mm)", Ask4Dist=True)
@param(N_HUB=LENGTH, TooltipShort=u"颈根外径", TooltipLong=u"锥形焊颈根部外径 X (mm)")
@param(D_RF=LENGTH, TooltipShort=u"突面外径", TooltipLong=u"RF 突面外径 R (mm)")
@param(F_RF=LENGTH, TooltipShort=u"突面高度", TooltipLong=u"RF 突面高度 (mm)")
@param(B_ID=LENGTH, TooltipShort=u"通孔内径", TooltipLong=u"法兰贯通内孔直径 B (mm)")
@param(D_BOSS=LENGTH, TooltipShort=u"取压短节外径", TooltipLong=u"侧向对称双取压短节外径 (mm)")
@param(L_BOSS=LENGTH, TooltipShort=u"取压短节伸长", TooltipLong=u"取压短节伸出法兰外缘长度 (mm)")
def FLANGE_ORIFICE_B1636(
    s,
    D=114.3,
    D_FL=255.0,
    C_THK=38.1,
    H_TOT=92.1,
    N_HUB=146.0,
    D_RF=157.2,
    F_RF=1.6,
    B_ID=102.3,
    D_BOSS=28.0,
    L_BOSS=26.0,
    ID=u"FLANGE_ORIFICE_B1636",
    **kw
):
    u"""ASME B16.36 孔板法兰单件 (Port 1 在 X=0 密封面, Port 2 在 X=H_TOT 对焊端, ±Z 侧向双取压短节)。"""
    D = max(25.0, float(D))
    D_FL = max(D + 50.0, float(D_FL))
    F_RF = max(0.0, min(8.0, float(F_RF)))
    C_THK = max(F_RF + 24.0, float(C_THK))
    H_TOT = float(H_TOT)
    if H_TOT < 1.0:
        H_TOT = 1.0
    N_HUB = max(D + 8.0, min(D_FL - 16.0, float(N_HUB)))
    D_RF = max(D + 6.0, min(D_FL - 12.0, float(D_RF)))
    B_ID = max(10.0, min(D - 2.0, float(B_ID)))
    D_BOSS = max(14.0, min(C_THK - F_RF - 4.0, float(D_BOSS)))
    L_BOSS = max(12.0, float(L_BOSS))

    r_in = B_ID / 2.0
    disc_len = max(18.0, C_THK - F_RF)

    # 1. RF 突面 + 加厚法兰盘
    if F_RF > 0.1:
        o_main = CYLINDER(s, R=D_RF / 2.0, H=F_RF + 0.2, O=0.0).rotateY(90.0)
        o_disc = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=0.0).rotateY(90.0).translate((F_RF, 0.0, 0.0))
        o_main.uniteWith(o_disc)
        o_disc.erase()
    else:
        o_main = CYLINDER(s, R=D_FL / 2.0, H=C_THK, O=0.0).rotateY(90.0)

    # 2. 锥形焊颈 + 对焊直唇
    neck_span = max(12.0, H_TOT - C_THK)
    weld_lip = min(6.0, neck_span * 0.22)
    cone_h = max(6.0, neck_span - weld_lip)
    o_cone = CONE(s, R1=N_HUB / 2.0, R2=D / 2.0, H=cone_h + 0.2, E=0.0).rotateY(90.0).translate((C_THK - 0.2, 0.0, 0.0))
    o_lip = CYLINDER(s, R=D / 2.0, H=weld_lip + 0.2, O=0.0).rotateY(90.0).translate((C_THK + cone_h - 0.2, 0.0, 0.0))
    o_cone.uniteWith(o_lip)
    o_lip.erase()
    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 3. 侧向对称双取压短节 (±Z 方向，位于加厚盘中部 X=tap_x)
    tap_x = F_RF + disc_len * 0.5
    r_fl = D_FL / 2.0
    total_boss_span = 2.0 * (r_fl + L_BOSS)
    o_taps = CYLINDER(s, R=D_BOSS / 2.0, H=total_boss_span, O=0.0).translate((tap_x, 0.0, -(r_fl + L_BOSS)))
    o_main.uniteWith(o_taps)
    o_taps.erase()

    # 取压短节端部加强凸台台阶
    collar_h = min(8.0, L_BOSS * 0.35)
    collar_r = D_BOSS / 2.0 + 2.5
    for sign in (1.0, -1.0):
        z0 = (r_fl + L_BOSS - collar_h) if sign > 0 else -(r_fl + L_BOSS)
        o_col = CYLINDER(s, R=collar_r, H=collar_h, O=0.0).translate((tap_x, 0.0, z0))
        o_main.uniteWith(o_col)
        o_col.erase()

    # 4. 贯通主流道 + 对称取压小通孔
    o_bore = CYLINDER(s, R=r_in, H=H_TOT + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    r_tap_hole = max(4.0, D_BOSS * 0.22)
    o_thole = CYLINDER(s, R=r_tap_hole, H=total_boss_span + 10.0, O=0.0).translate((tap_x, 0.0, -(r_fl + L_BOSS + 5.0)))
    o_main.subtractFrom(o_thole)
    o_thole.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H_TOT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOT', (0.0, 0.0, 0.0), (H_TOT, 0.0, 0.0))
