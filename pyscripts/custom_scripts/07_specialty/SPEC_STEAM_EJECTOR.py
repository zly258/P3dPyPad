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

@activate(Group="Instrument",
          TooltipShort=u"蒸汽喷射器/混合器 (HG/T 20592)",
          TooltipLong=u"拉瓦尔喷嘴型蒸汽喷射器/混合器，含动力蒸汽入口法兰、吸气室与顶部吸气法兰、收缩混合喉管、扩散管与出口法兰",
          LengthUnit="mm",
          Ports="3",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"蒸汽喷射器三端口外径、总长与吸气口中心高")
@param(D_MOTIVE=LENGTH, TooltipShort=u"动力蒸汽管径", TooltipLong=u"动力蒸汽入口接管外径 (mm)")
@param(D_SUCT=LENGTH, TooltipShort=u"吸气口管径", TooltipLong=u"侧向吸气接管外径 (mm)")
@param(D_OUT=LENGTH, TooltipShort=u"出口管径", TooltipLong=u"混合扩散出口管外径 (mm)")
@param(L_TOTAL=LENGTH, TooltipShort=u"喷射器总长", TooltipLong=u"动力入口法兰面至出口法兰面总长 L (mm)", Ask4Dist=True)
@param(H_SUCT=LENGTH, TooltipShort=u"吸气口高度", TooltipLong=u"主轴中心线至吸气法兰面高度 H (mm)", Ask4Dist=True)
@param(D_FL_M=LENGTH, TooltipShort=u"动力法兰外径", TooltipLong=u"动力蒸汽入口法兰外径 (mm)")
@param(D_FL_S=LENGTH, TooltipShort=u"吸气法兰外径", TooltipLong=u"吸气口法兰外径 (mm)")
@param(D_FL_O=LENGTH, TooltipShort=u"出口法兰外径", TooltipLong=u"混合出口法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"各端连接法兰厚度 (mm)")
def SPEC_STEAM_EJECTOR(
    s,
    D_MOTIVE=88.9,
    D_SUCT=114.3,
    D_OUT=114.3,
    L_TOTAL=780.0,
    H_SUCT=190.0,
    D_FL_M=200.0,
    D_FL_S=220.0,
    D_FL_O=220.0,
    C_FL=20.0,
    ID=u"SPEC_STEAM_EJECTOR",
    **kw
):
    u"""蒸汽喷射器 (吸气口中心在 X=0 朝 +Z, 动力口在 -X, 混合扩散出口在 +X)。"""
    D_MOTIVE = max(25.0, float(D_MOTIVE))
    D_SUCT = max(32.0, float(D_SUCT))
    D_OUT = max(32.0, float(D_OUT))
    C_FL = max(14.0, float(C_FL))
    D_FL_M = max(D_MOTIVE + 45.0, float(D_FL_M))
    D_FL_S = max(D_SUCT + 45.0, float(D_FL_S))
    D_FL_O = max(D_OUT + 45.0, float(D_FL_O))
    L_TOTAL = float(L_TOTAL)
    if L_TOTAL < 1.0:
        L_TOTAL = 1.0
    H_SUCT = float(H_SUCT)
    if H_SUCT < 1.0:
        H_SUCT = 1.0

    r_m = D_MOTIVE / 2.0
    r_s = D_SUCT / 2.0
    r_o = D_OUT / 2.0
    r_cham = r_s * 1.30
    r_throat = max(r_m * 0.62, r_o * 0.52)

    # 轴向分段 (X=0 为吸气室中心)
    l_left = L_TOTAL * 0.28
    l_right = L_TOTAL - l_left
    x_m = -l_left
    x_out = l_right
    l_cham = max(D_SUCT * 1.25, L_TOTAL * 0.20)
    x_c1 = -l_cham * 0.48
    x_c2 = l_cham * 0.52

    # 1. 动力蒸汽入口法兰与喷嘴颈段
    o_main = CYLINDER(s, R=D_FL_M / 2.0, H=C_FL, O=0.0).rotateY(90.0).translate((x_m, 0.0, 0.0))
    o_mneck = CYLINDER(s, R=r_m, H=(x_c1 - (x_m + C_FL)) + 12.0, O=0.0).rotateY(90.0).translate((x_m + C_FL - 4.0, 0.0, 0.0))
    o_main.uniteWith(o_mneck)
    o_mneck.erase()

    # 动力端对接加强法兰对
    o_mring = CYLINDER(s, R=r_cham * 1.08, H=C_FL * 0.85, O=0.0).rotateY(90.0).translate((x_c1 - C_FL * 0.4, 0.0, 0.0))
    o_main.uniteWith(o_mring)
    o_mring.erase()

    # 2. 扩大吸气室与顶部吸气法兰 (Port 3)
    o_cham = CYLINDER(s, R=r_cham, H=l_cham, O=0.0).rotateY(90.0).translate((x_c1, 0.0, 0.0))
    o_main.uniteWith(o_cham)
    o_cham.erase()

    o_sbranch = CYLINDER(s, R=r_s, H=H_SUCT - C_FL + 8.0, O=0.0).translate((0.0, 0.0, 0.0))
    o_main.uniteWith(o_sbranch)
    o_sbranch.erase()

    o_sfl = CYLINDER(s, R=D_FL_S / 2.0, H=C_FL, O=0.0).translate((0.0, 0.0, H_SUCT - C_FL))
    o_main.uniteWith(o_sfl)
    o_sfl.erase()

    # 3. 拉瓦尔收缩段 -> 混合喉管 -> 渐扩扩散管
    rem = max(60.0, (x_out - C_FL) - x_c2)
    l_conv = rem * 0.28
    l_throat = rem * 0.22
    l_diff = rem - l_conv - l_throat

    o_conv = CONE(s, R1=r_cham, R2=r_throat, H=l_conv + 4.0, E=0.0).rotateY(90.0).translate((x_c2 - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_conv)
    o_conv.erase()

    o_th = CYLINDER(s, R=r_throat, H=l_throat + 6.0, O=0.0).rotateY(90.0).translate((x_c2 + l_conv - 3.0, 0.0, 0.0))
    o_main.uniteWith(o_th)
    o_th.erase()

    o_diff = CONE(s, R1=r_throat, R2=r_o, H=l_diff + 6.0, E=0.0).rotateY(90.0).translate((x_c2 + l_conv + l_throat - 3.0, 0.0, 0.0))
    o_main.uniteWith(o_diff)
    o_diff.erase()

    # 4. 出口连接法兰 (Port 2)
    o_ofl = CYLINDER(s, R=D_FL_O / 2.0, H=C_FL, O=0.0).rotateY(90.0).translate((x_out - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_ofl)
    o_ofl.erase()

    s.setPoint((x_m, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((x_out, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, H_SUCT), (0.0, 0.0, 1.0))
    s.setLinearDimension('L_TOTAL', (x_m, 0.0, 0.0), (x_out, 0.0, 0.0))
    s.setLinearDimension('H_SUCT', (0.0, 0.0, 0.0), (0.0, 0.0, H_SUCT))
