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
          TooltipShort=u"法兰式电磁流量计 (JB/T 9248)",
          TooltipLong=u"化工法兰式一体型电磁流量计，含双端法兰、饱满励磁线圈鼓形外壳、加粗过渡颈及顶装方形液晶转换器表头",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"电磁流量计面距、线圈外径及顶表头高度")
@param(D=LENGTH, TooltipShort=u"管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面距 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰厚度 (mm)")
@param(D_COIL=LENGTH, TooltipShort=u"线圈壳径", TooltipLong=u"中间励磁线圈鼓形外壳外径 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"总高度", TooltipLong=u"管道中心至转换器表头顶面高度 (mm)", Ask4Dist=True)
def INST_FLOW_MAG(
    s,
    D=114.3,
    L_FACE=250.0,
    D_FL=220.0,
    C_FL=20.0,
    D_COIL=182.0,
    H_TOP=310.0,
    ID=u"INST_FLOW_MAG",
    **kw
):
    u"""法兰式电磁流量计 (Port 1: X=-L/2, Port 2: X=+L/2, 方形转换器在 +Z，液晶面朝 -Y)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 55.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    D_COIL = max(D + 36.0, float(D_COIL))
    H_TOP = float(H_TOP)
    if H_TOP < 1.0:
        H_TOP = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_coil = D_COIL / 2.0

    # 1. 双端法兰与内测量管
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()
    o_tube = CYLINDER(s, R=r_pipe * 1.12, H=L_FACE - 2.0 * C_FL + 8.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 4.0), 0.0, 0.0))
    o_main.uniteWith(o_tube)
    o_tube.erase()

    # 2. 中央励磁线圈鼓形外壳 + 左右封板端环
    l_coil = max(90.0, (L_FACE - 2.0 * C_FL) * 0.68)
    o_coil = CYLINDER(s, R=r_coil, H=l_coil, O=0.0).rotateY(90.0).translate((-l_coil / 2.0, 0.0, 0.0))
    o_main.uniteWith(o_coil)
    o_coil.erase()
    for sx in (-1.0, 1.0):
        o_ring = CYLINDER(s, R=r_coil + 5.0, H=12.0, O=0.0).rotateY(90.0).translate((sx * (l_coil / 2.0 - 6.0) - 6.0, 0.0, 0.0))
        o_main.uniteWith(o_ring)
        o_ring.erase()

    # 3. 顶装传感器过渡颈 + 方形液晶转换器表头
    h_head = 122.0
    w_head = 136.0
    d_head = 124.0
    z_head_bot = H_TOP - h_head
    o_neck = CYLINDER(s, R=28.0, H=max(40.0, z_head_bot - r_coil + 28.0), O=0.0).translate((0.0, 0.0, r_coil - 18.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()
    o_head = CORNERBOX(s, L=w_head, W=d_head, H=h_head).translate((-w_head / 2.0, -d_head / 2.0, z_head_bot))
    o_main.uniteWith(o_head)
    o_head.erase()
    # 前液晶显示框 (-Y) + 底部双格兰头
    o_bezel = CORNERBOX(s, L=w_head - 18.0, W=16.0, H=h_head - 22.0).translate((-(w_head - 18.0) / 2.0, -d_head / 2.0 - 12.0, z_head_bot + 11.0))
    o_main.uniteWith(o_bezel)
    o_bezel.erase()
    for sx in (-34.0, 34.0):
        o_gl = CYLINDER(s, R=12.0, H=26.0, O=0.0).translate((sx, 14.0, z_head_bot - 22.0))
        o_main.uniteWith(o_gl)
        o_gl.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_TOP', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
