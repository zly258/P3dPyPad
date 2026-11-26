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
          TooltipShort=u"弯头假管支腿/耳轴支座 (HG/T 21629 F1)",
          TooltipLong=u"弯头假管支腿/耳轴支座，含顶部管弧口假管、补强马鞍颈圈、底部四向加劲肋与重型锚固底板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"弯头假管支腿主要几何参数")
@param(D=LENGTH, TooltipShort=u"主管外径", TooltipLong=u"被支撑弯头/主管外径 D (mm)")
@param(D_TRUN=LENGTH, TooltipShort=u"假管外径", TooltipLong=u"竖直假管支腿外径 (mm)")
@param(H1=LENGTH, TooltipShort=u"支腿高度", TooltipLong=u"主管中心至底板下表面总高 H1 (mm)", Ask4Dist=True)
@param(B1=LENGTH, TooltipShort=u"底板边长", TooltipLong=u"方形底板边长 B1 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"底板厚度", TooltipLong=u"底板与加劲肋厚度 (mm)")
def SUPPORT_TRUNNION_ELBOW(
    s,
    D=219.1,
    D_TRUN=114.3,
    H1=400.0,
    B1=220.0,
    T_PLT=14.0,
    ID=u"SUPPORT_TRUNNION_ELBOW",
    **kw
):
    u"""弯头假管支腿/耳轴支座 (原点在主管中心线, 管道沿 X 轴, 假管沿 -Z 向下)。"""
    D = max(60.3, float(D))
    r_p = D / 2.0
    D_TRUN = max(32.0, min(D * 0.82, float(D_TRUN)))
    r_t = D_TRUN / 2.0
    t_wall = max(6.0, D_TRUN * 0.08)
    H1 = float(H1)
    if H1 < 1.0:
        H1 = 1.0
    B1 = float(B1)
    if B1 < 1.0:
        B1 = 1.0
    T_PLT = max(10.0, float(T_PLT))

    z_bot = -H1
    z_base_top = z_bot + T_PLT

    # 1. 干净方形底板
    o_main = CORNERBOX(s, L=B1, W=B1, H=T_PLT).translate((-B1 / 2.0, -B1 / 2.0, z_bot))

    # 2. 竖直假管（顶部深入主管半径以内后按主管外径做马鞍弧口裁切）
    trun_h = H1 - T_PLT + 1.0
    o_trun = CYLINDER(s, R=r_t, H=trun_h, O=max(0.0, r_t - t_wall)).translate((0.0, 0.0, z_base_top - 1.0))
    o_pcut = CYLINDER(s, R=r_p, H=D * 2.5, O=0.0).rotateY(90.0).translate((-D * 1.25, 0.0, 0.0))
    o_trun.subtractFrom(o_pcut)
    o_pcut.erase()
    o_main.uniteWith(o_trun)
    o_trun.erase()

    # 3. 顶部补强马鞍颈圈（与假管同轴加厚并同步做主管弧口裁切，马鞍弧口干净利落）
    r_pad = r_t + max(12.0, T_PLT * 0.9)
    z_neck_bot = -(r_p + max(28.0, T_PLT * 2.2))
    o_collar = CYLINDER(s, R=r_pad, H=(-z_neck_bot), O=max(0.0, r_t - t_wall)).translate((0.0, 0.0, z_neck_bot))
    o_pcut2 = CYLINDER(s, R=r_p, H=D * 2.5, O=0.0).rotateY(90.0).translate((-D * 1.25, 0.0, 0.0))
    o_collar.subtractFrom(o_pcut2)
    o_pcut2.erase()
    o_main.uniteWith(o_collar)
    o_collar.erase()

    # 4. 底部 4 块正交加劲肋板（将假管与底板刚性连接）
    gus_h = max(45.0, min(95.0, (H1 - r_p) * 0.32))
    gus_l = (B1 / 2.0 - r_t) * 0.85
    gus_t = max(8.0, T_PLT * 0.75)
    for ang_deg in (0.0, 90.0, 180.0, 270.0):
        o_gus = CORNERBOX(s, L=gus_l + 4.0, W=gus_t, H=gus_h).translate(
            (r_t - 4.0, -gus_t / 2.0, z_base_top - 1.0)).rotateZ(ang_deg)
        o_main.uniteWith(o_gus)
        o_gus.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H1', (0.0, 0.0, 0.0), (0.0, 0.0, z_bot))
    s.setLinearDimension('B1', (-B1 / 2.0, 0.0, z_bot), (B1 / 2.0, 0.0, z_bot))
