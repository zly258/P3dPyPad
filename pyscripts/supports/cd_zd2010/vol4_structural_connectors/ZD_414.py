# -*- coding: utf-8 -*-
# CD-ZD2010 414 自调平座（下部圆柱凸台底座 + 上部方形球面调平顶板 + 中心通孔）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="414自调平座", TooltipLong="CD-ZD2010 414 自调平座（方形顶板+圆柱凸台球铰座）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D_base=LENGTH, TooltipShort="底凸台径", TooltipLong="下部圆柱凸台直径 d", Ask4Dist=True)
@param(H=LENGTH, TooltipShort="总高度", TooltipLong="调平座总高 H")
@param(Sphere_R=LENGTH, TooltipShort="方板边长", TooltipLong="上部方形顶板边长 C")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_414(s, D_base=110.0, H=43.0, Sphere_R=120.0, ID=u"ZD_414", **kw):
    D_base = float(D_base); H = float(H); Sphere_R = float(Sphere_R)
    if D_base < 40.0: D_base = 80.0
    if H < 20.0: H = 41.0
    top_c = max(D_base * 1.08, Sphere_R)

    # 1. 上部方形调平顶板 (边长 top_c x top_c，高 h_top = H * 0.48，位于 Z in [-h_top, 0])
    h_top = H * 0.48
    h_bot = H - h_top
    o1 = BOX(s, L=top_c, W=h_top, H=top_c).translate((0.0, 0.0, -(h_top / 2.0)))

    # 2. 下部缩径圆柱凸台底座 (直径 D_base * 0.88，高 h_bot，位于 Z in [-H, -h_top]) + 球面过渡脖子
    r_boss = (D_base / 2.0) * 0.88
    o_boss = CYLINDER(s, R=r_boss, H=h_bot + 2.0, O=0.0).translate((0.0, 0.0, -H))
    o1.uniteWith(o_boss); o_boss.erase()

    # 3. 顶面球窝凹槽与中心通孔 (严格还原图集 414 方形顶板+下部圆柱凸台与内球窝特征)
    o_cup = CONE(s, R1=r_boss * 0.45, R2=r_boss * 0.82, H=h_top * 0.55, E=0.0).translate((0.0, 0.0, -(h_top * 0.52)))
    o1.subtractFrom(o_cup); o_cup.erase()
    o_hole = CYLINDER(s, R=r_boss * 0.35, H=H + 10.0, O=0.0).translate((0.0, 0.0, -(H + 5.0)))
    o1.subtractFrom(o_hole); o_hole.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension('D_base', (-(top_c / 2.0), 0.0, 0.0), ((top_c / 2.0), 0.0, 0.0))
