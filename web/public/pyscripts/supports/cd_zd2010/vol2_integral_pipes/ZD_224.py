# -*- coding: utf-8 -*-
# CD-ZD2010 224 立管焊接吊(支)座（竖直立管沿 Z 轴！立管左右两侧对称焊接水平底板 + 上部三角形竖向肋板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="224立管焊接吊座", TooltipLong="CD-ZD2010 224 立管焊接吊（支）座", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="立管外径 OD")
@param(L=LENGTH, TooltipShort="外挑距", TooltipLong="管心至单侧吊点跨距", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="肋板高", TooltipLong="上部三角形加劲肋高度 A")
@param(W=LENGTH, TooltipShort="底板宽", TooltipLong="水平承重底板宽度 B")
@param(d=LENGTH, TooltipShort="吊孔径", TooltipLong="吊杆螺栓孔径 D")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_224(s, D=219.0, L=395.0, H=328.0, W=120.0, d=22.0, ID=u"ZD_224", **kw):
    D = float(D); L = float(L); H = float(H); W = float(W); d = float(d)
    if D < 30.0: D = 30.0
    if d < 12.0: d = 12.0
    R1 = D / 2.0
    if W < d * 2.8: W = d * 3.5
    if H < 120.0: H = 200.0
    if L <= R1 + d * 2.5 + 30.0: L = R1 + d * 4.5 + 80.0
    t_pl = max(12.0, d * 0.6)
    t_rib = max(10.0, d * 0.45)

    # 1. 中心竖直立管短段 (沿 Z 轴，突出立管特征)
    pipe_t = max(6.0, min(14.0, R1 * 0.12))
    pipe_h = H * 1.4
    o1 = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h * 0.25)))

    # 2. 左右两侧 (±Y) 对称焊接水平底板 (总跨 2*(L + 1.8*d)，宽 W 沿 X，厚 t_pl 沿 Z)
    tot_span = (L + d * 1.8) * 2.0
    o_base = BOX(s, L=tot_span, W=t_pl, H=W).translate((0.0, 0.0, -(t_pl / 2.0)))
    o1.uniteWith(o_base); o_base.erase()

    # 3. 左右两侧底板上方的梯形/三角形竖向加劲肋板 (Z >= 0) + 吊杆通孔与吊杆示意
    arm_w = (tot_span / 2.0) - R1 * 0.7
    for sy in (-1.0, 1.0):
        yc = sy * (R1 * 0.7 + arm_w / 2.0)
        o_rib = BOX(s, L=arm_w, W=H, H=t_rib).translate((0.0, yc, H / 2.0))
        ang = degrees(atan2(arm_w * 0.78, H * 0.85))
        o_cut = BOX(s, L=arm_w * 2.0, W=H * 2.0, H=t_rib * 4.0).translate((0.0, sy * arm_w, 0.0)).rotateX(-sy * ang).translate((0.0, yc, H * 0.62))
        o_rib.subtractFrom(o_cut); o_cut.erase()
        o1.uniteWith(o_rib); o_rib.erase()

        # 两侧底板外端吊孔及穿入的竖向吊杆短段 (与图集 224 完全一致)
        yh = sy * L
        for sx in (-1.0, 1.0):
            xh = sx * (W * 0.28)
            o_h = CYLINDER(s, R=d / 2.0, H=t_pl * 4.0, O=0.0).translate((xh, yh, -(t_pl * 2.0)))
            o1.subtractFrom(o_h); o_h.erase()
        # 竖向吊杆与螺母示意
        o_rod = CYLINDER(s, R=(d / 2.0) * 0.82, H=H * 0.95, O=0.0).translate((0.0, yh, -(t_pl * 2.2)))
        o1.uniteWith(o_rod); o_rod.erase()

    # 4. 切除中心竖直立管内孔
    o_in = CYLINDER(s, R=R1 - pipe_t, H=pipe_h + 20.0, O=0.0).translate((0.0, 0.0, -(pipe_h * 0.25 + 10.0)))
    o1.subtractFrom(o_in); o_in.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (0.0, L, 0.0))
