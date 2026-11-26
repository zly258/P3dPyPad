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
          TooltipShort=u"自力式压力调节阀/氮封阀 (GB/T 12244)",
          TooltipLong=u"化工自力式微压/氮封压力调节阀，含双端法兰阀体、顶部弹簧设定筒、底部大直径执行膜室及外置取压导压管",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"自力式调节阀面距、膜室直径及上下高度")
@param(D=LENGTH, TooltipShort=u"管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面距 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰厚度 (mm)")
@param(D_DIAPH=LENGTH, TooltipShort=u"膜室直径", TooltipLong=u"底部大直径微压膜室盘外径 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"上部弹簧高", TooltipLong=u"管道中心至顶部设定弹簧罩顶高 (mm)", Ask4Dist=True)
@param(H_BOT=LENGTH, TooltipShort=u"下部膜室深", TooltipLong=u"管道中心至底部膜室底面深度 (mm)", Ask4Dist=True)
def INST_SELF_REGULATOR(
    s,
    D=60.3,
    L_FACE=254.0,
    D_FL=165.0,
    C_FL=18.0,
    D_DIAPH=310.0,
    H_TOP=270.0,
    H_BOT=240.0,
    ID=u"INST_SELF_REGULATOR",
    **kw
):
    u"""自力式压力调节阀/氮封阀 (Port 1: X=-L/2, Port 2: X=+L/2, 膜室在 -Z, 弹簧筒在 +Z)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 50.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    D_DIAPH = max(180.0, float(D_DIAPH))
    H_TOP = float(H_TOP)
    if H_TOP < 1.0:
        H_TOP = 1.0
    H_BOT = float(H_BOT)
    if H_BOT < 1.0:
        H_BOT = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_diaph = D_DIAPH / 2.0

    # 1. 双端法兰与球形阀体
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()
    o_pass = CYLINDER(s, R=r_pipe * 1.15, H=L_FACE - 2.0 * C_FL + 8.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 4.0), 0.0, 0.0))
    o_main.uniteWith(o_pass)
    o_pass.erase()
    r_body = max(r_pipe * 1.50, r_fl * 0.62)
    o_body = SPHERE(s, R=r_body)
    o_main.uniteWith(o_body)
    o_body.erase()

    # 2. 顶部压力设定弹簧筒 (+Z) + 设定螺杆帽
    o_bfl = CYLINDER(s, R=r_body * 0.88, H=20.0, O=0.0).translate((0.0, 0.0, r_body * 0.72))
    o_main.uniteWith(o_bfl)
    o_bfl.erase()
    h_spring = max(90.0, H_TOP - r_body * 0.72 - 36.0)
    o_spr = CYLINDER(s, R=38.0, H=h_spring, O=0.0).translate((0.0, 0.0, r_body * 0.72 + 12.0))
    o_main.uniteWith(o_spr)
    o_spr.erase()
    o_cap = CYLINDER(s, R=24.0, H=34.0, O=0.0).translate((0.0, 0.0, H_TOP - 34.0))
    o_main.uniteWith(o_cap)
    o_cap.erase()

    # 3. 底部大直径微压膜室 (-Z) + 连接支架柱
    h_pan = 72.0
    z_pan_top = -H_BOT + h_pan
    o_lneck = CYLINDER(s, R=34.0, H=max(50.0, -z_pan_top + 10.0), O=0.0).translate((0.0, 0.0, z_pan_top - 10.0))
    o_main.uniteWith(o_lneck)
    o_lneck.erase()
    z_rim = -H_BOT + h_pan * 0.5
    o_p1 = CONE(s, R1=r_diaph * 0.92, R2=r_diaph * 0.45, H=h_pan * 0.42).translate((0.0, 0.0, z_rim + 6.0))
    o_main.uniteWith(o_p1)
    o_p1.erase()
    o_rim = CYLINDER(s, R=r_diaph, H=20.0, O=0.0).translate((0.0, 0.0, z_rim - 10.0))
    o_main.uniteWith(o_rim)
    o_rim.erase()
    o_p2 = CONE(s, R1=r_diaph * 0.45, R2=r_diaph * 0.92, H=h_pan * 0.42).translate((0.0, 0.0, -H_BOT))
    o_main.uniteWith(o_p2)
    o_p2.erase()

    # 4. 特征外置取压导压管 (从出口侧 +X 引至膜室上盖)
    x_tap = half_l - C_FL - 22.0
    o_t1 = CYLINDER(s, R=10.0, H=max(40.0, -z_rim + 10.0), O=0.0).translate((x_tap, -28.0, z_rim))
    o_main.uniteWith(o_t1)
    o_t1.erase()
    o_t2 = CYLINDER(s, R=10.0, H=34.0, O=0.0).rotateX(-90.0).translate((x_tap, -32.0, 0.0))
    o_main.uniteWith(o_t2)
    o_t2.erase()
    o_t3 = CYLINDER(s, R=10.0, H=max(30.0, x_tap - r_diaph * 0.4 + 20.0), O=0.0).rotateY(90.0).translate((r_diaph * 0.4, -28.0, z_rim + 16.0))
    o_main.uniteWith(o_t3)
    o_t3.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_TOP', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
    s.setLinearDimension('H_BOT', (0.0, 0.0, 0.0), (0.0, 0.0, -H_BOT))
