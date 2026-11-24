# -*- coding: utf-8 -*-
# CD-ZD2010 202 加强焊接吊板（在 ZD_201 吊板底部增加贴合水平管外壁的弧形马鞍补强垫板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="202加强焊接吊板", TooltipLong="CD-ZD2010 202 加强焊接吊板（带弧形马鞍补强垫板）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="管道外径 OD")
@param(L=LENGTH, TooltipShort="板宽A", TooltipLong="主吊板底部长度 A")
@param(H=LENGTH, TooltipShort="中心高", TooltipLong="管心至吊孔中心高度 H", Ask4Dist=True)
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="主吊板及补强垫板厚度")
@param(B=LENGTH, TooltipShort="垫板长", TooltipLong="底部弧形马鞍补强垫板长度")
@param(d=LENGTH, TooltipShort="孔径", TooltipLong="吊孔直径 D")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_202(s, D=273.0, L=230.0, H=335.0, T=16.0, B=260.0, d=33.0, ID=u"ZD_202", **kw):
    D = float(D); L = float(L); H = float(H); T = float(T); B = float(B); d = float(d)
    if D < 30.0: D = 30.0
    if T < 6.0: T = 6.0
    if T > 36.0: T = 20.0
    if d < 12.0: d = 12.0
    R1 = D / 2.0
    if L < d * 2.5: L = d * 3.5
    if B < L + 20.0: B = L + 40.0
    if H <= R1 + T + d * 1.8: H = R1 + T + d * 2.5 + 40.0
    r_top = max(d * 1.25, L * 0.28)
    if r_top > L * 0.46: r_top = L * 0.44

    # 1. 底部贴合水平管外壁的 120° 弧形马鞍补强垫板 (长 B 沿 X，内径 R1，外径 R1+pad_t)
    pad_t = max(8.0, T * 0.75)
    R_pad = R1 + pad_t
    o1 = CYLINDER(s, R=R_pad, H=B, O=0.0).rotateY(90.0).translate((-(B / 2.0), 0.0, 0.0))
    o_in = CYLINDER(s, R=R1, H=B + 4.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 2.0), 0.0, 0.0))
    o1.subtractFrom(o_in); o_in.erase()
    # 仅保留顶部 Z >= R1 * 0.45 的马鞍弧面
    cut_h = R_pad * 2.0
    o_cut_bot = BOX(s, L=R_pad * 3.0, W=cut_h, H=B + 10.0).translate((0.0, 0.0, R1 * 0.45 - cut_h / 2.0))
    o1.subtractFrom(o_cut_bot); o_cut_bot.erase()

    # 2. 上部直立梯形主吊板 + 半圆弧顶耳头
    o_lug = BOX(s, L=T, W=H, H=L).translate((0.0, 0.0, H / 2.0))
    cut_dx = (L - r_top * 2.0) / 2.0
    if cut_dx > 4.0 and (H - R1) > 20.0:
        ang = degrees(atan2(cut_dx, H - R1 * 0.75))
        for sx in (-1.0, 1.0):
            mid_x = sx * (r_top + L / 2.0) * 0.5
            mid_z = (R1 * 0.75 + H) * 0.5
            o_cut = BOX(s, L=T * 4.0, W=H * 2.0, H=L).translate((sx * (L / 2.0), 0.0, 0.0)).rotateY(sx * ang).translate((mid_x, 0.0, mid_z))
            o_lug.subtractFrom(o_cut); o_cut.erase()
    o_head = CYLINDER(s, R=r_top, H=T, O=0.0).rotateX(90.0).translate((0.0, T / 2.0, H))
    o_lug.uniteWith(o_head); o_head.erase()
    o1.uniteWith(o_lug); o_lug.erase()

    # 3. 切除水平管道内孔 + 顶部吊孔 (Z = H)
    o_pipe = CYLINDER(s, R=R1, H=B + 20.0, O=0.0).rotateY(90.0).translate((-(B / 2.0 + 10.0), 0.0, 0.0))
    o1.subtractFrom(o_pipe); o_pipe.erase()
    o_hole = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateX(90.0).translate((0.0, T * 2.0, H))
    o1.subtractFrom(o_hole); o_hole.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H', (0.0, 0.0, 0.0), (0.0, 0.0, H))
