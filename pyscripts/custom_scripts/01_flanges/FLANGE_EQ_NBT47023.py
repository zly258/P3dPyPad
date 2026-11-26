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
          TooltipShort=u"压力容器长颈对焊法兰 (NB/T 47023 DN400~1200)",
          TooltipLong=u"NB/T 47023-2012 长颈对焊压力容器主法兰 (DN400~DN1200)，含厚重法兰盘、RF/FM 密封台阶与加长锥形容器焊颈",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"NB/T 47023 容器主法兰主要几何尺寸参数")
@param(D_VES=LENGTH, TooltipShort=u"筒体外径", TooltipLong=u"配用压力容器筒体外径 (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"容器主法兰外径 D (mm)")
@param(C_THK=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度 δ (mm)")
@param(H_TOT=LENGTH, TooltipShort=u"法兰总高", TooltipLong=u"长颈对焊容器法兰总高 H (mm)", Ask4Dist=True)
@param(N_HUB=LENGTH, TooltipShort=u"颈根外径", TooltipLong=u"大锥颈根部外径 N1 (mm)")
@param(D_RF=LENGTH, TooltipShort=u"密封面外径", TooltipLong=u"密封面外径 D2 (mm)")
@param(F_RF=LENGTH, TooltipShort=u"密封台阶高", TooltipLong=u"密封面突面高度 f (mm)")
@param(B_ID=LENGTH, TooltipShort=u"容器内径", TooltipLong=u"压力容器法兰内径 DN (mm)")
def FLANGE_EQ_NBT47023(
    s,
    D_VES=620.0,
    D_FL=760.0,
    C_THK=48.0,
    H_TOT=135.0,
    N_HUB=664.0,
    D_RF=674.0,
    F_RF=4.0,
    B_ID=600.0,
    ID=u"FLANGE_EQ_NBT47023",
    **kw
):
    u"""NB/T 47023 长颈对焊压力容器主法兰 (Port 1 在 X=0 密封面, Port 2 在 X=H_TOT 筒体对焊端)。"""
    B_ID = max(300.0, float(B_ID))
    D_VES = max(B_ID + 10.0, float(D_VES))
    D_FL = max(D_VES + 70.0, float(D_FL))
    F_RF = max(0.0, min(10.0, float(F_RF)))
    C_THK = max(F_RF + 18.0, float(C_THK))
    H_TOT = float(H_TOT)
    if H_TOT < 1.0:
        H_TOT = 1.0
    N_HUB = max(D_VES + 16.0, min(D_FL - 30.0, float(N_HUB)))
    D_RF = max(D_VES + 16.0, min(D_FL - 24.0, float(D_RF)))

    r_in = B_ID / 2.0
    disc_len = max(14.0, C_THK - F_RF)

    # 1. 密封面台阶 + 容器主法兰盘
    if F_RF > 0.1:
        o_main = CYLINDER(s, R=D_RF / 2.0, H=F_RF + 0.3, O=r_in).rotateY(90.0)
        o_disc = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=r_in).rotateY(90.0).translate((F_RF, 0.0, 0.0))
        o_main.uniteWith(o_disc)
        o_disc.erase()
    else:
        o_main = CYLINDER(s, R=D_FL / 2.0, H=C_THK, O=r_in).rotateY(90.0)

    # 2. 长锥颈 + 筒体对焊直段
    neck_span = max(30.0, H_TOT - C_THK)
    skirt_h = min(22.0, neck_span * 0.25)
    cone_h = max(16.0, neck_span - skirt_h)
    o_cone = CONE(s, R1=N_HUB / 2.0, R2=D_VES / 2.0, H=cone_h + 0.3, E=0.0).rotateY(90.0).translate((C_THK - 0.3, 0.0, 0.0))
    o_skirt = CYLINDER(s, R=D_VES / 2.0, H=skirt_h + 0.3, O=0.0).rotateY(90.0).translate((C_THK + cone_h - 0.3, 0.0, 0.0))
    o_cone.uniteWith(o_skirt)
    o_skirt.erase()
    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 3. 贯通容器大内孔
    o_bore = CYLINDER(s, R=r_in, H=H_TOT + 20.0, O=0.0).rotateY(90.0).translate((-10.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H_TOT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOT', (0.0, 0.0, 0.0), (H_TOT, 0.0, 0.0))
