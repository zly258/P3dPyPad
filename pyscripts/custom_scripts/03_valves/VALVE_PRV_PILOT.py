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
          TooltipShort=u"先导活塞式蒸汽减压阀 (Y43H)",
          TooltipLong=u"先导活塞式蒸汽减压阀，含双突面端法兰、球形主活塞阀体、上置大直径蝶形先导膜片室、顶部调压弹簧帽与侧导压管",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"先导活塞式蒸汽减压阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(D_DIAPH=LENGTH, TooltipShort=u"先导膜盖外径", TooltipLong=u"上置先导膜片室法兰外径 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"总高度", TooltipLong=u"管道中心至顶部调压螺杆顶面高度 H (mm)", Ask4Dist=True)
def VALVE_PRV_PILOT(
    s,
    D=88.9,
    L_FACE=260.0,
    D_FL=200.0,
    C_FL=20.0,
    D_DIAPH=210.0,
    H_TOP=390.0,
    ID=u"VALVE_PRV_PILOT",
    **kw
):
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    D_DIAPH = max(D_FL * 0.85, float(D_DIAPH))
    H_TOP = float(H_TOP)
    if H_TOP < 1.0:
        H_TOP = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.5
    r_rf = max(r_pipe + 8.0, r_fl * 0.72)
    fl_t = max(10.0, C_FL - rf_t)
    r_diaph = D_DIAPH / 2.0

    # 1. 左右突面端法兰 + 球形主活塞阀体
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

    o_pipe = CYLINDER(s, R=r_pipe * 1.15, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe)
    o_pipe.erase()

    r_body = min(half_l - C_FL - 8.0, r_pipe * 1.58)
    o_sph = SPHERE(s, R=r_body)
    o_main.uniteWith(o_sph)
    o_sph.erase()

    # 底部主阀底盖法兰
    o_bot_cap = CYLINDER(s, R=r_body * 0.82, H=24.0, O=0.0).translate((0.0, 0.0, -(r_body + 12.0)))
    o_main.uniteWith(o_bot_cap)
    o_bot_cap.erase()

    # 2. 主阀活塞缸颈 + 中法兰
    z_mf = r_body * 0.9
    o_mf = CYLINDER(s, R=r_body * 1.08, H=22.0, O=0.0).translate((0.0, 0.0, z_mf))
    o_main.uniteWith(o_mf)
    o_mf.erase()

    z_diaph = z_mf + 22.0 + max(38.0, r_pipe * 0.72)
    o_pneck = CYLINDER(s, R=r_body * 0.65, H=z_diaph - z_mf + 4.0, O=0.0).translate((0.0, 0.0, z_mf))
    o_main.uniteWith(o_pneck)
    o_pneck.erase()

    # 3. 标志性上置大直径先导膜片盖 (飞碟状上下两半膜盒)
    o_d_bot = CONE(s, R1=r_body * 0.65, R2=r_diaph, H=24.0, E=0.0).translate((0.0, 0.0, z_diaph - 18.0))
    o_main.uniteWith(o_d_bot)
    o_d_bot.erase()

    o_d_fl = CYLINDER(s, R=r_diaph, H=20.0, O=0.0).translate((0.0, 0.0, z_diaph + 4.0))
    o_main.uniteWith(o_d_fl)
    o_d_fl.erase()

    o_d_top = CONE(s, R1=r_diaph, R2=r_diaph * 0.42, H=28.0, E=0.0).translate((0.0, 0.0, z_diaph + 22.0))
    o_main.uniteWith(o_d_top)
    o_d_top.erase()

    # 4. 顶部调压弹簧罩与调压螺杆
    z_spr_bot = z_diaph + 46.0
    spr_h = max(72.0, H_TOP - z_spr_bot - 30.0)
    o_spr = CYLINDER(s, R=max(26.0, r_diaph * 0.34), H=spr_h, O=0.0).translate((0.0, 0.0, z_spr_bot))
    o_main.uniteWith(o_spr)
    o_spr.erase()

    # 顶部调压螺杆与锁紧螺母
    o_screw = CYLINDER(s, R=max(10.0, r_diaph * 0.12), H=36.0, O=0.0).translate((0.0, 0.0, z_spr_bot + spr_h - 6.0))
    o_main.uniteWith(o_screw)
    o_screw.erase()
    o_tbar = CYLINDER(s, R=8.0, H=max(64.0, r_diaph * 0.65), O=0.0).rotateY(90.0).translate((-max(32.0, r_diaph * 0.325), 0.0, z_spr_bot + spr_h + 22.0))
    o_main.uniteWith(o_tbar)
    o_tbar.erase()

    # 5. 侧挂先导反馈导压管 (连接出口侧阀颈与先导膜盒下腔)
    r_tube = 7.0
    tx = half_l - C_FL - 18.0
    o_t1 = CYLINDER(s, R=r_tube, H=z_diaph + 6.0, O=0.0).translate((tx, 0.0, 0.0))
    o_main.uniteWith(o_t1)
    o_t1.erase()
    o_t2 = CYLINDER(s, R=r_tube, H=tx + 6.0, O=0.0).rotateY(90.0).translate((0.0, 0.0, z_diaph))
    o_main.uniteWith(o_t2)
    o_t2.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_TOP', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
