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
          TooltipShort=u"自动排气阀 / 空气消除器",
          TooltipLong=u"化工管道自动排气阀（空气消除器），含底部HG/T 20592 PN16法兰、立式浮筒腔体、螺栓顶盖与顶部排气帽",
          LengthUnit="mm",
          Ports="1",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"自动排气阀底法兰、浮筒腔外径及总高尺寸参数")
@param(D=LENGTH, TooltipShort=u"进口管径", TooltipLong=u"底部进口接管外径 D (mm)")
@param(D_FL=LENGTH, TooltipShort=u"底法兰外径", TooltipLong=u"底部安装法兰外径 D_FL (mm)")
@param(C_FL=LENGTH, TooltipShort=u"底法兰厚度", TooltipLong=u"底部安装法兰厚度 C_FL (mm)")
@param(D_BODY=LENGTH, TooltipShort=u"浮筒腔外径", TooltipLong=u"立式浮筒腔筒体外径 D_BODY (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"阀门总高", TooltipLong=u"底法兰面至顶部排气帽顶面总高 H_TOTAL (mm)", Ask4Dist=True)
@param(D_CAP=LENGTH, TooltipShort=u"排气帽外径", TooltipLong=u"顶部排气帽外径 D_CAP (mm)")
def SPEC_TRAP_AIR_ELIMINATOR(
    s,
    D=88.9,
    D_FL=200.0,
    C_FL=20.0,
    D_BODY=219.0,
    H_TOTAL=460.0,
    D_CAP=95.0,
    ID=u"SPEC_TRAP_AIR_ELIMINATOR",
    **kw
):
    u"""自动排气阀/空气消除器 (底法兰面在 Z=0, Port 1 在原点朝向 -Z)。"""
    D = max(25.0, float(D))
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_BODY = max(D * 1.6, float(D_BODY))
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0
    D_CAP = max(40.0, float(D_CAP))

    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_body = D_BODY / 2.0
    r_cap = D_CAP / 2.0

    # 1. 底部单法兰与进气过渡锥颈
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0)
    h_neck = max(35.0, H_TOTAL * 0.10)
    o_neck = CYLINDER(s, R=r_pipe, H=h_neck + 6.0, O=0.0).translate((0.0, 0.0, C_FL - 3.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    z_cone = C_FL + h_neck
    h_cone = max(28.0, H_TOTAL * 0.08)
    o_cone = CONE(s, R1=r_pipe, R2=r_body, H=h_cone + 4.0, E=0.0).translate((0.0, 0.0, z_cone - 2.0))
    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 2. 立式浮筒腔体与螺栓顶盖法兰
    z_body_bot = z_cone + h_cone
    h_body = max(120.0, H_TOTAL * 0.48)
    o_body = CYLINDER(s, R=r_body, H=h_body + 4.0, O=0.0).translate((0.0, 0.0, z_body_bot - 2.0))
    o_main.uniteWith(o_body)
    o_body.erase()

    c_cover = max(16.0, C_FL * 0.9)
    r_cov = r_body * 1.18
    z_cov = z_body_bot + h_body
    o_cov_bot = CYLINDER(s, R=r_cov, H=c_cover, O=0.0).translate((0.0, 0.0, z_cov - c_cover))
    o_main.uniteWith(o_cov_bot)
    o_cov_bot.erase()

    o_cov_top = CYLINDER(s, R=r_cov, H=c_cover, O=0.0).translate((0.0, 0.0, z_cov - 1.0))
    o_main.uniteWith(o_cov_top)
    o_cov_top.erase()

    # 3. 侧面排污螺塞凸台
    o_plug = CYLINDER(s, R=max(12.0, r_pipe * 0.25), H=26.0, O=0.0).rotateY(90.0).translate((r_body - 4.0, 0.0, z_body_bot + h_body * 0.18))
    o_main.uniteWith(o_plug)
    o_plug.erase()

    # 4. 上部杠杆排气阀盖颈部与顶部排气帽
    z_bonnet = z_cov + c_cover - 2.0
    z_cap_top = H_TOTAL
    h_top_zone = max(55.0, z_cap_top - z_bonnet)
    h_cap = max(24.0, h_top_zone * 0.36)
    h_stem = h_top_zone - h_cap

    o_bonnet = CONE(s, R1=r_body * 0.62, R2=r_cap * 0.48, H=h_stem * 0.55 + 3.0, E=0.0).translate((0.0, 0.0, z_bonnet))
    o_main.uniteWith(o_bonnet)
    o_bonnet.erase()

    o_exhaust = CYLINDER(s, R=r_cap * 0.48, H=h_stem * 0.55 + 4.0, O=0.0).translate((0.0, 0.0, z_bonnet + h_stem * 0.45))
    o_main.uniteWith(o_exhaust)
    o_exhaust.erase()

    z_cap = z_cap_top - h_cap
    o_cap_rim = CYLINDER(s, R=r_cap, H=h_cap * 0.42 + 2.0, O=0.0).translate((0.0, 0.0, z_cap))
    o_main.uniteWith(o_cap_rim)
    o_cap_rim.erase()

    o_cap_cone = CONE(s, R1=r_cap, R2=r_cap * 0.35, H=h_cap * 0.60, E=0.0).translate((0.0, 0.0, z_cap + h_cap * 0.40))
    o_main.uniteWith(o_cap_cone)
    o_cap_cone.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
