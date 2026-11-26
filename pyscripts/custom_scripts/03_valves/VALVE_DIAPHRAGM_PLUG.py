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
          TooltipShort=u"法兰堰式衬氟隔膜阀 (GB/T 12239)",
          TooltipLong=u"法兰堰式衬氟隔膜阀，含突面端法兰、堰式流道阀体、宽扁椭圆形隔膜压紧中法兰、钟形阀盖、阀杆与手轮",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="FL")
@group("MainDimensions", TooltipLong=u"法兰堰式衬氟隔膜阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"法兰端面至端面结构长度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"端法兰外径 (mm)")
@param(C_FL=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"端法兰总厚度含突面 (mm)")
@param(H_OPEN=LENGTH, TooltipShort=u"全开总高", TooltipLong=u"管道中心至手轮顶面高度 H (mm)", Ask4Dist=True)
@param(D_HW=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"操作手轮外径 (mm)")
def VALVE_DIAPHRAGM_PLUG(
    s,
    D=88.9,
    L_FACE=254.0,
    D_FL=200.0,
    C_FL=20.0,
    H_OPEN=275.0,
    D_HW=240.0,
    ID=u"VALVE_DIAPHRAGM_PLUG",
    **kw
):
    D = max(25.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 40.0, float(D_FL))
    C_FL = max(14.0, float(C_FL))
    D_HW = max(110.0, float(D_HW))
    H_OPEN = float(H_OPEN)
    if H_OPEN < 1.0:
        H_OPEN = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 2.5
    r_rf = max(r_pipe + 8.0, r_fl * 0.72)
    fl_t = max(10.0, C_FL - rf_t)

    # 1. 左右突面端法兰 + 堰式低矮流道体
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

    # 2. 标志性宽扁跑道/圆形隔膜压紧中法兰 (比常规阀更宽更扁)
    r_diaph = min(half_l - C_FL - 8.0, r_pipe * 1.95)
    z_mf = r_pipe * 0.55
    mf_t = max(24.0, C_FL * 1.25)
    o_weir = CONE(s, R1=r_pipe * 1.15, R2=r_diaph * 0.96, H=z_mf + r_pipe * 0.75, E=0.0).translate((0.0, 0.0, -r_pipe * 0.7))
    o_main.uniteWith(o_weir)
    o_weir.erase()

    o_mf = CYLINDER(s, R=r_diaph * 1.12, H=mf_t, O=0.0).translate((0.0, 0.0, z_mf))
    o_main.uniteWith(o_mf)
    o_mf.erase()

    # 3. 钟形隔膜压板阀盖 (平滑收敛锥罩)
    z_hw = H_OPEN - max(18.0, D_HW * 0.07)
    z_bon_bot = z_mf + mf_t - 4.0
    z_bon_top = z_hw - max(36.0, D_HW * 0.16)
    if z_bon_top < z_bon_bot + 48.0:
        z_bon_top = z_bon_bot + 48.0
    o_bon = CONE(s, R1=r_diaph * 0.92, R2=max(24.0, r_pipe * 0.52), H=z_bon_top - z_bon_bot + 4.0, E=0.0).translate((0.0, 0.0, z_bon_bot))
    o_main.uniteWith(o_bon)
    o_bon.erase()

    # 顶部阀杆护套与指示帽
    r_stem = max(14.0, r_pipe * 0.3)
    o_neck = CYLINDER(s, R=r_stem * 1.4, H=z_hw - z_bon_top + 12.0, O=0.0).translate((0.0, 0.0, z_bon_top - 4.0))
    o_main.uniteWith(o_neck)
    o_neck.erase()
    o_ind = CYLINDER(s, R=r_stem * 0.85, H=20.0, O=0.0).translate((0.0, 0.0, z_hw))
    o_main.uniteWith(o_ind)
    o_ind.erase()

    # 4. 辐条手轮
    r_hw = D_HW / 2.0
    r_rim = max(8.5, D_HW * 0.044)
    o_rim = TORUS(s, R1=r_hw - r_rim, R2=r_rim).translate((0.0, 0.0, z_hw))
    o_main.uniteWith(o_rim)
    o_rim.erase()
    o_hub = CYLINDER(s, R=max(20.0, r_stem * 1.6), H=24.0, O=0.0).translate((0.0, 0.0, z_hw - 12.0))
    o_main.uniteWith(o_hub)
    o_hub.erase()
    for ang in (0.0, 90.0):
        o_sp = CYLINDER(s, R=r_rim * 0.72, H=(r_hw - r_rim) * 2.0, O=0.0).rotateY(90.0).translate((-(r_hw - r_rim), 0.0, z_hw)).rotateZ(ang)
        o_main.uniteWith(o_sp)
        o_sp.erase()

    s.setPoint((-half_l, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((half_l, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L_FACE', (-half_l, 0.0, 0.0), (half_l, 0.0, 0.0))
    s.setLinearDimension('H_OPEN', (0.0, 0.0, 0.0), (0.0, 0.0, H_OPEN))
