# -*- coding: utf-8 -*-
# CD-ZD2010 213 弯头支座（已合并 213/216：上部90°弯头 ARC3D + 下部竖直圆管支腿托座 + 底部方形底板与加劲肋）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="213热压弯头支座", TooltipLong="CD-ZD2010 213/216 弯头支座（90°弯头+竖直圆管支腿+底板加劲肋）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D=LENGTH, TooltipShort="管外径", TooltipLong="弯头外径 OD")
@param(R_bend=LENGTH, TooltipShort="弯曲半径", TooltipLong="90度弯头曲率半径 R")
@param(SH=LENGTH, TooltipShort="底高", TooltipLong="弯头水平端中心线至底板高度 H", Ask4Dist=True)
@param(SW=LENGTH, TooltipShort="底板宽", TooltipLong="方形底座宽度 B")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
def ZD_213(s, D=219.0, R_bend=305.0, SH=300.0, SW=210.0, ID=u"ZD_213", **kw):
    D = float(D); R_bend = float(R_bend); SH = float(SH); SW = float(SW)
    if D < 25.0: D = 25.0
    R1 = D / 2.0
    if R_bend <= R1 * 1.15: R_bend = R1 * 1.45
    if SH <= R1 + 40.0: SH = R1 + 90.0
    if SW <= D * 0.75: SW = D * 0.95 + 30.0
    ST = max(12.0, min(24.0, D * 0.07))
    wall_t = max(5.0, min(14.0, R1 * 0.14))

    # 1. 上部 90° 弯头 ARC3D (铁律6：ARC3D 的 D 为管半径 R1！旋转至 XZ 平面：一端在 (0,0,0) 朝 +X，另一端在 (-R_bend,0,R_bend) 朝 +Z)
    o_elb_out = ARC3D(s, D=R1, R=R_bend, A=90.0).rotateZ(90.0).rotateX(90.0)
    o_elb_in = ARC3D(s, D=R1 - wall_t, R=R_bend, A=90.0).rotateZ(90.0).rotateX(90.0)

    # 2. 下部竖直圆管支腿托座 (位于 X = -R_bend * 0.62，向上与 90° 弯头底部相贯焊接)
    leg_r = R1 * 0.68
    x_leg = -(R_bend * 0.62)
    z_top_leg = R_bend * 0.38
    leg_h = SH - ST + z_top_leg
    o_leg = CYLINDER(s, R=leg_r, H=leg_h, O=0.0).translate((x_leg, 0.0, -(SH - ST)))
    o_leg_in = CYLINDER(s, R=leg_r - wall_t * 0.85, H=leg_h + 4.0, O=0.0).translate((x_leg, 0.0, -(SH - ST + 2.0)))
    o_leg.subtractFrom(o_leg_in); o_leg_in.erase()
    # 用弯头外廓切出支腿顶部真实马鞍相贯口
    o_elb_cut = ARC3D(s, D=R1 - 1.0, R=R_bend, A=90.0).rotateZ(90.0).rotateX(90.0)
    o_leg.subtractFrom(o_elb_cut); o_elb_cut.erase()

    # 弯头空心化并与支腿合并
    o_elb_out.subtractFrom(o_elb_in); o_elb_in.erase()
    o1 = o_elb_out
    o1.uniteWith(o_leg); o_leg.erase()

    # 3. 底部方形底板 (□B = SW x SW) + 支腿根部十字 4 块三角形加劲肋板 (还原 213/216 支腿底板与肋板)
    o_base = BOX(s, L=SW, W=ST, H=SW).translate((x_leg, 0.0, -(SH - ST / 2.0)))
    o1.uniteWith(o_base); o_base.erase()

    rib_h = min(SH * 0.42, SW * 0.55)
    rib_w = (SW * 0.92)
    for rot_z in (0.0, 90.0):
        o_rib = BOX(s, L=wall_t, W=rib_h, H=rib_w).rotateZ(rot_z).translate((x_leg, 0.0, -(SH - ST - rib_h / 2.0)))
        o1.uniteWith(o_rib); o_rib.erase()
    # 清除伸入支腿内孔的肋板部分
    o_leg_clean = CYLINDER(s, R=leg_r - wall_t * 0.85, H=leg_h, O=0.0).translate((x_leg, 0.0, -(SH - ST)))
    o1.subtractFrom(o_leg_clean); o_leg_clean.erase()

    s.setPoint((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension('SH', (x_leg, 0.0, 0.0), (x_leg, 0.0, -SH))
