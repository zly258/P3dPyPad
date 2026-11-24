# -*- coding: utf-8 -*-
# CD-ZD2010 720~721 弹簧减振器（粗圆柱弹簧储能筒 + 侧壁双段刻度槽窗 + 前端锥台/阶梯过渡套与固定螺母 + 活塞杆 + 首尾两端球铰吊耳板）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="720弹簧减振器", TooltipLong="CD-ZD2010 720~721 弹簧减振器", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D_body=LENGTH, TooltipShort="套筒径D", TooltipLong="减振器壳体外径 D")
@param(L_install=LENGTH, TooltipShort="安装长L", TooltipLong="两端安装销孔中心距 L", Ask4Dist=True)
@param(Stroke_mm=LENGTH, TooltipShort="行程", TooltipLong="减振允许往复位移量")
@param(Pin_d=LENGTH, TooltipShort="销孔径d", TooltipLong="两端铰接销孔孔径 d")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_kN=LENGTH0, TooltipShort="减振荷载", TooltipLong="最大减振荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_720(s, D_body=159.0, L_install=829.0, Stroke_mm=65.0, Pin_d=15.0, ID=u"ZD_720", Load_kN=8.19, Weight_kg=38.32, **kw):
    D_body = float(D_body); L_install = float(L_install); Stroke_mm = float(Stroke_mm); Pin_d = float(Pin_d)
    if D_body < 60.0: D_body = 60.0
    if Pin_d < 10.0: Pin_d = 10.0
    if L_install < 300.0: L_install = 300.0

    # 对照图集 p.261 / p.277：粗圆柱弹簧储能筒 (长 K) + 侧壁双段刻度长槽窗 + 前端锥台与六角固定螺母套 + 伸缩调节螺杆 + 首尾两端扁平梯形球铰吊耳板
    R_body = D_body / 2.0
    thk = max(6.0, R_body * 0.12)
    lug_l = max(75.0, D_body * 0.65)
    casing_k = min(L_install * 0.56, max(180.0, L_install - lug_l * 2.4))
    rod_ext = max(60.0, L_install - casing_k - lug_l * 1.8)
    z_cyl_top = -lug_l
    z_cyl_btm = -(lug_l + casing_k)

    # 1. 粗圆柱弹簧储能筒 (空心圆筒 + 侧壁上下两段对称刻度观察窗 + 上下压板)
    o1 = CYLINDER(s, R=R_body, H=casing_k, O=0.0).translate((0.0, 0.0, z_cyl_btm))
    o_in = CYLINDER(s, R=R_body - thk, H=max(30.0, casing_k - thk * 2.4), O=0.0).translate((0.0, 0.0, z_cyl_btm + thk * 1.2))
    o1.subtractFrom(o_in); o_in.erase()

    # 侧壁两段行程观察槽窗 (对照 p.277 图 1：铭牌两侧左、右两段刻度窗)
    slot_w = max(14.0, R_body * 0.24)
    slot_h = min(casing_k * 0.34, max(30.0, Stroke_mm * 0.65))
    o_s1 = BOX(s, L=R_body * 2.5, W=slot_h, H=slot_w).translate((0.0, 0.0, z_cyl_top - casing_k * 0.26))
    o_s2 = BOX(s, L=R_body * 2.5, W=slot_h, H=slot_w).translate((0.0, 0.0, z_cyl_btm + casing_k * 0.26))
    o1.subtractFrom(o_s1); o_s1.erase()
    o1.subtractFrom(o_s2); o_s2.erase()

    # 筒内上下弹簧压板与中心芯轴（贯穿上下端板）
    o_core = CYLINDER(s, R=R_body * 0.42, H=casing_k - thk, O=0.0).translate((0.0, 0.0, z_cyl_btm + thk * 0.5))
    o1.uniteWith(o_core); o_core.erase()

    # 2. 前端 (下端) 锥台过渡套 + 荷载调整螺母与固定锁紧螺母 + 可调连接螺杆
    cone_h = max(32.0, D_body * 0.28)
    o_cone = CONE(s, R1=R_body * 0.48, R2=R_body * 0.82, H=cone_h, E=0.0).translate((0.0, 0.0, z_cyl_btm - cone_h))
    o_nut_fix = BOX(s, L=R_body * 0.95, W=cone_h * 0.55, H=R_body * 0.95).translate((0.0, 0.0, z_cyl_btm - cone_h * 1.25))
    rod_r = max(10.0, R_body * 0.24)
    o_rod = CYLINDER(s, R=rod_r, H=rod_ext + lug_l * 0.5, O=0.0).translate((0.0, 0.0, -(L_install - lug_l * 0.6)))
    o1.uniteWith(o_cone); o_cone.erase()
    o1.uniteWith(o_nut_fix); o_nut_fix.erase()
    o1.uniteWith(o_rod); o_rod.erase()

    # 3. 首端 (Z=0) 与尾端 (Z=-L_install) 梯形过渡连接吊耳板 + 球铰轴承孔 (对照 p.277 图 1 的连接板与销头 1)
    ear_t = max(12.0, Pin_d * 0.8)
    ear_r = max(Pin_d * 1.25, R_body * 0.34)
    # 首端连接板 (Z in [z_cyl_top, 0])
    o_top_lug = BOX(s, L=ear_t, W=lug_l, H=ear_r * 2.1).translate((0.0, 0.0, -lug_l / 2.0))
    o_top_disc = CYLINDER(s, R=ear_r, H=ear_t, O=0.0).rotateX(90.0).translate((0.0, ear_t / 2.0, 0.0))
    o_top_lug.uniteWith(o_top_disc); o_top_disc.erase()
    o_th = CYLINDER(s, R=Pin_d / 2.0, H=ear_t * 3.0, O=0.0).rotateX(90.0).translate((0.0, ear_t * 1.5, 0.0))
    o_top_lug.subtractFrom(o_th); o_th.erase()
    o1.uniteWith(o_top_lug); o_top_lug.erase()

    # 尾端销头 (Z = -L_install)
    btm_lug_h = lug_l * 0.85
    o_btm_lug = BOX(s, L=ear_t, W=btm_lug_h, H=ear_r * 2.0).translate((0.0, 0.0, -(L_install - btm_lug_h / 2.0)))
    o_btm_disc = CYLINDER(s, R=ear_r, H=ear_t, O=0.0).rotateX(90.0).translate((0.0, ear_t / 2.0, -L_install))
    o_btm_lug.uniteWith(o_btm_disc); o_btm_disc.erase()
    o_bh = CYLINDER(s, R=Pin_d / 2.0, H=ear_t * 3.0, O=0.0).rotateX(90.0).translate((0.0, ear_t * 1.5, -L_install))
    o_btm_lug.subtractFrom(o_bh); o_bh.erase()
    o1.uniteWith(o_btm_lug); o_btm_lug.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('L_install', (0.0, 0.0, 0.0), (0.0, 0.0, -L_install))
