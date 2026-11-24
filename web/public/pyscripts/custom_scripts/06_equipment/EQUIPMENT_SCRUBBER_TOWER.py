# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="3",
    TooltipShort=u"化工尾气喷淋洗涤吸收塔",
    TooltipLong=u"化工酸雾/VOCs/尾气净化用立式平底填料喷淋洗涤塔 (符合 HG/T 20592，含加粗底部贮液釜段、大口径进气方形/圆形风管口、双层外环喷淋分配母管、双层透光观察视镜窗、锥形过渡顶与高空净气排放口)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D_BODY=LENGTH, TooltipShort=u"洗涤塔直径", TooltipLong=u"喷淋塔直筒段公称外径 (mm)")
@param(H_TOWER=LENGTH, TooltipShort=u"塔体高度", TooltipLong=u"底板至塔顶锥封头切线的直筒高度 (mm)")
@param(D_GAS=LENGTH, TooltipShort=u"进排风管径", TooltipLong=u"下部进气口与塔顶净气排放口外径 (mm)")
@param(D_LIQ=LENGTH, TooltipShort=u"循环液管径", TooltipLong=u"底部循环泵吸入口与喷淋母管外径 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"风口法兰径", TooltipLong=u"进排风口法兰外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"尾气喷淋洗涤塔设备位号编码")
def EQUIPMENT_SCRUBBER_TOWER(s, D_BODY=1500.0, H_TOWER=3600.0, D_GAS=406.4, D_LIQ=114.3, FL_OD=540.0, ID=u"T-102-SCRUBBER", **kw):
    D_BODY = max(800.0, float(D_BODY))
    H_TOWER = max(2000.0, float(H_TOWER))
    D_GAS = max(168.3, float(D_GAS))
    D_LIQ = max(48.0, float(D_LIQ))
    FL_OD = max(D_GAS + 95.0, float(FL_OD))

    r_body = D_BODY / 2.0
    r_gas = D_GAS / 2.0
    r_liq = D_LIQ / 2.0
    r_fl = FL_OD / 2.0
    t_base = 30.0
    t_fl = 26.0

    # 1. 底部加厚锚固环板 + 下部加粗循环贮液釜段 + 主洗涤塔筒体 + 顶部锥形除雾封头
    h_sump = H_TOWER * 0.28
    o_m = CYLINDER(s, R=r_body * 1.16, H=t_base, O=0.0)
    o_sump = CYLINDER(s, R=r_body * 1.05, H=h_sump, O=0.0).translate((0.0, 0.0, t_base))
    o_shell = CYLINDER(s, R=r_body, H=H_TOWER - h_sump, O=0.0).translate((0.0, 0.0, t_base + h_sump))
    h_cone = r_body * 0.58
    o_cone = CONE(s, R1=r_body + 35.0, R2=r_gas, H=h_cone, E=0.0).translate((0.0, 0.0, t_base + H_TOWER))
    for p in (o_sump, o_shell, o_cone):
        o_m.uniteWith(p); p.erase()

    # 2. 双层外部环形喷淋液体分配母管 (TORUS) + 竖直喷淋总管 (+X) + 双层填料装卸视镜人孔 (+Y)
    z_sp1 = t_base + H_TOWER * 0.56
    z_sp2 = t_base + H_TOWER * 0.80
    r_hdr = r_body + r_liq * 1.35
    for zs in (z_sp1, z_sp2):
        hdr = TORUS(s, R1=r_hdr, R2=r_liq * 0.72).translate((0.0, 0.0, zs))
        o_m.uniteWith(hdr); hdr.erase()
        for ang in (0.0, 90.0, 180.0, 270.0):
            sp_in = CYLINDER(s, R=r_liq * 0.55, H=r_hdr, O=0.0).rotateY(90.0).translate((0.0, 0.0, zs)).rotateZ(ang)
            o_m.uniteWith(sp_in); sp_in.erase()

    # 竖直喷淋上水立管 (连接上下两层喷淋环)
    o_riser = CYLINDER(s, R=r_liq * 0.75, H=z_sp2 - (t_base + 220.0), O=0.0).translate((r_hdr, 0.0, t_base + 220.0))
    o_m.uniteWith(o_riser); o_riser.erase()

    # 双层填料观察视镜人孔 (+Y)
    for frac in (0.42, 0.68):
        zm = t_base + H_TOWER * frac
        mh = CYLINDER(s, R=240.0, H=r_body + 180.0, O=0.0).rotateX(-90.0).translate((0.0, 0.0, zm))
        mfl = CYLINDER(s, R=300.0, H=32.0, O=0.0).rotateX(-90.0).translate((0.0, r_body + 160.0, zm))
        o_m.uniteWith(mh); mh.erase()
        o_m.uniteWith(mfl); mfl.erase()

    # 3. 三个主端口:
    # Port 1: 下部废气进口 (-X, Z = t_base + H_TOWER * 0.30)
    # Port 2: 塔顶净气排放口 (+Z)
    # Port 3: 底部循环泵吸液口 (+X, Z = t_base + 220)
    ext_gas = r_body + 260.0
    z_gas_in = t_base + H_TOWER * 0.30
    n_gin = CYLINDER(s, R=r_gas, H=ext_gas, O=0.0).rotateY(-90.0).translate((0.0, 0.0, z_gas_in))
    f_gin = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).rotateY(-90.0).translate((-(ext_gas - t_fl), 0.0, z_gas_in))

    z_gas_out = t_base + H_TOWER + h_cone + 260.0
    n_gout = CYLINDER(s, R=r_gas, H=300.0, O=0.0).translate((0.0, 0.0, z_gas_out - 300.0))
    f_gout = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((0.0, 0.0, z_gas_out - t_fl))

    ext_liq = r_body * 1.05 + 220.0
    z_liq_out = t_base + 220.0
    n_lout = CYLINDER(s, R=r_liq, H=ext_liq, O=0.0).rotateY(90.0).translate((0.0, 0.0, z_liq_out))
    f_lout = CYLINDER(s, R=r_liq + 52.0, H=22.0, O=0.0).rotateY(90.0).translate((ext_liq - 22.0, 0.0, z_liq_out))

    for p in (n_gin, f_gin, n_gout, f_gout, n_lout, f_lout):
        o_m.uniteWith(p); p.erase()

    s.setPoint((-ext_gas, 0.0, z_gas_in), (-1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, z_gas_out), (0.0, 0.0, 1.0))
    s.setPoint((ext_liq, 0.0, z_liq_out), (1.0, 0.0, 0.0))
    s.setLinearDimension("D_BODY", (-r_body, 0.0, t_base + h_sump), (r_body, 0.0, t_base + h_sump))
    s.setLinearDimension("H_TOWER", (r_body, 0.0, t_base), (r_body, 0.0, t_base + H_TOWER))
