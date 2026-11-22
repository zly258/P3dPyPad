# -*- coding: utf-8 -*-
# CD-ZD2010 80000 混凝土梁端悬臂梁（单槽钢）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="80000单槽钢悬臂梁", TooltipLong="CD-ZD2010 80000 混凝土梁端悬臂梁（单槽钢）", LengthUnit="mm", Ports=1)
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
def ZD_80000(s, L=500.0, H=120.0, W=53.0, T=5.5, TF=9.0, ID=u"ZD_80000", Spec=u"[12", L_span=500.0, H_section=120.0, B_section=53.0, Load_kN=22.5, Weight_kg=15.0, **kw):
    L = float(L); H = float(H); W = float(W); T = float(T); TF = float(TF)
    if L <= 80.0: L = 400.0
    if H <= 30.0: H = 100.0
    if W <= 15.0: W = 48.0
    if T <= 1.5: T = 5.3
    if TF <= 2.0: TF = 8.5
    # 1. 单根 C 型槽钢水平悬臂梁 (沿 +X 轴跨长 L1 = L + 120，槽口朝 +Y)
    ext_a = min(150.0, L * 0.25)
    L1 = L + ext_a
    slot_w = max(2.0, W - T)
    slot_h = max(4.0, H - 2.0 * TF)
    o1 = BOX(s, L=W, W=H, H=L1).translate((L1 / 2.0, W / 2.0, 0.0))
    o_slot = BOX(s, L=slot_w + 10.0, W=slot_h, H=L1 + 20.0).translate((L1 / 2.0, T + (slot_w + 10.0) / 2.0, 0.0))
    o1.subtractFrom(o_slot); o_slot.erase()

    # 2. 根部混凝土预埋锚固端板 + 顶部与槽内焊接加劲肋 + 后侧预埋锚筋爪
    base_t = max(12.0, TF * 1.4)
    o_base = BOX(s, L=W + 70.0, W=H + 90.0, H=base_t).translate((-base_t / 2.0, W / 2.0, 10.0))
    o_rib_top = BOX(s, L=T * 1.6, W=55.0, H=75.0).translate((37.5, T / 2.0, H / 2.0 + 27.5))
    o_stiff = BOX(s, L=slot_w, W=slot_h, H=T * 1.5).translate((L, T + slot_w / 2.0, 0.0))
    o1.uniteWith(o_base); o_base.erase()
    o1.uniteWith(o_rib_top); o_rib_top.erase()
    o1.uniteWith(o_stiff); o_stiff.erase()

    s.setPoint((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (L, 0.0, 0.0))
