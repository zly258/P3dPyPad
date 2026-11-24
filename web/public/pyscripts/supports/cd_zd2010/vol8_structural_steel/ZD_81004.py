# -*- coding: utf-8 -*-
# CD-ZD2010 81004 混凝土梁端悬臂支架（带斜撑）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="81004带斜撑悬臂支架", TooltipLong="CD-ZD2010 81004 混凝土梁端悬臂支架（带斜撑）", LengthUnit="mm", Ports=1)
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
def ZD_81004(s, L=500.0, H=120.0, W=53.0, T=5.5, TF=9.0, ID=u"ZD_81004", Spec=u"[12", L_span=500.0, H_section=120.0, B_section=53.0, Load_kN=22.5, Weight_kg=15.0, **kw):
    L = float(L); H = float(H); W = float(W); T = float(T); TF = float(TF)
    if L <= 80.0: L = 400.0
    if H <= 30.0: H = 100.0
    if W <= 15.0: W = 48.0
    if T <= 1.5: T = 5.3
    if TF <= 2.0: TF = 8.5
    # 严格对照 cd_index_p375.png 与 ZD_81004_atlas.png (p.434)：
    # 在 ZD_81003 水平双臂悬臂框基础上，在水平框内 (XY 平面内！) 增加【十字交叉对角斜撑角钢/槽钢 (件 4)】！
    L2_span = max(320.0, min(600.0, L * 0.75))
    ext_a = min(150.0, L * 0.25)
    L1 = L + ext_a
    slot_w = max(2.0, W - T)
    slot_h = max(4.0, H - 2.0 * TF)

    # 1. 左右两根宽间距平行水平悬臂槽钢主梁 (件 1) + 根部生根板与上下腋板 (件 3)
    o1 = None
    for sy in (-1.0, 1.0):
        ym = sy * (L2_span / 2.0)
        o_arm = BOX(s, L=W, W=H, H=L1).translate((L1 / 2.0, ym, 0.0))
        o_cut = BOX(s, L=slot_w + 10.0, W=slot_h, H=L1 + 20.0).translate((L1 / 2.0, ym - sy * (T + (slot_w - W) / 2.0 + 5.0), 0.0))
        o_arm.subtractFrom(o_cut); o_cut.erase()
        base_t = 16.0
        o_base = BOX(s, L=W + 70.0, W=H + 110.0, H=base_t).translate((-base_t / 2.0, ym, 0.0))
        o_rt = BOX(s, L=12.0, W=55.0, H=85.0).translate((42.5, ym, H / 2.0 + 27.5))
        o_rb = BOX(s, L=12.0, W=55.0, H=85.0).translate((42.5, ym, -(H / 2.0 + 27.5)))
        for p in (o_base, o_rt, o_rb):
            o_arm.uniteWith(p); p.erase()
        if o1 is None:
            o1 = o_arm
        else:
            o1.uniteWith(o_arm); o_arm.erase()

    # 2. 前端横向连接双槽钢横梁 (件 2，间距 c_cross)
    c_cross = max(80.0, W * 1.6)
    cross_len = L2_span - W + 10.0
    x_inner_cross = L - c_cross / 2.0
    for xc in (x_inner_cross, L + c_cross / 2.0):
        o_cr = BOX(s, L=cross_len, W=H, H=W).translate((xc, 0.0, 0.0))
        o1.uniteWith(o_cr); o_cr.erase()

    # 3. 水平面 (XY 平面) 内的十字交叉对角斜撑构件 (件 4，绕 Z 轴旋转 ±diag_ang 连接根部至前端横梁内侧，对照 p.434 俯视图)
    dx_diag = max(120.0, x_inner_cross - W * 0.5)
    dy_diag = L2_span - W
    diag_len = sqrt(dx_diag * dx_diag + dy_diag * dy_diag)
    diag_ang = degrees(atan2(dy_diag, dx_diag))
    brace_w = max(36.0, W * 0.72)
    brace_h = max(12.0, H * 0.45)
    for s_ang in (-1.0, 1.0):
        o_diag = BOX(s, L=brace_w, W=brace_h, H=diag_len).rotateZ(s_ang * diag_ang).translate((dx_diag / 2.0 + W * 0.25, 0.0, 0.0))
        o1.uniteWith(o_diag); o_diag.erase()

    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (L, 0.0, 0.0))
