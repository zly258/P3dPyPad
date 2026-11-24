# -*- coding: utf-8 -*-
# CD-ZD2010 84042 混凝土梁端—端倒三角架（工字钢）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="84042工字钢倒三角架", TooltipLong="CD-ZD2010 84042 混凝土梁端—端倒三角架（工字钢）", LengthUnit="mm", Ports=1)
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
def ZD_84042(s, L=500.0, H=140.0, W=80.0, T=5.5, TF=9.1, ID=u"ZD_84042", Spec=u"I14", L_span=500.0, H_section=140.0, B_section=80.0, Load_kN=22.5, Weight_kg=15.0, **kw):
    L = float(L); H = float(H); W = float(W); T = float(T); TF = float(TF)
    if L <= 80.0: L = 400.0
    if H <= 30.0: H = 100.0
    if W <= 15.0: W = 48.0
    if T <= 1.5: T = 5.3
    if TF <= 2.0: TF = 8.5
    # 严格对照 cd_index_p378.png 与 ZD_84042_atlas.png (p.572)：
    # 84042 工字钢倒三角架：【下水平工字钢悬臂梁 (件 1) + 上部斜向工字钢拉杆 (件 2，位于水平梁上方 Z > 0！) + 根部竖直立柱与腹板加劲肋板 (件 3)】！
    ext_a = min(160.0, L * 0.35)
    L1 = L + ext_a
    i_slot_w = max(2.0, (W - T) / 2.0)
    i_slot_h = max(4.0, H - 2.0 * TF)

    # 1. 下部水平工字钢 I 悬臂主梁 (件 1，位于 Z = 0，对称双侧凹槽)
    o1 = BOX(s, L=W, W=H, H=L1).translate((L1 / 2.0, 0.0, 0.0))
    for sy in (-1.0, 1.0):
        o_c = BOX(s, L=i_slot_w + 10.0, W=i_slot_h, H=L1 + 20.0).translate((L1 / 2.0, sy * (T / 2.0 + (i_slot_w + 10.0) / 2.0), 0.0))
        o1.subtractFrom(o_c); o_c.erase()

    # 支点处双侧竖向腹板加劲肋 (件 3，对照 p.572 图示)
    stiff_t = max(8.0, T * 1.5)
    o_stiff = BOX(s, L=W - 2.0, W=i_slot_h, H=stiff_t).translate((L, 0.0, 0.0))
    o1.uniteWith(o_stiff); o_stiff.erase()

    # 2. 上部斜向工字钢拉杆 (件 2：位于水平梁上方 Z > 0！从根部上方 (0, 0, +dz) 斜向下连接至水平梁上翼缘 (L, 0, +H*0.42)，采用正角度 .rotateY(+angle_deg))
    dz = max(H * 2.2, L * 0.62)
    z_top_node = dz
    z_btm_node = H * 0.42
    dz_span = z_top_node - z_btm_node
    brace_l = sqrt(L * L + dz_span * dz_span)
    angle_deg = degrees(atan2(dz_span, L))

    o_br = BOX(s, L=W, W=H * 0.9, H=brace_l)
    for sy in (-1.0, 1.0):
        o_bc = BOX(s, L=i_slot_w + 10.0, W=i_slot_h * 0.88, H=brace_l + 20.0).translate((0.0, sy * (T / 2.0 + (i_slot_w + 10.0) / 2.0), 0.0))
        o_br.subtractFrom(o_bc); o_bc.erase()
    o_br.rotateY(angle_deg).translate((L / 2.0, 0.0, (z_top_node + z_btm_node) / 2.0))
    o1.uniteWith(o_br); o_br.erase()

    # 3. 根部竖直立柱与上下预埋生根端板、斜拉杆交汇加劲节点板
    base_t = 16.0
    o_wall_post = BOX(s, L=W, W=dz + H * 1.4, H=W * 0.65).translate((W * 0.325, 0.0, dz / 2.0))
    o_base_btm = BOX(s, L=W + 70.0, W=H + 90.0, H=base_t).translate((-base_t / 2.0, 0.0, 0.0))
    o_base_top = BOX(s, L=W + 70.0, W=H + 90.0, H=base_t).translate((-base_t / 2.0, 0.0, dz))
    o_gusset = BOX(s, L=T * 1.8, W=H * 0.85, H=130.0).translate((L - 25.0, 0.0, H * 0.45))
    for p in (o_wall_post, o_base_btm, o_base_top, o_gusset):
        o1.uniteWith(p); p.erase()

    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (L, 0.0, 0.0))
