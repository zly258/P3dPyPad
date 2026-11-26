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
          TooltipShort=u"法兰升降式止回阀 (GB/T 12235)",
          TooltipLong=u"法兰钢制升降式止回阀，含突面端法兰、球形阀体、圆形螺栓中法兰与加高圆柱导向阀盖",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"法兰升降式止回阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"顶盖总高", TooltipLong=u"管道中心至加高导向顶盖顶面高度 H (mm)", Ask4Dist=True)
def VALVE_CHECK_LIFT(
    s,
    D=88.9,
    L_FACE=241.0,
    D_FL=200.0,
    C_FL=20.0,
    H_TOP=210.0,
    ID=u"VALVE_CHECK_LIFT",
    **kw
):
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    H_TOP = float(H_TOP)
    if H_TOP < 1.0:
        H_TOP = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.5
    r_rf = max(r_pipe + 8.0, r_fl * 0.72)
    fl_t = max(10.0, C_FL - rf_t)

    # 1. 左右突面端法兰
    o_main = CYLINDER(s, R=r_rf, H=rf_t + 2.0, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl1 = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).rotateY(90.0).translate((-half_l + rf_t, 0.0, 0.0))
    o_main.uniteWith(o_fl1)
    o_fl1.erase()

    o_rf2 = CYLINDER(s, R=r_rf, H=rf_t + 2.0, O=0.0).rotateY(90.0).translate((half_l - rf_t - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_rf2)
    o_rf2.erase()
    o_fl2 = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    # 2. 流道颈 + 球形阀体 (与截止阀阀体同源)
    o_pipe = CYLINDER(s, R=r_pipe * 1.14, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe)
    o_pipe.erase()

    r_globe = min(half_l - C_FL - 6.0, r_pipe * 1.62)
    o_sph = SPHERE(s, R=r_globe)
    o_main.uniteWith(o_sph)
    o_sph.erase()

    # 3. 圆形中法兰 + 加高圆柱形阀瓣导向顶盖
    z_mf = r_globe * 0.85
    mf_t = max(24.0, C_FL * 1.3)
    r_mf = r_globe * 1.08
    o_mf = CYLINDER(s, R=r_mf, H=mf_t, O=0.0).translate((0.0, 0.0, z_mf))
    o_main.uniteWith(o_mf)
    o_mf.erase()

    z_bon_start = z_mf + mf_t - 4.0
    bon_h = max(48.0, H_TOP - z_bon_start - 18.0)
    o_bon = CYLINDER(s, R=r_mf * 0.62, H=bon_h, O=0.0).translate((0.0, 0.0, z_bon_start))
    o_main.uniteWith(o_bon)
    o_bon.erase()

    # 顶部封闭压帽 (六角/圆帽感)
    o_cap = CYLINDER(s, R=r_mf * 0.45, H=20.0, O=0.0).translate((0.0, 0.0, z_bon_start + bon_h - 4.0))
    o_main.uniteWith(o_cap)
    o_cap.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_TOP', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
