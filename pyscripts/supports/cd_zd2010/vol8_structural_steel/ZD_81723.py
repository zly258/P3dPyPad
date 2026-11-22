# -*- coding: utf-8 -*-
# CD-ZD2010 81723 包箍柱侧悬臂支架（无斜撑）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="81723包箍柱侧悬臂支架", TooltipLong="CD-ZD2010 81723 包箍柱侧悬臂支架（无斜撑）", LengthUnit="mm", Ports=1)
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
def ZD_81723(s, L=500.0, H=120.0, W=53.0, T=5.5, TF=9.0, ID=u"ZD_81723", Spec=u"[12", L_span=500.0, H_section=120.0, B_section=53.0, Load_kN=22.5, Weight_kg=15.0, **kw):
    L = float(L); H = float(H); W = float(W); T = float(T); TF = float(TF)
    if L <= 80.0: L = 400.0
    if H <= 30.0: H = 100.0
    if W <= 15.0: W = 48.0
    if T <= 1.5: T = 5.3
    if TF <= 2.0: TF = 8.5
    # 严格对照 cd_index_p375.png 与 ZD_81723_atlas.png (p.446)：
    # 抱紧方形混凝土柱身 (A × B) 的前后横向槽钢包箍 (件 4，带四角对穿长螺杆件 3 与贴柱垫板件 5) + 向 +X 侧水平伸出的双平行槽钢悬臂框 (件 1 + 前端横梁件 2)！
    col_A = max(360.0, min(550.0, L * 0.70))
    col_B = max(360.0, min(550.0, L * 0.70))
    L2_span = col_A + W + 40.0  # 左右两根水平悬臂槽钢紧贴柱两侧向外伸出
    ext_a = max(110.0, W * 2.2, min(180.0, L * 0.3))
    L1 = col_B + L + ext_a
    x_start = -col_B - 40.0
    x_mid = x_start + L1 / 2.0
    slot_w = max(2.0, W - T)
    slot_h = max(4.0, H - 2.0 * TF)

    # 1. 左右两根沿 X 轴夹持柱两侧并向 +X 伸出的平行水平悬臂槽钢主梁 (件 1)
    o1 = None
    for sy in (-1.0, 1.0):
        ym = sy * (L2_span / 2.0)
        o_arm = BOX(s, L=W, W=H, H=L1).translate((x_mid, ym, 0.0))
        o_cut = BOX(s, L=slot_w + 10.0, W=slot_h, H=L1 + 20.0).translate((x_mid, ym - sy * (T + (slot_w - W) / 2.0 + 5.0), 0.0))
        o_arm.subtractFrom(o_cut); o_cut.erase()
        if o1 is None:
            o1 = o_arm
        else:
            o1.uniteWith(o_arm); o_arm.erase()

    # 2. 悬臂框前端的两道横向连接槽钢横梁 (件 2，位于 X = L 附近)
    c_cross = max(80.0, W * 1.6)
    cross_len = L2_span - W + 10.0
    for xc in (L - c_cross / 2.0, L + c_cross / 2.0):
        o_cr = BOX(s, L=cross_len, W=H, H=W).translate((xc, 0.0, 0.0))
        o1.uniteWith(o_cr); o_cr.erase()

    # 3. 抱紧方形混凝土柱身 (X in [-col_B, 0]) 的前后横向槽钢包箍 (件 4) + 四角竖向/水平对穿双头螺杆 (件 3) + 柱面垫板 (件 5)
    clamp_y = L2_span + W * 2.0 + 100.0
    for x_hoop in (-col_B - W * 0.6, W * 0.6):
        # 上下两根横向夹柱槽钢 (件 4)
        for sz in (-1.0, 1.0):
            zh = sz * (H / 2.0 + W * 0.42)
            o_hch = BOX(s, L=clamp_y, W=W, H=H * 0.65).translate((x_hoop, 0.0, zh))
            o1.uniteWith(o_hch); o_hch.erase()

    # 两侧贯通柱前后的水平对穿长螺杆与螺母 (件 3)
    rod_r = 14.0
    rod_len = col_B + W * 3.0 + 80.0
    for sy in (-1.0, 1.0):
        yr = sy * (L2_span / 2.0 + W * 0.45)
        for sz in (-1.0, 1.0):
            zr = sz * (H / 2.0 + W * 0.42)
            o_rod = CYLINDER(s, R=rod_r, H=rod_len, O=0.0).rotateY(90.0).translate((-(col_B + W * 1.5 + 40.0), yr, zr))
            o1.uniteWith(o_rod); o_rod.erase()

    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (L, 0.0, 0.0))
