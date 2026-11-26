# -*- coding: utf-8 -*-
import math
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

@activate(Group="Support",
          TooltipShort=u"穿墙/穿楼板防水套管 (02S404)",
          TooltipLong=u"02S404 柔性/刚性穿墙防水套管，含同心钢套管、中央止水翼环法兰、端部密封压盘法兰与四向压紧螺栓耳",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"穿墙防水套管主要几何参数")
@param(D=LENGTH, TooltipShort=u"穿管外径", TooltipLong=u"内部穿越管道外径 D (mm)")
@param(D_SLV=LENGTH, TooltipShort=u"套管外径", TooltipLong=u"外部同心钢套管外径 (mm)")
@param(T_SLV=LENGTH, TooltipShort=u"套管壁厚", TooltipLong=u"同心钢套管壁厚 (mm)")
@param(L_WALL=LENGTH, TooltipShort=u"套管长度", TooltipLong=u"穿墙防水套管总长度 L_WALL (mm)", Ask4Dist=True)
@param(D_WING=LENGTH, TooltipShort=u"止水环外径", TooltipLong=u"中央圆形止水翼环外径 (mm)", Ask4Dist=True)
@param(T_WING=LENGTH, TooltipShort=u"止水环厚", TooltipLong=u"止水翼环法兰厚度 (mm)")
def SUPPORT_WALL_SLEEVE(
    s,
    D=168.3,
    D_SLV=219.1,
    T_SLV=8.0,
    L_WALL=300.0,
    D_WING=340.0,
    T_WING=12.0,
    ID=u"SUPPORT_WALL_SLEEVE",
    **kw
):
    u"""穿墙/穿楼板防水套管 (原点在套管中心线, 管道沿 X 轴穿越)。"""
    D = max(32.0, float(D))
    T_SLV = max(5.0, float(T_SLV))
    D_SLV = max(D + T_SLV * 2.0 + 24.0, float(D_SLV))
    L_WALL = float(L_WALL)
    if L_WALL < 1.0:
        L_WALL = 1.0
    D_WING = float(D_WING)
    if D_WING < 1.0:
        D_WING = 1.0
    T_WING = max(8.0, float(T_WING))

    r_slv_out = D_SLV / 2.0
    r_slv_in = r_slv_out - T_SLV
    r_wing = D_WING / 2.0

    # 1. 主同心钢套管（沿 X 轴居中）
    o_main = CYLINDER(s, R=r_slv_out, H=L_WALL, O=r_slv_in).rotateY(90.0).translate((-L_WALL / 2.0, 0.0, 0.0))

    # 2. 中央止水翼环法兰（焊于套管中部 x=0）
    o_wing = CYLINDER(s, R=r_wing, H=T_WING, O=r_slv_in).rotateY(90.0).translate((-T_WING / 2.0, 0.0, 0.0))
    o_main.uniteWith(o_wing)
    o_wing.erase()

    # 3. 迎水面端部密封法兰盘 + 4 根压盘螺柱（02S404 柔性防水套管标志特征）
    r_fl = r_slv_out + max(28.0, (r_wing - r_slv_out) * 0.65)
    fl_t = max(12.0, T_WING * 1.1)
    # 迎水面固定端法兰 + 密封压盘
    x_fl = L_WALL / 2.0 - fl_t
    o_fl = CYLINDER(s, R=r_fl, H=fl_t, O=r_slv_in).rotateY(90.0).translate((x_fl, 0.0, 0.0))
    o_main.uniteWith(o_fl)
    o_fl.erase()

    # 4 根均布压紧螺柱（先焊合于端法兰，再与外侧密封压盘融为单实体）
    gland_gap = max(16.0, fl_t * 1.3)
    x_gl = L_WALL / 2.0 + gland_gap
    stud_r = max(6.0, fl_t * 0.45)
    stud_pcd = (r_slv_out + r_fl) * 0.52
    stud_len = fl_t + gland_gap + fl_t * 0.85 + stud_r * 2.8
    for ang_deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(ang_deg)
        sy = stud_pcd * math.cos(rad)
        sz = stud_pcd * math.sin(rad)
        o_stud = CYLINDER(s, R=stud_r, H=stud_len, O=0.0).rotateY(90.0).translate(
            (x_fl - stud_r * 1.2, sy, sz))
        o_main.uniteWith(o_stud)
        o_stud.erase()

    # 外侧密封压盘环（套在4根螺柱上，融为单实体）
    o_gland = CYLINDER(s, R=r_fl * 0.96, H=fl_t * 0.85, O=D / 2.0 + 4.0).rotateY(90.0).translate((x_gl, 0.0, 0.0))
    o_main.uniteWith(o_gland)
    o_gland.erase()

    # 背水面端加固环（另一端齐平收口）
    o_ring2 = CYLINDER(s, R=r_slv_out + T_SLV * 1.2, H=fl_t * 0.8, O=r_slv_in).rotateY(90.0).translate(
        (-L_WALL / 2.0, 0.0, 0.0))
    o_main.uniteWith(o_ring2)
    o_ring2.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('L_WALL', (-L_WALL / 2.0, 0.0, r_slv_out), (L_WALL / 2.0, 0.0, r_slv_out))
    s.setLinearDimension('D_WING', (0.0, -r_wing, 0.0), (0.0, r_wing, 0.0))
