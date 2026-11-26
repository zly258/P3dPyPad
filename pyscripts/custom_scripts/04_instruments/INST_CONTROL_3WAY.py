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
          TooltipShort=u"气动薄膜三通调节阀 (GB/T 4213)",
          TooltipLong=u"化工气动薄膜三通分流/合流调节阀，含T型三端法兰阀体、双柱支架、侧装定位器及气动薄膜执行机构",
          LengthUnit="mm",
          Ports="3",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"三通调节阀面距、底口高、总高及膜头直径")
@param(D=LENGTH, TooltipShort=u"管外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"主通面距", TooltipLong=u"左右法兰端面距 L (mm)", Ask4Dist=True)
@param(H_BOT=LENGTH, TooltipShort=u"底法兰距", TooltipLong=u"中心线至底部第三口法兰面距离 (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"连接法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"上部总高", TooltipLong=u"中心线至膜头顶面高度 (mm)", Ask4Dist=True)
@param(D_ACT=LENGTH, TooltipShort=u"膜头直径", TooltipLong=u"气动薄膜执行机构外径 (mm)")
def INST_CONTROL_3WAY(
    s,
    D=88.9,
    L_FACE=310.0,
    H_BOT=165.0,
    D_FL=200.0,
    C_FL=20.0,
    H_TOTAL=620.0,
    D_ACT=320.0,
    ID=u"INST_CONTROL_3WAY",
    **kw
):
    u"""气动薄膜三通调节阀 (Port 1: X=-L/2, Port 2: X=+L/2, Port 3: Z=-H_BOT)。"""
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    H_BOT = float(H_BOT)
    if H_BOT < 1.0:
        H_BOT = 1.0
    D_FL = max(D + 55.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    H_TOTAL = float(H_TOTAL)
    if H_TOTAL < 1.0:
        H_TOTAL = 1.0
    D_ACT = max(180.0, float(D_ACT))

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    r_act = D_ACT / 2.0

    # 1. T型三端法兰与阀体通道
    o_main = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_fl2 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).rotateY(90.0).translate((half_l - C_FL, 0.0, 0.0))
    o_main.uniteWith(o_fl2)
    o_fl2.erase()
    o_fl3 = CYLINDER(s, R=r_fl, H=C_FL, O=0.0).translate((0.0, 0.0, -H_BOT))
    o_main.uniteWith(o_fl3)
    o_fl3.erase()

    o_hpass = CYLINDER(s, R=r_pipe * 1.18, H=L_FACE - 2.0 * C_FL + 8.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 4.0), 0.0, 0.0))
    o_main.uniteWith(o_hpass)
    o_hpass.erase()
    o_vpass = CYLINDER(s, R=r_pipe * 1.18, H=H_BOT - C_FL + 8.0, O=0.0).translate((0.0, 0.0, -(H_BOT - C_FL + 4.0)))
    o_main.uniteWith(o_vpass)
    o_vpass.erase()

    # 2. 中心三通球腔与上阀盖
    r_body = max(r_pipe * 1.55, r_fl * 0.68)
    o_body = SPHERE(s, R=r_body)
    o_main.uniteWith(o_body)
    o_body.erase()
    z_bonnet_top = r_body + 48.0
    o_bfl = CYLINDER(s, R=r_body * 0.90, H=22.0, O=0.0).translate((0.0, 0.0, r_body * 0.70))
    o_main.uniteWith(o_bfl)
    o_bfl.erase()
    o_bonnet = CYLINDER(s, R=r_body * 0.60, H=64.0, O=0.0).translate((0.0, 0.0, r_body * 0.70))
    o_main.uniteWith(o_bonnet)
    o_bonnet.erase()

    # 3. 双柱支架 + 定位器
    h_act_body = max(110.0, D_ACT * 0.36)
    z_act_bot = H_TOTAL - h_act_body
    h_yoke = max(110.0, z_act_bot - z_bonnet_top)
    o_ybase = CYLINDER(s, R=56.0, H=22.0, O=0.0).translate((0.0, 0.0, z_bonnet_top - 4.0))
    o_main.uniteWith(o_ybase)
    o_ybase.erase()
    o_ytop = CYLINDER(s, R=64.0, H=24.0, O=0.0).translate((0.0, 0.0, z_act_bot - 16.0))
    o_main.uniteWith(o_ytop)
    o_ytop.erase()
    for sx in (-1.0, 1.0):
        o_leg = CORNERBOX(s, L=24.0, W=32.0, H=h_yoke + 16.0).translate((sx * 42.0 - 12.0, -16.0, z_bonnet_top - 4.0))
        o_main.uniteWith(o_leg)
        o_leg.erase()
    o_stem = CYLINDER(s, R=13.0, H=h_yoke + 24.0, O=0.0).translate((0.0, 0.0, z_bonnet_top - 8.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()
    z_pos = z_bonnet_top + h_yoke * 0.32
    o_pos = CORNERBOX(s, L=94.0, W=64.0, H=90.0).translate((-47.0, -76.0, z_pos))
    o_main.uniteWith(o_pos)
    o_pos.erase()
    o_pbr = CORNERBOX(s, L=70.0, W=26.0, H=46.0).translate((-35.0, -26.0, z_pos + 22.0))
    o_main.uniteWith(o_pbr)
    o_pbr.erase()

    # 4. 气动膜头
    z_rim = z_act_bot + h_act_body * 0.48
    o_low = CONE(s, R1=r_act * 0.42, R2=r_act * 0.94, H=h_act_body * 0.44).translate((0.0, 0.0, z_act_bot))
    o_main.uniteWith(o_low)
    o_low.erase()
    o_rim = CYLINDER(s, R=r_act, H=24.0, O=0.0).translate((0.0, 0.0, z_rim - 12.0))
    o_main.uniteWith(o_rim)
    o_rim.erase()
    o_up = CONE(s, R1=r_act * 0.94, R2=r_act * 0.45, H=h_act_body * 0.44).translate((0.0, 0.0, z_rim + 8.0))
    o_main.uniteWith(o_up)
    o_up.erase()
    o_cap = CYLINDER(s, R=r_act * 0.34, H=26.0, O=0.0).translate((0.0, 0.0, H_TOTAL - 26.0))
    o_main.uniteWith(o_cap)
    o_cap.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, -H_BOT), (0.0, 0.0, -1.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_BOT', (0.0, 0.0, 0.0), (0.0, 0.0, -H_BOT))
    s.setLinearDimension('H_TOTAL', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOTAL))
