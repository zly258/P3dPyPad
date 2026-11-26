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
          TooltipShort=u"快开盲板 (Quick Opening Closure)",
          TooltipLong=u"清管器收发筒/过滤器快开盲板总成，含对焊筒节、锁紧卡箍环、弧形快开盲盖与侧向单臂铰链开启机构",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"快开盲板主要几何尺寸参数")
@param(D=LENGTH, TooltipShort=u"配用管外径", TooltipLong=u"对焊筒节管道外径 (mm)")
@param(B_ID=LENGTH, TooltipShort=u"筒节内径", TooltipLong=u"对焊筒节内孔直径 (mm)")
@param(D_CLAMP=LENGTH, TooltipShort=u"卡箍环外径", TooltipLong=u"锁紧卡箍环外径 (mm)")
@param(W_CLAMP=LENGTH, TooltipShort=u"卡箍环宽度", TooltipLong=u"锁紧卡箍环轴向宽度 (mm)")
@param(L_HUB=LENGTH, TooltipShort=u"筒节长度", TooltipLong=u"对焊筒节轴向长度 (mm)")
@param(L_TOT=LENGTH, TooltipShort=u"盲板总长", TooltipLong=u"快开盲板总轴向长度 (mm)", Ask4Dist=True)
def FLANGE_QUICK_CLOSURE(
    s,
    D=323.9,
    B_ID=303.2,
    D_CLAMP=430.0,
    W_CLAMP=76.0,
    L_HUB=160.0,
    L_TOT=330.0,
    ID=u"FLANGE_QUICK_CLOSURE",
    **kw
):
    u"""快开盲板 Quick Opening Closure (Port 1 在 X=0 筒节对焊端, +Y 侧带铰链开启臂)。"""
    D = max(100.0, float(D))
    B_ID = max(60.0, min(D - 8.0, float(B_ID)))
    D_CLAMP = max(D + 50.0, float(D_CLAMP))
    W_CLAMP = max(36.0, float(W_CLAMP))
    L_HUB = max(80.0, float(L_HUB))
    L_TOT = float(L_TOT)
    if L_TOT < 1.0:
        L_TOT = 1.0

    r_pipe = D / 2.0
    r_in = B_ID / 2.0
    r_clamp = D_CLAMP / 2.0
    r_neck = r_pipe + (r_clamp - r_pipe) * 0.45

    # 1. 对焊筒节 + 加厚过渡颈 (X: 0 -> L_HUB)
    lip_h = L_HUB * 0.55
    cone_h = L_HUB - lip_h
    o_main = CYLINDER(s, R=r_pipe, H=lip_h + 0.5, O=0.0).rotateY(90.0)
    o_cone = CONE(s, R1=r_pipe, R2=r_neck, H=cone_h + 1.0, E=0.0).rotateY(90.0).translate((lip_h - 0.5, 0.0, 0.0))
    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 2. 锁紧卡箍环 (X: L_HUB -> L_HUB + W_CLAMP) + 上下锁紧耳座
    o_clamp = CYLINDER(s, R=r_clamp, H=W_CLAMP + 1.0, O=0.0).rotateY(90.0).translate((L_HUB - 0.5, 0.0, 0.0))
    o_main.uniteWith(o_clamp)
    o_clamp.erase()

    lug_x = L_HUB + W_CLAMP * 0.5
    lug_h = max(24.0, r_clamp * 0.18)
    lug_w = max(28.0, W_CLAMP * 0.52)
    lug_t = max(26.0, r_clamp * 0.16)
    for sign in (1.0, -1.0):
        o_lug = BOX(s, L=lug_t, W=lug_h, H=lug_w).translate((lug_x, 0.0, sign * (r_clamp + lug_h * 0.35)))
        o_main.uniteWith(o_lug)
        o_lug.erase()

    # 3. 弧形快开盲盖 (X: L_HUB + W_CLAMP -> L_TOT，由门颈环 + 阶梯弧形封头组成)
    x_door = L_HUB + W_CLAMP
    door_span = max(40.0, L_TOT - x_door)
    rim_h = min(22.0, door_span * 0.25)
    dome_h = max(24.0, door_span - rim_h)
    r_door = r_neck * 0.96
    o_rim = CYLINDER(s, R=r_door, H=rim_h + 1.0, O=0.0).rotateY(90.0).translate((x_door - 0.5, 0.0, 0.0))
    o_main.uniteWith(o_rim)
    o_rim.erase()

    # 阶梯弧形穹顶盖 (圆台过渡 + 顶部球冠凸台，外形饱满且单实体稳定)
    o_dome1 = CONE(s, R1=r_door, R2=r_door * 0.62, H=dome_h * 0.65 + 0.5, E=0.0).rotateY(90.0).translate((x_door + rim_h - 0.5, 0.0, 0.0))
    o_dome2 = CONE(s, R1=r_door * 0.62, R2=r_door * 0.22, H=dome_h * 0.35 + 0.5, E=0.0).rotateY(90.0).translate((x_door + rim_h + dome_h * 0.65 - 0.5, 0.0, 0.0))
    o_main.uniteWith(o_dome1)
    o_dome1.erase()
    o_main.uniteWith(o_dome2)
    o_dome2.erase()

    # 4. 侧向铰链开启臂 (+Y 侧：筒节支座 + 竖直转轴 + 弯臂连接至门盖中心)
    y_pin = r_clamp + max(28.0, r_pipe * 0.16)
    pin_x = L_HUB - 20.0
    pin_r = max(14.0, D * 0.05)
    pin_h = max(110.0, D * 0.42)

    # 筒节侧向固定支座臂
    o_brk = BOX(s, L=y_pin - r_pipe * 0.6, W=pin_r * 2.2, H=pin_r * 2.4).translate((pin_x, (y_pin + r_pipe * 0.6) * 0.5, 0.0))
    o_main.uniteWith(o_brk)
    o_brk.erase()

    # 竖直铰链转轴柱 (沿 Z)
    o_pin = CYLINDER(s, R=pin_r, H=pin_h, O=0.0).translate((pin_x, y_pin, -pin_h * 0.5))
    o_main.uniteWith(o_pin)
    o_pin.erase()

    # 铰链开启悬臂：沿 +X 伸至门盖前方再折向 Y=0 与盲盖焊接
    arm_x_end = L_TOT - dome_h * 0.20
    arm_t = max(16.0, pin_r * 1.3)
    arm_h = max(24.0, pin_r * 1.8)
    o_arm1 = BOX(s, L=arm_t, W=arm_h, H=arm_x_end - pin_x + arm_t).translate(((pin_x + arm_x_end) * 0.5, y_pin, 0.0))
    o_arm2 = BOX(s, L=y_pin + arm_t * 0.5, W=arm_h, H=arm_t).translate((arm_x_end, y_pin * 0.5, 0.0))
    o_hub_cap = CYLINDER(s, R=max(20.0, r_door * 0.24), H=dome_h * 0.5, O=0.0).rotateY(90.0).translate((arm_x_end - dome_h * 0.4, 0.0, 0.0))
    o_main.uniteWith(o_arm1)
    o_arm1.erase()
    o_main.uniteWith(o_arm2)
    o_arm2.erase()
    o_main.uniteWith(o_hub_cap)
    o_hub_cap.erase()

    # 5. 筒节内孔（仅挖至筒节内腔，盲盖实心封堵）
    o_bore = CYLINDER(s, R=r_in, H=L_HUB + W_CLAMP * 0.5 + 5.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_bore)
    o_bore.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_TOT', (0.0, 0.0, 0.0), (L_TOT, 0.0, 0.0))
