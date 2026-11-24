# -*- coding: utf-8 -*-
# CD-ZD2010 225 加强立管焊接吊(支)座（竖直立管沿 Z 轴！左右对称焊接水平双槽钢横臂 + 顶部斜拉加强筋板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="225加强立管吊座", TooltipLong="CD-ZD2010 225 加强立管焊接吊（支）座", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="立管外径 OD")
@param(L=LENGTH, TooltipShort="外挑距", TooltipLong="管心至单侧吊点跨距", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="总高", TooltipLong="加劲肋板高度 A")
@param(W=LENGTH, TooltipShort="横臂宽", TooltipLong="双槽钢横臂总宽 B")
@param(Rib_T=LENGTH, TooltipShort="筋厚", TooltipLong="顶部斜拉加强筋板厚度")
@param(d=LENGTH, TooltipShort="吊孔径", TooltipLong="吊杆螺栓孔径 D")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_225(s, D=273.0, L=450.0, H=460.0, W=180.0, Rib_T=16.0, d=39.0, ID=u"ZD_225", **kw):
    D = float(D); L = float(L); H = float(H); W = float(W); Rib_T = float(Rib_T); d = float(d)
    if D < 40.0: D = 40.0
    if Rib_T < 8.0: Rib_T = 8.0
    if d < 14.0: d = 14.0
    R1 = D / 2.0
    if W < 100.0: W = 140.0
    if H < 160.0: H = 260.0
    if L <= R1 + d * 2.5 + 40.0: L = R1 + d * 4.5 + 100.0

    # 1. 中心竖直立管管段 (沿 Z 轴，突出立管特征)
    pipe_t = max(7.0, min(16.0, R1 * 0.12))
    pipe_h = H * 1.45
    o1 = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h * 0.3)))

    # 2. 左右两侧 (±Y) 对称焊接水平双槽钢横臂 (总跨 tot_span，前后两根槽钢位于 X = ±xc_ch)
    tot_span = (L + d * 1.8) * 2.0
    ch_h = max(80.0, W * 0.55)
    ch_w = max(42.0, W * 0.28)
    ch_t = max(6.5, ch_h * 0.085)
    xc_ch = min(W / 2.0 - ch_w / 2.0, R1 + ch_w * 0.35)
    for sx in (-1.0, 1.0):
        xc = sx * xc_ch
        o_ch = BOX(s, L=tot_span, W=ch_h, H=ch_w).translate((xc, 0.0, -(ch_h / 2.0)))
        o_cut_ch = BOX(s, L=tot_span + 4.0, W=ch_h - 2.0 * ch_t, H=ch_w - ch_t).translate((xc + sx * (ch_t / 2.0), 0.0, -(ch_h / 2.0)))
        o_ch.subtractFrom(o_cut_ch); o_cut_ch.erase()
        o1.uniteWith(o_ch); o_ch.erase()

    # 3. 顶部斜拉三角形加强筋板 (位于槽钢横臂上方 Z >= 0，双平行筋板夹持立管外壁)
    arm_w = (tot_span / 2.0) - R1 * 0.65
    rib_h = H - ch_h
    if rib_h < 80.0: rib_h = 120.0
    for sy in (-1.0, 1.0):
        yc = sy * (R1 * 0.65 + arm_w / 2.0)
        for sx in (-1.0, 1.0):
            xr = sx * (W / 2.0 - ch_w + Rib_T / 2.0)
            o_r = BOX(s, L=arm_w, W=rib_h, H=Rib_T).translate((xr, yc, rib_h / 2.0))
            ang = degrees(atan2(arm_w * 0.85, rib_h))
            o_cr = BOX(s, L=arm_w * 2.0, W=rib_h * 2.0, H=Rib_T * 4.0).translate((0.0, sy * arm_w, 0.0)).rotateX(-sy * ang).translate((xr, yc, rib_h * 0.55))
            o_r.subtractFrom(o_cr); o_cr.erase()
            o1.uniteWith(o_r); o_r.erase()

        # 横臂外端承重垫板与中心吊孔 Ød (Z向穿透)
        yh = sy * L
        o_pad = BOX(s, L=d * 2.6, W=ch_h, H=W * 0.85).translate((0.0, yh, -(ch_h / 2.0)))
        o1.uniteWith(o_pad); o_pad.erase()
        o_hole = CYLINDER(s, R=d / 2.0, H=ch_h + 20.0, O=0.0).translate((0.0, yh, -(ch_h + 10.0)))
        o1.subtractFrom(o_hole); o_hole.erase()

    # 4. 切除中心竖直立管内孔
    o_in = CYLINDER(s, R=R1 - pipe_t, H=pipe_h + 20.0, O=0.0).translate((0.0, 0.0, -(pipe_h * 0.3 + 10.0)))
    o1.subtractFrom(o_in); o_in.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, L, 0.0))
