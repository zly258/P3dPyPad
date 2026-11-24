# -*- coding: utf-8 -*-
# CD-ZD2010 740 拉撑杆（刚性厚壁无缝钢管撑杆 + 两端锥形收口过渡与调节螺母套 + 首尾关节轴承耳环）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="740拉撑杆", TooltipLong="CD-ZD2010 740 拉撑杆（刚性防晃撑杆）", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D_pipe=LENGTH, TooltipShort="撑杆管径D", TooltipLong="撑杆无缝钢管外径 D")
@param(L_min=LENGTH, TooltipShort="安装长L", TooltipLong="两端销中心工作长度 L", Ask4Dist=True)
@param(Pin_d=LENGTH, TooltipShort="铰孔径d", TooltipLong="端部铰接销孔孔径 d")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="许用荷载", TooltipLong="许用荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_740(s, D_pipe=100.0, L_min=1000.0, Pin_d=35.0, ID=u"ZD_740", Load_kN=80.0, Weight_kg=20.34, **kw):
    D_pipe = float(D_pipe); L_min = float(L_min); Pin_d = float(Pin_d)
    if D_pipe < 36.0: D_pipe = 36.0
    if Pin_d < 12.0: Pin_d = 12.0
    if L_min < 280.0: L_min = 280.0

    # 对照图集 p.261 / p.280 图 1：中部刚性厚壁钢管 ØD + 两端锥形收口过渡段 + 两端可调螺杆与锁紧六角螺母套 + 首尾球面关节轴承圆耳环 Ød
    R_pipe = D_pipe / 2.0
    ear_r = max(Pin_d * 1.18, R_pipe * 0.65)
    ear_t = max(14.0, Pin_d * 0.72)
    end_ext = max(65.0, ear_r * 1.9 + D_pipe * 0.55)
    cone_l = max(30.0, D_pipe * 0.45)
    pipe_l = max(80.0, L_min - end_ext * 2.0 - cone_l * 2.0)
    z_p1 = -(end_ext + cone_l)
    z_p2 = -(L_min - end_ext - cone_l)

    # 1. 中部刚性厚壁无缝钢管 (显式空心内壁)
    thk = max(5.0, R_pipe * 0.16)
    o1 = CYLINDER(s, R=R_pipe, H=pipe_l, O=0.0).translate((0.0, 0.0, z_p2))
    o_in = CYLINDER(s, R=R_pipe - thk, H=max(20.0, pipe_l - thk * 2.0), O=0.0).translate((0.0, 0.0, z_p2 + thk))
    o1.subtractFrom(o_in); o_in.erase()

    # 2. 两端对称锥形收口过渡段 (CONE) + 螺纹调节杆与锁紧螺母环
    r_shank = max(Pin_d * 0.48, R_pipe * 0.42)
    o_cone_top = CONE(s, R1=R_pipe, R2=r_shank, H=cone_l, E=0.0).translate((0.0, 0.0, z_p1))
    o_cone_btm = CONE(s, R1=r_shank, R2=R_pipe, H=cone_l, E=0.0).translate((0.0, 0.0, z_p2 - cone_l))
    o_rod_top = CYLINDER(s, R=r_shank, H=end_ext, O=0.0).translate((0.0, 0.0, -end_ext))
    o_rod_btm = CYLINDER(s, R=r_shank, H=end_ext, O=0.0).translate((0.0, 0.0, -L_min))
    o_nut_top = CYLINDER(s, R=r_shank * 1.45, H=cone_l * 0.55, O=0.0).translate((0.0, 0.0, -(end_ext * 0.78)))
    o_nut_btm = CYLINDER(s, R=r_shank * 1.45, H=cone_l * 0.55, O=0.0).translate((0.0, 0.0, -(L_min - end_ext * 0.45)))
    for p in (o_cone_top, o_cone_btm, o_rod_top, o_rod_btm, o_nut_top, o_nut_btm):
        o1.uniteWith(p); p.erase()

    # 3. 首尾两端球铰关节轴承圆耳环 (带内圈凸台与销孔 Ød)
    for zp in (0.0, -L_min):
        o_eye = CYLINDER(s, R=ear_r, H=ear_t, O=0.0).rotateY(90.0).translate((-ear_t / 2.0, 0.0, zp))
        o_bush = CYLINDER(s, R=Pin_d * 0.76, H=ear_t * 1.35, O=0.0).rotateY(90.0).translate((-ear_t * 0.675, 0.0, zp))
        o_eye.uniteWith(o_bush); o_bush.erase()
        o_hole = CYLINDER(s, R=Pin_d / 2.0, H=ear_t * 2.5, O=0.0).rotateY(90.0).translate((-ear_t * 1.25, 0.0, zp))
        o_eye.subtractFrom(o_hole); o_hole.erase()
        o1.uniteWith(o_eye); o_eye.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('L_min', (0.0, 0.0, 0.0), (0.0, 0.0, -L_min))
