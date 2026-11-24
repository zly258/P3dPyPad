# -*- coding: utf-8 -*-
# CD-ZD2010 80631 包箍梁底悬臂吊（双槽钢）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="80631包箍梁底悬臂梁", TooltipLong="CD-ZD2010 80631 包箍梁底悬臂吊（双槽钢）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要几何尺寸")
@param(L=LENGTH, TooltipShort="跨长L", TooltipLong="梁挑出跨度/总长 L", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="截面高H", TooltipLong="型钢截面高度 H")
@param(W=LENGTH, TooltipShort="截面宽W", TooltipLong="型钢翼缘宽度 W")
@param(T=LENGTH, TooltipShort="腹板厚T", TooltipLong="型钢腹板厚度 T")
@param(TF=LENGTH, TooltipShort="翼缘厚TF", TooltipLong="型钢翼缘厚度 TF")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Spec=STRING, TooltipShort="型钢型号", TooltipLong="型钢规格型号")
@param(L_span=LENGTH0, TooltipShort="计算跨距", TooltipLong="计算跨距(mm)")
@param(H_section=LENGTH0, TooltipShort="型钢高", TooltipLong="型钢高(mm)")
@param(B_section=LENGTH0, TooltipShort="型钢宽", TooltipLong="型钢宽(mm)")
@param(Load_kN=LENGTH0, TooltipShort="许用荷载", TooltipLong="许用荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_80631(s, L=500.0, H=120.0, W=53.0, T=5.5, TF=9.0, ID=u"ZD_80631", Spec=u"[12", L_span=500.0, H_section=120.0, B_section=53.0, Load_kN=22.5, Weight_kg=15.0, **kw):
    L = float(L); H = float(H); W = float(W); T = float(T); TF = float(TF)
    if L <= 80.0: L = 400.0
    if H <= 30.0: H = 100.0
    if W <= 15.0: W = 48.0
    if T <= 1.5: T = 5.3
    if TF <= 2.0: TF = 8.5
    # 对照图集 ZD_80631_atlas.png (p.425)：
    # 下部水平双槽钢悬臂梁 (件 1，总长 L1 = L + B + 200) + 上部抱紧混凝土梁 (宽 B × 高 H_beam) 的两组门形包箍组件 (件 2 单头螺杆 + 件 3 槽钢横担 + 件 4 底托板)
    C_GAP = 60.0
    beam_B = min(350.0, max(220.0, L * 0.55))
    beam_H = max(320.0, H * 2.4)
    L1 = L + beam_B + 180.0
    tot_w = W * 2.0 + C_GAP
    slot_w = max(2.0, W - T)
    slot_h = max(4.0, H - 2.0 * TF)

    # 1. 下部水平双槽钢背靠背悬臂主梁 (从 X = -beam_B - 100 延伸至 X = L + 80)
    x_start = -(beam_B + 100.0)
    x_mid = x_start + L1 / 2.0
    o1 = BOX(s, L=W, W=H, H=L1).translate((x_mid, -(C_GAP / 2.0 + W / 2.0), 0.0))
    o_c1 = BOX(s, L=slot_w + 10.0, W=slot_h, H=L1 + 20.0).translate((x_mid, -(C_GAP / 2.0 + T + (slot_w + 10.0) / 2.0), 0.0))
    o1.subtractFrom(o_c1); o_c1.erase()
    o2 = BOX(s, L=W, W=H, H=L1).translate((x_mid, (C_GAP / 2.0 + W / 2.0), 0.0))
    o_c2 = BOX(s, L=slot_w + 10.0, W=slot_h, H=L1 + 20.0).translate((x_mid, (C_GAP / 2.0 + T + (slot_w + 10.0) / 2.0), 0.0))
    o2.subtractFrom(o_c2); o_c2.erase()
    o1.uniteWith(o2); o2.erase()

    # 悬臂端连接缀板
    batten_t = 10.0
    o_bat = BOX(s, L=tot_w, W=batten_t, H=80.0).translate((L, 0.0, (H / 2.0 + batten_t / 2.0)))
    o1.uniteWith(o_bat); o_bat.erase()

    # 2. 上部抱紧混凝土梁的两组门形包箍组件 (位于混凝土梁两侧 X = -beam_B - 30 与 X = -30)
    y_rod = tot_w / 2.0 + 38.0
    hoop_w = y_rod * 2.0 + 60.0
    rod_r = 12.0
    for xh in (-(beam_B + 30.0), -30.0):
        # 梁顶横向 [5 槽钢压担 (件 3) + 梁底横向承托板与角钢卡块 (件 4)
        o_top_ch = BOX(s, L=hoop_w, W=50.0, H=38.0).translate((xh, 0.0, H / 2.0 + beam_H + 25.0))
        o_btm_pad = BOX(s, L=hoop_w, W=14.0, H=50.0).translate((xh, 0.0, -(H / 2.0 + 7.0)))
        o1.uniteWith(o_top_ch); o_top_ch.erase()
        o1.uniteWith(o_btm_pad); o_btm_pad.erase()
        # 左右两根竖直对穿长螺杆与双螺母 (件 2)
        for sy in (-1.0, 1.0):
            yr = sy * y_rod
            rod_len = beam_H + H + 110.0
            o_rod = CYLINDER(s, R=rod_r, H=rod_len, O=0.0).translate((xh, yr, -(H / 2.0 + 40.0)))
            o_nut1 = CYLINDER(s, R=rod_r * 1.7, H=18.0, O=0.0).translate((xh, yr, H / 2.0 + beam_H + 50.0))
            o_nut2 = CYLINDER(s, R=rod_r * 1.7, H=18.0, O=0.0).translate((xh, yr, -(H / 2.0 + 32.0)))
            o1.uniteWith(o_rod); o_rod.erase()
            o1.uniteWith(o_nut1); o_nut1.erase()
            o1.uniteWith(o_nut2); o_nut2.erase()

    s.setPoint((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (L, 0.0, 0.0))
