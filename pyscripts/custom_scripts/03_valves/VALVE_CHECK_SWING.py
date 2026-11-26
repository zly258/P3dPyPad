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
          TooltipShort=u"法兰旋启式止回阀 (GB/T 12236)",
          TooltipLong=u"法兰钢制旋启式止回阀，含突面端法兰、大容腔旋启阀体、圆形螺栓顶盖法兰、穹顶封盖、侧摇杆销轴凸台与顶部吊耳",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"法兰旋启式止回阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"阀盖总高", TooltipLong=u"管道中心至阀盖吊耳顶面高度 H (mm)", Ask4Dist=True)
def VALVE_CHECK_SWING(
    s,
    D=114.3,
    L_FACE=300.0,
    D_FL=220.0,
    C_FL=20.0,
    H_TOP=195.0,
    ID=u"VALVE_CHECK_SWING",
    **kw
):
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    H_TOP = float(H_TOP)
    if H_TOP < 1.0:
        H_TOP = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.5
    r_rf = max(r_pipe + 8.0, r_fl * 0.72)
    fl_t = max(10.0, C_FL - rf_t)

    # 1. 左右突面端法兰
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

    # 2. 流道颈 + 旋启式大肚阀腔
    o_pipe = CYLINDER(s, R=r_pipe * 1.14, H=L_FACE - 2.0 * C_FL + 6.0, O=0.0).rotateY(90.0).translate((-(half_l - C_FL + 3.0), 0.0, 0.0))
    o_main.uniteWith(o_pipe)
    o_pipe.erase()

    r_body = min(half_l - C_FL - 10.0, r_pipe * 1.56)
    o_sph = SPHERE(s, R=r_body).translate((0.0, 0.0, r_pipe * 0.12))
    o_main.uniteWith(o_sph)
    o_sph.erase()

    # 3. 顶部大直径螺栓顶盖法兰 + 穹顶盖板 + 顶部吊环凸耳
    z_cap_fl = H_TOP - max(52.0, r_pipe * 0.9)
    if z_cap_fl < r_body * 0.82:
        z_cap_fl = r_body * 0.82
    o_neck = CYLINDER(s, R=r_body * 0.84, H=z_cap_fl - r_body * 0.4 + 4.0, O=0.0).translate((0.0, 0.0, r_body * 0.4 - 4.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()

    cap_fl_t = max(24.0, C_FL * 1.35)
    r_cap_fl = r_body * 1.12
    o_cap_fl = CYLINDER(s, R=r_cap_fl, H=cap_fl_t, O=0.0).translate((0.0, 0.0, z_cap_fl - 2.0))
    o_main.uniteWith(o_cap_fl)
    o_cap_fl.erase()

    z_dome = z_cap_fl + cap_fl_t - 4.0
    dome_h = max(16.0, (H_TOP - z_dome) * 0.45)
    o_dome = CONE(s, R1=r_cap_fl * 0.78, R2=r_cap_fl * 0.42, H=dome_h, E=0.0).translate((0.0, 0.0, z_dome))
    o_main.uniteWith(o_dome)
    o_dome.erase()

    # 顶部吊环/吊耳
    lug_h = max(18.0, H_TOP - (z_dome + dome_h))
    o_lug = CYLINDER(s, R=max(14.0, r_pipe * 0.26), H=lug_h + 6.0, O=0.0).translate((0.0, 0.0, z_dome + dome_h - 4.0))
    o_main.uniteWith(o_lug)
    o_lug.erase()

    # 4. 侧面摇杆销轴螺塞凸台 (旋启止回阀典型特征)
    o_pin = CYLINDER(s, R=max(15.0, r_pipe * 0.28), H=r_body * 2.24, O=0.0).rotateX(90.0).translate((-r_body * 0.18, r_body * 1.12, r_body * 0.42))
    o_main.uniteWith(o_pin)
    o_pin.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_TOP', (0.0, 0.0, 0.0), (0.0, 0.0, H_TOP))
