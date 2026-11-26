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
          TooltipShort=u"轴向金属波纹膨胀节 (GB/T 12777)",
          TooltipLong=u"GB/T 12777 PN16 法兰连接轴向型金属波纹膨胀节，含双端法兰、多道环状波纹管与外置双限位拉杆耳板",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"轴向金属波纹膨胀节结构长度、波纹直径及拉杆尺寸参数")
@param(D=LENGTH, TooltipShort=u"连接管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰厚度 (mm)")
@param(D_BELLOW=LENGTH, TooltipShort=u"波纹外径", TooltipLong=u"金属波纹管波峰外径 (mm)")
@param(D_ROD=LENGTH, TooltipShort=u"拉杆直径", TooltipLong=u"外置双限位拉杆直径 (mm)")
def SPEC_EXPANSION_JOINT(
    s,
    D=114.3,
    L_FACE=300.0,
    D_FL=220.0,
    C_FL=20.0,
    D_BELLOW=156.0,
    D_ROD=18.0,
    ID=u"SPEC_EXPANSION_JOINT",
    **kw
):
    u"""轴向金属波纹膨胀节 (中心在原点, Port 1 在 X=-L/2, Port 2 在 X=+L/2, 双限位拉杆在 +/-Y)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_BELLOW = float(D_BELLOW)
    if D_BELLOW < 1.0:
        D_BELLOW = 1.0
    D_ROD = max(10.0, float(D_ROD))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_bel = D_BELLOW / 2.0
    r_rod = D_ROD / 2.0

    # 1. 双端法兰与核心管体
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    o_core = CYLINDER(s, R=r_pipe * 1.05, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_core)
    o_core.erase()

    # 2. 多道环状波纹管 (6道环状波峰)
    n_waves = 6
    bel_span = max(60.0, L_FACE - 2.0 * C_FL - 48.0)
    pitch = bel_span / float(n_waves)
    r_wave_tube = min(pitch * 0.40, (r_bel - r_pipe) * 0.65)
    r_wave_tube = max(6.0, r_wave_tube)
    r_wave_maj = max(r_pipe + 2.0, r_bel - r_wave_tube)
    x_start = -bel_span / 2.0 + pitch / 2.0
    for i in range(n_waves):
        wx = x_start + i * pitch
        o_w = TORUS(s, R1=r_wave_maj, R2=r_wave_tube).rotateY(90.0).translate((wx, 0.0, 0.0))
        o_main.uniteWith(o_w)
        o_w.erase()

    # 3. 外置双限位拉杆与耳板 (沿 +/-Y 对称布置)
    y_rod = r_fl + r_rod * 1.8
    lug_t = max(14.0, C_FL * 0.85)
    lug_w = r_rod * 3.8
    lug_len = y_rod - r_fl + r_rod * 2.2 + 12.0
    for sx in (-1.0, 1.0):
        lx = sx * (half_l - C_FL - lug_t * 0.5)
        for sy in (-1.0, 1.0):
            ly = sy * (r_fl - 12.0 + lug_len / 2.0)
            o_lug = BOX(s, L=lug_len, W=lug_w, H=lug_t).translate((lx, ly, 0.0))
            o_main.uniteWith(o_lug)
            o_lug.erase()

    rod_len = L_FACE - 2.0 * C_FL + 24.0
    for sy in (-1.0, 1.0):
        ry = sy * y_rod
        o_rod = CYLINDER(s, R=r_rod, H=rod_len, O=0.0).rotateY(90.0).translate((-rod_len / 2.0, ry, 0.0))
        o_main.uniteWith(o_rod)
        o_rod.erase()
        # 限位双螺母
        for sx in (-1.0, 1.0):
            nx = sx * (half_l - C_FL + 2.0) - (r_rod * 0.8 if sx > 0 else r_rod * 0.8)
            o_nut = CYLINDER(s, R=r_rod * 1.7, H=r_rod * 1.6, O=0.0).rotateY(90.0).translate((nx, ry, 0.0))
            o_main.uniteWith(o_nut)
            o_nut.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('D_BELLOW', (0.0, 0.0, -r_bel), (0.0, 0.0, r_bel))
