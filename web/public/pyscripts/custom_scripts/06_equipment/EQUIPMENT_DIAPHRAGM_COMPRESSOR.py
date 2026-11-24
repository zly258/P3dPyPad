# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"化工高压隔膜压缩机撬块",
    TooltipLong=u"化工高纯氢气/特种气体/剧毒气体零泄漏增压用卧式曲轴箱-立式大圆盘膜头隔膜压缩机撬块 (符合 GB/T 20322 / API 618，含重型槽钢底座、曲轴箱机身、多螺栓大直径圆盘隔膜气缸头、级间冷却器、皮带飞轮护罩与防爆电机)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(L_BASE=LENGTH, TooltipShort=u"撬座总长", TooltipLong=u"隔膜压缩机公用撬块底座总长 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"撬座宽度", TooltipLong=u"公用撬块底座总宽度 (mm)")
@param(H_TOTAL=LENGTH, TooltipShort=u"膜头顶高", TooltipLong=u"撬座底面至顶部隔膜气缸排气管口的总高度 (mm)")
@param(D_HEAD=LENGTH, TooltipShort=u"隔膜缸头径", TooltipLong=u"上部锻钢多螺栓圆盘隔膜气缸盖外径 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"进排气管径", TooltipLong=u"气体吸入口与高压排出口外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"高压隔膜压缩机机组位号编码")
def EQUIPMENT_DIAPHRAGM_COMPRESSOR(s, L_BASE=1650.0, W_BASE=920.0, H_TOTAL=1180.0, D_HEAD=560.0, D_NOZ=60.3, ID=u"C-101-DIAPHRAGM", **kw):
    L_BASE = max(1100.0, float(L_BASE))
    W_BASE = max(620.0, float(W_BASE))
    H_TOTAL = max(820.0, float(H_TOTAL))
    D_HEAD = max(360.0, float(D_HEAD))
    D_NOZ = max(25.0, float(D_NOZ))

    h_base = 95.0
    r_head = D_HEAD / 2.0
    r_noz = D_NOZ / 2.0
    r_fl = r_noz + 48.0
    t_fl = 22.0

    # 1. 重型型钢公用撬座底板 (BOX: H=dx=L_BASE, L=dy=W_BASE, W=dz=h_base)
    o_m = BOX(s, L=W_BASE, W=h_base, H=L_BASE).translate((0.0, 0.0, h_base * 0.5))

    # 2. 前侧曲轴箱机身 + 液压油缸中体 + 顶部重型12螺栓大圆盘隔膜气缸盖 (-X 侧)
    x_comp = -L_BASE * 0.22
    h_crank = (H_TOTAL - h_base) * 0.42
    o_crank = BOX(s, L=W_BASE * 0.58, W=h_crank, H=L_BASE * 0.42).translate((x_comp, -W_BASE * 0.08, h_base + h_crank * 0.5))
    z_hyd = h_base + h_crank
    h_hyd = (H_TOTAL - z_hyd) * 0.36
    o_hyd = CYLINDER(s, R=r_head * 0.58, H=h_hyd, O=0.0).translate((x_comp, -W_BASE * 0.08, z_hyd - 10.0))

    z_head_bot = z_hyd + h_hyd - 15.0
    h_disk = 145.0
    o_head = CYLINDER(s, R=r_head, H=h_disk, O=0.0).translate((x_comp, -W_BASE * 0.08, z_head_bot))
    for p in (o_crank, o_hyd, o_head):
        o_m.uniteWith(p); p.erase()

    # 隔膜缸头周向 12 颗高强紧固螺柱
    for k in range(12):
        ang = math.radians(30.0 * k)
        st = CYLINDER(s, R=14.0, H=h_disk + 32.0, O=0.0).translate((x_comp + r_head * 0.84 * math.cos(ang), -W_BASE * 0.08 + r_head * 0.84 * math.sin(ang), z_head_bot - 12.0))
        o_m.uniteWith(st); st.erase()

    # 3. 侧向卧式套管/列管级间冷却器 (+Y 侧) + 后端飞轮皮带全封闭护罩 + 防爆主电机 (+X 侧)
    o_cool = CYLINDER(s, R=85.0, H=L_BASE * 0.56, O=0.0).rotateY(90.0).translate((-L_BASE * 0.38, W_BASE * 0.32, h_base + 180.0))
    o_cped1 = BOX(s, L=90.0, W=180.0, H=40.0).translate((-L_BASE * 0.25, W_BASE * 0.32, h_base + 90.0))
    o_cped2 = BOX(s, L=90.0, W=180.0, H=40.0).translate((L_BASE * 0.05, W_BASE * 0.32, h_base + 90.0))
    o_guard = BOX(s, L=W_BASE * 0.72, W=h_crank * 1.25, H=135.0).translate((L_BASE * 0.36, 0.0, h_base + h_crank * 0.62))

    x_mot = L_BASE * 0.14
    r_mot = 165.0
    o_mot = CYLINDER(s, R=r_mot, H=380.0, O=0.0).rotateY(90.0).translate((x_mot - 190.0, -W_BASE * 0.12, h_base + r_mot + 55.0))
    o_mfoot = BOX(s, L=280.0, W=90.0, H=320.0).translate((x_mot, -W_BASE * 0.12, h_base + 45.0))
    for p in (o_cool, o_cped1, o_cped2, o_guard, o_mot, o_mfoot):
        o_m.uniteWith(p); p.erase()

    # 4. 隔膜缸头顶部进气法兰口 (Port 1, +Z) 与高压排气法兰口 (Port 2, +Z)
    yc = -W_BASE * 0.08
    x_suc = x_comp - r_head * 0.38
    x_dis = x_comp + r_head * 0.38
    n_s = CYLINDER(s, R=r_noz, H=H_TOTAL - z_head_bot, O=0.0).translate((x_suc, yc, z_head_bot))
    f_s = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((x_suc, yc, H_TOTAL - t_fl))
    n_d = CYLINDER(s, R=r_noz, H=H_TOTAL - z_head_bot, O=0.0).translate((x_dis, yc, z_head_bot))
    f_d = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((x_dis, yc, H_TOTAL - t_fl))
    for p in (n_s, f_s, n_d, f_d):
        o_m.uniteWith(p); p.erase()

    s.setPoint((x_suc, yc, H_TOTAL), (0.0, 0.0, 1.0))
    s.setPoint((x_dis, yc, H_TOTAL), (0.0, 0.0, 1.0))
    s.setLinearDimension("L_BASE", (-L_BASE / 2.0, 0.0, 0.0), (L_BASE / 2.0, 0.0, 0.0))
    s.setLinearDimension("W_BASE", (0.0, -W_BASE / 2.0, 0.0), (0.0, W_BASE / 2.0, 0.0))
    s.setLinearDimension("H_TOTAL", (x_comp, yc, 0.0), (x_comp, yc, H_TOTAL))
