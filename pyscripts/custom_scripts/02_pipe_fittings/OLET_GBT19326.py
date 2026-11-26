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
          TooltipShort=u"锻制对焊支管台 Weldolet (GB/T 19326)",
          TooltipLong=u"GB/T 19326-2022/MSS SP-97(已核实) 锻制对焊支管台 Weldolet，含主管马鞍裁切、锥形补强肩与贯通支管内孔",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="BV")
@group("MainDimensions", TooltipLong=u"锻制对焊支管台主要几何参数")
@param(D_RUN=LENGTH, TooltipShort=u"主管外径", TooltipLong=u"主管公称外径 D_RUN (mm)")
@param(D_BR=LENGTH, TooltipShort=u"支管外径", TooltipLong=u"支管对焊端外径 D_BR (mm)")
@param(D_BASE=LENGTH, TooltipShort=u"补强座外径", TooltipLong=u"支管台底部锥形补强肩外径 D_BASE (mm)")
@param(H_LEN=LENGTH, TooltipShort=u"支管台高度", TooltipLong=u"主管外壁至支管端面高度 A (mm)", Ask4Dist=True)
@param(WT_BR=LENGTH, TooltipShort=u"支管壁厚", TooltipLong=u"支管公称壁厚 T (mm)")
def OLET_GBT19326(
    s,
    D_RUN=219.1,
    D_BR=60.3,
    D_BASE=88.9,
    H_LEN=38.1,
    WT_BR=4.0,
    ID=u"OLET_GBT19326",
    **kw
):
    u"""锻制对焊支管台 Weldolet (主管沿 X 轴 Z=0, 支管沿 +Z 轴)。"""
    D_RUN = max(60.0, float(D_RUN))
    D_BR = max(20.0, min(D_RUN * 0.75, float(D_BR)))
    r_run = D_RUN / 2.0
    r_br = D_BR / 2.0
    r_base = max(r_br + 4.0, min(r_run * 0.90, float(D_BASE) / 2.0))
    H_LEN = float(H_LEN)
    if H_LEN < 1.0:
        H_LEN = 1.0
    WT_BR = max(2.0, min(r_br - 3.0, float(WT_BR)))
    r_br_in = r_br - WT_BR

    z_saddle = (r_run * r_run - r_base * r_base) ** 0.5
    z_bot = max(0.0, z_saddle - 8.0)
    z_top = r_run + H_LEN
    z_neck = r_run + H_LEN * 0.62

    # 底部锥形补强肩 + 上部支管对焊直颈
    o_body = CONE(s, R1=r_base, R2=r_br, H=z_neck - z_bot, E=0.0).translate((0.0, 0.0, z_bot))
    o_neck = CYLINDER(s, R=r_br, H=z_top - z_neck, O=0.0).translate((0.0, 0.0, z_neck))
    o_body.uniteWith(o_neck)
    o_neck.erase()

    # 主管马鞍裁切 + 支管贯通内孔
    run_cut_len = r_base * 2.0 + 24.0
    o_cut = CYLINDER(s, R=r_run, H=run_cut_len, O=0.0).rotateY(90.0).translate((-run_cut_len / 2.0, 0.0, 0.0))
    o_bore = CYLINDER(s, R=r_br_in, H=(z_top - z_bot) + 8.0, O=0.0).translate((0.0, 0.0, z_bot - 4.0))
    o_cut.uniteWith(o_bore)
    o_bore.erase()

    o_body.subtractFrom(o_cut)
    o_cut.erase()

    s.setPoint((0.0, 0.0, r_run), (0.0, 0.0, -1.0))
    s.setPoint((0.0, 0.0, z_top), (0.0, 0.0, 1.0))
    s.setLinearDimension('H_LEN', (0.0, 0.0, r_run), (0.0, 0.0, z_top))
