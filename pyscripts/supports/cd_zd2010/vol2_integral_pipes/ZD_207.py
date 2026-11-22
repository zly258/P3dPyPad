# -*- coding: utf-8 -*-
# CD-ZD2010 207 立管焊接吊板（竖直立管沿 Z 轴！左右两侧对称焊接两块带斜边与吊孔的水平伸出吊耳板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="207立管焊接吊板", TooltipLong="CD-ZD2010 207 立管焊接吊板", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="垂直管外径 OD")
@param(L=LENGTH, TooltipShort="总跨长", TooltipLong="左右两吊板外端总长 L", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="根部高", TooltipLong="吊板贴合管壁处高度 A")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="吊板厚度 H")
@param(d=LENGTH, TooltipShort="吊孔径", TooltipLong="销轴吊孔直径 D")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_207(s, D=108.0, L=398.0, H=120.0, T=22.0, d=17.5, ID=u"ZD_207", **kw):
    D = float(D); L = float(L); H = float(H); T = float(T); d = float(d)
    if D < 20.0: D = 20.0
    if T < 8.0: T = 8.0
    if d < 10.0: d = 10.0
    if d > H * 0.45: d = H * 0.25
    R1 = D / 2.0
    if H < 80.0: H = 100.0
    if L <= D + d * 6.0 + 80.0: L = D + d * 8.0 + 180.0

    # 1. 中央竖直立管管段示意环 (沿 Z 轴，突出立管特征，壁厚 thk_p)
    pipe_h = H * 1.45
    thk_p = max(5.0, min(12.0, R1 * 0.14))
    o1 = CYLINDER(s, R=R1, H=pipe_h, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0)))

    # 2. 左右两侧 (±Y) 对称焊接带下斜边的水平伸出吊耳板 (总跨 L，根部高 H，外端高 tip_h)
    o_ears = BOX(s, L=L, W=H, H=T)
    tip_h = max(d * 2.4, H * 0.48)
    cut_dz = H - tip_h
    arm_span = L / 2.0 - R1
    if cut_dz > 6.0 and arm_span > 20.0:
        ang = degrees(atan2(cut_dz, arm_span))
        for sy in (-1.0, 1.0):
            mid_y = sy * (R1 + L / 2.0) * 0.5
            mid_z = -(H / 2.0 - cut_dz * 0.5)
            o_cut = BOX(s, L=L, W=H * 2.0, H=T * 4.0).translate((0.0, 0.0, -H)).rotateX(sy * ang).translate((0.0, mid_y, mid_z))
            o_ears.subtractFrom(o_cut); o_cut.erase()

    # 3. 两侧吊耳板外端开圆孔 Ød (沿 X 轴穿透板厚 T)
    y_hole = L / 2.0 - max(22.0, d * 1.4)
    z_hole = (H / 2.0) - tip_h * 0.5
    for sy in (-1.0, 1.0):
        o_h = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateY(90.0).translate((-(T * 2.0), sy * y_hole, z_hole))
        o_ears.subtractFrom(o_h); o_h.erase()

    o1.uniteWith(o_ears); o_ears.erase()
    # 切除竖直立管内孔 (形成空心竖直立管 + 左右对称双斜边吊耳板)
    o_in = CYLINDER(s, R=R1 - thk_p, H=pipe_h + 10.0, O=0.0).translate((0.0, 0.0, -(pipe_h / 2.0 + 5.0)))
    o1.subtractFrom(o_in); o_in.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (0.0, -(L / 2.0), z_hole), (0.0, (L / 2.0), z_hole))
