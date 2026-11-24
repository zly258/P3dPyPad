# -*- coding: utf-8 -*-
# CD-ZD2010 106 立管管担（竖直立管沿 Z 轴！立管抱箍坐在两根平行水平槽钢组成的横担梁上，带加劲肋与两端支承孔）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="106立管管担", TooltipLong="CD-ZD2010 106 立管管担", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="垂直管道外径 OD")
@param(L=LENGTH, TooltipShort="横担长", TooltipLong="槽钢横担总长", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="槽钢高", TooltipLong="槽钢截面高度")
@param(W=LENGTH, TooltipShort="槽钢宽", TooltipLong="槽钢截面翼缘宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="槽钢壁厚及肋板厚")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_106(s, D=219.0, L=800.0, H=120.0, W=53.0, T=8.0, ID=u"ZD_106", **kw):
    D = float(D); L = float(L); H = float(H); W = float(W); T = float(T)
    if D < 20.0: D = 20.0
    if H < 50.0: H = 50.0
    if W < 25.0: W = 25.0
    if T < 4.0: T = 4.0
    if T > W * 0.35: T = W * 0.25
    R1 = D / 2.0
    if L <= D + 160.0: L = D + 260.0

    # 1. 前后两根平行水平槽钢横担梁 (沿 X 轴长 L，槽口向外，位于 Y = ±yc, Z in [-H, 0])
    yc = R1 + W / 2.0 + T
    o1 = BOX(s, L=W, W=H, H=L).translate((0.0, -yc, -(H / 2.0)))
    o_c1 = BOX(s, L=W - T, W=H - 2.0 * T, H=L + 4.0).translate((0.0, -(yc + T / 2.0), -(H / 2.0)))
    o1.subtractFrom(o_c1); o_c1.erase()

    o2 = BOX(s, L=W, W=H, H=L).translate((0.0, yc, -(H / 2.0)))
    o_c2 = BOX(s, L=W - T, W=H - 2.0 * T, H=L + 4.0).translate((0.0, (yc + T / 2.0), -(H / 2.0)))
    o2.subtractFrom(o_c2); o_c2.erase()
    o1.uniteWith(o2); o2.erase()

    # 2. 槽钢顶面承重过渡台板 + 竖直立管抱箍 + 4块 60° 放射加劲肋板 (Z >= 0)
    pad_x = D + W * 2.0
    pad_y = yc * 2.0 + W * 0.6
    o_pad = BOX(s, L=pad_y, W=T * 1.2, H=pad_x).translate((0.0, 0.0, T * 0.6))
    o1.uniteWith(o_pad); o_pad.erase()

    collar_h = max(H * 1.4, D * 0.55)
    o_col = CYLINDER(s, R=R1 + T * 1.4, H=collar_h + H, O=0.0).translate((0.0, 0.0, -H))
    o1.uniteWith(o_col); o_col.erase()

    # 4块斜向放射加劲肋板 (与图集 60° 翼肋一致)
    rib_len = (R1 + W * 1.3) * 2.0
    for ang in (30.0, -30.0):
        o_rib = BOX(s, L=T, W=collar_h * 0.85, H=rib_len).rotateZ(ang).translate((0.0, 0.0, collar_h * 0.425))
        o1.uniteWith(o_rib); o_rib.erase()

    # 3. 切除中心竖直立管通孔 (沿 Z 轴贯穿)
    o_pipe = CYLINDER(s, R=R1, H=collar_h + H + 40.0, O=0.0).translate((0.0, 0.0, -(H + 20.0)))
    o1.subtractFrom(o_pipe); o_pipe.erase()

    # 4. 横担梁两端横向连杆/支承通孔 (沿 Y 轴穿透两根槽钢腹板)
    hole_d = max(14.0, min(28.0, H * 0.22))
    xh = L / 2.0 - max(45.0, hole_d * 2.0)
    for sx in (-1.0, 1.0):
        o_h = CYLINDER(s, R=hole_d / 2.0, H=pad_y + 40.0, O=0.0).rotateX(90.0).translate((sx * xh, (pad_y + 40.0) / 2.0, -(H / 2.0)))
        o1.subtractFrom(o_h); o_h.erase()
        # 横向穿钉拉杆与两端紧固螺母垫圈
        o_tie = CYLINDER(s, R=(hole_d / 2.0) * 1.05, H=yc * 2.0 + W * 1.2, O=0.0).rotateX(90.0).translate((sx * xh, yc + W * 0.6, -(H / 2.0)))
        o1.uniteWith(o_tie); o_tie.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('L', (-(L / 2.0), 0.0, 0.0), ((L / 2.0), 0.0, 0.0))
