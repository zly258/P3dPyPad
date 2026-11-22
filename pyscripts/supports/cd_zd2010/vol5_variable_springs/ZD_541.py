# -*- coding: utf-8 -*-
# CD-ZD2010 541 吊杆调节支撑式变力弹簧组件（圆柱弹簧筒体 + 底部两侧对称向下延伸的双槽钢支腿立柱及底脚板 + 顶部调节螺杆）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="541支撑式变力弹簧", TooltipLong="CD-ZD2010 541 吊杆调节支撑式变力弹簧组件", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D_casing=LENGTH, TooltipShort="筒径", TooltipLong="壳筒外径")
@param(H_free=LENGTH, TooltipShort="安装高", TooltipLong="0位总安装高度 H0", Ask4Dist=True)
@param(Thread_d=LENGTH, TooltipShort="调节杆径", TooltipLong="顶部调节螺杆直径 d")
@param(Travel_mm=LENGTH, TooltipShort="行程", TooltipLong="弹簧行程")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_min_kN=LENGTH0, TooltipShort="最小荷载", TooltipLong="最小工作荷载(kN)")
@param(Load_max_kN=LENGTH0, TooltipShort="最大荷载", TooltipLong="最大工作荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_541(s, D_casing=214.0, H_free=511.0, Thread_d=20.0, Travel_mm=75.0, ID=u"ZD_541", Load_min_kN=5.4, Load_max_kN=11.564, Weight_kg=36.5, **kw):
    D_casing = float(D_casing); H_free = float(H_free); Thread_d = float(Thread_d); Travel_mm = float(Travel_mm)
    if D_casing < 60.0: D_casing = 60.0
    if H_free < 160.0: H_free = 160.0
    if Thread_d < 10.0: Thread_d = 10.0
    RT = D_casing / 2.0
    thk = max(5.0, min(10.0, RT * 0.12))
    cap_t = max(8.0, min(18.0, RT * 0.14))

    # 图集 541 特征：H_free 为总高 H0，上部伸出调节螺杆 top_rod_h，中部圆柱筒体 cyl_h，底部两侧双槽钢支腿 leg_h
    top_rod_h = max(45.0, min(H_free * 0.20, Thread_d * 3.0))
    leg_h = max(45.0, min(H_free * 0.22, RT * 0.9))
    cyl_h = max(80.0, H_free - top_rod_h - leg_h)
    z_cyl_top = -top_rod_h
    z_cyl_btm = -(top_rod_h + cyl_h)

    # 1. 中部圆柱弹簧筒体与上下端盖 (Z in [z_cyl_btm, z_cyl_top])
    o1 = CYLINDER(s, R=RT, H=cyl_h, O=0.0).translate((0.0, 0.0, z_cyl_btm))
    o_in = CYLINDER(s, R=RT - thk, H=max(20.0, cyl_h - cap_t * 2.0), O=0.0).translate((0.0, 0.0, z_cyl_btm + cap_t))
    o1.subtractFrom(o_in); o_in.erase()
    o_top = CYLINDER(s, R=RT + 4.0, H=cap_t, O=0.0).translate((0.0, 0.0, z_cyl_top - cap_t))
    o_btm = CYLINDER(s, R=RT + 6.0, H=cap_t, O=0.0).translate((0.0, 0.0, z_cyl_btm))
    o1.uniteWith(o_top); o_top.erase()
    o1.uniteWith(o_btm); o_btm.erase()

    # 2. 侧壁行程刻度长槽窗与压板指针
    slot_w = max(12.0, RT * 0.20)
    slot_h = min(cyl_h * 0.65, max(25.0, Travel_mm + 16.0))
    slot_z = z_cyl_btm + cyl_h * 0.45
    o_slot = BOX(s, L=RT * 2.5, W=slot_h, H=slot_w).translate((0.0, 0.0, slot_z))
    o1.subtractFrom(o_slot); o_slot.erase()
    plate_z = slot_z + min(Travel_mm * 0.2, slot_h * 0.25)
    o_piston = CYLINDER(s, R=RT - thk * 1.2, H=cap_t * 1.2, O=0.0).translate((0.0, 0.0, plate_z - cap_t * 0.6))
    o_ptr = BOX(s, L=RT * 2.15, W=6.0, H=slot_w * 0.75).translate((0.0, 0.0, plate_z))
    o1.uniteWith(o_piston); o_piston.erase()
    o1.uniteWith(o_ptr); o_ptr.erase()

    # 3. 顶部调节螺杆与花兰调节螺母套 (直达 Z = 0.0)
    o_rod = CYLINDER(s, R=Thread_d / 2.0, H=top_rod_h + (z_cyl_top - plate_z) + 25.0, O=0.0).translate((0.0, 0.0, plate_z - 25.0))
    o_sleeve = CYLINDER(s, R=Thread_d * 0.95, H=top_rod_h * 0.55, O=0.0).translate((0.0, 0.0, -top_rod_h * 0.7))
    o1.uniteWith(o_rod); o_rod.erase()
    o1.uniteWith(o_sleeve); o_sleeve.erase()

    # 4. 底部两侧对称向下延伸的双槽钢支腿立柱及外翻底脚板 (直达 Z = -H_free，对照图集 p.227)
    ch_h = max(36.0, RT * 0.55)
    ch_w = max(24.0, RT * 0.32)
    ch_t = max(6.0, thk * 0.85)
    foot_t = max(8.0, cap_t * 0.8)
    leg_y = RT * 0.58
    for sy in (-1.0, 1.0):
        # 竖向槽钢支腿 (开口向外)
        o_leg = BOX(s, L=ch_w, W=leg_h + 4.0, H=ch_h).translate((0.0, sy * leg_y, z_cyl_btm - leg_h / 2.0 + 2.0))
        o_cut = BOX(s, L=ch_w, W=leg_h + 10.0, H=max(8.0, ch_h - ch_t * 2.0)).translate((0.0, sy * (leg_y + ch_t), z_cyl_btm - leg_h / 2.0))
        o_leg.subtractFrom(o_cut); o_cut.erase()
        # 底部外翻水平底脚板
        foot_w = ch_w * 1.65
        o_foot = BOX(s, L=foot_w, W=foot_t, H=ch_h * 1.35).translate((0.0, sy * (leg_y + (foot_w - ch_w) * 0.35), -H_free + foot_t / 2.0))
        o1.uniteWith(o_leg); o_leg.erase()
        o1.uniteWith(o_foot); o_foot.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('H_free', (0.0, 0.0, 0.0), (0.0, 0.0, -H_free))
