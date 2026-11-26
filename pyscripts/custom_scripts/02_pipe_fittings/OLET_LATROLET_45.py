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

@activate(Group="Tee",
          TooltipShort=u"45°斜支管台 Latrolet (GB/T 19326)",
          TooltipLong=u"GB/T 19326 / MSS SP-97 锻制45度斜支管台 Latrolet，含主管马鞍裁切、倾斜45度锥形补强肩与支管对焊端",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"45度斜支管台主要几何参数")
@param(D_RUN=LENGTH, TooltipShort=u"主管外径", TooltipLong=u"主管公称外径 D_RUN (mm)")
@param(D_BR=LENGTH, TooltipShort=u"支管外径", TooltipLong=u"45度斜支管对焊端外径 D_BR (mm)")
@param(D_BASE=LENGTH, TooltipShort=u"补强座外径", TooltipLong=u"斜支管台底部补强锥肩外径 D_BASE (mm)")
@param(H_LEN=LENGTH, TooltipShort=u"斜支管外伸长", TooltipLong=u"主管外壁交点沿45度轴线至支管端面长度 H_LEN (mm)", Ask4Dist=True)
@param(WT_BR=LENGTH, TooltipShort=u"支管壁厚", TooltipLong=u"支管公称壁厚 T (mm)")
def OLET_LATROLET_45(
    s,
    D_RUN=219.1,
    D_BR=60.3,
    D_BASE=92.0,
    H_LEN=70.0,
    WT_BR=4.0,
    ID=u"OLET_LATROLET_45",
    **kw
):
    u"""45度斜支管台 Latrolet (主管沿 X 轴 Z=0, 斜支管沿 +45° XZ 平面)。"""
    D_RUN = max(60.0, float(D_RUN))
    D_BR = max(20.0, min(D_RUN * 0.70, float(D_BR)))
    r_run = D_RUN / 2.0
    r_br = D_BR / 2.0
    r_base = max(r_br + 4.0, min(r_run * 0.85, float(D_BASE) / 2.0))
    H_LEN = float(H_LEN)
    if H_LEN < 1.0:
        H_LEN = 1.0
    WT_BR = max(2.0, min(r_br - 3.0, float(WT_BR)))
    r_br_in = r_br - WT_BR

    c45 = 0.7071067811865476
    # 主管圆柱壁 z = r_run 与 45° 射线 (t*c45, 0, t*c45) 的交点参数 t_wall = r_run / c45
    t_wall = r_run / c45
    t_bot = max(r_run * 0.65, t_wall - r_base * 0.95)
    t_neck = t_wall + H_LEN * 0.58
    t_top = t_wall + H_LEN

    # 沿本地 +Z 建锥形补强肩与支管直颈，再绕 Y 轴旋转 45° 落入 +X/+Z 象限
    o_body = CONE(s, R1=r_base, R2=r_br, H=t_neck - t_bot, E=0.0).translate((0.0, 0.0, t_bot)).rotateY(45.0)
    o_neck = CYLINDER(s, R=r_br, H=t_top - t_neck, O=0.0).translate((0.0, 0.0, t_neck)).rotateY(45.0)
    o_body.uniteWith(o_neck)
    o_neck.erase()

    # 主管马鞍裁切 + 45° 斜支管贯通内孔
    run_cut_len = t_top * c45 * 2.0 + r_base * 2.0 + 40.0
    o_cut = CYLINDER(s, R=r_run, H=run_cut_len, O=0.0).rotateY(90.0).translate((-run_cut_len * 0.25, 0.0, 0.0))
    o_bore = CYLINDER(s, R=r_br_in, H=(t_top - t_bot) + 16.0, O=0.0).translate((0.0, 0.0, t_bot - 8.0)).rotateY(45.0)
    o_cut.uniteWith(o_bore)
    o_bore.erase()

    o_body.subtractFrom(o_cut)
    o_cut.erase()

    p_wall = (t_wall * c45, 0.0, r_run)
    p_top = (t_top * c45, 0.0, t_top * c45)
    s.setPoint(p_wall, (-c45, 0.0, -c45))
    s.setPoint(p_top, (c45, 0.0, c45))
    s.setLinearDimension('H_LEN', p_wall, p_top)
