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
          TooltipShort=u"板式平焊法兰 (HG/T 20592 PL PN16 RF)",
          TooltipLong=u"HG/T 20592-2009 PN16 RF 板式平焊法兰(PL)，清晰突面密封台阶、平板法兰盘与贯通平焊内孔",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"板式平焊法兰主要几何尺寸参数")
@param(D=LENGTH, TooltipShort=u"配用管外径", TooltipLong=u"配用钢管外径 A (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰盘外径 D (mm)")
@param(C_THK=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰总厚度 C (mm，含突面)", Ask4Dist=True)
@param(D_RF=LENGTH, TooltipShort=u"突面外径", TooltipLong=u"RF 突面外径 d (mm)")
@param(F_RF=LENGTH, TooltipShort=u"突面高度", TooltipLong=u"RF 突面高度 f1 (mm)")
@param(B_ID=LENGTH, TooltipShort=u"通孔内径", TooltipLong=u"平焊套入通孔内径 B1 (mm)")
def FLANGE_PL_HGT20592(
    s,
    D=114.3,
    D_FL=220.0,
    C_THK=22.0,
    D_RF=158.0,
    F_RF=2.0,
    B_ID=116.0,
    ID=u"FLANGE_PL_HGT20592",
    **kw
):
    u"""HG/T 20592 PN16 RF 板式平焊法兰 (Port 1 在 X=0 密封面, Port 2 在 X=C_THK 背面)。"""
    D = max(15.0, float(D))
    D_FL = max(D + 30.0, float(D_FL))
    F_RF = max(0.0, min(8.0, float(F_RF)))
    C_THK = float(C_THK)
    if C_THK < 1.0:
        C_THK = 1.0
    D_RF = max(D + 6.0, min(D_FL - 8.0, float(D_RF)))
    B_ID = max(6.0, min(D_RF - 6.0, float(B_ID)))

    r_in = B_ID / 2.0
    disc_len = max(4.0, C_THK - F_RF)

    if F_RF > 0.1:
        o_main = CYLINDER(s, R=D_RF / 2.0, H=F_RF + 0.2, O=r_in).rotateY(90.0)
        o_disc = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=r_in).rotateY(90.0).translate((F_RF, 0.0, 0.0))
        o_main.uniteWith(o_disc)
        o_disc.erase()
    else:
        o_main = CYLINDER(s, R=D_FL / 2.0, H=C_THK, O=r_in).rotateY(90.0)

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((C_THK, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('C_THK', (0.0, 0.0, 0.0), (C_THK, 0.0, 0.0))
