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
          TooltipShort=u"对夹刀闸阀 / 料浆阀 (MSS SP-81)",
          TooltipLong=u"对夹式明杆刀闸阀(料浆阀)，含超薄平板对夹阀体、压料填料函、顶部双柱龙门架、明杆与辐条手轮",
          LengthUnit="mm",
          Ports="2",
          FirstPortEndtypes="WAF")
@group("MainDimensions", TooltipLong=u"对夹刀闸阀外形尺寸")
@param(D=LENGTH, TooltipShort=u"公称管径外径", TooltipLong=u"连接管道外径 D (mm)")
@param(L_FACE=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"对夹薄板阀体总厚度 L (mm)", Ask4Dist=True)
@param(D_FL=LENGTH, TooltipShort=u"阀体圆盘外径", TooltipLong=u"对夹刀闸阀圆盘部分外径 (mm)")
@param(H_OPEN=LENGTH, TooltipShort=u"全开总高", TooltipLong=u"管道中心至明杆顶部全开高度 H (mm)", Ask4Dist=True)
@param(D_HW=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"操作手轮外径 (mm)")
def VALVE_KNIFE_GATE(
    s,
    D=168.3,
    L_FACE=57.0,
    D_FL=285.0,
    H_OPEN=640.0,
    D_HW=300.0,
    ID=u"VALVE_KNIFE_GATE",
    **kw
):
    D = max(50.0, float(D))
    L_FACE = float(L_FACE)
    if L_FACE < 1.0:
        L_FACE = 1.0
    D_FL = max(D + 55.0, float(D_FL))
    D_HW = max(160.0, float(D_HW))
    H_OPEN = float(H_OPEN)
    if H_OPEN < 1.0:
        H_OPEN = 1.0

    half_l = L_FACE / 2.0
    r_pipe = D / 2.0
    r_fl = D_FL / 2.0
    rf_t = 3.0

    # 1. 薄板对夹阀体 (下半圆盘 + 上半矩形胸膛 + 两侧密封突面)
    o_main = CYLINDER(s, R=r_fl, H=L_FACE - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(half_l - rf_t), 0.0, 0.0))
    o_rf = CYLINDER(s, R=r_fl * 0.78, H=L_FACE, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    o_main.uniteWith(o_rf)
    o_rf.erase()

    # 上半部矩形闸板箱体 (薄板特征)
    chest_w = r_fl * 1.65
    z_chest_top = r_fl * 1.18
    o_chest = CORNERBOX(s, L=L_FACE - 2.0 * rf_t, W=chest_w, H=z_chest_top).translate((-(half_l - rf_t), -chest_w / 2.0, 0.0))
    o_main.uniteWith(o_chest)
    o_chest.erase()

    # 顶部矩形填料压盖
    gland_w = chest_w * 0.92
    o_gland = CORNERBOX(s, L=L_FACE + 10.0, W=gland_w, H=22.0).translate((-(half_l + 5.0), -gland_w / 2.0, z_chest_top - 4.0))
    o_main.uniteWith(o_gland)
    o_gland.erase()

    # 2. 标志性顶部双柱龙门支架 (两根扁钢立柱沿 ±Y 分布 + 顶部水平横梁)
    z_hw = H_OPEN - max(95.0, r_pipe * 1.25)
    if z_hw < z_chest_top + 120.0:
        z_hw = z_chest_top + 120.0
    portal_h = z_hw - z_chest_top
    col_t = max(14.0, L_FACE * 0.28)
    col_w = max(24.0, chest_w * 0.12)
    span_y = chest_w * 0.44
    for sy in (-1.0, 1.0):
        o_col = CORNERBOX(s, L=col_t, W=col_w, H=portal_h).translate((-col_t / 2.0, sy * span_y - col_w / 2.0, z_chest_top + 6.0))
        o_main.uniteWith(o_col)
        o_col.erase()

    # 龙门顶横梁
    beam_h = max(22.0, col_w * 0.85)
    o_beam = CORNERBOX(s, L=col_t * 2.2, W=span_y * 2.0 + col_w * 1.2, H=beam_h).translate((-col_t * 1.1, -(span_y + col_w * 0.6), z_hw - beam_h - 6.0))
    o_main.uniteWith(o_beam)
    o_beam.erase()

    # 中部裸露刀闸板上缘 (略高于填料函，增强刀闸阀辨识度)
    o_blade = CORNERBOX(s, L=max(8.0, L_FACE * 0.16), W=r_pipe * 1.65, H=portal_h * 0.22).translate((-max(4.0, L_FACE * 0.08), -r_pipe * 0.825, z_chest_top + 12.0))
    o_main.uniteWith(o_blade)
    o_blade.erase()

    # 3. 明杆 + 辐条手轮
    r_stem = max(10.0, r_pipe * 0.14)
    o_stem = CYLINDER(s, R=r_stem, H=H_OPEN - z_chest_top + 10.0, O=0.0).translate((0.0, 0.0, z_chest_top - 10.0))
    o_main.uniteWith(o_stem)
    o_stem.erase()

    r_hw = D_HW / 2.0
    r_rim = max(9.5, D_HW * 0.042)
    o_rim = TORUS(s, R1=r_hw - r_rim, R2=r_rim).translate((0.0, 0.0, z_hw))
    o_main.uniteWith(o_rim)
    o_rim.erase()
    o_hub = CYLINDER(s, R=max(22.0, r_stem * 2.1), H=26.0, O=0.0).translate((0.0, 0.0, z_hw - 13.0))
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
