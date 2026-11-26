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

@activate(Group="Instrument",
          TooltipShort=u"鹤管装车臂 (HG/T 21608)",
          TooltipLong=u"顶部装车用化工鹤管装车臂，含底立柱安装法兰、旋转接头组、弹簧平衡缸、水平外臂、外端旋转弯头及带密闭锥的竖直垂管",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"鹤管装车臂管径、底法兰、立柱高、外臂长及垂管长")
@param(D=LENGTH, TooltipShort=u"鹤管公称外径", TooltipLong=u"装车臂主管外径 D (mm)")
@param(D_FL=LENGTH, TooltipShort=u"底法兰外径", TooltipLong=u"立柱底部安装法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"底法兰厚度", TooltipLong=u"立柱底部安装法兰厚度 (mm)")
@param(H_RISER=LENGTH, TooltipShort=u"立柱高度", TooltipLong=u"底法兰面至水平外臂中心线高度 H (mm)", Ask4Dist=True)
@param(L_ARM=LENGTH, TooltipShort=u"水平臂长", TooltipLong=u"立柱中心至垂管中心水平臂总长 L (mm)", Ask4Dist=True)
@param(L_DROP=LENGTH, TooltipShort=u"垂管长度", TooltipLong=u"水平臂中心线至垂管底端总长 (mm)")
def SPEC_LOADING_ARM(
    s,
    D=114.3,
    D_FL=220.0,
    C_FL=20.0,
    H_RISER=1800.0,
    L_ARM=1600.0,
    L_DROP=1200.0,
    ID=u"SPEC_LOADING_ARM",
    **kw
):
    u"""鹤管装车臂 (底法兰面在 Z=0, Port 1 朝向 -Z, 水平外臂沿 +X, 垂管向下沿 -Z)。"""
    D = max(50.0, float(D))
    D_FL = max(D + 50.0, float(D_FL))
    C_FL = max(16.0, float(C_FL))
    H_RISER = float(H_RISER)
    if H_RISER < 1.0:
        H_RISER = 1.0
    L_ARM = float(L_ARM)
    if L_ARM < 1.0:
        L_ARM = 1.0
    L_DROP = max(500.0, min(H_RISER - 150.0, float(L_DROP)))

    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_swivel = r_pipe * 1.48

    # 1. 底立柱法兰与竖直立柱管
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0)
    o_riser = CYLINDER(s, R=r_pipe, H=H_RISER - C_FL + 8.0, O=0.0).translate((0.0, 0.0, C_FL - 4.0))
    o_main.uniteWith(o_riser)
    o_riser.erase()

    # 2. 立柱顶旋转接头组件 (立式旋转套 + 弯头球体 + 水平旋转套)
    o_sw1 = CYLINDER(s, R=r_swivel, H=D * 1.15, O=0.0).translate((0.0, 0.0, H_RISER - D * 1.4))
    o_main.uniteWith(o_sw1)
    o_sw1.erase()

    o_el1 = SPHERE(s, R=r_pipe * 1.32).translate((0.0, 0.0, H_RISER))
    o_main.uniteWith(o_el1)
    o_el1.erase()

    o_sw2 = CYLINDER(s, R=r_swivel, H=D * 1.05, O=0.0).rotateY(90.0).translate((D * 0.45, 0.0, H_RISER))
    o_main.uniteWith(o_sw2)
    o_sw2.erase()

    # 3. 水平内/外臂与中段旋转接头环
    o_arm = CYLINDER(s, R=r_pipe, H=L_ARM + 8.0, O=0.0).rotateY(90.0).translate((-4.0, 0.0, H_RISER))
    o_main.uniteWith(o_arm)
    o_arm.erase()

    o_sw_mid = CYLINDER(s, R=r_swivel * 0.96, H=D * 1.10, O=0.0).rotateY(90.0).translate((L_ARM * 0.46, 0.0, H_RISER))
    o_main.uniteWith(o_sw_mid)
    o_sw_mid.erase()

    # 弹簧平衡缸 (斜撑连接立柱上部与水平内臂)
    x_cb0, z_cb0 = 0.0, H_RISER - D * 2.8
    x_cb1, z_cb1 = L_ARM * 0.34, H_RISER
    l_cb = math.hypot(x_cb1 - x_cb0, z_cb1 - z_cb0)
    ang_cb = math.degrees(math.atan2(x_cb1 - x_cb0, z_cb1 - z_cb0))
    o_cb = CYLINDER(s, R=r_pipe * 0.62, H=l_cb, O=0.0).rotateY(ang_cb).translate((x_cb0, 0.0, z_cb0))
    o_main.uniteWith(o_cb)
    o_cb.erase()

    # 4. 外端旋转接头弯头与竖直垂管
    o_el2 = SPHERE(s, R=r_pipe * 1.32).translate((L_ARM, 0.0, H_RISER))
    o_main.uniteWith(o_el2)
    o_el2.erase()

    o_sw3 = CYLINDER(s, R=r_swivel, H=D * 1.10, O=0.0).translate((L_ARM, 0.0, H_RISER - D * 1.55))
    o_main.uniteWith(o_sw3)
    o_sw3.erase()

    z_drop_bot = H_RISER - L_DROP
    o_drop = CYLINDER(s, R=r_pipe * 0.88, H=L_DROP + 4.0, O=0.0).translate((L_ARM, 0.0, z_drop_bot))
    o_main.uniteWith(o_drop)
    o_drop.erase()

    # 垂管中部密闭防溅锥与底端导流罩
    o_splash = CONE(s, R1=r_pipe * 2.15, R2=r_pipe * 1.05, H=D * 1.10, E=0.0).translate((L_ARM, 0.0, z_drop_bot + L_DROP * 0.42))
    o_main.uniteWith(o_splash)
    o_splash.erase()

    o_tip = CYLINDER(s, R=r_pipe * 1.08, H=max(32.0, D * 0.32), O=0.0).translate((L_ARM, 0.0, z_drop_bot))
    o_main.uniteWith(o_tip)
    o_tip.erase()

    # 垂管操作扶手
    o_grip = BOX(s, L=18.0, W=D * 1.4, H=D * 1.1).translate((L_ARM + r_pipe * 1.3, 0.0, z_drop_bot + L_DROP * 0.65))
    o_main.uniteWith(o_grip)
    o_grip.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('H_RISER', (0.0, 0.0, 0.0), (0.0, 0.0, H_RISER))
    s.setLinearDimension('L_ARM', (0.0, 0.0, H_RISER), (L_ARM, 0.0, H_RISER))
