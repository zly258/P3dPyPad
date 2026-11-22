# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"液压隔膜计量加药泵组",
    TooltipLong=u"化工酸碱/阻垢剂/催化剂定量加注用液压隔膜计量泵撬块 (符合 GB/T 7782 / API 675，含底座撬块、蜗轮曲柄箱、冲程千分尺调节手轮、立式防爆电机、圆盘隔膜泵头、上下单向阀组与出口脉动阻尼器)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(L_BASE=LENGTH, TooltipShort=u"底座长度", TooltipLong=u"计量泵组底座总长度 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"底座宽度", TooltipLong=u"计量泵组底座总宽度 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"立式电机高", TooltipLong=u"底座底面至立式防爆电机风扇罩顶部的总高度 (mm)")
@param(D_HEAD=LENGTH, TooltipShort=u"隔膜泵头径", TooltipLong=u"前端PTFE液压隔膜泵头圆盘外径 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"进出液管径", TooltipLong=u"加药泵上下单向阀进出口管径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"液压隔膜计量加药泵位号编码")
def EQUIPMENT_METERING_PUMP(s, L_BASE=680.0, W_BASE=380.0, H_TOTAL=640.0, D_HEAD=210.0, D_NOZ=33.7, ID=u"P-104-METERING", **kw):
    L_BASE = max(450.0, float(L_BASE))
    W_BASE = max(260.0, float(W_BASE))
    H_TOTAL = max(450.0, float(H_TOTAL))
    D_HEAD = max(130.0, float(D_HEAD))
    D_NOZ = max(20.0, float(D_NOZ))

    h_base = 55.0
    r_head = D_HEAD / 2.0
    r_noz = D_NOZ / 2.0
    r_fl = r_noz + 38.0
    t_fl = 16.0

    # 1. 底部型钢撬座底板 (BOX: H=dx=L_BASE, L=dy=W_BASE, W=dz=h_base)
    o_m = BOX(s, L=W_BASE, W=h_base, H=L_BASE).translate((0.0, 0.0, h_base * 0.5))

    # 2. 中部蜗轮曲柄传动箱 + 后端冲程调节千分尺手轮 (+X) + 顶部立式防爆电机
    x_gear = 55.0
    h_gear = (H_TOTAL - h_base) * 0.44
    z_axis = h_base + h_gear * 0.62
    o_gear = BOX(s, L=W_BASE * 0.58, W=h_gear, H=L_BASE * 0.36).translate((x_gear, 0.0, h_base + h_gear * 0.5))

    # 后端冲程调节手轮 (+X)
    x_dial_start = x_gear + L_BASE * 0.18
    o_dial_neck = CYLINDER(s, R=38.0, H=95.0, O=0.0).rotateY(90.0).translate((x_dial_start, 0.0, z_axis))
    o_dial_knob = CYLINDER(s, R=56.0, H=32.0, O=0.0).rotateY(90.0).translate((x_dial_start + 85.0, 0.0, z_axis))

    # 顶部立式防爆电机
    z_mot_bot = h_base + h_gear
    h_mot = H_TOTAL - z_mot_bot
    r_mot = min(W_BASE * 0.32, 105.0)
    o_mfl = CYLINDER(s, R=r_mot * 1.15, H=24.0, O=0.0).translate((x_gear, 0.0, z_mot_bot - 4.0))
    o_mot = CYLINDER(s, R=r_mot, H=h_mot * 0.78, O=0.0).translate((x_gear, 0.0, z_mot_bot + 16.0))
    o_fan = CONE(s, R1=r_mot * 1.04, R2=r_mot * 0.72, H=h_mot * 0.22, E=0.0).translate((x_gear, 0.0, z_mot_bot + h_mot * 0.78))
    o_jbox = BOX(s, L=75.0, W=75.0, H=65.0).translate((x_gear, r_mot + 28.0, z_mot_bot + h_mot * 0.45))
    for p in (o_gear, o_dial_neck, o_dial_knob, o_mfl, o_mot, o_fan, o_jbox):
        o_m.uniteWith(p); p.erase()

    # 3. 前端液压缸套 + PTFE圆盘隔膜泵头 (-X) + 上下球型单向阀组与进出口法兰
    x_head = -L_BASE * 0.34
    len_yoke = (x_gear - L_BASE * 0.18) - x_head + 20.0
    o_yoke = CYLINDER(s, R=r_head * 0.56, H=len_yoke, O=0.0).rotateY(90.0).translate((x_head, 0.0, z_axis))
    o_head = CYLINDER(s, R=r_head, H=62.0, O=0.0).rotateY(90.0).translate((x_head - 45.0, 0.0, z_axis))
    o_hped = BOX(s, L=90.0, W=z_axis - h_base, H=55.0).translate((x_head - 15.0, 0.0, h_base + (z_axis - h_base) * 0.5))
    for p in (o_yoke, o_head, o_hped):
        o_m.uniteWith(p); p.erase()

    # 出口脉动阻尼器蓄能罐 (位于隔膜泵头侧后方 +Y)
    o_damp_cyl = CYLINDER(s, R=58.0, H=165.0, O=0.0).translate((x_head + 65.0, W_BASE * 0.28, h_base))
    o_damp_top = SPHERE(s, R=58.0).translate((x_head + 65.0, W_BASE * 0.28, h_base + 165.0))
    o_damp_pipe = BOX(s, L=W_BASE * 0.28, W=24.0, H=24.0).translate((x_head + 65.0, W_BASE * 0.14, h_base + 70.0))
    for p in (o_damp_cyl, o_damp_top, o_damp_pipe):
        o_m.uniteWith(p); p.erase()

    # 泵头底部吸入单向阀口 (Port 1, -Z) 与顶部排出单向阀口 (Port 2, +Z)
    x_port = x_head - 18.0
    z_suc = max(25.0, z_axis - r_head - 75.0)
    z_dis = z_axis + r_head + 85.0
    o_v_suc = CYLINDER(s, R=r_noz * 1.35, H=z_axis - z_suc, O=0.0).translate((x_port, 0.0, z_suc))
    o_f_suc = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((x_port, 0.0, z_suc))
    o_v_dis = CYLINDER(s, R=r_noz * 1.35, H=z_dis - z_axis, O=0.0).translate((x_port, 0.0, z_axis))
    o_f_dis = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((x_port, 0.0, z_dis - t_fl))
    for p in (o_v_suc, o_f_suc, o_v_dis, o_f_dis):
        o_m.uniteWith(p); p.erase()

    s.setPoint((x_port, 0.0, z_suc), (0.0, 0.0, -1.0))
    s.setPoint((x_port, 0.0, z_dis), (0.0, 0.0, 1.0))
    s.setLinearDimension("L_BASE", (-L_BASE / 2.0, 0.0, 0.0), (L_BASE / 2.0, 0.0, 0.0))
    s.setLinearDimension("W_BASE", (0.0, -W_BASE / 2.0, 0.0), (0.0, W_BASE / 2.0, 0.0))
    s.setLinearDimension("H_TOTAL", (x_gear, 0.0, 0.0), (x_gear, 0.0, H_TOTAL))
