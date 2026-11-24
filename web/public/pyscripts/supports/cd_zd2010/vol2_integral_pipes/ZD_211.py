# -*- coding: utf-8 -*-
# CD-ZD2010 211 垂直管道支架翼板（竖直立管沿 Z 轴！立管四周焊接 4 块直角梯形竖向翼板，坐落在底部双槽钢底座框上）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="211垂直管道支架翼板", TooltipLong="CD-ZD2010 211 垂直管道支架翼板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="垂直立管外径 OD")
@param(L=LENGTH, TooltipShort="翼板跨距", TooltipLong="翼板总跨宽 D2", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="翼板高", TooltipLong="翼板沿立管纵向高度 H")
@param(T=LENGTH, TooltipShort="翼板厚", TooltipLong="翼板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_211(s, D=219.0, L=419.0, H=250.0, T=16.0, ID=u"ZD_211", **kw):
    D = float(D); L = float(L); H = float(H); T = float(T)
    if D < 30.0: D = 30.0
    if T < 6.0: T = 6.0
    if T > 32.0: T = 16.0
    if H < 100.0: H = 150.0
    R1 = D / 2.0
    span_d2 = L if L > D + 60.0 else (D + L * 2.0)
    wing_ext = (span_d2 - D) / 2.0
    if wing_ext < 50.0:
        wing_ext = 100.0
        span_d2 = D + 200.0

    # 1. 中心竖直立管短段 (沿 Z 轴，壁厚 pipe_t，完整还原图集 211 立管本体)
    pipe_t = max(6.0, min(14.0, R1 * 0.12))
    pipe_len = H * 1.45
    o1 = CYLINDER(s, R=R1, H=pipe_len, O=0.0).translate((0.0, 0.0, -(H * 0.35)))

    # 2. 立管四周对称焊接 4 块直角梯形竖向翼板 (位于 X = ±x_off，向 ±Y 挑出)
    x_off = R1 * 0.52
    step_h = H * 0.34
    slope_h = H - step_h
    theta = degrees(atan2(slope_h, wing_ext))
    big = (wing_ext + H) * 2.0
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            yc = sy * (R1 * 0.65 + wing_ext / 2.0)
            w_len = wing_ext + R1 * 0.35
            o_w = BOX(s, L=w_len, W=H, H=T).translate((sx * x_off, yc, H / 2.0))
            o_cut = BOX(s, L=big, W=big, H=T * 4.0).translate((0.0, 0.0, big / 2.0)).rotateX(-sy * theta).translate((sx * x_off, sy * (R1 + wing_ext / 2.0), step_h + slope_h / 2.0))
            o_w.subtractFrom(o_cut); o_cut.erase()
            o1.uniteWith(o_w); o_w.erase()

    # 3. 底部承重双槽钢横梁底座框 (沿 X 轴延伸，支撑 4 块翼板底缘)
    ch_h = step_h
    ch_w = max(45.0, ch_h * 0.48)
    ch_t = max(6.0, ch_h * 0.09)
    beam_len = span_d2 * 1.25
    y_beam = R1 + wing_ext * 0.45
    for sy in (-1.0, 1.0):
        yc_b = sy * y_beam
        o_b = BOX(s, L=ch_w, W=ch_h + 4.0, H=beam_len).translate((0.0, yc_b, -(ch_h / 2.0) + 2.0))
        o_cb = BOX(s, L=ch_w - ch_t, W=ch_h - 2.0 * ch_t, H=beam_len + 4.0).translate((0.0, yc_b + sy * (ch_t / 2.0), -(ch_h / 2.0)))
        o_b.subtractFrom(o_cb); o_cb.erase()
        o1.uniteWith(o_b); o_b.erase()

    # 4. 切除竖直立管内孔
    o_in = CYLINDER(s, R=R1 - pipe_t, H=pipe_len + 20.0, O=0.0).translate((0.0, 0.0, -(H * 0.35 + 10.0)))
    o1.subtractFrom(o_in); o_in.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (0.0, -(span_d2 / 2.0), 0.0), (0.0, (span_d2 / 2.0), 0.0))
