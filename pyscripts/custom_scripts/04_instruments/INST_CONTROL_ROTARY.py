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
          TooltipShort=u"气动V型球阀/偏心旋转调节阀 (ISO 5211)",
          TooltipLong=u"化工气动V型球阀/偏心旋转调节阀，含双端法兰紧凑旋转阀体、气动双活塞齿轮齿条执行器及顶装智能定位器/回讯器",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"气动旋转调节阀面距、法兰及执行器尺寸")
@param(D=LENGTH, TooltipShort=u"管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面距 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰厚度 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"总高度", TooltipLong=u"管道中心至定位器顶面总高 (mm)", Ask4Dist=True)
@param(L_ACT=LENGTH, TooltipShort=u"气缸长度", TooltipLong=u"气动旋转执行器缸体总长 (mm)")
def INST_CONTROL_ROTARY(
    s,
    D=114.3,
    L_FACE=229.0,
    D_FL=220.0,
    C_FL=20.0,
    H_TOTAL=480.0,
    L_ACT=320.0,
    ID=u"INST_CONTROL_ROTARY",
    **kw
):
    u"""气动V型球阀/偏心旋转调节阀 (Port 1: X=-L/2, Port 2: X=+L/2, 气缸与定位器在 +Z)。"""
    D = max(32.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 55.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0
    L_ACT = max(180.0, float(L_ACT))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0

    # 1. 双端法兰与偏心旋转阀体
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()
    r_body = max(r_pipe * 1.38, r_fl * 0.65)
    o_body = CYLINDER(s, R=r_body, H=L_FACE - 2.0 * C_FL + 8.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 4.0), 0.0, 0.0))
    o_main.uniteWith(o_body)
    o_body.erase()
    # 偏心旋转阀轴套鼓包 (竖向圆柱)
    o_boss = CYLINDER(s, R=r_body * 0.62, H=r_body * 2.15, O=0.0).translate((0.0, 0.0, -r_body * 1.05))
    o_main.uniteWith(o_boss)
    o_boss.erase()

    # 2. ISO 5211 支架与安装法兰板
    z_pad = r_body + 56.0
    o_neck = CYLINDER(s, R=34.0, H=64.0, O=0.0).translate((0.0, 0.0, r_body * 0.85))
    o_main.uniteWith(o_neck)
    o_neck.erase()
    o_pad = CORNERBOX(s, L=106.0, W=106.0, H=18.0).translate((-53.0, -53.0, z_pad - 6.0))
    o_main.uniteWith(o_pad)
    o_pad.erase()

    # 3. 卧式气动齿轮齿条双活塞执行器 (沿 X 轴)
    d_cyl = max(108.0, L_ACT * 0.36)
    r_cyl = d_cyl / 2.0
    z_cyl_c = z_pad + 12.0 + r_cyl
    o_act_box = CORNERBOX(s, L=L_ACT * 0.78, W=d_cyl * 0.92, H=d_cyl * 0.96).translate((-L_ACT * 0.39, -d_cyl * 0.46, z_pad + 10.0))
    o_main.uniteWith(o_act_box)
    o_act_box.erase()
    o_act_cyl = CYLINDER(s, R=r_cyl, H=L_ACT * 0.86, O=0.0).rotateY(90.0).translate((-L_ACT * 0.43, 0.0, z_cyl_c))
    o_main.uniteWith(o_act_cyl)
    o_act_cyl.erase()
    # 左右弹簧端盖
    for sx in (-1.0, 1.0):
        o_ec = CYLINDER(s, R=r_cyl * 1.05, H=26.0, O=0.0).rotateY(90.0).translate((sx * (L_ACT * 0.43) - 13.0, 0.0, z_cyl_c))
        o_main.uniteWith(o_ec)
        o_ec.erase()

    # 4. 顶装智能定位器 + 回讯指示圆顶 + 侧装电磁阀块
    z_act_top = z_cyl_c + r_cyl
    h_pos = max(72.0, H_TOTAL - z_act_top - 26.0)
    o_pstem = CYLINDER(s, R=24.0, H=28.0, O=0.0).translate((0.0, 0.0, z_act_top - 6.0))
    o_main.uniteWith(o_pstem)
    o_pstem.erase()
    o_pos = CORNERBOX(s, L=116.0, W=92.0, H=h_pos).translate((-58.0, -46.0, z_act_top + 14.0))
    o_main.uniteWith(o_pos)
    o_pos.erase()
    o_beacon = CYLINDER(s, R=24.0, H=26.0, O=0.0).translate((0.0, 0.0, z_act_top + 14.0 + h_pos - 4.0))
    o_main.uniteWith(o_beacon)
    o_beacon.erase()
    # 侧装 NAMUR 电磁阀 (-Y)
    o_sol = CORNERBOX(s, L=78.0, W=42.0, H=52.0).translate((-39.0, -r_cyl - 36.0, z_cyl_c - 26.0))
    o_main.uniteWith(o_sol)
    o_sol.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
