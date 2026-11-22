# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
# VALVE_GATE: AutoCAD Plant 3D 工业级法兰连接明杆楔式闸阀 (Rising Stem Gate Valve Z41H)
# 几何特征：两端高颈法兰 + 扁圆膨胀闸板腔 + 螺栓连接中法兰阀盖 + 填料函压盖 + 横向对称双立柱支架 + 明杆梯形螺杆 + 四辐条手轮
import math
from aqa.math import *
from varmain.primitiv import *
from varmain.divsub.divutil import *
from varmain.custom import *


@activate(Group="Valve", TooltipShort=u"明杆楔式闸阀", TooltipLong=u"工业级法兰连接明杆楔式闸阀总成（Z41H 带螺栓中法兰、双柱支架与手轮）", LengthUnit="mm", Ports=2)
@group("MainDimensions", TooltipLong=u"闸阀主要结构尺寸")
@param(D=LENGTH, TooltipShort=u"公称外径", TooltipLong=u"管道公称外径 OD")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"两端法兰密封面间距 Face-to-Face", Ask4Dist=True)
@param(H=LENGTH, TooltipShort=u"总装高度", TooltipLong=u"管道轴线至手轮顶部中心总装高度")
@param(W_DIA=LENGTH0, TooltipShort=u"手轮直径", TooltipLong=u"手轮外圈回转直径，0时自动匹配")
@param(FL_OD=LENGTH0, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径，0时自动匹配")
@param(FL_T=LENGTH0, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度，0时自动匹配")
@param(ID=STRING, TooltipShort=u"阀门位号", TooltipLong=u"阀门标识位号，如 GV-101")
@param(SPEC=STRING, TooltipShort=u"规格型号", TooltipLong=u"公称压力等级，如 Z41H-16C DN100")
def VALVE_GATE(s, D=114.3, L=230.0, H=420.0, W_DIA=0.0, FL_OD=0.0, FL_T=0.0, ID=u"GATE-DN100", SPEC=u"Z41H-16C DN100", **kw):
    D = float(D)
    L = float(L)
    H = float(H)
    W_DIA = float(W_DIA)
    FL_OD = float(FL_OD)
    FL_T = float(FL_T)

    r_pipe = D / 2.0
    if FL_OD <= D:
        FL_OD = D * 1.85
    r_flange = FL_OD / 2.0

    if FL_T <= 0.0:
        FL_T = max(18.0, D * 0.18)

    if L <= 2.0 * FL_T + 20.0:
        L = 2.0 * FL_T + D

    if H <= D * 2.2:
        H = D * 3.5

    if W_DIA <= 0.0:
        W_DIA = max(180.0, D * 1.85)
    r_wheel = W_DIA / 2.0

    xc = L / 2.0  # 阀体中心 X

    # 1. 两端连接法兰盘 (带密封面凸台 RF)
    rf_h = 3.0
    rf_r = r_pipe * 1.32
    o_main = CYLINDER(s, R=rf_r, H=rf_h + 1.0, O=0.0).rotateY(90.0).translate((0.0, 0.0, 0.0))
    o_fl1 = CYLINDER(s, R=r_flange, H=FL_T, O=0.0).rotateY(90.0).translate((rf_h, 0.0, 0.0))
    o_main.uniteWith(o_fl1); o_fl1.erase()

    o_rf2 = CYLINDER(s, R=rf_r, H=rf_h + 1.0, O=0.0).rotateY(-90.0).translate((L, 0.0, 0.0))
    o_main.uniteWith(o_rf2); o_rf2.erase()
    o_fl2 = CYLINDER(s, R=r_flange, H=FL_T, O=0.0).rotateY(-90.0).translate((L - rf_h, 0.0, 0.0))
    o_main.uniteWith(o_fl2); o_fl2.erase()

    # 2. 水平流道筒体 (两端与法兰背面融合)
    body_pipe_len = L - 2.0 * (rf_h + FL_T) + 4.0
    if body_pipe_len > 0.0:
        o_bpipe = CYLINDER(s, R=r_pipe * 1.18, H=body_pipe_len, O=0.0).rotateY(90.0).translate((rf_h + FL_T - 2.0, 0.0, 0.0))
        o_main.uniteWith(o_bpipe); o_bpipe.erase()

    # 3. 楔式闸阀扁圆闸板腔与底部圆弧包底 (顺管向紧凑、横管向宽阔，还原真实闸阀阀体比例)
    cav_rx = min(r_pipe * 1.12, (L - 2.0 * FL_T) * 0.42)
    cav_ry = r_pipe * 1.35
    cav_h = r_pipe * 1.45
    o_cav_bot = ELLIPSOIDHEAD(s, R=cav_rx, H=cav_ry * 0.55).rotateX(180.0).translate((xc, 0.0, -r_pipe * 0.35))
    o_main.uniteWith(o_cav_bot); o_cav_bot.erase()

    o_cav_mid = CYLINDER(s, R1=cav_rx, R2=cav_ry, H=cav_h + r_pipe * 0.35, O=0.0).translate((xc, 0.0, -r_pipe * 0.35))
    o_main.uniteWith(o_cav_mid); o_cav_mid.erase()

    # 4. 阀体-阀盖连接中法兰 (Bonnet Flange + 均布六角螺栓)
    z_bonnet = cav_h
    bon_rx = cav_rx * 1.28
    bon_ry = cav_ry * 1.25
    bon_t = max(14.0, FL_T * 0.72)
    o_bon_fl = CYLINDER(s, R1=bon_rx, R2=bon_ry, H=bon_t * 2.0, O=0.0).translate((xc, 0.0, z_bonnet - bon_t))
    o_main.uniteWith(o_bon_fl); o_bon_fl.erase()

    bolt_w = max(10.0, r_pipe * 0.22)
    bolt_h = max(6.0, bon_t * 0.45)
    for i in range(6):
        ang = (float(i) / 6.0) * 2.0 * math.pi
        bx = xc + (bon_rx * 0.82) * math.cos(ang)
        by = (bon_ry * 0.82) * math.sin(ang)
        o_bn = NUT_BOLT_HEAD_6_001(s, W=bolt_w, H=bolt_h).rotateY(-90.0).translate((bx, by, z_bonnet + bon_t - 1.0))
        o_main.uniteWith(o_bn); o_bn.erase()

    # 5. 阀盖锥颈与填料函压盖 (Stuffing Box & Gland Follower)
    cone_h = max(36.0, D * 0.42)
    r_stuff = r_pipe * 0.56
    o_cone = CONE(s, R1=cav_rx * 0.92, R2=r_stuff, H=cone_h).translate((xc, 0.0, z_bonnet + bon_t - 2.0))
    o_main.uniteWith(o_cone); o_cone.erase()

    z_gland = z_bonnet + bon_t + cone_h - 2.0
    gland_h = max(14.0, D * 0.14)
    # 填料压盖法兰 (横向椭圆耳板 BOX)
    o_gland = BOX(s, L=r_stuff * 2.8, W=gland_h * 0.65, H=r_stuff * 1.8).translate((xc, 0.0, z_gland + gland_h * 0.5))
    o_main.uniteWith(o_gland); o_gland.erase()
    o_gneck = CYLINDER(s, R=r_stuff * 1.15, H=gland_h, O=0.0).translate((xc, 0.0, z_gland))
    o_main.uniteWith(o_gneck); o_gneck.erase()

    # 6. Yoke 双立柱支架 (严格沿横管向 Y=±col_spread 对称布置，修正旧版 BOX 轴向错误)
    z_yoke_base = z_gland + gland_h * 0.8
    z_wheel = H - 28.0
    yoke_h = max(75.0, z_wheel - z_yoke_base - 18.0)
    col_thick_x = max(10.0, D * 0.11)  # 顺管向厚度 (对应 BOX 的 H)
    col_width_y = max(12.0, D * 0.13)  # 横管向宽度 (对应 BOX 的 L)
    col_spread_y = r_stuff * 1.08

    # 原生 BOX(s, L, W, H): H 沿 X, L 沿 Y, W 沿 Z (高度)
    o_col1 = BOX(s, L=col_width_y, W=yoke_h, H=col_thick_x).translate((xc, -col_spread_y, z_yoke_base + yoke_h / 2.0))
    o_main.uniteWith(o_col1); o_col1.erase()
    o_col2 = BOX(s, L=col_width_y, W=yoke_h, H=col_thick_x).translate((xc, +col_spread_y, z_yoke_base + yoke_h / 2.0))
    o_main.uniteWith(o_col2); o_col2.erase()

    # 支架顶部手轮轴承座 (Yoke Head & Stem Nut)
    yoke_top_h = 20.0
    o_ybridge = BOX(s, L=col_spread_y * 2.0 + col_width_y, W=yoke_top_h * 0.7, H=col_thick_x * 1.4).translate((xc, 0.0, z_yoke_base + yoke_h))
    o_main.uniteWith(o_ybridge); o_ybridge.erase()
    o_ytop = CYLINDER(s, R=col_spread_y * 0.95, H=yoke_top_h, O=0.0).translate((xc, 0.0, z_yoke_base + yoke_h - 4.0))
    o_main.uniteWith(o_ytop); o_ytop.erase()

    # 7. 明杆梯形螺纹上升阀杆 (Rising Stem)
    stem_r = max(7.0, D * 0.09)
    o_stem = CYLINDER(s, R=stem_r, H=H - z_bonnet, O=0.0).translate((xc, 0.0, z_bonnet))
    o_main.uniteWith(o_stem); o_stem.erase()

    # 8. 经典四辐条手轮 + 顶部锁紧六角螺母 (Handwheel)
    wheel_rim_t = max(10.0, r_wheel * 0.11)
    o_rim = TORUS(s, R1=r_wheel - wheel_rim_t * 0.5, R2=wheel_rim_t * 0.55).translate((xc, 0.0, z_wheel))
    o_main.uniteWith(o_rim); o_rim.erase()

    hub_r = max(15.0, stem_r * 2.2)
    o_whub = CYLINDER(s, R=hub_r, H=wheel_rim_t * 1.3, O=0.0).translate((xc, 0.0, z_wheel - wheel_rim_t * 0.65))
    o_main.uniteWith(o_whub); o_whub.erase()

    spoke_r = max(4.0, wheel_rim_t * 0.36)
    spoke_len = r_wheel - wheel_rim_t * 0.4
    for i in range(4):
        ang = float(i) * 90.0
        o_spk = CYLINDER(s, R=spoke_r, H=spoke_len, O=0.0).rotateY(90.0).rotateZ(ang).translate((xc, 0.0, z_wheel))
        o_main.uniteWith(o_spk); o_spk.erase()

    # 手轮顶部锁紧螺母
    o_wnut = NUT_BOLT_HEAD_6_001(s, W=stem_r * 3.2, H=wheel_rim_t * 0.8).rotateY(-90.0).translate((xc, 0.0, z_wheel + wheel_rim_t * 0.65))
    o_main.uniteWith(o_wnut); o_wnut.erase()

    # 9. 贯通内流道掏空
    r_core = r_pipe * 0.90
    o_flow = CYLINDER(s, R=r_core, H=L + 10.0, O=0.0).rotateY(90.0).translate((-5.0, 0.0, 0.0))
    o_main.subtractFrom(o_flow)
    o_flow.erase()

    # 10. 端口定义与轴测尺寸标注锚点
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L, 0.0, 0.0), (1.0, 0.0, 0.0))

    s.setLinearDimension("H", (0.0, 0.0, 0.0), (0.0, 0.0, H))
    s.setLinearDimension("FL_OD", (0.0, 0.0, -r_flange), (0.0, 0.0, r_flange))
    s.setLinearDimension("L", (0.0, 0.0, -r_flange), (L, 0.0, -r_flange))
    s.setLinearDimension("W_DIA", (xc, -r_wheel, z_wheel), (xc, r_wheel, z_wheel))
    s.setLinearDimension("D", (L, 0.0, -r_pipe), (L, 0.0, r_pipe))
