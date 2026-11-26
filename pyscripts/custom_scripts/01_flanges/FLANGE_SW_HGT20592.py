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
          TooltipShort=u"承插焊法兰 (HG/T 20592 SW PN40 RF)",
          TooltipLong=u"HG/T 20592-2009 PN40 RF 承插焊法兰(SW)，含清晰 RF 突面、承插加强颈与内部阶梯承插孔台阶",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"承插焊法兰主要几何尺寸参数")
@param(D=LENGTH, TooltipShort=u"配用管外径", TooltipLong=u"配用小口径钢管外径 A (mm)")
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰盘外径 D (mm)")
@param(C_THK=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度 C (mm)")
@param(H_TOT=LENGTH, TooltipShort=u"法兰总高", TooltipLong=u"承插焊法兰总高 H (mm)", Ask4Dist=True)
@param(N_HUB=LENGTH, TooltipShort=u"承插颈外径", TooltipLong=u"承插颈外径 N (mm)")
@param(D_RF=LENGTH, TooltipShort=u"突面外径", TooltipLong=u"RF 突面外径 d (mm)")
@param(F_RF=LENGTH, TooltipShort=u"突面高度", TooltipLong=u"RF 突面高度 f1 (mm)")
@param(B_ID=LENGTH, TooltipShort=u"流体通孔径", TooltipLong=u"前端流体贯通内径 B2 (mm)")
@param(B_SOCK=LENGTH, TooltipShort=u"承插孔内径", TooltipLong=u"后端阶梯承插孔内径 B1 (mm)")
@param(U_DEPTH=LENGTH, TooltipShort=u"承插深度", TooltipLong=u"阶梯承插孔深度 U (mm)")
def FLANGE_SW_HGT20592(
    s,
    D=33.7,
    D_FL=115.0,
    C_THK=18.0,
    H_TOT=28.0,
    N_HUB=48.0,
    D_RF=68.0,
    F_RF=2.0,
    B_ID=27.0,
    B_SOCK=34.5,
    U_DEPTH=13.0,
    ID=u"FLANGE_SW_HGT20592",
    **kw
):
    u"""HG/T 20592 PN40 RF 承插焊法兰 (Port 1 在 X=0 密封面, Port 2 在 X=H_TOT 承插口端)。"""
    D = max(10.0, float(D))
    D_FL = max(D + 24.0, float(D_FL))
    F_RF = max(0.0, min(6.0, float(F_RF)))
    C_THK = max(F_RF + 6.0, float(C_THK))
    H_TOT = float(H_TOT)
    if H_TOT < 1.0:
        H_TOT = 1.0
    B_ID = max(4.0, min(D - 2.0, float(B_ID)))
    B_SOCK = max(B_ID + 2.0, float(B_SOCK))
    N_HUB = max(B_SOCK + 6.0, min(D_FL - 10.0, float(N_HUB)))
    D_RF = max(B_ID + 6.0, min(D_FL - 8.0, float(D_RF)))
    U_DEPTH = max(4.0, min(H_TOT - 5.0, float(U_DEPTH)))

    disc_len = max(4.0, C_THK - F_RF)

    # 1. 外轮廓（突面 + 法兰盘 + 微锥承插颈）
    if F_RF > 0.1:
        o_main = CYLINDER(s, R=D_RF / 2.0, H=F_RF + 0.2, O=0.0).rotateY(90.0)
        o_disc = CYLINDER(s, R=D_FL / 2.0, H=disc_len, O=0.0).rotateY(90.0).translate((F_RF, 0.0, 0.0))
        o_main.uniteWith(o_disc)
        o_disc.erase()
    else:
        o_main = CYLINDER(s, R=D_FL / 2.0, H=C_THK, O=0.0).rotateY(90.0)

    neck_h = max(4.0, H_TOT - C_THK)
    o_hub = CONE(s, R1=(N_HUB + 2.0) / 2.0, R2=N_HUB / 2.0, H=neck_h + 0.2, E=0.0).rotateY(90.0).translate((C_THK - 0.2, 0.0, 0.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()

    # 2. 贯通流体小孔
    o_bore = CYLINDER(s, R=B_ID / 2.0, H=H_TOT + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    # 3. 后端阶梯承插大孔
    o_sock = CYLINDER(s, R=B_SOCK / 2.0, H=U_DEPTH + 4.0, O=0.0).rotateY(90.0).translate((H_TOT - U_DEPTH, 0.0, 0.0))
    o_main.subtractFrom(o_sock)
    o_sock.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((H_TOT, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOT', (0.0, 0.0, 0.0), (H_TOT, 0.0, 0.0))
