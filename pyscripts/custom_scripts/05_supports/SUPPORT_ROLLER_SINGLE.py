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
          TooltipShort=u"单滚轮滑动支座 (HG/T 21629 E1)",
          TooltipLong=u"单滚轮滑动支座，含重型底板、两侧阶梯轴承座与加强筋、通长钢芯轴及中间双锥腰形钢滚轮",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"单滚轮滑动支座主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支撑管道外径 D (mm)")
@param(H1=LENGTH, TooltipShort=u"支座高度", TooltipLong=u"管底至底板下表面净高 H1 (mm)", Ask4Dist=True)
@param(ROLL_D=LENGTH, TooltipShort=u"滚轮中径", TooltipLong=u"中间滚轮咽部最小外径 (mm)")
@param(ROLL_L=LENGTH, TooltipShort=u"滚轮长度", TooltipLong=u"滚轮轴向长度 (mm)")
@param(L1=LENGTH, TooltipShort=u"底板长度", TooltipLong=u"底板沿管道轴向长度 L1 (mm)")
@param(B1=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"底板横向总宽度 B1 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"底板厚度", TooltipLong=u"支座底板厚度 (mm)")
def SUPPORT_ROLLER_SINGLE(
    s,
    D=219.1,
    H1=140.0,
    ROLL_D=76.0,
    ROLL_L=160.0,
    L1=180.0,
    B1=280.0,
    T_PLT=14.0,
    ID=u"SUPPORT_ROLLER_SINGLE",
    **kw
):
    u"""单滚轮滑动支座 (原点在管道中心线, 管道沿 X 轴, 滚轮轴沿 Y 轴)。"""
    D = max(60.3, float(D))
    r_p = D / 2.0
    ROLL_D = max(45.0, float(ROLL_D))
    r_roll = ROLL_D / 2.0
    ROLL_L = max(80.0, float(ROLL_L))
    H1 = float(H1)
    if H1 < 1.0:
        H1 = 1.0
    L1 = float(L1)
    if L1 < 1.0:
        L1 = 1.0
    B1 = float(B1)
    if B1 < 1.0:
        B1 = 1.0
    T_PLT = max(10.0, float(T_PLT))

    z_bot = -(r_p + H1)
    z_base_top = z_bot + T_PLT
    z_axis = -(r_p + r_roll)
    shaft_r = max(14.0, r_roll * 0.42)

    # 1. 重型底板（干净平板）
    o_main = CORNERBOX(s, L=L1, W=B1, H=T_PLT).translate((-L1 / 2.0, -B1 / 2.0, z_bot))

    # 2. 两侧轴承座立墙（带半圆轴承顶帽与前后加强肋）
    brg_w = max(22.0, (B1 - ROLL_L) * 0.36)
    brg_l = max(shaft_r * 3.8, L1 * 0.52)
    brg_h = max(30.0, z_axis - (z_base_top - 1.0))
    y_brg_in = ROLL_L / 2.0 + 4.0
    for sy in (-1.0, 1.0):
        by = y_brg_in if sy > 0 else -(y_brg_in + brg_w)
        o_ped = CORNERBOX(s, L=brg_l, W=brg_w, H=brg_h).translate((-brg_l / 2.0, by, z_base_top - 1.0))
        o_main.uniteWith(o_ped)
        o_ped.erase()

        # 半圆轴承座顶帽
        o_cap = CYLINDER(s, R=brg_l * 0.48, H=brg_w, O=0.0).rotateX(-90.0).translate((0.0, by, z_axis))
        o_main.uniteWith(o_cap)
        o_cap.erase()

        # 轴承座前后加劲肋
        rib_t = max(10.0, brg_w * 0.45)
        rib_l = (L1 - brg_l) * 0.45
        for sx in (-1.0, 1.0):
            rx = (brg_l / 2.0 - 2.0) if sx > 0 else -(brg_l / 2.0 + rib_l - 2.0)
            o_rib = CORNERBOX(s, L=rib_l, W=rib_t, H=brg_h * 0.72).translate(
                (rx, by + (brg_w - rib_t) / 2.0, z_base_top - 1.0))
            o_main.uniteWith(o_rib)
            o_rib.erase()

    # 3. 贯穿两侧轴承座的钢芯轴（沿 Y 方向）
    shaft_len = (y_brg_in + brg_w + 10.0) * 2.0
    o_shaft = CYLINDER(s, R=shaft_r, H=shaft_len, O=0.0).rotateX(-90.0).translate((0.0, -shaft_len / 2.0, z_axis))
    o_main.uniteWith(o_shaft)
    o_shaft.erase()

    # 4. 中间双锥腰形钢滚轮（中段圆柱 + 两侧锥形扩肩，自然托抱管道底部）
    mid_l = ROLL_L * 0.40
    cone_l = (ROLL_L - mid_l) / 2.0
    r_shoulder = min(r_roll * 1.38, r_roll + 18.0)
    o_rmid = CYLINDER(s, R=r_roll, H=mid_l + 2.0, O=0.0).rotateX(-90.0).translate((0.0, -(mid_l + 2.0) / 2.0, z_axis))
    o_main.uniteWith(o_rmid)
    o_rmid.erase()

    # +Y 侧锥肩：从 mid_l/2 (r_roll) 扩至 ROLL_L/2 (r_shoulder)
    o_c1 = CONE(s, R1=r_roll, R2=r_shoulder, H=cone_l).rotateX(-90.0).translate((0.0, mid_l / 2.0, z_axis))
    o_main.uniteWith(o_c1)
    o_c1.erase()
    # -Y 侧锥肩：从 -ROLL_L/2 (r_shoulder) 缩至 -mid_l/2 (r_roll)
    o_c2 = CONE(s, R1=r_shoulder, R2=r_roll, H=cone_l).rotateX(-90.0).translate((0.0, -ROLL_L / 2.0, z_axis))
    o_main.uniteWith(o_c2)
    o_c2.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H1', (0.0, 0.0, -r_p), (0.0, 0.0, z_bot))
    s.setLinearDimension('B1', (0.0, -B1 / 2.0, z_bot), (0.0, B1 / 2.0, z_bot))
    s.setLinearDimension('L1', (-L1 / 2.0, 0.0, z_bot), (L1 / 2.0, 0.0, z_bot))
