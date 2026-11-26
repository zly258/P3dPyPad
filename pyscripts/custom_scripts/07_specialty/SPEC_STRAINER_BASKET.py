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
          TooltipShort=u"法兰篮式过滤器 (HG/T 21637)",
          TooltipLong=u"HG/T 21637 PN16 法兰连接立式篮式过滤器，含双端法兰、立式加大滤筒、顶部快开盲法兰盖与底部支腿",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"篮式过滤器结构长度、立式筒体及高度尺寸参数")
@param(D=LENGTH, TooltipShort=u"连接管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰厚度 (mm)")
@param(D_BODY=LENGTH, TooltipShort=u"滤筒外径", TooltipLong=u"立式滤筒外径 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"上部高度", TooltipLong=u"管道中心至顶部盲盖高度 (mm)", Ask4Dist=True)
@param(H_BOT=LENGTH, TooltipShort=u"下部高度", TooltipLong=u"管道中心至支腿底面高度 (mm)", Ask4Dist=True)
def SPEC_STRAINER_BASKET(
    s,
    D=114.3,
    L_FACE=460.0,
    D_FL=220.0,
    C_FL=20.0,
    D_BODY=273.0,
    H_TOP=290.0,
    H_BOT=420.0,
    ID=u"SPEC_STRAINER_BASKET",
    **kw
):
    u"""法兰篮式过滤器 (中心在原点, Port 1 在 X=-L/2, Port 2 在 X=+L/2, 立式滤筒沿 Z 轴)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_BODY = max(D * 1.5, float(D_BODY))
    H_TOP = float(H_TOP)
    if H_TOP < 1.0:
        H_TOP = 1.0
    H_BOT = float(H_BOT)
    if H_BOT < 1.0:
        H_BOT = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_body = D_BODY / 2.0
    r_top_fl = r_body * 1.24
    c_top = max(18.0, C_FL * 1.1)

    # 1. 双端法兰与横向接管
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()

    o_noz = CYLINDER(s, R=r_pipe * 1.08, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_noz)
    o_noz.erase()

    # 2. 立式加大滤筒与底部封头
    z_shell_bot = -H_BOT * 0.62
    z_fl_bot = H_TOP - 2.0 * c_top - 26.0
    shell_h = max(80.0, z_fl_bot - z_shell_bot)
    o_shell = CYLINDER(s, R=r_body, H=shell_h + 6.0, O=0.0).translate((0.0, 0.0, z_shell_bot))
    o_main.uniteWith(o_shell)
    o_shell.erase()

    o_bot_head = HALFSPHERE(s, R=r_body).rotateX(180.0).translate((0.0, 0.0, z_shell_bot + 4.0))
    o_main.uniteWith(o_bot_head)
    o_bot_head.erase()

    # 3. 顶部设备法兰 + 快开盲法兰盖 + 快开压紧横梁与手柄
    o_top_fl = CYLINDER(s, R=r_top_fl, H=c_top, O=0.0).translate((0.0, 0.0, z_fl_bot))
    o_main.uniteWith(o_top_fl)
    o_top_fl.erase()

    o_blind = CYLINDER(s, R=r_top_fl, H=c_top, O=0.0).translate((0.0, 0.0, z_fl_bot + c_top - 2.0))
    o_main.uniteWith(o_blind)
    o_blind.erase()

    o_yoke = BOX(s, L=r_top_fl * 1.6, W=18.0, H=28.0).translate((0.0, 0.0, z_fl_bot + 2.0 * c_top + 6.0))
    o_main.uniteWith(o_yoke)
    o_yoke.erase()

    o_handle = CYLINDER(s, R=max(10.0, r_body * 0.11), H=26.0, O=0.0).translate((0.0, 0.0, z_fl_bot + 2.0 * c_top - 4.0))
    o_main.uniteWith(o_handle)
    o_handle.erase()

    # 4. 底部三支腿及底板
    leg_r = max(12.0, r_body * 0.12)
    leg_ring = r_body * 0.68
    leg_top_z = z_shell_bot + 24.0
    leg_h = max(40.0, leg_top_z - (-H_BOT))
    for ang_deg in (0.0, 120.0, 240.0):
        rad = ang_deg * 3.14159265 / 180.0
        lx = leg_ring * cos(rad)
        ly = leg_ring * sin(rad)
        o_leg = CYLINDER(s, R=leg_r, H=leg_h, O=0.0).translate((lx, ly, -H_BOT))
        o_main.uniteWith(o_leg)
        o_leg.erase()
        o_pad = CYLINDER(s, R=leg_r * 1.9, H=10.0, O=0.0).translate((lx, ly, -H_BOT))
        o_main.uniteWith(o_pad)
        o_pad.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_TOP', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
    s.setLinearDimension('H_BOT', (0.0, 0.0, 0.0), (0.0, 0.0, -H_BOT))
