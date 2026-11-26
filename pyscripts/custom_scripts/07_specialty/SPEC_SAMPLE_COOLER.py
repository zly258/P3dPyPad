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

@activate(Group="Valve",
          TooltipShort=u"高压取样冷却器 (SH/T 3104)",
          TooltipLong=u"立式蛇管高压取样冷却器，含圆柱冷却壳体、上下端法兰盖、上下样液进出口、双侧冷却水接口与后置安装背板",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="THD")
@group("MainDimensions", TooltipLong=u"取样冷却器壳体尺寸、接管伸出量及安装背板参数")
@param(D=LENGTH, TooltipShort=u"样液管外径", TooltipLong=u"上下样液进出口接管外径 D (mm)")
@param(D_SHELL=LENGTH, TooltipShort=u"冷却壳外径", TooltipLong=u"立式圆柱冷却壳体外径 (mm)")
@param(H_SHELL=LENGTH, TooltipShort=u"冷却壳高度", TooltipLong=u"冷却壳体总高度 (mm)", Ask4Dist=True)
@param(L_NOZ=LENGTH, TooltipShort=u"样液口伸出", TooltipLong=u"上下样液接口自壳体端面伸出长度 (mm)")
@param(W_PLATE=LENGTH, TooltipShort=u"背板宽度", TooltipLong=u"后置安装支架背板宽度 (mm)")
@param(H_PLATE=LENGTH, TooltipShort=u"背板高度", TooltipLong=u"后置安装支架背板高度 (mm)")
def SPEC_SAMPLE_COOLER(
    s,
    D=21.3,
    D_SHELL=114.3,
    H_SHELL=320.0,
    L_NOZ=65.0,
    W_PLATE=160.0,
    H_PLATE=360.0,
    ID=u"SPEC_SAMPLE_COOLER",
    **kw
):
    u"""高压取样冷却器 (中心在原点, 样液口在上下 +/-Z, 冷却水口朝 +X, 安装背板在 -Y)。"""
    D = max(12.0, float(D))
    D_SHELL = max(D * 3.2, float(D_SHELL))
    H_SHELL = float(H_SHELL)
    if H_SHELL < 1.0:
        H_SHELL = 1.0
    L_NOZ = max(30.0, float(L_NOZ))
    W_PLATE = float(W_PLATE)
    if W_PLATE < 1.0:
        W_PLATE = 1.0
    H_PLATE = max(H_SHELL, float(H_PLATE))

    r_sample = D / 2.0
    r_shell = D_SHELL / 2.0
    half_h = H_SHELL / 2.0
    c_cap = max(14.0, D_SHELL * 0.14)
    r_cap = r_shell * 1.18

    # 1. 立式圆柱冷却壳体与上下法兰封盖
    o_main = CYLINDER(s, R=r_shell, H=H_SHELL - 2.0 * c_cap + 8.0, O=0.0).translate((0.0, 0.0, -(half_h - c_cap + 4.0)))

    o_cap_top = CYLINDER(s, R=r_cap, H=c_cap, O=0.0).translate((0.0, 0.0, half_h - c_cap))
    o_main.uniteWith(o_cap_top)
    o_cap_top.erase()

    o_cap_bot = CYLINDER(s, R=r_cap, H=c_cap, O=0.0).translate((0.0, 0.0, -half_h))
    o_main.uniteWith(o_cap_bot)
    o_cap_bot.erase()

    # 2. 上下样液进出口接管与卡套螺母凸台 (Port 1 在顶, Port 2 在底)
    o_top_noz = CYLINDER(s, R=r_sample, H=L_NOZ + 6.0, O=0.0).translate((0.0, 0.0, half_h - 6.0))
    o_main.uniteWith(o_top_noz)
    o_top_noz.erase()

    o_top_nut = CYLINDER(s, R=r_sample * 1.55, H=max(14.0, L_NOZ * 0.28), O=0.0).translate((0.0, 0.0, half_h + L_NOZ * 0.45))
    o_main.uniteWith(o_top_nut)
    o_top_nut.erase()

    o_bot_noz = CYLINDER(s, R=r_sample, H=L_NOZ + 6.0, O=0.0).translate((0.0, 0.0, -(half_h + L_NOZ)))
    o_main.uniteWith(o_bot_noz)
    o_bot_noz.erase()

    o_bot_nut = CYLINDER(s, R=r_sample * 1.55, H=max(14.0, L_NOZ * 0.28), O=0.0).translate((0.0, 0.0, -(half_h + L_NOZ * 0.72)))
    o_main.uniteWith(o_bot_nut)
    o_bot_nut.erase()

    # 3. 上下冷却水侧接口 (朝 +X)
    r_cw = max(13.0, D_SHELL * 0.13)
    l_cw = max(45.0, D_SHELL * 0.48)
    for sz in (-1.0, 1.0):
        zc = sz * (half_h - c_cap - r_cw * 2.2)
        o_cw = CYLINDER(s, R=r_cw, H=l_cw + r_shell * 0.4, O=0.0).rotateY(90.0).translate((r_shell * 0.6, 0.0, zc))
        o_main.uniteWith(o_cw)
        o_cw.erase()

        o_cw_fl = CYLINDER(s, R=r_cw * 1.55, H=max(12.0, r_cw * 0.8), O=0.0).rotateY(90.0).translate((r_shell + l_cw - max(12.0, r_cw * 0.8), 0.0, zc))
        o_main.uniteWith(o_cw_fl)
        o_cw_fl.erase()

    # 4. 后置安装背板与双连接支耳 (位于 -Y 侧)
    t_plate = 10.0
    y_plate = -(r_cap + 18.0)
    o_plate = BOX(s, L=t_plate, W=H_PLATE, H=W_PLATE).translate((0.0, y_plate, 0.0))
    o_main.uniteWith(o_plate)
    o_plate.erase()

    for sz in (-1.0, 1.0):
        zb = sz * (half_h * 0.58)
        o_brk = BOX(s, L=abs(y_plate) - r_shell * 0.65, W=max(24.0, D_SHELL * 0.22), H=r_shell * 1.15).translate((0.0, (y_plate - r_shell * 0.65) / 2.0, zb))
        o_main.uniteWith(o_brk)
        o_brk.erase()

    z_p1 = half_h + L_NOZ
    z_p2 = -(half_h + L_NOZ)
    s.setPoint((0.0, 0.0, z_p1), (0.0, 0.0, 1.0))
    s.setPoint((0.0, 0.0, z_p2), (0.0, 0.0, -1.0))
    s.setLinearDimension('H_SHELL', (0.0, 0.0, -half_h), (0.0, 0.0, half_h))
    s.setLinearDimension('W_PLATE', (-W_PLATE / 2.0, y_plate, 0.0), (W_PLATE / 2.0, y_plate, 0.0))
