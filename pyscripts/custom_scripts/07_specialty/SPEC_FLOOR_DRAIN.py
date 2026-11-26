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

@activate(Group="Cap",
          TooltipShort=u"防爆工业地漏 (HG/T 20570)",
          TooltipLong=u"化工防爆工业水封地漏，含方形带格栅顶盘、锥形集水漏斗腔、圆柱防爆水封筒及底部直出排水管",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"工业地漏顶盘宽、水封腔径、总深及排水管外径")
@param(D=LENGTH, TooltipShort=u"底排水管外径", TooltipLong=u"底部排水出口管外径 D (mm)")
@param(W_TOP=LENGTH, TooltipShort=u"顶格栅盘宽", TooltipLong=u"方形顶格栅面板边长 W (mm)", Ask4Dist=True)
@param(H_TOTAL=LENGTH, TooltipShort=u"地漏总深", TooltipLong=u"地坪顶面至底部排水口总深度 H (mm)", Ask4Dist=True)
@param(D_TRAP=LENGTH, TooltipShort=u"水封腔外径", TooltipLong=u"防爆水封圆柱腔外径 (mm)")
def SPEC_FLOOR_DRAIN(
    s,
    D=114.3,
    W_TOP=250.0,
    H_TOTAL=280.0,
    D_TRAP=180.0,
    ID=u"SPEC_FLOOR_DRAIN",
    **kw
):
    u"""防爆工业地漏 (地坪面在 Z=0, 整体向下延伸至 -H_TOTAL, Port 1 在底部朝 -Z)。"""
    D = max(50.0, float(D))
    D_TRAP = max(D * 1.35, float(D_TRAP))
    W_TOP = float(W_TOP)
    if W_TOP < 1.0:
        W_TOP = 1.0
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0

    r_out = D / 2.0
    r_trap = D_TRAP / 2.0
    t_top = max(16.0, H_TOTAL * 0.065)

    # 1. 方形顶格栅盘体与表面格栅凸条
    o_main = BOX(s, L=W_TOP, W=t_top, H=W_TOP).translate((0.0, 0.0, -t_top / 2.0))

    n_bars = 5
    span = W_TOP * 0.74
    for i in range(n_bars):
        yb = -span / 2.0 + span * float(i) / float(n_bars - 1)
        o_bar = BOX(s, L=max(8.0, W_TOP * 0.045), W=6.0, H=W_TOP * 0.80).translate((0.0, yb, 2.0))
        o_main.uniteWith(o_bar)
        o_bar.erase()

    # 2. 锥形集水漏斗腔
    z_fun_bot = -H_TOTAL * 0.40
    o_funnel = CONE(s, R1=r_trap, R2=W_TOP * 0.44, H=(-z_fun_bot) - t_top + 6.0, E=0.0).translate((0.0, 0.0, z_fun_bot))
    o_main.uniteWith(o_funnel)
    o_funnel.erase()

    # 3. 防爆圆柱水封腔体与中部加强环
    z_trap_bot = -H_TOTAL * 0.74
    o_trap = CYLINDER(s, R=r_trap, H=z_fun_bot - z_trap_bot + 8.0, O=0.0).translate((0.0, 0.0, z_trap_bot - 2.0))
    o_main.uniteWith(o_trap)
    o_trap.erase()

    o_ring = CYLINDER(s, R=r_trap * 1.08, H=max(14.0, H_TOTAL * 0.055), O=0.0).translate((0.0, 0.0, (z_fun_bot + z_trap_bot) / 2.0 - 7.0))
    o_main.uniteWith(o_ring)
    o_ring.erase()

    # 4. 底部缩径锥与排水直管 (Port 1 在 -H_TOTAL)
    z_red_bot = -H_TOTAL * 0.84
    o_red = CONE(s, R1=r_out, R2=r_trap, H=z_trap_bot - z_red_bot + 4.0, E=0.0).translate((0.0, 0.0, z_red_bot))
    o_main.uniteWith(o_red)
    o_red.erase()

    o_out = CYLINDER(s, R=r_out, H=z_red_bot - (-H_TOTAL) + 6.0, O=0.0).translate((0.0, 0.0, -H_TOTAL))
    o_main.uniteWith(o_out)
    o_out.erase()

    s.setPoint((0.0, 0.0, -H_TOTAL), (0.0, 0.0, -1.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, -H_TOTAL))
    s.setLinearDimension('W_TOP', (-W_TOP / 2.0, 0.0, 0.0), (W_TOP / 2.0, 0.0, 0.0))
