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

@activate(Group="Blind",
          TooltipShort=u"法兰盖/盲法兰 (HG/T 20592 BL PN16 RF)",
          TooltipLong=u"HG/T 20592-2009 PN16 RF 突面法兰盖(盲法兰 BL)，实心封堵结构，含清晰 RF 突面台阶与加厚盲板盘",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"法兰盖/盲法兰主要几何尺寸参数")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"盲法兰外径 D (mm)")
@param(C_THK=LENGTH, TooltipShort=u"盲板厚度", TooltipLong=u"盲法兰总厚度 C (mm，含突面)", Ask4Dist=True)
@param(D_RF=LENGTH, TooltipShort=u"突面外径", TooltipLong=u"RF 突面密封面外径 d (mm)")
@param(F_RF=LENGTH, TooltipShort=u"突面高度", TooltipLong=u"RF 突面高度 f1 (mm)")
def FLANGE_BL_HGT20592(
    s,
    D_FL=220.0,
    C_THK=20.0,
    D_RF=158.0,
    F_RF=2.0,
    ID=u"FLANGE_BL_HGT20592",
    **kw
):
    u"""HG/T 20592 PN16 RF 盲法兰 (Port 1 在 X=0 密封面)。"""
    D_FL = max(60.0, float(D_FL))
    F_RF = max(0.0, min(8.0, float(F_RF)))
    C_THK = float(C_THK)
    if C_THK < 1.0:
        C_THK = 1.0
    D_RF = max(30.0, min(D_FL - 12.0, float(D_RF)))

    disc_len = max(6.0, C_THK - F_RF)

    if F_RF > 0.1:
        o_main = CYLINDER(s, R=D_RF / 2.0, H=F_RF + 0.2, O=0.0).rotateY(90.0)
        o_disc = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=0.0).rotateY(90.0).translate((F_RF, 0.0, 0.0))
        o_main.uniteWith(o_disc)
        o_disc.erase()
    else:
        o_main = CYLINDER(s, R=D_FL / 2.0, H=C_THK, O=0.0).rotateY(90.0)

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('C_THK', (0.0, 0.0, 0.0), (C_THK, 0.0, 0.0))
