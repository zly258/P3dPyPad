# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *
import math

@activate(Group="Equipment", Ports=2, TooltipShort=u"化工卧式单级离心泵组 (ISO 2858 / IH型)", TooltipLong=u"化工行业标准 ISO 2858 / GB/T 5662 IH型单级单吸悬臂式化工离心泵组 (Horizontal End-Suction Chemical Centrifugal Pump)，含共用型钢底座、蜗壳泵体、轴向吸入法兰口、顶部中心垂直吐出法兰口、轴承悬架体、联轴器护罩与防爆电机", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"设备主要结构尺寸：筒体、封头、接管与支承高度")
@param(DN_SUC=LENGTH, TooltipShort=u"轴向吸入口外径", Ask4Dist=True, TooltipLong=u"轴向吸入口外径")
@param(DN_DIS=LENGTH, TooltipShort=u"顶部吐出口外径", Ask4Dist=True, TooltipLong=u"顶部吐出口外径")
@param(L_BASE=LENGTH, TooltipShort=u"共用底座总长 L", Ask4Dist=True, TooltipLong=u"共用底座总长 L")
@param(W_BASE=LENGTH, TooltipShort=u"共用底座总宽 B", Ask4Dist=True, TooltipLong=u"共用底座总宽 B")
@param(H_AXIS=LENGTH, TooltipShort=u"泵轴中心高 H1", Ask4Dist=True, TooltipLong=u"泵轴中心高 H1")
@param(H_DIS=LENGTH, TooltipShort=u"中心至吐出口高 H2", Ask4Dist=True, TooltipLong=u"中心至吐出口高 H2")
@param(ID=STRING, TooltipShort=u"机泵位号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def EQUIPMENT_CENTRIFUGAL_PUMP(s, DN_SUC=114.3, DN_DIS=88.9, L_BASE=1250.0, W_BASE=490.0, H_AXIS=310.0, H_DIS=280.0, ID="P-101A", **kw):
    DN_SUC = max(40.0, float(DN_SUC))
    DN_DIS = max(32.0, float(DN_DIS))
    L_BASE = max(800.0, float(L_BASE))
    W_BASE = max(320.0, float(W_BASE))
    H_AXIS = max(220.0, float(H_AXIS))
    H_DIS = max(180.0, float(H_DIS))

    r_suc = DN_SUC / 2.0
    r_dis = DN_DIS / 2.0
    r_fl_suc = r_suc + 52.0
    r_fl_dis = r_dis + 50.0
    fl_t = 22.0

    # 坐标系约定：
    # 轴向吸入法兰端面 (Port 1) 位于 (0, 0, H_AXIS) 朝向 (-1, 0, 0)
    # 蜗壳中心位于 (x_vol, 0, H_AXIS)，顶部吐出法兰端面 (Port 2) 位于 (x_vol, 0, H_AXIS + H_DIS) 朝向 (0, 0, 1)
    h_base = 90.0
    x_vol = 140.0
    x_base_start = 50.0

    # 1. 共用重型槽钢底座 (Baseplate: x in [x_base_start, x_base_start + L_BASE], z in [0, h_base])
    o_pump = BOX(s, L=W_BASE, W=h_base, H=L_BASE).translate((x_base_start + L_BASE * 0.5, 0.0, h_base * 0.5))
    # 底座两侧下沿折边
    o_base_cut = BOX(s, L=W_BASE - 36.0, W=h_base - 18.0, H=L_BASE - 36.0).translate((x_base_start + L_BASE * 0.5, 0.0, (h_base - 18.0) * 0.5 - 2.0))
    o_pump.subtractFrom(o_base_cut); o_base_cut.erase()

    # 2. 蜗壳泵体 (Volute Casing) + 泵体双支脚 + 轴向吸入管嘴 + 顶部垂直吐出管嘴
    r_vol = max(H_DIS * 0.72, r_suc * 2.2)
    w_vol = max(130.0, DN_SUC * 1.15)
    o_vol = CYLINDER(s, R=r_vol, H=w_vol, O=0.0).rotateY(90.0).translate((x_vol - w_vol * 0.45, 0.0, H_AXIS))
    o_pump.uniteWith(o_vol); o_vol.erase()

    # 蜗壳支脚
    h_foot = H_AXIS - h_base - r_vol * 0.45
    o_pfoot = BOX(s, L=r_vol * 1.45, W=h_foot + r_vol * 0.5, H=w_vol * 0.75).translate((x_vol, 0.0, h_base + (h_foot + r_vol * 0.5) * 0.5))
    o_pump.uniteWith(o_pfoot); o_pfoot.erase()

    # 轴向吸入管嘴 + RF 法兰 (端面在 x = 0)
    o_suc_pipe = CYLINDER(s, R=r_suc, H=x_vol, O=0.0).rotateY(90.0).translate((0.0, 0.0, H_AXIS))
    o_suc_fl = CYLINDER(s, R=r_fl_suc, H=fl_t, O=0.0).rotateY(90.0).translate((0.0, 0.0, H_AXIS))
    o_suc_bore = CYLINDER(s, R=r_suc * 0.85, H=x_vol * 0.75, O=0.0).rotateY(90.0).translate((-5.0, 0.0, H_AXIS))
    o_pump.uniteWith(o_suc_pipe); o_suc_pipe.erase()
    o_pump.uniteWith(o_suc_fl); o_suc_fl.erase()
    o_pump.subtractFrom(o_suc_bore); o_suc_bore.erase()

    # 顶部垂直吐出管嘴 + RF 法兰 (端面在 z = H_AXIS + H_DIS)
    z_dis_top = H_AXIS + H_DIS
    o_dis_pipe = CYLINDER(s, R=r_dis, H=H_DIS, O=0.0).translate((x_vol, 0.0, H_AXIS))
    o_dis_fl = CYLINDER(s, R=r_fl_dis, H=fl_t, O=0.0).translate((x_vol, 0.0, z_dis_top - fl_t))
    o_dis_bore = CYLINDER(s, R=r_dis * 0.85, H=110.0, O=0.0).translate((x_vol, 0.0, z_dis_top - 105.0))
    o_pump.uniteWith(o_dis_pipe); o_dis_pipe.erase()
    o_pump.uniteWith(o_dis_fl); o_dis_fl.erase()
    o_pump.subtractFrom(o_dis_bore); o_dis_bore.erase()

    # 3. 轴承悬架体 (Bearing Bracket) + 托架支撑柱 + 联轴器安全护罩
    x_brg_start = x_vol + w_vol * 0.55
    l_brg = L_BASE * 0.25
    r_brg = r_vol * 0.52
    o_brg = CONE(s, R1=r_vol * 0.78, R2=r_brg, H=l_brg, E=0.0).rotateY(90.0).translate((x_brg_start, 0.0, H_AXIS))
    o_brg_ped = BOX(s, L=r_brg * 1.3, W=H_AXIS - h_base, H=75.0).translate((x_brg_start + l_brg * 0.72, 0.0, h_base + (H_AXIS - h_base) * 0.5))
    o_pump.uniteWith(o_brg); o_brg.erase()
    o_pump.uniteWith(o_brg_ped); o_brg_ped.erase()

    x_cpl_start = x_brg_start + l_brg
    l_cpl = L_BASE * 0.14
    r_cpl = r_brg * 1.05
    o_guard = CYLINDER(s, R=r_cpl, H=l_cpl + 10.0, O=0.0).rotateY(90.0).translate((x_cpl_start - 5.0, 0.0, H_AXIS))
    o_pump.uniteWith(o_guard); o_guard.erase()

    # 4. 卧式防爆三相异步电动机 (TEFC Explosion-Proof Motor + Fins + Terminal Box + Mounting Feet)
    x_mot_start = x_cpl_start + l_cpl
    l_mot = (x_base_start + L_BASE - 55.0) - x_mot_start
    r_mot = min(W_BASE * 0.44, r_vol * 0.94)
    o_mot = CYLINDER(s, R=r_mot, H=l_mot * 0.82, O=0.0).rotateY(90.0).translate((x_mot_start, 0.0, H_AXIS))
    o_fan = CONE(s, R1=r_mot * 1.02, R2=r_mot * 0.76, H=l_mot * 0.18, E=0.0).rotateY(90.0).translate((x_mot_start + l_mot * 0.82, 0.0, H_AXIS))
    o_pump.uniteWith(o_mot); o_mot.erase()
    o_pump.uniteWith(o_fan); o_fan.erase()

    # 电机垫高底座与底脚 + 顶部防爆接线盒
    h_mfoot = H_AXIS - h_base
    o_mfoot = BOX(s, L=r_mot * 1.65, W=h_mfoot, H=l_mot * 0.68).translate((x_mot_start + l_mot * 0.42, 0.0, h_base + h_mfoot * 0.5))
    o_jbox = BOX(s, L=110.0, W=95.0, H=115.0).translate((x_mot_start + l_mot * 0.35, 0.0, H_AXIS + r_mot + 35.0))
    o_pump.uniteWith(o_mfoot); o_mfoot.erase()
    o_pump.uniteWith(o_jbox); o_jbox.erase()

    s.setPoint((0.0, 0.0, H_AXIS), (-1.0, 0.0, 0.0))
    s.setPoint((x_vol, 0.0, z_dis_top), (0.0, 0.0, 1.0))

    s.setLinearDimension("L_BASE", (x_base_start, -W_BASE * 0.5, 0.0), (x_base_start + L_BASE, -W_BASE * 0.5, 0.0))
    s.setLinearDimension("W_BASE", (x_base_start + L_BASE, -W_BASE * 0.5, 0.0), (x_base_start + L_BASE, W_BASE * 0.5, 0.0))
    s.setLinearDimension("H_AXIS", (0.0, -W_BASE * 0.5, 0.0), (0.0, -W_BASE * 0.5, H_AXIS))
    s.setLinearDimension("H_DIS", (0.0, -W_BASE * 0.5, H_AXIS), (0.0, -W_BASE * 0.5, z_dis_top))
