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
          TooltipShort=u"放空消声器",
          TooltipLong=u"化工安全阀/放空管用立式放空消声器，含底部单法兰、锥形扩口、大直径消声筒体与顶部防雨帽",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"放空消声器筒径、总高及法兰尺寸参数")
@param(D=LENGTH, TooltipShort=u"入口管外径", TooltipLong=u"底部入口连接管外径 D (mm)")
@param(D_FL=LENGTH, TooltipShort=u"底法兰外径", TooltipLong=u"底部安装法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"底法兰厚度", TooltipLong=u"底部安装法兰厚度 (mm)")
@param(D_BODY=LENGTH, TooltipShort=u"消声筒外径", TooltipLong=u"大直径消声筒体外径 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"消声器总高", TooltipLong=u"底法兰面至防雨帽顶端总高 H (mm)", Ask4Dist=True)
@param(H_BODY=LENGTH, TooltipShort=u"筒体高度", TooltipLong=u"大直径消声直筒段高度 (mm)")
def SPEC_SILENCER_VENT(
    s,
    D=114.3,
    D_FL=220.0,
    C_FL=20.0,
    D_BODY=325.0,
    H_TOTAL=1100.0,
    H_BODY=620.0,
    ID=u"SPEC_SILENCER_VENT",
    **kw
):
    u"""放空消声器 (底法兰面在 Z=0, Port 1 在原点朝向 -Z, 筒体与防雨帽沿 +Z)。"""
    D = max(25.0, float(D))
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_BODY = float(D_BODY)
    if D_BODY < 1.0:
        D_BODY = 1.0
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0
    H_BODY = max(D_BODY * 0.8, min(H_TOTAL * 0.68, float(H_BODY)))

    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_body = D_BODY / 2.0

    # 1. 底部单法兰与入口短管
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0)
    h_neck = max(45.0, H_TOTAL * 0.08)
    o_neck = CYLINDER(s, R=r_pipe * 1.05, H=h_neck + 6.0, O=0.0).translate((0.0, 0.0, C_FL - 3.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    # 2. 锥形扩口过渡段
    z_cone_bot = C_FL + h_neck
    h_cone = max(70.0, H_TOTAL * 0.14)
    o_cone = CONE(s, R1=r_pipe * 1.05, R2=r_body, H=h_cone + 4.0, E=0.0).translate((0.0, 0.0, z_cone_bot - 2.0))
    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 3. 大直径消声筒体与上下加强环
    z_body_bot = z_cone_bot + h_cone
    o_body = CYLINDER(s, R=r_body, H=H_BODY + 4.0, O=0.0).translate((0.0, 0.0, z_body_bot - 2.0))
    o_main.uniteWith(o_body)
    o_body.erase()

    ring_h = max(16.0, H_BODY * 0.03)
    for z_ring in (z_body_bot + 10.0, z_body_bot + H_BODY - ring_h - 10.0):
        o_ring = CYLINDER(s, R=r_body + max(10.0, r_body * 0.07), H=ring_h, O=0.0).translate((0.0, 0.0, z_ring))
        o_main.uniteWith(o_ring)
        o_ring.erase()

    # 4. 顶部防雨帽与 4 根支撑立柱
    z_body_top = z_body_bot + H_BODY
    rem_h = max(60.0, H_TOTAL - z_body_top)
    cap_h = rem_h * 0.52
    z_cap_bot = H_TOTAL - cap_h
    post_h = z_cap_bot - z_body_top + 16.0
    post_r = max(8.0, r_body * 0.06)
    post_ring = r_body * 0.78
    for k in range(4):
        ang = (k * 90.0 + 45.0) * 3.14159265 / 180.0
        px = post_ring * cos(ang)
        py = post_ring * sin(ang)
        o_post = CYLINDER(s, R=post_r, H=post_h, O=0.0).translate((px, py, z_body_top - 6.0))
        o_main.uniteWith(o_post)
        o_post.erase()

    o_cap = CONE(s, R1=r_body * 1.18, R2=r_body * 0.12, H=cap_h, E=0.0).translate((0.0, 0.0, z_cap_bot))
    o_main.uniteWith(o_cap)
    o_cap.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
    s.setLinearDimension('D_BODY', (-r_body, 0.0, z_body_bot + H_BODY / 2.0), (r_body, 0.0, z_body_bot + H_BODY / 2.0))
