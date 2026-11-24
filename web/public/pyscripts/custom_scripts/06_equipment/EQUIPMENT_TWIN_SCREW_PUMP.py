# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"化工卧式双螺杆容积泵组",
    TooltipLong=u"化工高粘度聚合物/重油/沥青输送用卧式双螺杆容积泵机组 (符合 API 676，含公用型钢底座、双缸8字形保温夹套泵体、同步齿轮箱、内置安全回流阀、联轴器护罩与防爆驱动电机)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(L_BASE=LENGTH, TooltipShort=u"底座总长", TooltipLong=u"双螺杆泵组公用底座总长度 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"底座宽度", TooltipLong=u"公用底座总宽度 (mm)")
@param(H_AXIS=LENGTH, TooltipShort=u"主轴中心高", TooltipLong=u"底座底面至驱动主轴中心线的高度 (mm)")
@param(D_SUC=LENGTH, TooltipShort=u"吸入口管径", TooltipLong=u"泵体顶部吸入口接管外径 (mm)")
@param(D_DIS=LENGTH, TooltipShort=u"排出口管径", TooltipLong=u"泵体顶部排出口接管外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"卧式双螺杆泵机组位号编码")
def EQUIPMENT_TWIN_SCREW_PUMP(s, L_BASE=1450.0, W_BASE=520.0, H_AXIS=310.0, D_SUC=114.3, D_DIS=88.9, ID=u"P-105-2SCREW", **kw):
    L_BASE = max(900.0, float(L_BASE))
    W_BASE = max(360.0, float(W_BASE))
    H_AXIS = max(220.0, float(H_AXIS))
    D_SUC = max(48.0, float(D_SUC))
    D_DIS = max(42.0, float(D_DIS))

    h_base = 75.0
    r_suc = D_SUC / 2.0
    r_dis = D_DIS / 2.0
    r_fl_s = r_suc + 52.0
    r_fl_d = r_dis + 48.0
    t_fl = 22.0

    # 1. 公用槽钢底座 (BOX: H=dx=L_BASE, L=dy=W_BASE, W=dz=h_base)
    o_m = BOX(s, L=W_BASE, W=h_base, H=L_BASE).translate((0.0, 0.0, h_base * 0.5))

    # 2. 前端双螺杆 8 字形双膛保温泵壳 + 同步齿轮箱 (-X 侧)
    x_pump_start = -L_BASE * 0.44
    l_casing = L_BASE * 0.36
    r_bore = max(72.0, W_BASE * 0.19)
    dy_screw = r_bore * 0.72
    for sy in (-1.0, 1.0):
        cyl = CYLINDER(s, R=r_bore, H=l_casing, O=0.0).rotateY(90.0).translate((x_pump_start, sy * dy_screw, H_AXIS))
        o_m.uniteWith(cyl); cyl.erase()

    # 夹套矩形加强中段 + 支脚 + 前后端盖 + 顶部内置安全溢流阀筒
    o_jkt = BOX(s, L=(r_bore + dy_screw) * 1.95, W=r_bore * 1.85, H=l_casing * 0.78).translate((x_pump_start + l_casing * 0.48, 0.0, H_AXIS))
    o_pfoot = BOX(s, L=W_BASE * 0.78, W=H_AXIS - h_base, H=l_casing * 0.72).translate((x_pump_start + l_casing * 0.5, 0.0, h_base + (H_AXIS - h_base) * 0.5))
    o_end_cap = BOX(s, L=(r_bore + dy_screw) * 2.05, W=r_bore * 2.05, H=38.0).translate((x_pump_start + 19.0, 0.0, H_AXIS))
    o_rv = CYLINDER(s, R=r_bore * 0.52, H=l_casing * 0.55, O=0.0).rotateY(90.0).translate((x_pump_start + l_casing * 0.18, 0.0, H_AXIS + r_bore * 1.05))
    for p in (o_jkt, o_pfoot, o_end_cap, o_rv):
        o_m.uniteWith(p); p.erase()

    # 3. 中部联轴器安全护罩 + 后端卧式防爆电机 (+X 侧)
    x_guard = x_pump_start + l_casing
    l_guard = L_BASE * 0.14
    o_guard = CYLINDER(s, R=r_bore * 0.78, H=l_guard + 20.0, O=0.0).rotateY(90.0).translate((x_guard - 10.0, 0.0, H_AXIS))
    o_m.uniteWith(o_guard); o_guard.erase()

    x_mot = x_guard + l_guard
    l_mot = L_BASE * 0.36
    r_mot = r_bore * 1.25
    o_mot = CYLINDER(s, R=r_mot, H=l_mot * 0.78, O=0.0).rotateY(90.0).translate((x_mot, 0.0, H_AXIS))
    o_fan = CONE(s, R1=r_mot * 1.04, R2=r_mot * 0.72, H=l_mot * 0.22, E=0.0).rotateY(90.0).translate((x_mot + l_mot * 0.78, 0.0, H_AXIS))
    o_mfoot = BOX(s, L=r_mot * 1.65, W=H_AXIS - h_base, H=l_mot * 0.65).translate((x_mot + l_mot * 0.42, 0.0, h_base + (H_AXIS - h_base) * 0.5))
    o_jbox = BOX(s, L=105.0, W=95.0, H=110.0).translate((x_mot + l_mot * 0.38, 0.0, H_AXIS + r_mot + 35.0))
    for p in (o_mot, o_fan, o_mfoot, o_jbox):
        o_m.uniteWith(p); p.erase()

    # 4. 顶部前侧吸入法兰口 (Port 1, +Z) 与后侧排出法兰口 (Port 2, +Z)
    x_suc = x_pump_start + l_casing * 0.22
    x_dis = x_pump_start + l_casing * 0.78
    z_ports = H_AXIS + r_bore + 185.0
    n_s = CYLINDER(s, R=r_suc, H=r_bore + 185.0, O=0.0).translate((x_suc, 0.0, H_AXIS))
    f_s = CYLINDER(s, R=r_fl_s, H=t_fl, O=0.0).translate((x_suc, 0.0, z_ports - t_fl))
    n_d = CYLINDER(s, R=r_dis, H=r_bore + 185.0, O=0.0).translate((x_dis, 0.0, H_AXIS))
    f_d = CYLINDER(s, R=r_fl_d, H=t_fl, O=0.0).translate((x_dis, 0.0, z_ports - t_fl))
    for p in (n_s, f_s, n_d, f_d):
        o_m.uniteWith(p); p.erase()

    s.setPoint((x_suc, 0.0, z_ports), (0.0, 0.0, 1.0))
    s.setPoint((x_dis, 0.0, z_ports), (0.0, 0.0, 1.0))
    s.setLinearDimension("L_BASE", (-L_BASE / 2.0, 0.0, 0.0), (L_BASE / 2.0, 0.0, 0.0))
    s.setLinearDimension("W_BASE", (0.0, -W_BASE / 2.0, 0.0), (0.0, W_BASE / 2.0, 0.0))
    s.setLinearDimension("H_AXIS", (-L_BASE / 2.0, 0.0, 0.0), (-L_BASE / 2.0, 0.0, H_AXIS))
