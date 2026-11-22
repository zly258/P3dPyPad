# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"赤道正切柱式球形储罐",
    TooltipLong=u"化工液化石油气/丙烯/液氨高压球形储罐 (符合 GB/T 12337 / NB/T 47041，含球壳本体、6根赤道正切圆管支柱与柱脚底板、柱间抗震拉杆环梁、顶部气相安全阀管口与底部液相进出口)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D_SPHERE=LENGTH, TooltipShort=u"球罐外径", TooltipLong=u"球形储罐壳体公称外径 (mm)")
@param(H_CENTER=LENGTH, TooltipShort=u"赤道中心高", TooltipLong=u"球心赤道平面至柱脚底板底面的高度 (mm)")
@param(D_COL=LENGTH, TooltipShort=u"支柱管外径", TooltipLong=u"赤道正切支承立柱圆管外径 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"进出料管径", TooltipLong=u"顶底进出料法兰管口外径 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"管口法兰径", TooltipLong=u"管口配对法兰外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"球罐位号", TooltipLong=u"球形储罐设备位号与规格编码")
def EQUIPMENT_SPHERICAL_TANK(s, D_SPHERE=2800.0, H_CENTER=2100.0, D_COL=273.0, D_NOZ=219.1, FL_OD=340.0, ID=u"V-301-DN2800", **kw):
    D_SPHERE = max(1400.0, float(D_SPHERE))
    r_sph = D_SPHERE / 2.0
    H_CENTER = max(r_sph + 450.0, float(H_CENTER))
    D_COL = max(133.0, float(D_COL))
    r_col = D_COL / 2.0
    D_NOZ = max(88.9, float(D_NOZ))
    FL_OD = max(D_NOZ + 80.0, float(FL_OD))

    r_noz = D_NOZ / 2.0
    r_fl = FL_OD / 2.0
    t_fl = 28.0
    t_base = 30.0

    # 1. 高压球罐本体 (球心位于 Z = H_CENTER)
    o_m = SPHERE(s, R=r_sph).translate((0.0, 0.0, H_CENTER))

    # 赤道温差补强带环与顶部操作平台护栏冠环
    o_eq_band = CYLINDER(s, R=r_sph + 18.0, H=240.0, O=0.0).translate((0.0, 0.0, H_CENTER - 120.0))
    o_top_plat = CYLINDER(s, R=r_sph * 0.42, H=35.0, O=r_sph * 0.36).translate((0.0, 0.0, H_CENTER + r_sph * 0.92))
    o_m.uniteWith(o_eq_band); o_eq_band.erase()
    o_m.uniteWith(o_top_plat); o_top_plat.erase()

    # 2. 6 根赤道正切圆管支柱 + 鞍式连接贴板 + 柱脚方形锚固底板
    r_pcd = r_sph + r_col * 0.35
    h_col = H_CENTER + 160.0
    w_bp = D_COL * 1.65
    for i in range(6):
        ang_deg = 60.0 * i
        ang_rad = math.radians(ang_deg)
        xc = r_pcd * math.cos(ang_rad)
        yc = r_pcd * math.sin(ang_rad)
        col = CYLINDER(s, R=r_col, H=h_col, O=0.0).translate((xc, yc, t_base))
        cap = CONE(s, R1=r_col, R2=r_col * 0.3, H=D_COL * 0.9, E=0.0).translate((xc, yc, t_base + h_col))
        pad = BOX(s, L=D_COL * 1.15, W=420.0, H=r_col * 1.8).rotateZ(ang_deg).translate((xc - r_col * 0.45 * math.cos(ang_rad), yc - r_col * 0.45 * math.sin(ang_rad), H_CENTER - 30.0))
        bp = BOX(s, L=w_bp, W=t_base, H=w_bp).rotateZ(ang_deg).translate((xc, yc, t_base * 0.5))
        for p in (col, cap, pad, bp):
            o_m.uniteWith(p); p.erase()

    # 支柱中部抗震水平连接环梁
    z_tie = H_CENTER * 0.42
    o_tie = TORUS(s, R1=r_pcd, R2=r_col * 0.32).translate((0.0, 0.0, z_tie))
    o_m.uniteWith(o_tie); o_tie.erase()

    # 3. 顶部气相管口 (Port 2, +Z) 与底部液相出料管口 (Port 1, -Z) + 顶人孔
    z_top_port = H_CENTER + r_sph + 240.0
    n_top = CYLINDER(s, R=r_noz, H=300.0, O=0.0).translate((0.0, 0.0, H_CENTER + r_sph - 60.0))
    f_top = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((0.0, 0.0, z_top_port - t_fl))

    z_bot_port = H_CENTER - r_sph - 240.0
    n_bot = CYLINDER(s, R=r_noz, H=300.0, O=0.0).translate((0.0, 0.0, z_bot_port))
    f_bot = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((0.0, 0.0, z_bot_port))
    for p in (n_top, f_top, n_bot, f_bot):
        o_m.uniteWith(p); p.erase()

    s.setPoint((0.0, 0.0, z_bot_port), (0.0, 0.0, -1.0))
    s.setPoint((0.0, 0.0, z_top_port), (0.0, 0.0, 1.0))
    s.setLinearDimension("D_SPHERE", (-r_sph, 0.0, H_CENTER), (r_sph, 0.0, H_CENTER))
    s.setLinearDimension("H_CENTER", (0.0, 0.0, 0.0), (0.0, 0.0, H_CENTER))
