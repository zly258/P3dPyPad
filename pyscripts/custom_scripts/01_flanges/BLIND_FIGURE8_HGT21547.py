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
          TooltipShort=u"8字盲板 (HG/T 21547 PN16 RF)",
          TooltipLong=u"HG/T 21547-2016 管道用 8 字盲板，由通孔环、实心盲板盘与加厚连接柄组成，含中心定位吊装孔",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"8字盲板主要几何尺寸参数")
@param(D_OUT=LENGTH, TooltipShort=u"盘外径", TooltipLong=u"盲板盘与通孔环外径 D (mm)")
@param(B_ID=LENGTH, TooltipShort=u"通孔内径", TooltipLong=u"通孔环内径 B (mm)")
@param(T_DISC=LENGTH, TooltipShort=u"盘厚度", TooltipLong=u"盲板盘与通孔环厚度 T (mm)", Ask4Dist=True)
@param(C_DIST=LENGTH, TooltipShort=u"中心距", TooltipLong=u"通孔环与实心盲盘中心距 C (mm)")
@param(W_WEB=LENGTH, TooltipShort=u"连接柄宽", TooltipLong=u"中间加厚连接柄宽度 W (mm)")
@param(T_WEB=LENGTH, TooltipShort=u"连接柄厚", TooltipLong=u"加厚连接柄厚度 Tw (mm)")
def BLIND_FIGURE8_HGT21547(
    s,
    D_OUT=162.0,
    B_ID=106.3,
    T_DISC=14.0,
    C_DIST=180.0,
    W_WEB=44.0,
    T_WEB=18.0,
    ID=u"BLIND_FIGURE8_HGT21547",
    **kw
):
    u"""HG/T 21547 8字盲板 (通孔环居中于原点, Port 1 在 X=0, Port 2 在 X=T_DISC, 实心盘位于 +Z)。"""
    D_OUT = max(60.0, float(D_OUT))
    B_ID = max(15.0, min(D_OUT - 16.0, float(B_ID)))
    T_DISC = float(T_DISC)
    if T_DISC < 1.0:
        T_DISC = 1.0
    C_DIST = max(D_OUT + 12.0, float(C_DIST))
    W_WEB = max(18.0, min(D_OUT * 0.55, float(W_WEB)))
    T_WEB = max(T_DISC, float(T_WEB))

    # 1. 通孔环 (位于原点，X: 0 -> T_DISC)
    o_main = CYLINDER(s, R=D_OUT / 2.0, H=T_DISC, O=B_ID / 2.0).rotateY(90.0)

    # 2. 实心盲板盘 (位于 Z = C_DIST)
    o_blind = CYLINDER(s, R=D_OUT / 2.0, H=T_DISC, O=0.0).rotateY(90.0).translate((0.0, 0.0, C_DIST))
    o_main.uniteWith(o_blind)
    o_blind.erase()

    # 3. 加厚连接柄 (跨接两盘之间，居中于 X = T_DISC/2，厚度 T_WEB 形成清晰加厚台阶)
    web_z_len = C_DIST - D_OUT + 22.0
    o_web = BOX(s, L=W_WEB, W=web_z_len, H=T_WEB).translate((T_DISC * 0.5, 0.0, C_DIST * 0.5))
    o_main.uniteWith(o_web)
    o_web.erase()

    # 4. 清理通孔环内腔（避免连接柄探入通孔）+ 连接柄中心孔
    o_bore = CYLINDER(s, R=B_ID / 2.0, H=T_WEB + 10.0, O=0.0).rotateY(90.0).translate((-(T_WEB - T_DISC) * 0.5 - 5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    r_hole = max(5.0, min(W_WEB * 0.24, (C_DIST - D_OUT) * 0.35))
    if r_hole >= 4.0:
        o_wh = CYLINDER(s, R=r_hole, H=T_WEB + 10.0, O=0.0).rotateY(90.0).translate((-(T_WEB - T_DISC) * 0.5 - 5.0, 0.0, C_DIST * 0.5))
        o_main.subtractFrom(o_wh)
        o_wh.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((T_DISC, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('T_DISC', (0.0, 0.0, 0.0), (T_DISC, 0.0, 0.0))
