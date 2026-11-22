# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="4",
    TooltipShort=u"AKT型釜式重沸器",
    TooltipLong=u"化工精馏塔底 AKT 型釜式重沸器 (符合 GB/T 151 / TEMA AKT 标准，含前端管箱与对夹大法兰、管束圆筒段、偏心扩径锥壳、大直径气液分离釜式壳体、不等高双鞍座与管壳程4管口)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D_BUNDLE=LENGTH, TooltipShort=u"管束段直径", TooltipLong=u"前端管箱与管束圆筒段外径 (mm)")
@param(D_KETTLE=LENGTH, TooltipShort=u"釜壳段直径", TooltipLong=u"后端扩大气液分离釜体段外径 (mm)")
@param(L_TOTAL=LENGTH, TooltipShort=u"直筒总长", TooltipLong=u"管箱、锥段与扩大釜壳段合计长度 (mm)")
@param(H_CENTER=LENGTH, TooltipShort=u"管束中心高", TooltipLong=u"前端管束中心线至鞍座底板底面的距离 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"管口外径", TooltipLong=u"主要壳程与管程接管外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"AKT型釜式重沸器位号编码")
def EQUIPMENT_KETTLE_REBOILER(s, D_BUNDLE=600.0, D_KETTLE=1000.0, L_TOTAL=3400.0, H_CENTER=750.0, D_NOZ=168.3, ID=u"E-102-AKT600/1000", **kw):
    D_BUNDLE = max(350.0, float(D_BUNDLE))
    D_KETTLE = max(D_BUNDLE * 1.4, float(D_KETTLE))
    L_TOTAL = max(2000.0, float(L_TOTAL))
    r_bun = D_BUNDLE / 2.0
    r_ket = D_KETTLE / 2.0
    H_CENTER = max(r_ket + 220.0, float(H_CENTER))
    D_NOZ = max(60.3, float(D_NOZ))

    r_noz = D_NOZ / 2.0
    r_fl = r_noz + 55.0
    t_fl = 24.0
    z_bot = -H_CENTER

    # 底母线齐平: 管束段中心在 Z=0, 扩大釜体中心在 Z = +(r_ket - r_bun)
    ecc_z = r_ket - r_bun
    l_chan = L_TOTAL * 0.22
    l_cone = L_TOTAL * 0.20
    l_ket = L_TOTAL * 0.58
    x0 = -L_TOTAL * 0.5
    x1 = x0 + l_chan
    x2 = x1 + l_cone
    x3 = x0 + L_TOTAL

    # 1. 前端管箱 + 管箱平盖/封头 + 管板对夹大法兰环
    o_m = CYLINDER(s, R=r_bun, H=l_chan, O=0.0).rotateY(90.0).translate((x0, 0.0, 0.0))
    o_ch_cov = CYLINDER(s, R=r_bun + 55.0, H=65.0, O=0.0).rotateY(90.0).translate((x0 - 45.0, 0.0, 0.0))
    o_ts_fl = CYLINDER(s, R=r_bun + 60.0, H=85.0, O=0.0).rotateY(90.0).translate((x1 - 42.5, 0.0, 0.0))
    o_m.uniteWith(o_ch_cov); o_ch_cov.erase()
    o_m.uniteWith(o_ts_fl); o_ts_fl.erase()

    # 2. 偏心扩径锥壳 (底母线平齐，顶部抬升 ecc_z) + 扩大釜式壳体 + 后端椭圆形封头 + 后端头盖大法兰
    # CONE E 参数沿局部 +X 偏心; rotateY(90) 后原 +X 变为 -Z，故取 E = -ecc_z 使偏心朝 +Z
    o_cone = CONE(s, R1=r_bun, R2=r_ket, H=l_cone, E=-ecc_z).rotateY(90.0).translate((x1, 0.0, 0.0))
    o_ket = CYLINDER(s, R=r_ket, H=l_ket, O=0.0).rotateY(90.0).translate((x2, 0.0, ecc_z))
    o_rear_fl = CYLINDER(s, R=r_ket + 55.0, H=75.0, O=0.0).rotateY(90.0).translate((x3 - 55.0, 0.0, ecc_z))
    o_rear_hd = ELLIPSOIDHEAD(s, R=r_ket, H=r_ket * 0.5).rotateY(90.0).translate((x3, 0.0, ecc_z))
    for p in (o_cone, o_ket, o_rear_fl, o_rear_hd):
        o_m.uniteWith(p); p.erase()

    # 3. 前后双鞍式支座 (底面均齐平于 Z = z_bot = -H_CENTER)
    t_b = 24.0
    for xs, r_cur, z_c in ((x0 + l_chan * 0.55, r_bun, 0.0), (x2 + l_ket * 0.65, r_ket, ecc_z)):
        w_sad = r_cur * 1.75
        l_sad = 220.0
        h_s = (z_c - r_cur * 0.5) - (z_bot + t_b)
        bp = BOX(s, L=w_sad, W=t_b, H=l_sad).translate((xs, 0.0, z_bot + t_b * 0.5))
        wb = BOX(s, L=w_sad * 0.88, W=h_s, H=20.0).translate((xs, 0.0, z_bot + t_b + h_s * 0.5))
        sad = CYLINDER(s, R=r_cur + 18.0, H=l_sad, O=0.0).rotateY(90.0).translate((xs - l_sad * 0.5, 0.0, z_c))
        trim = BOX(s, L=(r_cur + 30.0) * 2.2, W=r_cur * 1.5, H=l_sad + 20.0).translate((xs, 0.0, z_c + r_cur * 0.45))
        sad.subtractFrom(trim); trim.erase()
        for p in (bp, wb, sad):
            o_m.uniteWith(p); p.erase()

    # 4. 四个工艺接管:
    # Port 1: 管箱上部热媒蒸汽进口 (+Z at x_tube)
    # Port 2: 管箱下部凝液出口 (-Z at x_tube)
    # Port 3: 釜体顶部二次蒸汽大口径气相出口 (+Z at x_vap)
    # Port 4: 釜体后端底部溢流塔底采出口 (-Z at x_liq)
    x_tube = x0 + l_chan * 0.45
    z_p1 = r_bun + 170.0
    z_p2 = -(r_bun + 170.0)
    n1 = CYLINDER(s, R=r_noz * 0.85, H=z_p1, O=0.0).translate((x_tube, 0.0, 0.0))
    f1 = CYLINDER(s, R=r_fl * 0.88, H=t_fl, O=0.0).translate((x_tube, 0.0, z_p1 - t_fl))
    n2 = CYLINDER(s, R=r_noz * 0.85, H=abs(z_p2), O=0.0).translate((x_tube, 0.0, z_p2))
    f2 = CYLINDER(s, R=r_fl * 0.88, H=t_fl, O=0.0).translate((x_tube, 0.0, z_p2))

    x_vap = x2 + l_ket * 0.38
    z_p3 = ecc_z + r_ket + 210.0
    n3 = CYLINDER(s, R=r_noz * 1.15, H=r_ket + 210.0, O=0.0).translate((x_vap, 0.0, ecc_z))
    f3 = CYLINDER(s, R=r_fl * 1.15, H=t_fl, O=0.0).translate((x_vap, 0.0, z_p3 - t_fl))

    x_liq = x2 + l_ket * 0.82
    z_p4 = ecc_z - r_ket - 180.0
    n4 = CYLINDER(s, R=r_noz, H=r_ket + 180.0, O=0.0).translate((x_liq, 0.0, z_p4))
    f4 = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((x_liq, 0.0, z_p4))

    for p in (n1, f1, n2, f2, n3, f3, n4, f4):
        o_m.uniteWith(p); p.erase()

    s.setPoint((x_tube, 0.0, z_p1), (0.0, 0.0, 1.0))
    s.setPoint((x_tube, 0.0, z_p2), (0.0, 0.0, -1.0))
    s.setPoint((x_vap, 0.0, z_p3), (0.0, 0.0, 1.0))
    s.setPoint((x_liq, 0.0, z_p4), (0.0, 0.0, -1.0))
    s.setLinearDimension("L_TOTAL", (x0, 0.0, z_bot), (x3, 0.0, z_bot))
    s.setLinearDimension("D_KETTLE", (x_vap, -r_ket, ecc_z), (x_vap, r_ket, ecc_z))
    s.setLinearDimension("H_CENTER", (x0, 0.0, z_bot), (x0, 0.0, 0.0))
