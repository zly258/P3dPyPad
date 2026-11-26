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
          TooltipShort=u"法兰蒸汽疏水阀 (倒吊桶/浮球式)",
          TooltipLong=u"法兰连接机械式蒸汽疏水阀，含左右突面端法兰、顶部连接阀头、下沉式圆柱疏水储水桶、螺栓封盖法兰与底部排污螺塞",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"法兰蒸汽疏水阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(D_POT=LENGTH, TooltipShort=u"疏水桶外径", TooltipLong=u"下沉式倒吊桶/浮球桶体外径 (mm)")
@param(H_DROP=LENGTH, TooltipShort=u"下沉深度", TooltipLong=u"管道中心至疏水桶底面高度 (mm)", Ask4Dist=True)
def VALVE_STEAM_TRAP(
    s,
    D=33.4,
    L_FACE=210.0,
    D_FL=115.0,
    C_FL=16.0,
    D_POT=138.0,
    H_DROP=195.0,
    ID=u"VALVE_STEAM_TRAP",
    **kw
):
    D = max(18.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 35.0, float(D_FL))
    C_FL = max(12.0, float(C_FL))
    D_POT = max(D * 2.2, min(L_FACE - 2.0 * C_FL - 12.0, float(D_POT)))
    H_DROP = float(H_DROP)
    if H_DROP < 1.0:
        H_DROP = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.0
    r_rf = max(r_pipe + 6.0, r_fl * 0.7)
    fl_t = max(10.0, C_FL - rf_t)
    r_pot = D_POT / 2.0

    # 1. 左右突面端法兰 + 水平通道头
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

    o_pipe = CYLINDER(s, R=r_pipe * 1.28, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe)
    o_pipe.erase()

    # 2. 上部阀头与螺栓盖法兰
    z_top = r_pipe * 1.55 + 22.0
    o_head = CYLINDER(s, R=r_pot * 0.88, H=z_top + r_pipe * 1.2, O=0.0).translate((0.0, 0.0, -r_pipe * 1.2))
    o_main.uniteWith(o_head)
    o_head.erase()

    z_pot_fl = -(r_pipe * 1.15)
    o_pfl = CYLINDER(s, R=r_pot * 1.14, H=22.0, O=0.0).translate((0.0, 0.0, z_pot_fl - 22.0))
    o_main.uniteWith(o_pfl)
    o_pfl.erase()

    # 3. 标志性下沉圆柱形疏水储水桶 + 底部封头与排污螺塞
    pot_bot_z = -H_DROP + 18.0
    pot_h = (z_pot_fl - 18.0) - pot_bot_z
    o_pot = CYLINDER(s, R=r_pot, H=pot_h, O=0.0).translate((0.0, 0.0, pot_bot_z))
    o_main.uniteWith(o_pot)
    o_pot.erase()

    o_bot_cap = CONE(s, R1=r_pot * 0.65, R2=r_pot, H=16.0, E=0.0).translate((0.0, 0.0, pot_bot_z - 14.0))
    o_main.uniteWith(o_bot_cap)
    o_bot_cap.erase()

    o_plug = CYLINDER(s, R=max(11.0, r_pot * 0.2), H=18.0, O=0.0).translate((0.0, 0.0, -H_DROP))
    o_main.uniteWith(o_plug)
    o_plug.erase()

    # 顶部排气螺塞
    o_vent = CYLINDER(s, R=max(10.0, r_pot * 0.18), H=16.0, O=0.0).translate((0.0, 0.0, z_top - 4.0))
    o_main.uniteWith(o_vent)
    o_vent.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_DROP', (0.0, 0.0, 0.0), (0.0, 0.0, -H_DROP))
