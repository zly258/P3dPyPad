# -*- coding: utf-8 -*-
# CD-ZD2010 521 单吊板连接变力弹簧组件（圆柱弹簧筒体 + 侧壁刻度槽 + 顶盖中心焊接直立圆头单耳吊板 + 底部伸出吊杆）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="521单吊板变力弹簧", TooltipLong="CD-ZD2010 521 单吊板连接变力弹簧组件", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D_casing=LENGTH, TooltipShort="筒体外径", TooltipLong="弹簧壳筒外径")
@param(H_free=LENGTH, TooltipShort="壳筒高", TooltipLong="筒体高度", Ask4Dist=True)
@param(Pin_d=LENGTH, TooltipShort="销轴孔径", TooltipLong="顶吊耳销轴孔径 d1")
@param(Travel_mm=LENGTH, TooltipShort="工作行程", TooltipLong="额定位移量")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_min_kN=LENGTH0, TooltipShort="最小荷载", TooltipLong="最小工作荷载(kN)")
@param(Load_max_kN=LENGTH0, TooltipShort="最大荷载", TooltipLong="最大工作荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_521(s, D_casing=214.0, H_free=391.0, Pin_d=26.0, Travel_mm=75.0, ID=u"ZD_521", Load_min_kN=5.4, Load_max_kN=11.564, Weight_kg=39.0, **kw):
    D_casing = float(D_casing); H_free = float(H_free); Pin_d = float(Pin_d); Travel_mm = float(Travel_mm)
    if D_casing < 60.0: D_casing = 60.0
    if H_free < 120.0: H_free = 120.0
    if Pin_d < 10.0: Pin_d = 10.0
    RT = D_casing / 2.0
    thk = max(5.0, min(10.0, RT * 0.12))
    cap_t = max(8.0, min(18.0, RT * 0.14))

    # 1. 空心圆柱弹簧筒体与上下端盖 (Z in [-H_free, 0])
    o1 = CYLINDER(s, R=RT, H=H_free, O=0.0).translate((0.0, 0.0, -H_free))
    o_in = CYLINDER(s, R=RT - thk, H=max(20.0, H_free - cap_t * 2.0), O=0.0).translate((0.0, 0.0, -(H_free - cap_t)))
    o1.subtractFrom(o_in); o_in.erase()
    o_top = CYLINDER(s, R=RT + 4.0, H=cap_t, O=0.0).translate((0.0, 0.0, -cap_t))
    o_btm = CYLINDER(s, R=RT + 4.0, H=cap_t, O=0.0).translate((0.0, 0.0, -H_free))
    o1.uniteWith(o_top); o_top.erase()
    o1.uniteWith(o_btm); o_btm.erase()

    # 2. 侧壁行程刻度槽窗与压板指针
    slot_w = max(12.0, RT * 0.20)
    slot_h = min(H_free * 0.65, max(30.0, Travel_mm + 20.0))
    slot_z = -(H_free * 0.55)
    o_slot = BOX(s, L=RT * 2.5, W=slot_h, H=slot_w).translate((0.0, 0.0, slot_z))
    o1.subtractFrom(o_slot); o_slot.erase()
    plate_z = slot_z + min(Travel_mm * 0.25, slot_h * 0.3)
    o_piston = CYLINDER(s, R=RT - thk * 1.2, H=cap_t * 1.2, O=0.0).translate((0.0, 0.0, plate_z - cap_t * 0.6))
    o_ptr = BOX(s, L=RT * 2.15, W=6.0, H=slot_w * 0.75).translate((0.0, 0.0, plate_z))
    o1.uniteWith(o_piston); o_piston.erase()
    o1.uniteWith(o_ptr); o_ptr.erase()

    # 3. 顶盖中心焊接直立圆头单耳吊板 (图集 521：销孔中心距顶盖 f，外圆弧半径 e，板厚 t)
    ear_r = max(Pin_d * 1.05, 18.0)
    ear_f = max(Pin_d * 1.45, 26.0)
    ear_t = max(12.0, Pin_d * 0.65)
    ear_w = ear_r * 2.0
    o_ear_rect = BOX(s, L=ear_t, W=ear_f + 6.0, H=ear_w).translate((0.0, 0.0, (ear_f - 6.0) / 2.0))
    o_ear_top = CYLINDER(s, R=ear_r, H=ear_t, O=0.0).rotateX(90.0).translate((0.0, ear_t / 2.0, ear_f))
    o_ear_rect.uniteWith(o_ear_top); o_ear_top.erase()
    o_hole = CYLINDER(s, R=Pin_d / 2.0, H=ear_t * 3.0, O=0.0).rotateX(90.0).translate((0.0, ear_t * 1.5, ear_f))
    o_ear_rect.subtractFrom(o_hole); o_hole.erase()
    o1.uniteWith(o_ear_rect); o_ear_rect.erase()

    # 4. 底部伸出吊杆与锁紧套
    rod_d = max(12.0, Pin_d * 0.75)
    btm_ext = max(45.0, rod_d * 2.2)
    rod_l = (H_free + plate_z) + btm_ext
    o_btm_rod = CYLINDER(s, R=rod_d / 2.0, H=rod_l, O=0.0).translate((0.0, 0.0, -(H_free + btm_ext)))
    o_nut = CYLINDER(s, R=rod_d * 0.9, H=rod_d * 1.3, O=0.0).translate((0.0, 0.0, -(H_free + btm_ext * 0.6)))
    o1.uniteWith(o_btm_rod); o_btm_rod.erase()
    o1.uniteWith(o_nut); o_nut.erase()

    s.setPoint((0.0, 0.0, ear_f), (0.0, 0.0, 1.0))
    s.setLinearDimension('H_free', (0.0, 0.0, 0.0), (0.0, 0.0, -H_free))
