# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
# SUPPORT_PIPE_CLAMP: AutoCAD Plant 3D 标准带管卡滑动管托支架 (Pipe Clamp Shoe Support HG/T 21629)
# 几何特征：上下分瓣扁钢抱箍 + 两侧双耳板与六角紧固螺栓/螺母 + 顺管向中央承重立板 + 横向双加劲肋板 + 带地脚槽孔滑动底板
from aqa.math import *
from varmain.primitiv import *
from varmain.divsub.divutil import *
from varmain.custom import *


@activate(Group="Support", TooltipShort=u"管卡滑动管托", TooltipLong=u"标准管道管卡焊接滑动管托总成（HG/T 21629 带双耳紧固螺栓、加劲肋与底座）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong=u"管托主要结构尺寸")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支撑管道公称外径 OD")
@param(H=LENGTH, TooltipShort=u"支架总高", TooltipLong=u"管中心线至底板底面的总装安装高度", Ask4Dist=True)
@param(L_SHOE=LENGTH, TooltipShort=u"管托长度", TooltipLong=u"顺管向立板与底板总长度")
@param(W_BASE=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"横管向支承底板宽度")
@param(T_BASE=LENGTH0, TooltipShort=u"底板厚度", TooltipLong=u"底板钢板公称厚度")
@param(T_CLAMP=LENGTH0, TooltipShort=u"管卡板厚", TooltipLong=u"抱箍扁钢厚度，0时自动匹配")
@param(W_CLAMP=LENGTH0, TooltipShort=u"管卡板宽", TooltipLong=u"抱箍扁钢宽度，0时自动匹配")
@param(ID=STRING, TooltipShort=u"支架位号", TooltipLong=u"支架编号，如 PS-101")
def SUPPORT_PIPE_CLAMP(s, D=114.3, H=150.0, L_SHOE=200.0, W_BASE=160.0, T_BASE=10.0, T_CLAMP=0.0, W_CLAMP=0.0, ID=u"PS-DN100-H150", **kw):
    D = float(D)
    H = float(H)
    L_SHOE = float(L_SHOE)
    W_BASE = float(W_BASE)
    T_BASE = float(T_BASE)
    T_CLAMP = float(T_CLAMP)
    W_CLAMP = float(W_CLAMP)

    r_pipe = D / 2.0
    if T_CLAMP <= 0.0:
        T_CLAMP = max(6.0, D * 0.055)
    if W_CLAMP <= 0.0:
        W_CLAMP = max(40.0, D * 0.35)
    if T_BASE <= 0.0:
        T_BASE = 10.0
    if H <= (r_pipe + T_BASE + 25.0):
        H = r_pipe + T_BASE + 55.0
    if W_BASE <= (D + 40.0):
        W_BASE = D + 70.0
    if L_SHOE <= W_CLAMP * 1.4:
        L_SHOE = W_CLAMP * 1.8

    r_clamp_out = r_pipe + T_CLAMP
    ear_gap = max(10.0, T_CLAMP * 1.6)
    ear_ext = max(36.0, D * 0.32)

    # 1. 上下分瓣抱箍圆环主体（沿 X 轴居中，宽 W_CLAMP）
    o_main = CYLINDER(s, R=r_clamp_out, H=W_CLAMP, O=0.0).rotateY(90.0).translate((-W_CLAMP / 2.0, 0.0, 0.0))

    # 2. 抱箍左右水平紧固外耳板 (Upper & Lower Ear Plates, 留出上下夹紧间隙 ear_gap)
    z_upper_ear = ear_gap / 2.0 + T_CLAMP / 2.0
    z_lower_ear = -(ear_gap / 2.0 + T_CLAMP / 2.0)
    y_ear_center = r_pipe + ear_ext / 2.0

    # 原生 BOX(s, L, W, H): H 沿 X (W_CLAMP), L 沿 Y (ear_ext), W 沿 Z (T_CLAMP)
    for sign_y in (1.0, -1.0):
        o_eu = BOX(s, L=ear_ext + 6.0, W=T_CLAMP, H=W_CLAMP).translate((0.0, sign_y * (y_ear_center - 3.0), z_upper_ear))
        o_el = BOX(s, L=ear_ext + 6.0, W=T_CLAMP, H=W_CLAMP).translate((0.0, sign_y * (y_ear_center - 3.0), z_lower_ear))
        o_main.uniteWith(o_eu); o_eu.erase()
        o_main.uniteWith(o_el); o_el.erase()

    # 切除左右耳板之间的水平夹紧缝隙槽 (仅切两侧外耳区，保留抱箍圆环与下部腹板连接)
    for sign_y in (1.0, -1.0):
        o_gap = BOX(s, L=ear_ext + 20.0, W=ear_gap, H=W_CLAMP + 10.0).translate((0.0, sign_y * (r_clamp_out + ear_ext * 0.5), 0.0))
        o_main.subtractFrom(o_gap); o_gap.erase()

    # 3. 左右双耳紧固螺栓与上下六角螺母 (穿过上下耳板并将其锁紧融合)
    bolt_r = max(5.5, T_CLAMP * 0.85)
    nut_w = bolt_r * 3.3
    nut_h = max(7.0, bolt_r * 1.3)
    bolt_h = ear_gap + 2.0 * T_CLAMP + 2.0 * nut_h + 12.0
    bolt_y = r_pipe + ear_ext * 0.58

    for sign_y in (1.0, -1.0):
        by = sign_y * bolt_y
        o_bolt = CYLINDER(s, R=bolt_r, H=bolt_h, O=0.0).translate((0.0, by, -bolt_h / 2.0))
        o_main.uniteWith(o_bolt); o_bolt.erase()
        # 上螺母与下螺母
        o_nt = NUT_BOLT_HEAD_6_001(s, W=nut_w, H=nut_h).rotateY(-90.0).translate((0.0, by, ear_gap / 2.0 + T_CLAMP))
        o_nb = NUT_BOLT_HEAD_6_001(s, W=nut_w, H=nut_h).rotateY(90.0).translate((0.0, by, -(ear_gap / 2.0 + T_CLAMP)))
        o_main.uniteWith(o_nt); o_nt.erase()
        o_main.uniteWith(o_nb); o_nb.erase()

    # 4. 下部弧形鞍板与顺管向中央承重立板 + 横向加劲肋板 (消除旧版两侧过高挡墙缺陷)
    t_web = max(8.0, T_CLAMP * 1.15)
    # 4.1 顺管向 120° 弧形承托鞍板 (长 L_SHOE，紧贴管道下半周)
    o_cradle = CYLINDER(s, R=r_clamp_out, H=L_SHOE, O=0.0).rotateY(90.0).translate((-L_SHOE / 2.0, 0.0, 0.0))
    o_cradle_cut = BOX(s, L=r_clamp_out * 2.5, W=r_clamp_out * 1.6, H=L_SHOE + 10.0).translate((0.0, 0.0, r_clamp_out * 0.45))
    o_cradle.subtractFrom(o_cradle_cut); o_cradle_cut.erase()
    o_main.uniteWith(o_cradle); o_cradle.erase()

    # 4.2 顺管向中央纵向主立板 (从管道底部直达底板顶面)
    web_top_z = -r_pipe * 0.72
    web_bot_z = -H + T_BASE
    web_h = max(16.0, web_top_z - web_bot_z)
    z_web_mid = web_bot_z + web_h / 2.0
    o_web = BOX(s, L=t_web, W=web_h + 4.0, H=L_SHOE).translate((0.0, 0.0, z_web_mid))
    o_main.uniteWith(o_web); o_web.erase()

    # 4.3 横向对称加劲肋板 (位于 X = ±W_CLAMP * 0.35 处，连接下耳板、鞍座与底板)
    rib_w = min(W_BASE * 0.78, D + 2.0 * T_CLAMP + 20.0)
    rib_top_z = -(ear_gap / 2.0 + T_CLAMP * 0.5)
    rib_h = max(16.0, rib_top_z - web_bot_z)
    z_rib_mid = web_bot_z + rib_h / 2.0
    for sign_x in (1.0, -1.0):
        rx = sign_x * min(W_CLAMP * 0.36, L_SHOE * 0.28)
        o_rib = BOX(s, L=rib_w, W=rib_h + 2.0, H=t_web).translate((rx, 0.0, z_rib_mid))
        o_main.uniteWith(o_rib); o_rib.erase()

    # 5. 水平滑动底板 (Base Plate, 位于 Z = -H 处)
    z_base = -H + T_BASE / 2.0
    o_base = BOX(s, L=W_BASE, W=T_BASE, H=L_SHOE).translate((0.0, 0.0, z_base))
    o_main.uniteWith(o_base); o_base.erase()

    # 6. 底板四角安装长圆孔
    slot_r = max(6.5, T_BASE * 0.65)
    slot_len = max(22.0, L_SHOE * 0.16)
    slot_y_off = W_BASE * 0.34
    slot_x_off = L_SHOE * 0.32
    for sy in (slot_y_off, -slot_y_off):
        for sx in (slot_x_off, -slot_x_off):
            o_slot = BOX(s, L=slot_r * 1.8, W=T_BASE + 6.0, H=slot_len).translate((sx, sy, z_base))
            o_main.subtractFrom(o_slot); o_slot.erase()

    # 7. 管道通径内孔一次性精准差集
    o_pipe_cutter = CYLINDER(s, R=r_pipe, H=L_SHOE + 40.0, O=0.0).rotateY(90.0).translate((-(L_SHOE / 2.0 + 20.0), 0.0, 0.0))
    o_main.subtractFrom(o_pipe_cutter)
    o_pipe_cutter.erase()

    # 8. 端口定义与轴测尺寸标注锚点
    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))

    s.setLinearDimension("D", (-W_CLAMP / 2.0, 0.0, -r_pipe), (-W_CLAMP / 2.0, 0.0, r_pipe))
    s.setLinearDimension("H", (0.0, 0.0, 0.0), (0.0, 0.0, -H))
    s.setLinearDimension("L_SHOE", (-L_SHOE / 2.0, -W_BASE / 2.0, -H), (L_SHOE / 2.0, -W_BASE / 2.0, -H))
    s.setLinearDimension("W_BASE", (L_SHOE / 2.0, -W_BASE / 2.0, -H), (L_SHOE / 2.0, W_BASE / 2.0, -H))
    s.setLinearDimension("W_CLAMP", (-W_CLAMP / 2.0, 0.0, r_clamp_out), (W_CLAMP / 2.0, 0.0, r_clamp_out))
