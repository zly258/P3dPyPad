# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"水环式真空泵机组",
    TooltipLong=u"化工减压精馏/真空抽滤用 2BV/2BE 型双级水环式真空泵机组 (符合 JB/T 7255，含公用型钢底座、圆筒工作腔泵体、前后分配器锥盖、顶部鹅颈吸排气集管弯头、联轴器护罩与电机)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(L_BASE=LENGTH, TooltipShort=u"底座总长", TooltipLong=u"水环真空泵机组公用底座长度 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"底座宽度", TooltipLong=u"公用底座总宽度 (mm)")
@param(H_AXIS=LENGTH, TooltipShort=u"泵轴中心高", TooltipLong=u"底座底面至真空泵主轴中心线的高度 (mm)")
@param(D_CYL=LENGTH, TooltipShort=u"泵腔外径", TooltipLong=u"水环真空泵叶轮工作腔圆筒外径 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"吸排气管径", TooltipLong=u"顶部吸气与排气集管法兰口外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"水环式真空泵机组位号与抽气量编码")
def EQUIPMENT_LIQUID_RING_VACUUM_PUMP(s, L_BASE=1380.0, W_BASE=540.0, H_AXIS=330.0, D_CYL=460.0, D_NOZ=88.9, ID=u"VP-101-2BE", **kw):
    L_BASE = max(850.0, float(L_BASE))
    W_BASE = max(380.0, float(W_BASE))
    D_CYL = max(280.0, float(D_CYL))
    r_cyl = D_CYL / 2.0
    H_AXIS = max(r_cyl + 85.0, float(H_AXIS))
    D_NOZ = max(42.0, float(D_NOZ))

    h_base = 75.0
    r_noz = D_NOZ / 2.0
    r_fl = r_noz + 48.0
    t_fl = 22.0

    # 1. 公用槽钢底座
    o_m = BOX(s, L=W_BASE, W=h_base, H=L_BASE).translate((0.0, 0.0, h_base * 0.5))

    # 2. 水环真空泵工作腔主圆筒 + 前后分配器端盖 + 双轴承座支脚 (-X 侧)
    x_pump_c = -L_BASE * 0.25
    l_cyl = L_BASE * 0.28
    o_cyl = CYLINDER(s, R=r_cyl, H=l_cyl, O=0.0).rotateY(90.0).translate((x_pump_c - l_cyl * 0.5, 0.0, H_AXIS))
    o_fl_f = CYLINDER(s, R=r_cyl + 28.0, H=28.0, O=0.0).rotateY(90.0).translate((x_pump_c - l_cyl * 0.5, 0.0, H_AXIS))
    o_fl_r = CYLINDER(s, R=r_cyl + 28.0, H=28.0, O=0.0).rotateY(90.0).translate((x_pump_c + l_cyl * 0.5 - 28.0, 0.0, H_AXIS))
    o_brg_f = CYLINDER(s, R=r_cyl * 0.42, H=85.0, O=0.0).rotateY(-90.0).translate((x_pump_c - l_cyl * 0.5, 0.0, H_AXIS))
    o_brg_r = CYLINDER(s, R=r_cyl * 0.42, H=85.0, O=0.0).rotateY(90.0).translate((x_pump_c + l_cyl * 0.5, 0.0, H_AXIS))
    o_pfoot = BOX(s, L=r_cyl * 1.55, W=H_AXIS - h_base, H=l_cyl * 0.92).translate((x_pump_c, 0.0, h_base + (H_AXIS - h_base) * 0.5))
    for p in (o_cyl, o_fl_f, o_fl_r, o_brg_f, o_brg_r, o_pfoot):
        o_m.uniteWith(p); p.erase()

    # 两侧吸排气分配集管支管 (连接前后分配器端盖至顶部法兰口)
    z_top_port = H_AXIS + r_cyl + 150.0
    dy_man = r_cyl * 0.48
    for sy in (-1.0, 1.0):
        ym = sy * dy_man
        hdr = BOX(s, L=D_NOZ * 1.25, W=r_cyl * 0.72, H=l_cyl * 1.12).translate((x_pump_c, ym, H_AXIS + r_cyl * 0.72))
        nz = CYLINDER(s, R=r_noz, H=r_cyl + 150.0, O=0.0).translate((x_pump_c, ym, H_AXIS))
        fl = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((x_pump_c, ym, z_top_port - t_fl))
        for p in (hdr, nz, fl):
            o_m.uniteWith(p); p.erase()

    # 3. 联轴器护罩 + 后端卧式电机 (+X 侧)
    x_guard = x_pump_c + l_cyl * 0.5 + 65.0
    l_guard = L_BASE * 0.14
    o_guard = CYLINDER(s, R=r_cyl * 0.38, H=l_guard + 40.0, O=0.0).rotateY(90.0).translate((x_guard - 20.0, 0.0, H_AXIS))
    o_m.uniteWith(o_guard); o_guard.erase()

    x_mot = x_guard + l_guard
    l_mot = L_BASE * 0.34
    r_mot = r_cyl * 0.78
    o_mot = CYLINDER(s, R=r_mot, H=l_mot * 0.78, O=0.0).rotateY(90.0).translate((x_mot, 0.0, H_AXIS))
    o_fan = CONE(s, R1=r_mot * 1.04, R2=r_mot * 0.72, H=l_mot * 0.22, E=0.0).rotateY(90.0).translate((x_mot + l_mot * 0.78, 0.0, H_AXIS))
    o_mfoot = BOX(s, L=r_mot * 1.6, W=H_AXIS - h_base, H=l_mot * 0.65).translate((x_mot + l_mot * 0.42, 0.0, h_base + (H_AXIS - h_base) * 0.5))
    o_jbox = BOX(s, L=95.0, W=90.0, H=100.0).translate((x_mot + l_mot * 0.36, 0.0, H_AXIS + r_mot + 32.0))
    for p in (o_mot, o_fan, o_mfoot, o_jbox):
        o_m.uniteWith(p); p.erase()

    s.setPoint((x_pump_c, -dy_man, z_top_port), (0.0, 0.0, 1.0))
    s.setPoint((x_pump_c, dy_man, z_top_port), (0.0, 0.0, 1.0))
    s.setLinearDimension("L_BASE", (-L_BASE / 2.0, 0.0, 0.0), (L_BASE / 2.0, 0.0, 0.0))
    s.setLinearDimension("W_BASE", (0.0, -W_BASE / 2.0, 0.0), (0.0, W_BASE / 2.0, 0.0))
    s.setLinearDimension("H_AXIS", (-L_BASE / 2.0, 0.0, 0.0), (-L_BASE / 2.0, 0.0, H_AXIS))
