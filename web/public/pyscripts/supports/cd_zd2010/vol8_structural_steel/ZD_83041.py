# -*- coding: utf-8 -*-
# CD-ZD2010 83041 混凝土梁端—端正三角架（双槽钢）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="83041双槽钢正三角架", TooltipLong="CD-ZD2010 83041 混凝土梁端—端正三角架（双槽钢）", LengthUnit="mm", Ports=1)
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
def ZD_83041(s, L=500.0, H=120.0, W=53.0, T=5.5, TF=9.0, ID=u"ZD_83041", Spec=u"[12", L_span=500.0, H_section=120.0, B_section=53.0, Load_kN=22.5, Weight_kg=15.0, **kw):
    L = float(L); H = float(H); W = float(W); T = float(T); TF = float(TF)
    if L <= 80.0: L = 400.0
    if H <= 30.0: H = 100.0
    if W <= 15.0: W = 48.0
    if T <= 1.5: T = 5.3
    if TF <= 2.0: TF = 8.5
    # 严格对照 cd_index_p378.png 与 ZD_83041_atlas.png (p.560)：
    # 83041 正三角架：【上水平双槽钢悬臂梁 (件 1) + 下部斜向双槽钢支撑压杆 (件 2，斜撑位于水平梁下方 Z < 0！) + 根部竖直贴壁双节点构造】！
    C_GAP = 60.0
    ext_a = min(160.0, L * 0.35)
    L1 = L + ext_a
    tot_w = W * 2.0 + C_GAP
    slot_w = max(2.0, W - T)
    slot_h = max(4.0, H - 2.0 * TF)

    # 1. 上部水平双槽钢背靠背悬臂主梁 (件 1，位于 Z = 0，沿 +X 伸出总长 L1)
    o1 = BOX(s, L=W, W=H, H=L1).translate((L1 / 2.0, -(C_GAP / 2.0 + W / 2.0), 0.0))
    o_c1 = BOX(s, L=slot_w + 10.0, W=slot_h, H=L1 + 20.0).translate((L1 / 2.0, -(C_GAP / 2.0 + T + (slot_w + 10.0) / 2.0), 0.0))
    o1.subtractFrom(o_c1); o_c1.erase()
    o2 = BOX(s, L=W, W=H, H=L1).translate((L1 / 2.0, (C_GAP / 2.0 + W / 2.0), 0.0))
    o_c2 = BOX(s, L=slot_w + 10.0, W=slot_h, H=L1 + 20.0).translate((L1 / 2.0, (C_GAP / 2.0 + T + (slot_w + 10.0) / 2.0), 0.0))
    o2.subtractFrom(o_c2); o_c2.erase()
    o1.uniteWith(o2); o2.erase()

    # 水平主梁顶面 [5 缀条/定位块与中间连接缀板
    batten_t = 10.0
    o_bat = BOX(s, L=tot_w, W=batten_t, H=80.0).translate((L, 0.0, (H / 2.0 + batten_t / 2.0)))
    o1.uniteWith(o_bat); o_bat.erase()

    # 2. 下部斜向双槽钢支撑杆 (件 2：位于水平梁下方 Z < 0！从根部下方 (0, 0, -dz) 斜向上连接至水平梁下缘 (L, 0, -H/2)，采用负角度 .rotateY(-angle_deg))
    dz = max(H * 2.2, L * 0.62)
    z_top_node = -(H * 0.35)
    z_btm_node = -dz
    dz_span = z_top_node - z_btm_node
    brace_l = sqrt(L * L + dz_span * dz_span)
    angle_deg = degrees(atan2(dz_span, L))
    for sy in (-1.0, 1.0):
        yb = sy * (C_GAP / 2.0 + W / 2.0)
        o_br = BOX(s, L=W, W=H * 0.88, H=brace_l).rotateY(-angle_deg).translate((L / 2.0, yb, (z_top_node + z_btm_node) / 2.0))
        o1.uniteWith(o_br); o_br.erase()

    # 3. 根部竖直贴壁双槽钢立柱与上下预埋节点板、交汇处中心节点板 (夹在双槽钢净距 C_GAP 之间)
    base_t = 16.0
    o_wall_post = BOX(s, L=tot_w, W=dz + H * 1.4, H=W * 0.85).translate((W * 0.425, 0.0, -dz / 2.0))
    o_base_top = BOX(s, L=tot_w + 60.0, W=H + 80.0, H=base_t).translate((-base_t / 2.0, 0.0, 0.0))
    o_base_btm = BOX(s, L=tot_w + 60.0, W=H + 80.0, H=base_t).translate((-base_t / 2.0, 0.0, -dz))
    o_gusset_join = BOX(s, L=C_GAP, W=H * 0.9, H=140.0).translate((L, 0.0, -(H * 0.25)))
    for p in (o_wall_post, o_base_top, o_base_btm, o_gusset_join):
        o1.uniteWith(p); p.erase()

    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (L, 0.0, 0.0))
