# -*- coding: utf-8 -*-
# CD-ZD2010 314 三孔连接板（上窄下宽圆角三角形过渡板，1 顶孔 + 2 底孔）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="314三孔连接板", TooltipLong="CD-ZD2010 314 三孔连接板（圆角三角形三孔板）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(L1=LENGTH, TooltipShort="纵孔距", TooltipLong="顶孔至底双孔中心线高 H", Ask4Dist=True)
@param(L2=LENGTH, TooltipShort="横孔距", TooltipLong="底部双孔水平中心距 C")
@param(W=LENGTH, TooltipShort="端圆宽", TooltipLong="孔周圆角外径/宽度")
@param(T=LENGTH, TooltipShort="板厚", TooltipLong="连接板厚度")
@param(d=LENGTH, TooltipShort="孔径", TooltipLong="穿销孔直径 D")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_314(s, L1=160.0, L2=140.0, W=60.0, T=12.0, d=22.0, ID=u"ZD_314", **kw):
    L1 = float(L1); L2 = float(L2); W = float(W); T = float(T); d = float(d)
    if d < 8.0: d = 8.0
    if W <= d * 1.5: W = d * 2.2
    if L1 < W: L1 = W * 2.0
    if L2 < W: L2 = W * 1.8
    r_corner = W / 2.0

    # 1. 上窄下宽梯形芯板 + 3个顶点圆弧包络 (顶孔在 (0,0,0)，底两孔在 (±L2/2, 0, -L1))
    tot_w = L2 + W
    o1 = BOX(s, L=T, W=L1, H=tot_w).translate((0.0, 0.0, -(L1 / 2.0)))
    cut_dx = (tot_w - W) / 2.0
    if cut_dx > 4.0:
        ang = degrees(atan2(cut_dx, L1))
        for sx in (-1.0, 1.0):
            mid_x = sx * (W / 2.0 + tot_w / 2.0) * 0.5
            mid_z = -(L1 * 0.5)
            o_cut = BOX(s, L=T * 4.0, W=L1 * 3.0, H=tot_w * 2.0).translate((sx * tot_w, 0.0, 0.0)).rotateY(-sx * ang).translate((mid_x, 0.0, mid_z))
            o1.subtractFrom(o_cut); o_cut.erase()

    # 3个孔位的圆角耳头与底部水平连接带
    o_bot_band = BOX(s, L=T, W=r_corner, H=L2).translate((0.0, 0.0, -(L1 + r_corner / 2.0)))
    o1.uniteWith(o_bot_band); o_bot_band.erase()
    for px, pz in ((0.0, 0.0), (-(L2 / 2.0), -L1), ((L2 / 2.0), -L1)):
        o_c = CYLINDER(s, R=r_corner, H=T, O=0.0).rotateX(90.0).translate((px, T / 2.0, pz))
        o1.uniteWith(o_c); o_c.erase()

    # 2. 切除 1 顶孔 + 2 底孔
    for px, pz in ((0.0, 0.0), (-(L2 / 2.0), -L1), ((L2 / 2.0), -L1)):
        o_h = CYLINDER(s, R=d / 2.0, H=T * 4.0, O=0.0).rotateX(90.0).translate((px, T * 2.0, pz))
        o1.subtractFrom(o_h); o_h.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('L1', (0.0, 0.0, 0.0), (0.0, 0.0, -L1))
