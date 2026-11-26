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
          TooltipShort=u"科里奥利质量流量计 (GB/T 31130)",
          TooltipLong=u"化工高精度科里奥利质量流量计，含双端法兰分流器、饱满下垂梯形/U形双测量管保护壳及顶装一体化双腔变送器表头",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"科里奥利质量流量计面距、下垂壳高及顶表头尺寸")
@param(D=LENGTH, TooltipShort=u"管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"法兰面距", TooltipLong=u"流量计法兰端面距 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(H_DROP=LENGTH, TooltipShort=u"下垂壳深", TooltipLong=u"管道中心至下垂保护壳底面深度 (mm)", Ask4Dist=True)
@param(H_TOP=LENGTH, TooltipShort=u"表头总高", TooltipLong=u"管道中心至顶装表头顶面高度 (mm)")
@param(W_CASE=LENGTH, TooltipShort=u"保护壳宽", TooltipLong=u"双管保护壳横向宽度 (mm)")
def INST_FLOW_CORIOLIS(
    s,
    D=60.3,
    L_FACE=510.0,
    D_FL=165.0,
    C_FL=18.0,
    H_DROP=340.0,
    H_TOP=285.0,
    W_CASE=122.0,
    ID=u"INST_FLOW_CORIOLIS",
    **kw
):
    u"""科里奥利质量流量计 (Port 1: X=-L/2, Port 2: X=+L/2, 下垂U/梯形壳在 -Z, 表头在 +Z)。"""
    D = max(20.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 45.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    H_DROP = float(H_DROP)
    if H_DROP < 1.0:
        H_DROP = 1.0
    H_TOP = max(190.0, float(H_TOP))
    W_CASE = max(72.0, float(W_CASE))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0

    # 1. 双端法兰与分流器横管
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()
    o_bar = CYLINDER(s, R=max(r_pipe * 1.18, 30.0), H=L_FACE - 2.0 * C_FL + 8.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 4.0), 0.0, 0.0))
    o_main.uniteWith(o_bar)
    o_bar.erase()

    # 2. 下垂梯形/U形双测量管保护壳 (-Z)
    l_top = (L_FACE - 2.0 * C_FL) * 0.86
    l_bot = l_top * 0.62
    o_topbox = CORNERBOX(s, L=l_top, W=W_CASE * 0.88, H=max(58.0, D * 1.15)).translate((-l_top / 2.0, -W_CASE * 0.44, -max(46.0, D * 0.85)))
    o_main.uniteWith(o_topbox)
    o_topbox.erase()
    h_trap = H_DROP - 20.0
    o_trap = PYRAMID(s, L=l_top, W=W_CASE, H=h_trap, HT=h_trap / (1.0 - 0.62)).rotateX(180.0).translate((0.0, 0.0, -20.0))
    o_main.uniteWith(o_trap)
    o_trap.erase()
    for sy in (-1.0, 1.0):
        o_rib = CYLINDER(s, R=W_CASE * 0.25, H=l_bot * 0.92, O=0.0).rotateY(90.0).translate((-l_bot * 0.46, sy * W_CASE * 0.28, -H_DROP + W_CASE * 0.26))
        o_main.uniteWith(o_rib)
        o_rib.erase()

    # 3. 顶装双腔防爆变送器表头 (+Z)
    r_head = 60.0
    z_head_c = H_TOP - r_head
    o_neck = CYLINDER(s, R=24.0, H=max(45.0, z_head_c - 10.0), O=0.0).translate((0.0, 0.0, 10.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()
    l_head = 152.0
    o_head = CYLINDER(s, R=r_head, H=l_head, O=0.0).rotateX(-90.0).translate((0.0, -l_head / 2.0, z_head_c))
    o_main.uniteWith(o_head)
    o_head.erase()
    o_fcap = CYLINDER(s, R=r_head + 6.0, H=16.0, O=0.0).rotateX(-90.0).translate((0.0, -l_head / 2.0 - 8.0, z_head_c))
    o_main.uniteWith(o_fcap)
    o_fcap.erase()
    for sx in (-1.0, 1.0):
        o_gl = CYLINDER(s, R=13.0, H=26.0, O=0.0).rotateY(sx * 90.0).translate((sx * (r_head - 6.0), 18.0, z_head_c - 6.0))
        o_main.uniteWith(o_gl)
        o_gl.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_DROP', (0.0, 0.0, 0.0), (0.0, 0.0, -H_DROP))
