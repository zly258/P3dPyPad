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
          TooltipShort=u"法兰 Y 型过滤器 (HG/T 21637)",
          TooltipLong=u"HG/T 21637 PN16 法兰连接 Y 型管道过滤器，含双端法兰、直管体、45度向下斜滤筒与盲法兰排污盖",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"Y 型过滤器结构长度及斜滤筒外形尺寸参数")
@param(D=LENGTH, TooltipShort=u"连接管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰厚度 (mm)")
@param(L_LEG=LENGTH, TooltipShort=u"斜滤筒长度", TooltipLong=u"管道中心至排污盲法兰端面斜向长度 (mm)", Ask4Dist=True)
@param(D_LEG=LENGTH, TooltipShort=u"斜滤筒外径", TooltipLong=u"45度斜向滤筒外径 (mm)")
def SPEC_STRAINER_Y(
    s,
    D=114.3,
    L_FACE=350.0,
    D_FL=220.0,
    C_FL=20.0,
    L_LEG=260.0,
    D_LEG=133.0,
    ID=u"SPEC_STRAINER_Y",
    **kw
):
    u"""法兰 Y 型过滤器 (中心在原点, Port 1 在 X=-L/2, Port 2 在 X=+L/2, 斜滤筒沿 +X/-Z 45度向下)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    L_LEG = float(L_LEG)
    if L_LEG < 1.0:
        L_LEG = 1.0
    D_LEG = max(D * 1.05, float(D_LEG))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_body = r_pipe * 1.12
    r_leg = D_LEG / 2.0
    r_cap_fl = r_leg * 1.42
    c_cap = max(14.0, C_FL * 0.9)

    # 1. 双端法兰与直管主体
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    o_body = CYLINDER(s, R=r_body, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_body)
    o_body.erase()

    # 2. 45度向下斜滤筒 + 滤筒端法兰 + 盲法兰排污盖 + 排污丝堵
    leg_net = max(40.0, L_LEG - 2.0 * c_cap)
    o_leg = CYLINDER(s, R=r_leg, H=leg_net + 10.0, O=0.0).translate((0.0, 0.0, -10.0))
    o_cap_fl = CYLINDER(s, R=r_cap_fl, H=c_cap, O=0.0).translate((0.0, 0.0, leg_net - 2.0))
    o_leg.uniteWith(o_cap_fl)
    o_cap_fl.erase()

    o_blind = CYLINDER(s, R=r_cap_fl, H=c_cap, O=0.0).translate((0.0, 0.0, leg_net + c_cap - 4.0))
    o_leg.uniteWith(o_blind)
    o_blind.erase()

    o_plug = CYLINDER(s, R=max(10.0, r_leg * 0.22), H=max(16.0, c_cap * 0.9), O=0.0).translate((0.0, 0.0, leg_net + 2.0 * c_cap - 6.0))
    o_leg.uniteWith(o_plug)
    o_plug.erase()

    # 旋转 135 度使 +Z 指向 (+X, 0, -Z) 45 度向下
    o_leg.rotateY(135.0).translate((-half_l * 0.12, 0.0, 0.0))
    o_main.uniteWith(o_leg)
    o_leg.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('L_LEG', (0.0, 0.0, 0.0), (L_LEG * 0.7071, 0.0, -L_LEG * 0.7071))
