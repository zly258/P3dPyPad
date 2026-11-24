# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
# SUPPORT_BEAM_BOLTED_HANGER: AutoCAD Plant 3D 标准带螺栓管夹长吊杆支吊架 (Beam Bolted Hanger)
# 100% 还原官方构件库 Beam Bolted Hanger 几何特征与参数定义 (D, K, H, W, L, HD3, SH, OH)
from aqa.math import *
from varmain.primitiv import *
from varmain.divsub.divutil import *
from varmain.custom import *


@activate(Group="Support", TooltipShort=u"双耳管夹吊杆吊架", TooltipLong=u"标准梁夹螺栓吊杆分瓣管夹吊架总成 (Beam Bolted Hanger)", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong=u"吊架主要结构尺寸")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被吊挂管道公称外径 OD")
@param(K=LENGTH, TooltipShort=u"管夹总高", TooltipLong=u"上下扁钢抱箍耳板外缘总高")
@param(H=LENGTH, TooltipShort=u"吊杆高度", TooltipLong=u"管道中心线至上部梁底安装高度", Ask4Dist=True)
@param(W=LENGTH, TooltipShort=u"耳板间隙", TooltipLong=u"左右两瓣抱箍耳板之间的夹紧净距")
@param(L=LENGTH, TooltipShort=u"抱箍宽度", TooltipLong=u"抱箍扁钢顺管向宽度")
@param(HD3=LENGTH, TooltipShort=u"吊杆直径", TooltipLong=u"长吊杆圆钢/螺杆公称直径")
@param(SH=LENGTH0, TooltipShort=u"梁翼缘厚", TooltipLong=u"上部型钢梁翼缘板夹持厚度")
@param(OH=LENGTH0, TooltipShort=u"顶部伸出", TooltipLong=u"吊杆穿过上部锁紧螺母后的顶部外露长度")
@param(ID=STRING, TooltipShort=u"吊架位号", TooltipLong=u"支吊架标识编号，如 BH-101")
def SUPPORT_BEAM_BOLTED_HANGER(
    s,
    D=114.3,
    K=170.0,
    H=380.0,
    W=12.0,
    L=40.0,
    HD3=16.0,
    SH=14.0,
    OH=22.0,
    ID=u"BH-DN100",
    **kw
):
    D = float(D)
    K = float(K)
    H = float(H)
    W = float(W)
    L = float(L)
    HD3 = float(HD3)
    SH = float(SH)
    OH = float(OH)

    r_pipe = D / 2.0
    t_bar = max(6.0, L * 0.16)
    if K <= D + 2.0 * t_bar + 20.0:
        K = D + 2.0 * t_bar + 45.0
    if W <= 4.0:
        W = 10.0
    if L <= 16.0:
        L = 36.0
    if HD3 <= 6.0:
        HD3 = 14.0
    if SH <= 4.0:
        SH = 12.0
    if OH <= 8.0:
        OH = 20.0
    if H <= K / 2.0 + 60.0:
        H = K / 2.0 + 180.0

    r_out = r_pipe + t_bar
    half_gap = W / 2.0

    # 1. 分瓣抱箍圆环主体 (管轴沿 Y，圆环截面在 XZ 平面，正对左下方等轴测视角)
    o_main = CYLINDER(s, R=r_out, H=L, O=0.0).rotateX(-90.0).translate((0.0, -L / 2.0, 0.0))

    # 2. 上下抱箍紧固立耳板 (左右两瓣在 X=±(half_gap + t_bar/2) 处立起，中间留夹紧缝隙 W)
    ear_h = max(18.0, (K / 2.0) - r_pipe)
    z_top_ear_mid = r_pipe + ear_h / 2.0
    z_bot_ear_mid = -(r_pipe + ear_h / 2.0)
    x_ear_left = -(half_gap + t_bar / 2.0)
    x_ear_right = +(half_gap + t_bar / 2.0)

    # 原生 BOX(s, L, W, H): H 沿 X, L 沿 Y, W 沿 Z
    o_tl = BOX(s, L=L, W=ear_h + 6.0, H=t_bar).translate((x_ear_left, 0.0, z_top_ear_mid - 3.0))
    o_tr = BOX(s, L=L, W=ear_h + 6.0, H=t_bar).translate((x_ear_right, 0.0, z_top_ear_mid - 3.0))
    o_bl = BOX(s, L=L, W=ear_h + 6.0, H=t_bar).translate((x_ear_left, 0.0, z_bot_ear_mid + 3.0))
    o_br = BOX(s, L=L, W=ear_h + 6.0, H=t_bar).translate((x_ear_right, 0.0, z_bot_ear_mid + 3.0))
    o_main.uniteWith(o_tl); o_tl.erase()
    o_main.uniteWith(o_tr); o_tr.erase()
    o_main.uniteWith(o_bl); o_bl.erase()
    o_main.uniteWith(o_br); o_br.erase()

    # 上耳顶部连接横桥承板 (用于穿入中央吊杆并承载下部锁紧螺母)
    bridge_w = W + 2.0 * t_bar
    bridge_t = t_bar
    o_bridge = BOX(s, L=L, W=bridge_t, H=bridge_w).translate((0.0, 0.0, K / 2.0 - bridge_t / 2.0))
    o_main.uniteWith(o_bridge); o_bridge.erase()

    # 3. 切除管道通径内孔与上下夹紧缝隙槽 W
    o_bore = CYLINDER(s, R=r_pipe, H=L + 10.0, O=0.0).rotateX(-90.0).translate((0.0, -(L / 2.0 + 5.0), 0.0))
    o_main.subtractFrom(o_bore); o_bore.erase()

    # 下耳板通缝与上耳板下部夹紧缝 (保留顶部横桥连接成单一连通体)
    o_slot_bot = BOX(s, L=L + 10.0, W=K / 2.0 + 10.0, H=W).translate((0.0, 0.0, -(K / 4.0 + 2.0)))
    o_main.subtractFrom(o_slot_bot); o_slot_bot.erase()
    slot_top_h = max(4.0, K / 2.0 - bridge_t - r_pipe + 4.0)
    o_slot_top = BOX(s, L=L + 10.0, W=slot_top_h, H=W).translate((0.0, 0.0, r_pipe + slot_top_h / 2.0 - 2.0))
    o_main.subtractFrom(o_slot_top); o_slot_top.erase()

    # 4. 中央垂直长吊杆 (从上耳板内部一直延伸至 H + SH + OH)
    r_rod = HD3 / 2.0
    z_rod_start = K / 2.0 - bridge_t
    z_rod_top = H + SH + OH
    rod_len = z_rod_top - z_rod_start
    o_rod = CYLINDER(s, R=r_rod, H=rod_len, O=0.0).translate((0.0, 0.0, z_rod_start))
    o_main.uniteWith(o_rod); o_rod.erase()

    # 5. 吊杆六角螺母与垫圈 (管夹顶部螺母 + 顶部双螺母组件)
    nut_w = HD3 * 1.65
    nut_h = max(8.0, HD3 * 0.65)
    washer_r = nut_w * 0.62
    washer_t = max(2.5, HD3 * 0.16)

    # 5.1 管夹顶部锁紧螺母 (Z = K/2 处)
    o_w1 = CYLINDER(s, R=washer_r, H=washer_t, O=0.0).translate((0.0, 0.0, K / 2.0))
    o_main.uniteWith(o_w1); o_w1.erase()
    o_nut1 = NUT_BOLT_HEAD_6_001(s, W=nut_w, H=nut_h).rotateY(-90.0).translate((0.0, 0.0, K / 2.0 + washer_t))
    o_main.uniteWith(o_nut1); o_nut1.erase()

    # 5.2 顶部梁夹双锁紧螺母组件 (位于 Z = H + SH 处)
    z_beam_top = H + SH
    o_w2 = CYLINDER(s, R=washer_r, H=washer_t, O=0.0).translate((0.0, 0.0, z_beam_top - washer_t))
    o_main.uniteWith(o_w2); o_w2.erase()
    o_nut2 = NUT_BOLT_HEAD_6_001(s, W=nut_w, H=nut_h).rotateY(-90.0).translate((0.0, 0.0, z_beam_top))
    o_main.uniteWith(o_nut2); o_nut2.erase()
    o_nut3 = NUT_BOLT_HEAD_6_001(s, W=nut_w, H=nut_h).rotateY(-90.0).translate((0.0, 0.0, z_beam_top + nut_h))
    o_main.uniteWith(o_nut3); o_nut3.erase()

    # 6. 端口定义与 8 项原厂轴测尺寸标注锚点 (100% 对应 Beam Bolted Hanger 预览图)
    s.setPoint((0.0, 0.0, 0.0), (0.0, 1.0, 0.0))

    # 左侧分层与共线链式竖直尺寸: D (内径) -> K (抱箍总高) -> H + SH + OH
    s.setLinearDimension("D", (-r_pipe * 0.35, -L / 2.0, -r_pipe), (-r_pipe * 0.35, -L / 2.0, r_pipe))
    s.setLinearDimension("K", (0.0, -L / 2.0, -K / 2.0), (0.0, -L / 2.0, K / 2.0))
    s.setLinearDimension("H", (0.0, 0.0, 0.0), (0.0, 0.0, H))
    s.setLinearDimension("SH", (0.0, 0.0, H), (0.0, 0.0, H + SH))
    s.setLinearDimension("OH", (0.0, 0.0, H + SH), (0.0, 0.0, H + SH + OH))

    # 下部耳板间隙 W 与抱箍宽度 L
    s.setLinearDimension("W", (-half_gap, -L / 2.0, -K / 2.0), (half_gap, -L / 2.0, -K / 2.0))
    s.setLinearDimension("L", (r_out * 0.72, -L / 2.0, -r_out * 0.72), (r_out * 0.72, L / 2.0, -r_out * 0.72))

    # 中部吊杆直径 HD3
    z_hd3 = K / 2.0 + (H - K / 2.0) * 0.52
    s.setLinearDimension("HD3", (-r_rod, 0.0, z_hd3), (r_rod, 0.0, z_hd3))
