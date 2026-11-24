# -*- coding: utf-8 -*-
# CD-ZD2010 223 立管焊接支座（竖直立管沿 Z 轴！水平支承托板 + 直角三角形竖向加劲肋板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="223立管焊接支座", TooltipLong="CD-ZD2010 223 立管焊接支座", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="立管外径 OD")
@param(L=LENGTH, TooltipShort="外挑长", TooltipLong="支座外挑跨长", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="肋板高", TooltipLong="三角形加劲肋板高度 A")
@param(W=LENGTH, TooltipShort="托板宽", TooltipLong="水平托板宽度 B")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="钢板厚度")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_223(s, D=159.0, L=320.0, H=240.0, W=120.0, T=14.0, ID=u"ZD_223", **kw):
    D = float(D); L = float(L); H = float(H); W = float(W); T = float(T)
    if D < 25.0: D = 25.0
    if T < 6.0: T = 6.0
    if T > 28.0: T = 14.0
    R1 = D / 2.0
    if W < 50.0: W = 80.0
    if W > D * 1.8 + 80.0: W = D * 0.85 + 40.0
    if H < 80.0: H = 180.0
    if H > 800.0: H = 260.0
    arm_l = L if L > R1 + 60.0 else (R1 + L + 120.0)
    if arm_l > R1 + 500.0: arm_l = R1 + 260.0

    # 1. 中心竖直立管管段 (沿 Z 轴，突出立管特征)
    pipe_t = max(5.0, min(12.0, R1 * 0.12))
    pipe_h = H * 1.4
    o1 = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h * 0.35)))

    # 2. 单侧 (+X) 焊接水平承重托板 + 下部直角三角形加劲肋板
    o_plate = BOX(s, L=W, W=T, H=arm_l).translate((arm_l / 2.0, 0.0, -(T / 2.0)))
    o1.uniteWith(o_plate); o_plate.erase()

    rib_len = arm_l - R1 * 0.6
    xc_rib = R1 * 0.6 + rib_len / 2.0
    o_rib = BOX(s, L=T, W=H, H=rib_len).translate((xc_rib, 0.0, -(T + H / 2.0)))
    ang = degrees(atan2(rib_len * 0.88, H))
    o_cut = BOX(s, L=T * 4.0, W=H * 2.5, H=rib_len * 2.0).translate((rib_len, 0.0, 0.0)).rotateY(-ang).translate((xc_rib, 0.0, -(T + H * 0.55)))
    o_rib.subtractFrom(o_cut); o_cut.erase()
    o1.uniteWith(o_rib); o_rib.erase()

    # 3. 切除中心竖直立管内孔
    o_in = CYLINDER(s, R=R1 - pipe_t, H=pipe_h + 20.0, O=0.0).translate((0.0, 0.0, -(pipe_h * 0.35 + 10.0)))
    o1.subtractFrom(o_in); o_in.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (0.0, 0.0, 0.0), (arm_l, 0.0, 0.0))
