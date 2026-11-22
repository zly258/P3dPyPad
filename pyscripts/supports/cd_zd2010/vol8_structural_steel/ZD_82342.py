# -*- coding: utf-8 -*-
# CD-ZD2010 82342 双混凝土梁端—端简支梁（工字钢）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="82342工字钢简支梁", TooltipLong="CD-ZD2010 82342 双混凝土梁端—端简支梁（工字钢）", LengthUnit="mm", Ports=1)
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
def ZD_82342(s, L=800.0, H=140.0, W=80.0, T=5.5, TF=9.1, ID=u"ZD_82342", Spec=u"I14", L_span=800.0, H_section=140.0, B_section=80.0, Load_kN=22.5, Weight_kg=15.0, **kw):
    L = float(L); H = float(H); W = float(W); T = float(T); TF = float(TF)
    if L <= 80.0: L = 400.0
    if H <= 30.0: H = 100.0
    if W <= 15.0: W = 48.0
    if T <= 1.5: T = 5.3
    if TF <= 2.0: TF = 8.5
    # 1. 工字钢 I 跨接简支梁 (对称双侧凹槽)
    i_slot_w = max(2.0, (W - T) / 2.0)
    i_slot_h = max(4.0, H - 2.0 * TF)
    o1 = BOX(s, L=W, W=H, H=L).translate((L / 2.0, 0.0, 0.0))
    for sy in (-1.0, 1.0):
        o_c = BOX(s, L=i_slot_w + 10.0, W=i_slot_h, H=L + 20.0).translate((L / 2.0, sy * (T / 2.0 + (i_slot_w + 10.0) / 2.0), 0.0))
        o1.subtractFrom(o_c); o_c.erase()

    # 2. 两端与跨中腹板竖向加劲肋 + 左右两端支承端板与下部托肋
    stiff_t = max(8.0, T * 1.4)
    for xs in (L * 0.25, L * 0.50, L * 0.75):
        o_st = BOX(s, L=W - 4.0, W=i_slot_h, H=stiff_t).translate((xs, 0.0, 0.0))
        o1.uniteWith(o_st); o_st.erase()

    end_t = max(14.0, TF * 1.5)
    for xe, dir_x in ((0.0, 1.0), (L, -1.0)):
        o_end = BOX(s, L=W + 70.0, W=H + 90.0, H=end_t).translate((xe - dir_x * (end_t / 2.0), 0.0, 0.0))
        o_rib = BOX(s, L=12.0, W=55.0, H=75.0).translate((xe + dir_x * 37.5, 0.0, -(H / 2.0 + 27.5)))
        o1.uniteWith(o_end); o_end.erase()
        o1.uniteWith(o_rib); o_rib.erase()

    s.setPoint((L / 2.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (L, 0.0, 0.0))
