# -*- coding: utf-8 -*-
# CD-ZD2010 105 立管管夹（竖直立管沿 Z 轴！两片抱箍夹持竖直管 + 左右双腹板支承牛腿 + 夹耳与端部螺栓孔）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="105立管管夹", TooltipLong="CD-ZD2010 105 立管管夹（垂直管承重抱箍）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="垂直管道外径 OD")
@param(L=LENGTH, TooltipShort="支承跨距", TooltipLong="两侧承重牛腿总跨长", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="耳间距", TooltipLong="两侧平行支承腹板间距")
@param(B=LENGTH, TooltipShort="板宽", TooltipLong="抱箍扁钢高度/支耳高")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="扁钢板厚")
@param(d=LENGTH, TooltipShort="螺栓径", TooltipLong="穿螺栓孔径")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_105(s, D=219.0, L=540.0, H=60.0, B=80.0, T=10.0, d=16.0, ID=u"ZD_105", **kw):
    D = float(D); L = float(L); H = float(H); B = float(B); T = float(T); d = float(d)
    if D < 15.0: D = 15.0
    if T < 4.0: T = 4.0
    if B < 30.0: B = 30.0
    if d < 8.0: d = 8.0
    if d > B * 0.55: d = B * 0.4
    R1 = D / 2.0
    R2 = R1 + T
    if L <= D + 100.0: L = D + 220.0
    gap = max(14.0, min(40.0, H * 0.35))

    # 1. 竖直立管两半圆抱箍 (沿 Z 轴高 B，在 Y 轴方向留夹缝 gap)
    o1 = CYLINDER(s, R=R2, H=B, O=0.0).translate((0.0, 0.0, -(B / 2.0)))
    o_in = CYLINDER(s, R=R1, H=B + 4.0, O=0.0).translate((0.0, 0.0, -(B / 2.0 + 2.0)))
    o1.subtractFrom(o_in); o_in.erase()
    o_seam = BOX(s, L=R2 * 3.0, W=B + 6.0, H=gap)
    o1.subtractFrom(o_seam); o_seam.erase()

    # 2. 左右两侧水平伸出双腹板支承牛腿 (沿 Y 轴总长 L，两片平行腹板位于 X = ±(gap/2 + T/2))
    arm_len = (L - D * 0.6) / 2.0
    for sy in (-1.0, 1.0):
        yc = sy * (R1 * 0.7 + arm_len / 2.0)
        for sx in (-1.0, 1.0):
            xc = sx * (gap / 2.0 + T / 2.0)
            o_arm = BOX(s, L=arm_len, W=B, H=T).translate((xc, yc, 0.0))
            o1.uniteWith(o_arm); o_arm.erase()
        # 牛腿内部连接衬板与顶部加劲小耳 (h)
        o_pad = BOX(s, L=d * 2.2, W=B, H=gap).translate((0.0, sy * (L / 2.0 - d * 1.3), 0.0))
        o1.uniteWith(o_pad); o_pad.erase()
        o_lug = BOX(s, L=T * 3.0, W=B * 0.55, H=gap + T * 2.0).translate((0.0, sy * (R2 + T * 1.5), B / 2.0 + B * 0.25))
        o1.uniteWith(o_lug); o_lug.erase()

    # 3. 切除中心竖直立管通孔 (Z 轴)
    o_pipe = CYLINDER(s, R=R1, H=B * 3.0, O=0.0).translate((0.0, 0.0, -(B * 1.5)))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    # 4. 靠近管壁的夹紧螺栓孔 + 牛腿端部的支承螺栓孔 (沿 X 轴穿透双腹板)
    tot_x = gap + T * 4.0
    y_clamp = R2 + d * 1.15
    y_end = L / 2.0 - d * 1.3
    if y_end <= y_clamp + d * 1.5: y_end = y_clamp + d * 2.0
    for sy in (-1.0, 1.0):
        for yh in (sy * y_clamp, sy * y_end):
            o_h = CYLINDER(s, R=d / 2.0, H=tot_x, O=0.0).rotateY(90.0).translate((-(tot_x / 2.0), yh, 0.0))
            o1.subtractFrom(o_h); o_h.erase()
        # 在夹紧孔处装入横向夹紧螺栓杆与两侧螺栓头/螺母
        o_bolt = CYLINDER(s, R=(d / 2.0) * 0.8, H=gap + T * 3.2, O=0.0).rotateY(90.0).translate((-((gap + T * 3.2) / 2.0), sy * y_clamp, 0.0))
        o1.uniteWith(o_bolt); o_bolt.erase()
        for sx_b in (-1.0, 1.0):
            xb = (gap / 2.0 + T) if sx_b > 0 else -(gap / 2.0 + T + T * 0.6)
            o_bhead = CYLINDER(s, R=d * 0.75, H=T * 0.6, O=0.0).rotateY(90.0).translate((xb, sy * y_clamp, 0.0))
            o1.uniteWith(o_bhead); o_bhead.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (0.0, -(L / 2.0), 0.0), (0.0, (L / 2.0), 0.0))
