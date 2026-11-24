# -*- coding: utf-8 -*-
# CD-ZD2010 82341 双混凝土梁端—端简支梁（双槽钢）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="82341双槽钢简支梁", TooltipLong="CD-ZD2010 82341 双混凝土梁端—端简支梁（双槽钢）", LengthUnit="mm", Ports=1)
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
def ZD_82341(s, L=800.0, H=120.0, W=53.0, T=5.5, TF=9.0, ID=u"ZD_82341", Spec=u"[12", L_span=800.0, H_section=120.0, B_section=53.0, Load_kN=22.5, Weight_kg=15.0, **kw):
    L = float(L); H = float(H); W = float(W); T = float(T); TF = float(TF)
    if L <= 80.0: L = 400.0
    if H <= 30.0: H = 100.0
    if W <= 15.0: W = 48.0
    if T <= 1.5: T = 5.3
    if TF <= 2.0: TF = 8.5
    # 1. 双槽钢 ][ 跨接简支梁 (带净间距 C_GAP = 60mm)
    C_GAP = 60.0
    tot_w = W * 2.0 + C_GAP
    slot_w = max(2.0, W - T)
    slot_h = max(4.0, H - 2.0 * TF)
    o1 = BOX(s, L=W, W=H, H=L).translate((L / 2.0, -(C_GAP / 2.0 + W / 2.0), 0.0))
    o_c1 = BOX(s, L=slot_w + 10.0, W=slot_h, H=L + 20.0).translate((L / 2.0, -(C_GAP / 2.0 + T + (slot_w + 10.0) / 2.0), 0.0))
    o1.subtractFrom(o_c1); o_c1.erase()
    o2 = BOX(s, L=W, W=H, H=L).translate((L / 2.0, (C_GAP / 2.0 + W / 2.0), 0.0))
    o_c2 = BOX(s, L=slot_w + 10.0, W=slot_h, H=L + 20.0).translate((L / 2.0, (C_GAP / 2.0 + T + (slot_w + 10.0) / 2.0), 0.0))
    o2.subtractFrom(o_c2); o_c2.erase()
    o1.uniteWith(o2); o2.erase()

    # 2. 中间连接缀板与夹心垫板
    batten_t = 10.0
    batten_l = min(90.0, L * 0.14)
    for xb in (L * 0.28, L * 0.50, L * 0.72):
        o_bat = BOX(s, L=tot_w, W=batten_t, H=batten_l).translate((xb, 0.0, (H / 2.0 + batten_t / 2.0)))
        o_pad = BOX(s, L=C_GAP, W=H * 0.85, H=batten_t).translate((xb, 0.0, 0.0))
        o1.uniteWith(o_bat); o_bat.erase()
        o1.uniteWith(o_pad); o_pad.erase()

    # 3. 左右两端 (X = 0 与 X = L) 支承端板与下部双肋板
    end_t = max(14.0, TF * 1.5)
    for xe, dir_x in ((0.0, 1.0), (L, -1.0)):
        o_end = BOX(s, L=tot_w + 60.0, W=H + 80.0, H=end_t).translate((xe - dir_x * (end_t / 2.0), 0.0, 0.0))
        o1.uniteWith(o_end); o_end.erase()
        for sy in (-1.0, 1.0):
            o_rib = BOX(s, L=10.0, W=50.0, H=70.0).translate((xe + dir_x * 35.0, sy * (C_GAP / 2.0 + T / 2.0), -(H / 2.0 + 25.0)))
            o1.uniteWith(o_rib); o_rib.erase()

    s.setPoint((L / 2.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (L, 0.0, 0.0))
