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
          TooltipShort=u"电动单座调节阀 (GB/T 4213)",
          TooltipLong=u"化工电动单座调节阀，含双端法兰球形阀体、双柱支架、顶部电动执行机构箱体、侧装伺服电机、液晶控制盒及应急手轮",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"电动调节阀面距、法兰、总高及手轮直径")
@param(D=LENGTH, TooltipShort=u"管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面距 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰厚度 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"总高度", TooltipLong=u"管道中心至电动执行器顶面总高 (mm)", Ask4Dist=True)
@param(D_WHEEL=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"电动执行器应急手轮直径 (mm)")
def INST_CONTROL_ELECTRIC(
    s,
    D=88.9,
    L_FACE=310.0,
    D_FL=200.0,
    C_FL=20.0,
    H_TOTAL=640.0,
    D_WHEEL=210.0,
    ID=u"INST_CONTROL_ELECTRIC",
    **kw
):
    u"""电动单座调节阀 (Port 1: X=-L/2, Port 2: X=+L/2, 电动执行头在 +Z)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 55.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0
    D_WHEEL = max(140.0, float(D_WHEEL))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_wh = D_WHEEL / 2.0

    # 1. 双端法兰与球形阀体
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()
    o_pass = CYLINDER(s, R=r_pipe * 1.15, H=L_FACE - 2.0 * C_FL + 8.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 4.0), 0.0, 0.0))
    o_main.uniteWith(o_pass)
    o_pass.erase()

    r_body = max(r_pipe * 1.55, r_fl * 0.68)
    o_body = SPHERE(s, R=r_body)
    o_main.uniteWith(o_body)
    o_body.erase()
    o_bcap = CYLINDER(s, R=r_body * 0.80, H=24.0, O=0.0).translate((0.0, 0.0, -r_body - 12.0))
    o_main.uniteWith(o_bcap)
    o_bcap.erase()
    z_bonnet_top = r_body + 48.0
    o_bfl = CYLINDER(s, R=r_body * 0.90, H=22.0, O=0.0).translate((0.0, 0.0, r_body * 0.70))
    o_main.uniteWith(o_bfl)
    o_bfl.erase()
    o_bonnet = CYLINDER(s, R=r_body * 0.60, H=64.0, O=0.0).translate((0.0, 0.0, r_body * 0.70))
    o_main.uniteWith(o_bonnet)
    o_bonnet.erase()

    # 2. 刚性双柱支架
    h_gear = 175.0
    z_gear_bot = H_TOTAL - h_gear - 24.0
    h_yoke = max(110.0, z_gear_bot - z_bonnet_top)
    o_ybase = CYLINDER(s, R=56.0, H=22.0, O=0.0).translate((0.0, 0.0, z_bonnet_top - 4.0))
    o_main.uniteWith(o_ybase)
    o_ybase.erase()
    o_ytop = CYLINDER(s, R=66.0, H=24.0, O=0.0).translate((0.0, 0.0, z_gear_bot - 14.0))
    o_main.uniteWith(o_ytop)
    o_ytop.erase()
    for sx in (-1.0, 1.0):
        o_leg = CORNERBOX(s, L=24.0, W=34.0, H=h_yoke + 16.0).translate((sx * 44.0 - 12.0, -17.0, z_bonnet_top - 4.0))
        o_main.uniteWith(o_leg)
        o_leg.erase()
    o_stem = CYLINDER(s, R=14.0, H=h_yoke + 24.0, O=0.0).translate((0.0, 0.0, z_bonnet_top - 8.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    # 3. 顶部电动执行机构 (主减速箱 + 右侧卧式伺服电机 + 前侧液晶控制箱 + 顶装应急手轮)
    z_gear_mid = z_gear_bot + h_gear * 0.5
    o_gear = CORNERBOX(s, L=168.0, W=144.0, H=h_gear).translate((-84.0, -72.0, z_gear_bot))
    o_main.uniteWith(o_gear)
    o_gear.erase()
    # 侧装电动伺服电机 (+X)
    o_motor = CYLINDER(s, R=64.0, H=165.0, O=0.0).rotateY(90.0).translate((74.0, 0.0, z_gear_mid + 6.0))
    o_main.uniteWith(o_motor)
    o_motor.erase()
    o_mcap = CYLINDER(s, R=68.0, H=24.0, O=0.0).rotateY(90.0).translate((232.0, 0.0, z_gear_mid + 6.0))
    o_main.uniteWith(o_mcap)
    o_mcap.erase()
    # 前侧液晶就地控制盒 (-Y)
    o_ctrl = CORNERBOX(s, L=126.0, W=56.0, H=112.0).translate((-63.0, -120.0, z_gear_bot + 26.0))
    o_main.uniteWith(o_ctrl)
    o_ctrl.erase()
    # 顶部应急手轮 (+Z)
    o_wstem = CYLINDER(s, R=20.0, H=34.0, O=0.0).translate((0.0, 0.0, z_gear_bot + h_gear - 8.0))
    o_main.uniteWith(o_wstem)
    o_wstem.erase()
    z_wh = H_TOTAL - 12.0
    o_ring = TORUS(s, R1=r_wh - 12.0, R2=12.0).translate((0.0, 0.0, z_wh))
    o_main.uniteWith(o_ring)
    o_ring.erase()
    for ang in (0.0, 60.0, 120.0):
        o_sp = CYLINDER(s, R=9.0, H=(r_wh - 12.0) * 2.0, O=0.0).rotateY(90.0).translate((-(r_wh - 12.0), 0.0, 0.0)).rotateZ(ang).translate((0.0, 0.0, z_wh))
        o_main.uniteWith(o_sp)
        o_sp.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
