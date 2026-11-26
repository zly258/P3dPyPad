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
          TooltipShort=u"角钢三角形牛腿支架",
          TooltipLong=u"角钢三角形牛腿支架，含立墙背板、水平角钢横臂、斜撑角钢、节点板与管底垫块",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"角钢三角形牛腿支架主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支撑管道外径 D (mm)")
@param(L_ARM=LENGTH, TooltipShort=u"悬臂长度", TooltipLong=u"立墙背板至管道中心水平距 (mm)", Ask4Dist=True)
@param(H_BRK=LENGTH, TooltipShort=u"牛腿高度", TooltipLong=u"三角形牛腿竖向高度 (mm)", Ask4Dist=True)
@param(ANG_W=LENGTH, TooltipShort=u"角钢肢宽", TooltipLong=u"等边角钢肢宽 (mm)")
@param(ANG_T=LENGTH, TooltipShort=u"角钢厚度", TooltipLong=u"等边角钢肢厚 (mm)")
@param(T_PLT=LENGTH, TooltipShort=u"背板厚度", TooltipLong=u"立墙锚固背板厚度 (mm)")
def SUPPORT_BRACKET_KNEE(
    s,
    D=114.3,
    L_ARM=380.0,
    H_BRK=340.0,
    ANG_W=63.0,
    ANG_T=6.0,
    T_PLT=12.0,
    ID=u"SUPPORT_BRACKET_KNEE",
    **kw
):
    u"""角钢三角形牛腿支架 (原点在管道中心线, 管道沿 X 轴, 立墙在 -Y 侧)。"""
    D = max(25.0, float(D))
    r_p = D / 2.0
    L_ARM = float(L_ARM)
    if L_ARM < 1.0:
        L_ARM = 1.0
    H_BRK = float(H_BRK)
    if H_BRK < 1.0:
        H_BRK = 1.0
    ANG_W = max(40.0, float(ANG_W))
    ANG_T = max(4.0, float(ANG_T))
    T_PLT = max(8.0, float(T_PLT))

    pad_t = max(8.0, T_PLT * 0.7)
    z_arm_top = -r_p - pad_t
    z_arm_mid = z_arm_top - ANG_W / 2.0
    y_wall = -L_ARM
    y_tip = r_p + 60.0
    arm_len = y_tip - (y_wall + T_PLT - 2.0)

    # 1. 整体立墙背板（干净平板）
    plt_w = max(140.0, ANG_W * 2.4)
    plt_h = H_BRK + ANG_W * 1.4
    z_plt_bot = z_arm_top - H_BRK - ANG_W * 0.7
    o_main = CORNERBOX(s, L=plt_w, W=T_PLT, H=plt_h).translate((-plt_w / 2.0, y_wall, z_plt_bot))

    # 2. 水平角钢横臂（沿 +Y 方向延伸）
    o_arm = CSTE_L(s, W=ANG_W, H=ANG_W, T=ANG_T, L=arm_len).rotateX(-90.0).translate(
        (0.0, y_wall + T_PLT - 2.0, z_arm_mid))
    o_main.uniteWith(o_arm)
    o_arm.erase()

    # 3. 斜撑角钢（构成清晰三角形牛腿）
    y_b_top = y_tip - ANG_W * 0.9
    z_b_top = z_arm_top - ANG_W + 6.0
    y_b_bot = y_wall + T_PLT - 2.0
    z_b_bot = z_arm_top - H_BRK
    dy = y_b_top - y_b_bot
    dz = z_b_top - z_b_bot
    brace_len = math.sqrt(dy * dy + dz * dz) + 16.0
    # +Z 绕 X 旋 -theta 指向 (0, +sin(theta), +cos(theta))
    theta_deg = math.degrees(math.atan2(dy, dz))
    o_brace = CSTE_L(s, W=ANG_W, H=ANG_W, T=ANG_T, L=brace_len).rotateX(-theta_deg).translate(
        (0.0, y_b_bot - 4.0, z_b_bot - 4.0))
    # 裁除伸入墙背板后方与横臂上方的余料
    o_cwall = CORNERBOX(s, L=plt_w * 2.0, W=200.0, H=plt_h * 2.0).translate(
        (-plt_w, y_wall - 200.0 + 1.0, z_plt_bot - 100.0))
    o_brace.subtractFrom(o_cwall)
    o_cwall.erase()
    o_ctop = CORNERBOX(s, L=plt_w * 2.0, W=arm_len + 200.0, H=200.0).translate(
        (-plt_w, y_wall - 50.0, z_arm_top - ANG_T))
    o_brace.subtractFrom(o_ctop)
    o_ctop.erase()
    o_main.uniteWith(o_brace)
    o_brace.erase()

    # 4. 管底垫块（带弧口防滑垫板）
    pad_l = max(80.0, ANG_W * 1.4)
    pad_w = max(80.0, D * 0.75)
    o_pad = CORNERBOX(s, L=pad_l, W=pad_w, H=pad_t + r_p * 0.22).translate(
        (-pad_l / 2.0, -pad_w / 2.0, z_arm_top - 1.0))
    o_pcut = CYLINDER(s, R=r_p, H=pad_l + 40.0, O=0.0).rotateY(90.0).translate((-(pad_l / 2.0 + 20.0), 0.0, 0.0))
    o_pad.subtractFrom(o_pcut)
    o_pcut.erase()
    o_main.uniteWith(o_pad)
    o_pad.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_ARM', (0.0, y_wall, z_arm_top), (0.0, 0.0, z_arm_top))
    s.setLinearDimension('H_BRK', (0.0, y_wall, z_arm_top), (0.0, y_wall, z_arm_top - H_BRK))
