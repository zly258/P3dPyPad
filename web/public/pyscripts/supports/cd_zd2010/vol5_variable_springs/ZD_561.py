# -*- coding: utf-8 -*-
# CD-ZD2010 561 支架式变力弹簧组件（搁置式弹簧筒体 + 底部宽方形底座板 + 四角放射状斜向三角形加劲肋 + 顶部圆形承重托盘与载荷柱）
from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *
@activate(Group="Support", TooltipShort="561支架式变力弹簧", TooltipLong="CD-ZD2010 561 支架式变力弹簧组件", LengthUnit="mm", Ports=1)
@group("MainDimensions", TooltipLong="主要尺寸参数")
@param(D_casing=LENGTH, TooltipShort="筒外径", TooltipLong="壳筒直径 D")
@param(H_free=LENGTH, TooltipShort="总高度", TooltipLong="0位组件总高度 H0", Ask4Dist=True)
@param(Base_L=LENGTH, TooltipShort="底板长", TooltipLong="方形底座边长 B")
@param(Base_W=LENGTH, TooltipShort="底板宽", TooltipLong="方形底座宽度 B")
@param(Travel_mm=LENGTH, TooltipShort="行程", TooltipLong="额定工作位移量")
@param(ID=STRING, TooltipShort="位号", TooltipLong="部件位号")
@param(Load_min_kN=LENGTH0, TooltipShort="最小荷载", TooltipLong="最小工作荷载(kN)")
@param(Load_max_kN=LENGTH0, TooltipShort="最大荷载", TooltipLong="最大工作荷载(kN)")
@param(Weight_kg=LENGTH0, TooltipShort="质量", TooltipLong="组件质量(kg)")
def ZD_561(s, D_casing=214.0, H_free=531.0, Base_L=290.0, Base_W=290.0, Travel_mm=75.0, ID=u"ZD_561", Load_min_kN=5.4, Load_max_kN=11.564, Weight_kg=45.8, **kw):
    D_casing = float(D_casing); H_free = float(H_free); Base_L = float(Base_L); Base_W = float(Base_W); Travel_mm = float(Travel_mm)
    if D_casing < 60.0: D_casing = 60.0
    if H_free < 150.0: H_free = 150.0
    if Base_L < D_casing + 30.0: Base_L = D_casing + 50.0
    if Base_W < D_casing + 30.0: Base_W = Base_L
    RT = D_casing / 2.0
    thk = max(5.0, min(10.0, RT * 0.12))
    base_t = max(12.0, min(22.0, RT * 0.16))

    # 图集 561 特征：底部方形底板 (四角带斜向 U 形安装槽孔 + 四角放射状斜向三角形加劲肋) + 中部圆筒 + 上部载荷柱 D1 + 顶部圆形托盘法兰 D
    col_h = max(50.0, min(H_free * 0.26, Travel_mm + 45.0))
    cyl_h = max(80.0, H_free - base_t - col_h)
    z_base_top = -(H_free - base_t)
    z_cyl_top = -col_h

    # 1. 底部宽方形底座板 (Z in [-H_free, z_base_top]) + 四角安装孔
    o1 = BOX(s, L=Base_W, W=base_t, H=Base_L).translate((0.0, 0.0, -(H_free - base_t / 2.0)))
    hole_r = max(8.0, min(16.0, Base_L * 0.04))
    bolt_offset = Base_L * 0.38
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            o_bh = CYLINDER(s, R=hole_r, H=base_t * 3.0, O=0.0).translate((sx * bolt_offset, sy * bolt_offset, -H_free - base_t))
            o1.subtractFrom(o_bh); o_bh.erase()

    # 2. 搁置式空心圆柱弹簧筒体与侧壁刻度槽 (Z in [z_base_top, z_cyl_top])
    o_cyl = CYLINDER(s, R=RT, H=cyl_h + 2.0, O=0.0).translate((0.0, 0.0, z_base_top - 2.0))
    o_in = CYLINDER(s, R=RT - thk, H=max(20.0, cyl_h - thk * 2.0), O=0.0).translate((0.0, 0.0, z_base_top + thk))
    o_cyl.subtractFrom(o_in); o_in.erase()
    slot_w = max(12.0, RT * 0.20)
    slot_h = min(cyl_h * 0.65, max(25.0, Travel_mm + 16.0))
    slot_z = z_base_top + cyl_h * 0.5
    o_slot = BOX(s, L=RT * 2.5, W=slot_h, H=slot_w).translate((0.0, 0.0, slot_z))
    o_cyl.subtractFrom(o_slot); o_slot.erase()
    o1.uniteWith(o_cyl); o_cyl.erase()

    # 3. 四角放射状斜向三角形加劲肋 (沿 45°, 135°, 225°, 315° 对角线连接底座四角与弹簧筒外壁)
    rib_len = max(20.0, (Base_L * 0.64 - RT))
    rib_h = min(cyl_h * 0.55, rib_len * 1.4)
    rib_t = max(8.0, thk)
    for ang in (45.0, 135.0, 225.0, 315.0):
        o_rib = BOX(s, L=rib_t, W=rib_h, H=rib_len + 12.0).translate((RT + rib_len / 2.0 - 6.0, 0.0, z_base_top + rib_h / 2.0))
        # 斜切外上角形成三角形肋板
        cut_diag = sqrt(rib_len * rib_len + rib_h * rib_h) * 1.5
        tilt = degrees(atan2(rib_len, rib_h))
        o_rcut = BOX(s, L=rib_t * 3.0, W=cut_diag, H=cut_diag).rotateY(-tilt).translate((RT + rib_len * 0.85, 0.0, z_base_top + rib_h * 0.85))
        o_rib.subtractFrom(o_rcut); o_rcut.erase()
        o_rib.rotateZ(ang)
        o1.uniteWith(o_rib); o_rib.erase()

    # 4. 上部管状载荷柱 (直径 D1 ≈ 0.85*D) + 横向锁定销孔 + 顶部圆形承重托盘 (直径 D_casing，顶面位于 Z = 0.0)
    r_col = RT * 0.82
    o_col = CYLINDER(s, R=r_col, H=col_h + cyl_h * 0.35, O=0.0).translate((0.0, 0.0, z_cyl_top - cyl_h * 0.35))
    o_col_in = CYLINDER(s, R=max(10.0, r_col - thk), H=col_h, O=0.0).translate((0.0, 0.0, z_cyl_top - 5.0))
    o_col.subtractFrom(o_col_in); o_col_in.erase()
    # 载荷柱侧面调节孔
    o_pin = CYLINDER(s, R=max(6.0, RT * 0.08), H=r_col * 3.0, O=0.0).rotateY(90.0).translate((-r_col * 1.5, 0.0, -col_h * 0.45))
    o_col.subtractFrom(o_pin); o_pin.erase()
    o1.uniteWith(o_col); o_col.erase()

    # 顶部圆形承重托盘盖板
    top_plate_t = max(12.0, base_t * 0.85)
    o_top_plate = CYLINDER(s, R=RT, H=top_plate_t, O=0.0).translate((0.0, 0.0, -top_plate_t))
    o1.uniteWith(o_top_plate); o_top_plate.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    s.setLinearDimension('H_free', (0.0, 0.0, 0.0), (0.0, 0.0, -H_free))
