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

@activate(Group="Valve",
          TooltipShort=u"管道阻火器 (GB/T 13347)",
          TooltipLong=u"GB/T 13347 PN16 法兰连接管道阻火器，含双端法兰、对称锥形扩径段与中间加大阻火芯法兰壳体",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"管道阻火器结构长度与阻火芯壳体尺寸参数")
@param(D=LENGTH, TooltipShort=u"连接管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"端法兰外径", TooltipLong=u"两端连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"端法兰厚度", TooltipLong=u"两端连接法兰厚度 (mm)")
@param(D_CORE=LENGTH, TooltipShort=u"阻火芯壳径", TooltipLong=u"中间阻火芯法兰壳体外径 (mm)")
@param(L_CORE=LENGTH, TooltipShort=u"阻火芯长度", TooltipLong=u"中间阻火芯双法兰壳体总长 (mm)")
def SPEC_FLAME_ARRESTER(
    s,
    D=114.3,
    L_FACE=400.0,
    D_FL=220.0,
    C_FL=20.0,
    D_CORE=340.0,
    L_CORE=110.0,
    ID=u"SPEC_FLAME_ARRESTER",
    **kw
):
    u"""管道阻火器 (中心在原点, Port 1 在 X=-L/2, Port 2 在 X=+L/2)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_CORE = float(D_CORE)
    if D_CORE < 1.0:
        D_CORE = 1.0
    L_CORE = max(50.0, min(L_FACE * 0.5, float(L_CORE)))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_core_fl = D_CORE / 2.0
    r_core_body = r_core_fl * 0.80
    half_core = L_CORE / 2.0
    c_mid = max(16.0, C_FL * 1.05)

    # 1. 双端法兰
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    # 2. 对称锥形扩径段 (两端法兰向中间阻火芯平滑过渡)
    cone_len = max(20.0, half_l - C_FL - half_core + 6.0)
    o_cone1 = CONE(s, R1=r_pipe * 1.08, R2=r_core_body, H=cone_len, E=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_cone1)
    o_cone1.erase()

    o_cone2 = CONE(s, R1=r_core_body, R2=r_pipe * 1.08, H=cone_len, E=0.0).rotateY(90.0).translate((half_core - 3.0, 0.0, 0.0))
    o_main.uniteWith(o_cone2)
    o_cone2.erase()

    # 3. 中间阻火芯双法兰壳体
    o_core = CYLINDER(s, R=r_core_body, H=L_CORE, O=0.0).rotateY(90.0).translate((-half_core, 0.0, 0.0))
    o_main.uniteWith(o_core)
    o_core.erase()

    o_mfl1 = CYLINDER(s, R=r_core_fl, H=c_mid, O=0.0).rotateY(90.0).translate((-half_core, 0.0, 0.0))
    o_main.uniteWith(o_mfl1)
    o_mfl1.erase()

    o_mfl2 = CYLINDER(s, R=r_core_fl, H=c_mid, O=0.0).rotateY(90.0).translate((half_core - c_mid, 0.0, 0.0))
    o_main.uniteWith(o_mfl2)
    o_mfl2.erase()

    # 4. 阻火芯壳体圆周紧固螺栓柱（6根均布）
    bolt_ring = (r_core_body + r_core_fl) / 2.0
    bolt_r = max(6.0, c_mid * 0.34)
    for k in range(6):
        ang = k * 60.0 * 3.14159265 / 180.0
        by = bolt_ring * cos(ang)
        bz = bolt_ring * sin(ang)
        o_bolt = CYLINDER(s, R=bolt_r, H=L_CORE + 16.0, O=0.0).rotateY(90.0).translate((-(half_core + 8.0), by, bz))
        o_main.uniteWith(o_bolt)
        o_bolt.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('D_CORE', (0.0, 0.0, -r_core_fl), (0.0, 0.0, r_core_fl))
