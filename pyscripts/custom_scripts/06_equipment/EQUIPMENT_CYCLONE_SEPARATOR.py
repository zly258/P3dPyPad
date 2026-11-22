# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="3",
    TooltipShort=u"立式切向进气旋风分离器",
    TooltipLong=u"化工催化/干燥/煤气工段气固切向进气旋风分离器 (含上部捕集圆筒、长锥体分离段、切向蜗壳进气口、顶部中心升气管净气出口、底部卸灰锥口与三腿支承架)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D_BODY=LENGTH, TooltipShort=u"筒体直径", TooltipLong=u"旋风分离器上部圆筒直径 (mm)")
@param(H_CYL=LENGTH, TooltipShort=u"直筒高度", TooltipLong=u"上部圆筒段高度 (mm)")
@param(H_CONE=LENGTH, TooltipShort=u"锥段高度", TooltipLong=u"下部圆锥分离段高度 (mm)")
@param(H_LEGS=LENGTH, TooltipShort=u"支腿高度", TooltipLong=u"地面至锥段下法兰口的净空支腿高度 (mm)")
@param(D_GAS=LENGTH, TooltipShort=u"进排气管径", TooltipLong=u"切向进气口与中心净气出口外径 (mm)")
@param(D_DUST=LENGTH, TooltipShort=u"卸灰口管径", TooltipLong=u"底部卸灰法兰口外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"旋风分离器设备位号与规格编码")
def EQUIPMENT_CYCLONE_SEPARATOR(s, D_BODY=900.0, H_CYL=1100.0, H_CONE=1650.0, H_LEGS=850.0, D_GAS=273.0, D_DUST=168.3, ID=u"CY-101-DN900", **kw):
    D_BODY = max(400.0, float(D_BODY))
    H_CYL = max(500.0, float(H_CYL))
    H_CONE = max(750.0, float(H_CONE))
    H_LEGS = max(450.0, float(H_LEGS))
    D_GAS = max(88.9, float(D_GAS))
    D_DUST = max(60.3, float(D_DUST))

    r_body = D_BODY / 2.0
    r_gas = D_GAS / 2.0
    r_dust = D_DUST / 2.0
    r_fl_gas = r_gas + 55.0
    r_fl_dust = r_dust + 50.0
    t_fl = 24.0

    z_dust = H_LEGS
    z_cone_top = z_dust + 120.0 + H_CONE
    z_cyl_top = z_cone_top + H_CYL

    # 1. 底部卸灰短管与法兰 (Port 3 at Z = z_dust) + 下部锥体 + 上部圆筒 + 顶盖法兰环
    o_m = CYLINDER(s, R=r_dust, H=140.0, O=0.0).translate((0.0, 0.0, z_dust))
    o_fl_bot = CYLINDER(s, R=r_fl_dust, H=t_fl, O=0.0).translate((0.0, 0.0, z_dust))
    o_cone = CONE(s, R1=r_dust, R2=r_body, H=H_CONE, E=0.0).translate((0.0, 0.0, z_dust + 120.0))
    o_cyl = CYLINDER(s, R=r_body, H=H_CYL, O=0.0).translate((0.0, 0.0, z_cone_top))
    o_top_ring = CYLINDER(s, R=r_body + 45.0, H=32.0, O=0.0).translate((0.0, 0.0, z_cyl_top - 32.0))
    o_roof = CONE(s, R1=r_body + 45.0, R2=r_gas * 1.35, H=140.0, E=0.0).translate((0.0, 0.0, z_cyl_top))
    for p in (o_fl_bot, o_cone, o_cyl, o_top_ring, o_roof):
        o_m.uniteWith(p); p.erase()

    # 锥体中部加强抱箍环与 3 根圆管支承立腿 (连接至地面 Z=0)
    z_band = z_dust + 120.0 + H_CONE * 0.58
    r_band = r_dust + (r_body - r_dust) * 0.58
    o_band = CYLINDER(s, R=r_band + 35.0, H=80.0, O=0.0).translate((0.0, 0.0, z_band - 40.0))
    o_m.uniteWith(o_band); o_band.erase()

    r_leg_pcd = r_band + 65.0
    for i in range(3):
        ang_deg = 120.0 * i + 30.0
        ang_rad = math.radians(ang_deg)
        xl = r_leg_pcd * math.cos(ang_rad)
        yl = r_leg_pcd * math.sin(ang_rad)
        leg = CYLINDER(s, R=48.0, H=z_band + 20.0, O=0.0).translate((xl, yl, 18.0))
        lug = BOX(s, L=90.0, W=120.0, H=130.0).rotateZ(ang_deg).translate(((r_band + 25.0) * math.cos(ang_rad), (r_band + 25.0) * math.sin(ang_rad), z_band))
        bp = BOX(s, L=180.0, W=18.0, H=180.0).rotateZ(ang_deg).translate((xl, yl, 9.0))
        for p in (leg, lug, bp):
            o_m.uniteWith(p); p.erase()

    # 2. 上部切向进气矩形蜗壳过渡段 + 进气圆法兰口 (Port 1 at -X, Y = +y_tang)
    y_tang = r_body - r_gas * 0.65
    z_inlet = z_cyl_top - r_gas * 1.35
    x_inlet = -(r_body + 240.0)
    o_scroll = BOX(s, L=r_gas * 1.9, W=r_gas * 2.2, H=r_body * 1.15).translate((-r_body * 0.45, y_tang, z_inlet))
    o_n_in = CYLINDER(s, R=r_gas, H=abs(x_inlet), O=0.0).rotateY(-90.0).translate((0.0, y_tang, z_inlet))
    o_f_in = CYLINDER(s, R=r_fl_gas, H=t_fl, O=0.0).rotateY(-90.0).translate((x_inlet, y_tang, z_inlet))
    for p in (o_scroll, o_n_in, o_f_in):
        o_m.uniteWith(p); p.erase()

    # 3. 顶部中心插入式升气管净气出口 (Port 2 at +Z)
    z_gas_out = z_cyl_top + 420.0
    o_vortex = CYLINDER(s, R=r_gas * 1.05, H=480.0, O=0.0).translate((0.0, 0.0, z_cyl_top - 60.0))
    o_f_out = CYLINDER(s, R=r_fl_gas, H=t_fl, O=0.0).translate((0.0, 0.0, z_gas_out - t_fl))
    o_m.uniteWith(o_vortex); o_vortex.erase()
    o_m.uniteWith(o_f_out); o_f_out.erase()

    s.setPoint((x_inlet, y_tang, z_inlet), (-1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, z_gas_out), (0.0, 0.0, 1.0))
    s.setPoint((0.0, 0.0, z_dust), (0.0, 0.0, -1.0))
    s.setLinearDimension("D_BODY", (-r_body, 0.0, z_cone_top), (r_body, 0.0, z_cone_top))
    s.setLinearDimension("H_CONE", (r_body, 0.0, z_dust + 120.0), (r_body, 0.0, z_cone_top))
    s.setLinearDimension("H_CYL", (r_body, 0.0, z_cone_top), (r_body, 0.0, z_cyl_top))
