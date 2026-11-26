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

@activate(Group="Support",
          TooltipShort=u"U型螺栓管卡 (HG/T 21629 J1)",
          TooltipLong=u"HG/T 21629-2021 J1 U型螺栓管卡，含半圆弧弯杆、双竖直螺杆、双螺母垫圈与底部垫板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"U型螺栓管卡主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被卡紧管道外径 D (mm)")
@param(BOLT_D=LENGTH, TooltipShort=u"圆钢直径", TooltipLong=u"U型螺栓圆钢直径 (mm)")
@param(L_LEG=LENGTH, TooltipShort=u"直腿长度", TooltipLong=u"管中心线以下直腿总长 (mm)", Ask4Dist=True)
@param(PLT_L=LENGTH, TooltipShort=u"垫板长度", TooltipLong=u"底部承压垫板沿管轴向长度 (mm)")
@param(PLT_B=LENGTH, TooltipShort=u"垫板宽度", TooltipLong=u"底部承压垫板横向宽度 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"垫板厚度", TooltipLong=u"底部承压垫板厚度 (mm)")
def SUPPORT_UBOLT_HGT21629(
    s,
    D=114.3,
    BOLT_D=12.0,
    L_LEG=100.0,
    PLT_L=80.0,
    PLT_B=180.0,
    T_PLT=10.0,
    ID=u"SUPPORT_UBOLT_HGT21629",
    **kw
):
    u"""U型螺栓管卡 (原点在管道中心线, 管道沿 X 轴, 垫板在管底 -Z)。"""
    D = max(21.3, float(D))
    r_p = D / 2.0
    BOLT_D = max(8.0, float(BOLT_D))
    r_rod = BOLT_D / 2.0
    r_bend = r_p + r_rod
    T_PLT = max(6.0, float(T_PLT))
    L_LEG = float(L_LEG)
    if L_LEG < 1.0:
        L_LEG = 1.0
    PLT_L = max(BOLT_D * 4.0, float(PLT_L))
    PLT_B = float(PLT_B)
    if PLT_B < 1.0:
        PLT_B = 1.0

    z_plt_top = -r_p
    z_plt_bot = z_plt_top - T_PLT

    # 1. 底部承压垫板（干净平板）
    o_main = CORNERBOX(s, L=PLT_L, W=PLT_B, H=T_PLT).translate((-PLT_L / 2.0, -PLT_B / 2.0, z_plt_bot))

    # 2. 半圆弧 U 型弯杆（位于 YZ 平面，覆盖管道上半圆 z >= 0）
    # TORUS 默认在 XY 平面，绕 Y 旋 90° 后进入 YZ 平面
    o_arc = TORUS(s, R1=r_bend, R2=r_rod).rotateY(90.0)
    o_cut_bot = CORNERBOX(s, L=BOLT_D * 4.0, W=r_bend * 3.0, H=r_bend * 2.0).translate(
        (-BOLT_D * 2.0, -r_bend * 1.5, -r_bend * 2.0))
    o_arc.subtractFrom(o_cut_bot)
    o_cut_bot.erase()

    # 3. 双竖直螺杆直腿 + 垫板上下紧固螺母
    for sy in (-1.0, 1.0):
        ly = sy * r_bend
        o_leg = CYLINDER(s, R=r_rod, H=L_LEG + 1.0, O=0.0).translate((0.0, ly, -L_LEG))
        o_arc.uniteWith(o_leg)
        o_leg.erase()

        # 垫板上方止退螺母 + 垫板下方双紧固螺母
        nut_r = BOLT_D * 0.90
        nut_h = BOLT_D * 0.80
        for nz in (z_plt_top - 0.5, z_plt_bot - nut_h + 0.5, z_plt_bot - nut_h * 2.05 + 0.5):
            o_nut = CYLINDER(s, R=nut_r, H=nut_h, O=0.0).translate((0.0, ly, nz))
            o_main.uniteWith(o_nut)
            o_nut.erase()

    o_main.uniteWith(o_arc)
    o_arc.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_LEG', (0.0, r_bend, 0.0), (0.0, r_bend, -L_LEG))
    s.setLinearDimension('PLT_B', (0.0, -PLT_B / 2.0, z_plt_bot), (0.0, PLT_B / 2.0, z_plt_bot))
