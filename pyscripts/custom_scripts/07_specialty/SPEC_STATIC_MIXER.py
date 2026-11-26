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
          TooltipShort=u"管式法兰静态混合器",
          TooltipLong=u"SV/SX 型化工管式法兰静态混合器，含双端法兰、直管主体、外表面混合节段标识环与上部加药支口",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"静态混合器结构长度、管径及加药支口尺寸参数")
@param(D=LENGTH, TooltipShort=u"混合器管径", TooltipLong=u"主管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"端法兰外径", TooltipLong=u"主端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"端法兰厚度", TooltipLong=u"主端法兰厚度 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"加药口管径", TooltipLong=u"加药支口接管外径 (mm)")
@param(H_NOZ=LENGTH, TooltipShort=u"加药口高度", TooltipLong=u"管道中心至加药支口法兰面高度 (mm)", Ask4Dist=True)
def SPEC_STATIC_MIXER(
    s,
    D=114.3,
    L_FACE=800.0,
    D_FL=220.0,
    C_FL=20.0,
    D_NOZ=33.7,
    H_NOZ=160.0,
    ID=u"SPEC_STATIC_MIXER",
    **kw
):
    u"""管式法兰静态混合器 (中心在原点, Port 1 在 X=-L/2, Port 2 在 X=+L/2, 加药支口在进口侧 +Z)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_NOZ = max(18.0, float(D_NOZ))
    H_NOZ = float(H_NOZ)
    if H_NOZ < 1.0:
        H_NOZ = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_noz = D_NOZ / 2.0
    r_noz_fl = max(r_noz * 2.2, r_noz + 26.0)
    c_noz_fl = max(12.0, C_FL * 0.75)

    # 1. 双端法兰与直管主体
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    o_body = CYLINDER(s, R=r_pipe, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_body)
    o_body.erase()

    # 2. 外表面 3 道混合单元节段标识环
    ring_w = max(14.0, L_FACE * 0.025)
    for frac in (-0.12, 0.12, 0.34):
        rx = frac * L_FACE - ring_w / 2.0
        o_ring = CYLINDER(s, R=r_pipe + max(8.0, r_pipe * 0.14), H=ring_w, O=0.0).rotateY(90.0).translate((rx, 0.0, 0.0))
        o_main.uniteWith(o_ring)
        o_ring.erase()

    # 3. 进口侧上部 (+Z) 加药支口（带补强圈与小法兰）
    x_noz = -L_FACE * 0.30
    o_pad = CYLINDER(s, R=r_noz * 1.55, H=r_pipe + 10.0, O=0.0).translate((x_noz, 0.0, 0.0))
    o_main.uniteWith(o_pad)
    o_pad.erase()

    o_noz = CYLINDER(s, R=r_noz, H=H_NOZ - c_noz_fl + 4.0, O=0.0).translate((x_noz, 0.0, 0.0))
    o_main.uniteWith(o_noz)
    o_noz.erase()

    o_nfl = CYLINDER(s, R=r_noz_fl, H=c_noz_fl, O=0.0).translate((x_noz, 0.0, H_NOZ - c_noz_fl))
    o_main.uniteWith(o_nfl)
    o_nfl.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_NOZ', (x_noz, 0.0, 0.0), (x_noz, 0.0, H_NOZ))
