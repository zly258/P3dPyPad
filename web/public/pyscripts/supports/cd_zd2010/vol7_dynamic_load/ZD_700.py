# -*- coding: utf-8 -*-
# CD-ZD2010 700~702 液压阻尼器（主液压缸筒 + 侧置储油补偿副筒/控制阀块 + 伸缩活塞杆 + 首尾两端关节轴承单耳环与连接销座）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="700液压阻尼器", TooltipLong="CD-ZD2010 700~702 液压阻尼器", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D_body=LENGTH, TooltipShort="缸筒外径D", TooltipLong="液压缸体外径 D")
@param(L_min=LENGTH, TooltipShort="安装长Amid", TooltipLong="两端关节销孔中心安装间距", Ask4Dist=True)
@param(Stroke_mm=LENGTH, TooltipShort="阻尼行程", TooltipLong="液压活塞最大位移行程")
@param(Pin_d=LENGTH, TooltipShort="销孔径d", TooltipLong="两端关节轴承销孔直径 d")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="额定荷载", TooltipLong="额定荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_700(s, D_body=129.0, L_min=420.0, Stroke_mm=120.0, Pin_d=25.0, ID=u"ZD_700", Load_kN=45.0, Weight_kg=11.2, **kw):
    D_body = float(D_body); L_min = float(L_min); Stroke_mm = float(Stroke_mm); Pin_d = float(Pin_d)
    if D_body < 40.0: D_body = 40.0
    if Pin_d < 10.0: Pin_d = 10.0
    if L_min < 200.0: L_min = 200.0

    # 对照图集 p.261 / p.268：主液压缸筒 + 侧置控制阀块与储油补偿副筒 + 伸缩活塞杆 + 首尾两端球铰单耳环与前后端销座组件
    R_cyl = D_body / 2.0
    ear_r = max(Pin_d * 1.15, R_cyl * 0.35)
    ear_t = max(12.0, Pin_d * 0.72)
    neck_l = ear_r * 1.4
    rod_ext = min(L_min * 0.38, max(50.0, Stroke_mm * 0.55 + 30.0))
    cyl_l = max(80.0, L_min - rod_ext - neck_l * 2.0)
    z_cyl_top = -neck_l
    z_cyl_btm = -(neck_l + cyl_l)

    # 1. 主液压缸筒 + 前后方形端盖法兰
    o1 = CYLINDER(s, R=R_cyl, H=cyl_l, O=0.0).translate((0.0, 0.0, z_cyl_btm))
    cap_h = max(16.0, cyl_l * 0.12)
    cap_w = D_body * 0.92
    o_cap1 = BOX(s, L=cap_w, W=cap_h, H=cap_w).translate((0.0, 0.0, z_cyl_top - cap_h / 2.0))
    o_cap2 = BOX(s, L=cap_w, W=cap_h, H=cap_w).translate((0.0, 0.0, z_cyl_btm + cap_h / 2.0))
    o1.uniteWith(o_cap1); o_cap1.erase()
    o1.uniteWith(o_cap2); o_cap2.erase()

    # 2. 侧置液压控制阀块与储油补偿副筒 (区分于弹簧减振器的核心特征！)
    manifold_w = D_body * 0.45
    manifold_h = cyl_l * 0.68
    o_man = BOX(s, L=manifold_w, W=manifold_h, H=manifold_w * 0.85).translate((R_cyl + manifold_w * 0.35, 0.0, z_cyl_btm + cyl_l * 0.5))
    o_acc = CYLINDER(s, R=R_cyl * 0.36, H=cyl_l * 0.75, O=0.0).translate((R_cyl + manifold_w * 0.52, manifold_w * 0.35, z_cyl_btm + cyl_l * 0.12))
    o1.uniteWith(o_man); o_man.erase()
    o1.uniteWith(o_acc); o_acc.erase()

    # 3. 活塞杆导向套、伸缩活塞杆与行程指示环
    rod_r = max(8.0, R_cyl * 0.36)
    o_gland = CYLINDER(s, R=rod_r * 1.45, H=neck_l * 0.6, O=0.0).translate((0.0, 0.0, z_cyl_btm - neck_l * 0.5))
    o_rod = CYLINDER(s, R=rod_r, H=rod_ext + neck_l * 1.2, O=0.0).translate((0.0, 0.0, -(L_min - ear_r * 0.5)))
    o_boot = CYLINDER(s, R=rod_r * 1.25, H=rod_ext * 0.35, O=0.0).translate((0.0, 0.0, z_cyl_btm - neck_l * 0.4 - rod_ext * 0.35))
    o1.uniteWith(o_gland); o_gland.erase()
    o1.uniteWith(o_rod); o_rod.erase()
    o1.uniteWith(o_boot); o_boot.erase()

    # 4. 首尾两端关节轴承球铰单耳环与双耳连接叉座 (Z = 0.0 与 Z = -L_min)
    o_neck_top = CYLINDER(s, R=rod_r * 1.15, H=neck_l + 6.0, O=0.0).translate((0.0, 0.0, z_cyl_top - 4.0))
    o1.uniteWith(o_neck_top); o_neck_top.erase()
    for zp in (0.0, -L_min):
        o_eye = CYLINDER(s, R=ear_r, H=ear_t, O=0.0).rotateY(90.0).translate((-ear_t / 2.0, 0.0, zp))
        o_hole = CYLINDER(s, R=Pin_d / 2.0, H=ear_t * 3.0, O=0.0).rotateY(90.0).translate((-ear_t * 1.5, 0.0, zp))
        o_eye.subtractFrom(o_hole); o_hole.erase()
        o1.uniteWith(o_eye); o_eye.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('L_min', (0.0, 0.0, 0.0), (0.0, 0.0, -L_min))
