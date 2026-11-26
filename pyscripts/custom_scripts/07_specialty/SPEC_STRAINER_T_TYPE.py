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
          TooltipShort=u"T 型管道过滤器 (HG/T 21637)",
          TooltipLong=u"HG/T 21637 法兰连接 T 型管道过滤器，含水平直通法兰管体、垂直下伸滤筒与快开盲法兰排污盖",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"T 型过滤器结构长度、法兰及下伸滤筒尺寸")
@param(D=LENGTH, TooltipShort=u"连接管外径", TooltipLong=u"管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"法兰面间距", TooltipLong=u"两端法兰密封面间距 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"端法兰外径", TooltipLong=u"连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"端法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(D_BODY=LENGTH, TooltipShort=u"滤筒外径", TooltipLong=u"垂直下伸滤筒主体外径 (mm)")
@param(H_DROP=LENGTH, TooltipShort=u"滤筒下伸高度", TooltipLong=u"管中心线至底部盲盖排污口总高 H (mm)", Ask4Dist=True)
def SPEC_STRAINER_T_TYPE(
    s,
    D=114.3,
    L_FACE=350.0,
    D_FL=220.0,
    C_FL=20.0,
    D_BODY=159.0,
    H_DROP=260.0,
    ID=u"SPEC_STRAINER_T_TYPE",
    **kw
):
    u"""T 型管道过滤器 (主轴沿 X, 滤筒垂直向下沿 -Z, 两端法兰面在 +/-L_FACE/2)。"""
    D = max(25.0, float(D))
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_BODY = max(D * 1.15, float(D_BODY))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    H_DROP = float(H_DROP)
    if H_DROP < 1.0:
        H_DROP = 1.0

    half_l = L_FACE / 2.0
    r_fl = D_FL / 2.0
    r_pipe = D / 2.0 * 1.10
    r_body = D_BODY / 2.0
    r_cap_fl = r_body * 1.32
    c_cap = max(14.0, C_FL * 0.90)

    # 1. 双端法兰与水平直通管体
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    o_run = CYLINDER(s, R=r_pipe, H=L_FACE - 2.0 * C_FL + 8.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 4.0), 0.0, 0.0))
    o_main.uniteWith(o_run)
    o_run.erase()

    # 2. 顶部三通补强盖帽与吊耳
    h_top = r_pipe * 1.15
    o_top = CYLINDER(s, R=r_body * 0.92, H=h_top + 12.0, O=0.0).translate((0.0, 0.0, -6.0))
    o_main.uniteWith(o_top)
    o_top.erase()

    o_top_cap = CYLINDER(s, R=r_body * 1.02, H=max(14.0, c_cap * 0.8), O=0.0).translate((0.0, 0.0, h_top))
    o_main.uniteWith(o_top_cap)
    o_top_cap.erase()

    # 3. 垂直下伸滤筒 + 底法兰 + 盲盖 + 底部排污丝堵
    plug_h = max(16.0, c_cap * 0.85)
    z_blind_bot = -(H_DROP - plug_h)
    z_fl_top = z_blind_bot + 2.0 * c_cap
    barrel_h = max(30.0, -z_fl_top + 12.0)

    o_barrel = CYLINDER(s, R=r_body, H=barrel_h, O=0.0).translate((0.0, 0.0, z_fl_top - 4.0))
    o_main.uniteWith(o_barrel)
    o_barrel.erase()

    o_bfl = CYLINDER(s, R=r_cap_fl, H=c_cap, O=0.0).translate((0.0, 0.0, z_blind_bot + c_cap))
    o_main.uniteWith(o_bfl)
    o_bfl.erase()

    o_blind = CYLINDER(s, R=r_cap_fl, H=c_cap + 2.0, O=0.0).translate((0.0, 0.0, z_blind_bot))
    o_main.uniteWith(o_blind)
    o_blind.erase()

    o_plug = CYLINDER(s, R=max(12.0, r_body * 0.22), H=plug_h + 4.0, O=0.0).translate((0.0, 0.0, -H_DROP))
    o_main.uniteWith(o_plug)
    o_plug.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_DROP', (0.0, 0.0, 0.0), (0.0, 0.0, -H_DROP))
