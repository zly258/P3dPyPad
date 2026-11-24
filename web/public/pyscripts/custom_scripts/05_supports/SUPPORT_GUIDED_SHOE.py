# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"化工导向限位管托 (HG/T 21629 XD)",
    TooltipLong=u"化工管廊热膨胀管段轴向导向、横向限位防倾覆管托 (XD 型，符合 HG/T 21629，含弧形承重鞍座、T型腹板与横肋、底部PTFE滑板及两侧外包重型L型导向防掀翻卡轨底座)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支承管道公称外径 (mm)")
@param(H=LENGTH, TooltipShort=u"管托高度", TooltipLong=u"管道中心至滑动管托底面的高度 (mm)")
@param(L_SHOE=LENGTH, TooltipShort=u"管托长度", TooltipLong=u"管托本体轴向长度 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"管托底宽", TooltipLong=u"管托滑动底板横向宽度 (mm)")
@param(T_PLATE=LENGTH, TooltipShort=u"钢板厚度", TooltipLong=u"管托腹板与底板名义壁厚 (mm)")
@param(L_GUIDE=LENGTH, TooltipShort=u"导向座长", TooltipLong=u"外侧L型防倾覆导向限位卡座长度 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"导向管托图集规格编码")
def SUPPORT_GUIDED_SHOE(s, D=219.1, H=180.0, L_SHOE=300.0, W_BASE=180.0, T_PLATE=12.0, L_GUIDE=140.0, ID=u"XD-DN200", **kw):
    D = max(25.0, float(D))
    r_pipe = D / 2.0
    t = max(8.0, float(T_PLATE))
    H = max(r_pipe + 45.0, float(H))
    L_SHOE = max(150.0, float(L_SHOE))
    W_BASE = max(80.0, float(W_BASE))
    L_GUIDE = min(L_SHOE * 0.72, max(60.0, float(L_GUIDE)))

    # 1. T型滑动管托本体 (底板 + 腹板 + 120° 弧形鞍板 + 两端横向加劲肋)
    o_m = BOX(s, L=W_BASE, W=t, H=L_SHOE).translate((0.0, 0.0, -H + t * 0.5))
    h_web = H - r_pipe - t * 0.5
    o_web = BOX(s, L=t, W=h_web, H=L_SHOE).translate((0.0, 0.0, -H + t + h_web * 0.5))
    o_m.uniteWith(o_web); o_web.erase()

    r_sad = r_pipe + t
    o_sad = CYLINDER(s, R=r_sad, H=L_SHOE, O=0.0).rotateY(90.0).translate((-L_SHOE * 0.5, 0.0, 0.0))
    h_cut = 2.0 * r_sad
    o_cut_top = BOX(s, L=2.0 * r_sad + 20.0, W=h_cut, H=L_SHOE + 10.0).translate((0.0, 0.0, -r_pipe * 0.45 + h_cut * 0.5))
    o_sad.subtractFrom(o_cut_top); o_cut_top.erase()
    o_m.uniteWith(o_sad); o_sad.erase()

    h_rib = H - r_pipe * 0.86 - t
    w_rib = min(W_BASE * 0.88, 2.0 * r_pipe * 0.86)
    for sx in (-1.0, 1.0):
        rib = BOX(s, L=w_rib, W=h_rib, H=t).translate((sx * L_SHOE * 0.36, 0.0, -H + t + h_rib * 0.5))
        o_m.uniteWith(rib); rib.erase()

    # 2. 下部加宽钢梁生根底座垫板 + 两侧重型 L 型防倾覆导向卡轨 + 外侧双三角加劲肋
    t_pad = max(12.0, t)
    w_pad = W_BASE + 8.0 * t
    o_pad = BOX(s, L=w_pad, W=t_pad, H=L_GUIDE * 1.45).translate((0.0, 0.0, -H - t_pad * 0.5))
    o_m.uniteWith(o_pad); o_pad.erase()

    clip_h = t * 3.2
    lip_w = t * 2.8
    for sy in (-1.0, 1.0):
        y_wall = sy * (W_BASE * 0.5 + t * 0.85)
        v_wall = BOX(s, L=t * 1.3, W=clip_h, H=L_GUIDE).translate((0.0, y_wall, -H + clip_h * 0.5 - 2.0))
        y_lip = sy * (W_BASE * 0.5 + t * 1.5 - lip_w * 0.5)
        h_lip = BOX(s, L=lip_w, W=t * 1.1, H=L_GUIDE).translate((0.0, y_lip, -H + clip_h - t * 0.55))
        o_m.uniteWith(v_wall); v_wall.erase()
        o_m.uniteWith(h_lip); h_lip.erase()
        for sx in (-0.32, 0.32):
            gus = BOX(s, L=t * 2.2, W=clip_h * 0.9, H=t).translate((sx * L_GUIDE, sy * (W_BASE * 0.5 + t * 2.4), -H + clip_h * 0.45))
            o_m.uniteWith(gus); gus.erase()

    # 切除管道流道
    o_pipe_cut = CYLINDER(s, R=r_pipe, H=L_SHOE + 20.0, O=0.0).rotateY(90.0).translate((-L_SHOE * 0.5 - 10.0, 0.0, 0.0))
    o_m.subtractFrom(o_pipe_cut); o_pipe_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("H", (0.0, 0.0, -H), (0.0, 0.0, 0.0))
    s.setLinearDimension("L_SHOE", (-L_SHOE * 0.5, 0.0, -H), (L_SHOE * 0.5, 0.0, -H))
    s.setLinearDimension("W_BASE", (0.0, -W_BASE * 0.5, -H), (0.0, W_BASE * 0.5, -H))
