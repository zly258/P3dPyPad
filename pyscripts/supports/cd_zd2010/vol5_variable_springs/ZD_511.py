# -*- coding: utf-8 -*-
# CD-ZD2010 511 吊杆连接变力弹簧组件（圆柱弹簧筒体 + 侧壁行程刻度长槽窗 + 顶盖与底盖 + 顶部中心吊杆螺纹孔座 + 顶盖两侧对称小吊耳 + 底部吊杆及花兰螺母）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="511吊杆变力弹簧", TooltipLong="CD-ZD2010 511 吊杆连接变力弹簧组件", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D_casing=LENGTH, TooltipShort="外筒径", TooltipLong="弹簧保护壳筒外径")
@param(H_free=LENGTH, TooltipShort="壳筒高", TooltipLong="弹簧壳体高度", Ask4Dist=True)
@param(Thread_d=LENGTH, TooltipShort="吊杆径", TooltipLong="主吊杆公称螺纹直径")
@param(Travel_mm=LENGTH, TooltipShort="工作行程", TooltipLong="弹簧工作位移行程量")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_min_kN=LENGTH0, TooltipShort="最小荷载", TooltipLong="最小工作荷载(kN)")
@param(Load_max_kN=LENGTH0, TooltipShort="最大荷载", TooltipLong="最大工作荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_511(s, D_casing=214.0, H_free=408.0, Thread_d=20.0, Travel_mm=75.0, ID=u"ZD_511", Load_min_kN=5.4, Load_max_kN=11.564, Weight_kg=38.7, **kw):
    D_casing = float(D_casing); H_free = float(H_free); Thread_d = float(Thread_d); Travel_mm = float(Travel_mm)
    if D_casing < 60.0: D_casing = 60.0
    if H_free < 120.0: H_free = 120.0
    if Thread_d < 10.0: Thread_d = 10.0
    RT = D_casing / 2.0
    thk = max(5.0, min(10.0, RT * 0.12))
    cap_t = max(8.0, min(18.0, RT * 0.14))

    # 1. 空心圆柱弹簧筒体 (Z in [-H_free, 0])
    o1 = CYLINDER(s, R=RT, H=H_free, O=0.0).translate((0.0, 0.0, -H_free))
    o_in = CYLINDER(s, R=RT - thk, H=max(20.0, H_free - cap_t * 2.0), O=0.0).translate((0.0, 0.0, -(H_free - cap_t)))
    o1.subtractFrom(o_in); o_in.erase()

    # 2. 侧壁双侧对称行程刻度长槽窗 (由 Travel_mm 驱动) + 铭牌凸框
    slot_w = max(12.0, RT * 0.20)
    slot_h = min(H_free * 0.65, max(30.0, Travel_mm + 20.0))
    slot_z = -(H_free * 0.55)
    o_slot = BOX(s, L=RT * 2.5, W=slot_h, H=slot_w).translate((0.0, 0.0, slot_z))
    o1.subtractFrom(o_slot); o_slot.erase()

    # 3. 顶盖与底盖圆盘 (带微凸包边)
    o_top = CYLINDER(s, R=RT + 4.0, H=cap_t, O=0.0).translate((0.0, 0.0, -cap_t))
    o_btm = CYLINDER(s, R=RT + 4.0, H=cap_t, O=0.0).translate((0.0, 0.0, -H_free))
    o1.uniteWith(o_top); o_top.erase()
    o1.uniteWith(o_btm); o_btm.erase()

    # 4. 顶部中心吊杆螺纹孔座 + 向上伸出上连接吊杆段 (1.5*d) + 锁紧六角螺母
    boss_r = max(Thread_d * 0.95, RT * 0.25)
    boss_h = max(16.0, Thread_d * 0.8)
    o_boss = CYLINDER(s, R=boss_r, H=boss_h, O=0.0).translate((0.0, 0.0, -2.0))
    o_top_rod = CYLINDER(s, R=Thread_d / 2.0, H=Thread_d * 2.2 + boss_h, O=0.0).translate((0.0, 0.0, -boss_h * 0.5))
    o1.uniteWith(o_boss); o_boss.erase()
    o1.uniteWith(o_top_rod); o_top_rod.erase()

    # 5. 顶盖外侧对称小吊耳 (图集 511 特征：顶盖下方筒体上部两侧小起吊耳环)
    lug_r = max(10.0, RT * 0.14)
    lug_t = max(6.0, thk * 0.8)
    lug_z = -(cap_t + lug_r * 1.3)
    for sy in (-1.0, 1.0):
        o_lug = BOX(s, L=lug_r * 1.4, W=lug_r * 2.0, H=lug_t).translate((0.0, sy * (RT + lug_r * 0.4), lug_z))
        o_lh = CYLINDER(s, R=lug_r * 0.45, H=lug_t * 3.0, O=0.0).rotateY(90.0).translate((-lug_t * 1.5, sy * (RT + lug_r * 0.55), lug_z))
        o_lug.subtractFrom(o_lh); o_lh.erase()
        o1.uniteWith(o_lug); o_lug.erase()

    # 6. 内部弹簧压板、行程指示指针 + 底部伸出吊杆及花兰调节螺母套
    plate_z = slot_z + min(Travel_mm * 0.25, slot_h * 0.3)
    o_piston = CYLINDER(s, R=RT - thk * 1.2, H=cap_t * 1.2, O=0.0).translate((0.0, 0.0, plate_z - cap_t * 0.6))
    o_ptr = BOX(s, L=RT * 2.15, W=6.0, H=slot_w * 0.75).translate((0.0, 0.0, plate_z))
    o1.uniteWith(o_piston); o_piston.erase()
    o1.uniteWith(o_ptr); o_ptr.erase()

    btm_ext = max(45.0, Thread_d * 2.2)
    rod_l = (H_free + plate_z) + btm_ext
    o_btm_rod = CYLINDER(s, R=Thread_d / 2.0, H=rod_l, O=0.0).translate((0.0, 0.0, -(H_free + btm_ext)))
    o_nut = CYLINDER(s, R=Thread_d * 0.9, H=Thread_d * 1.4, O=0.0).translate((0.0, 0.0, -(H_free + btm_ext * 0.65)))
    o1.uniteWith(o_btm_rod); o_btm_rod.erase()
    o1.uniteWith(o_nut); o_nut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('H_free', (0.0, 0.0, 0.0), (0.0, 0.0, -H_free))
