# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"鼓风式翅片管空冷器",
    TooltipLong=u"石化与化工塔顶冷凝/馏分冷却用水平鼓风式翅片管空冷式热交换器 (ACHE，符合 GB/T 15386 / GB/T 28712.6 / API 661，含水平翅片管束框架、两端丝堵管箱与进出口法兰、下部混风箱、双轴流风机风筒与叶轮及四立柱钢架)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(L_BUNDLE=LENGTH, TooltipShort=u"管束总长", TooltipLong=u"空冷器翅片管束与前后管箱总长度 (mm)")
@param(W_BUNDLE=LENGTH, TooltipShort=u"管束宽度", TooltipLong=u"空冷器管束框架横向宽度 (mm)")
@param(H_FRAME=LENGTH, TooltipShort=u"框架高度", TooltipLong=u"地面柱脚至管束底面的支承钢架高度 (mm)")
@param(D_FAN=LENGTH, TooltipShort=u"风机风筒径", TooltipLong=u"下部双轴流冷却风机风筒直径 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"管箱接管径", TooltipLong=u"两端管箱介质进出料法兰管口外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"鼓风式空冷器设备位号编码")
def EQUIPMENT_AIR_COOLED_EXCHANGER(s, L_BUNDLE=3600.0, W_BUNDLE=1800.0, H_FRAME=1650.0, D_FAN=1250.0, D_NOZ=168.3, ID=u"EC-101-ACHE", **kw):
    L_BUNDLE = max(2200.0, float(L_BUNDLE))
    W_BUNDLE = max(1200.0, float(W_BUNDLE))
    H_FRAME = max(1100.0, float(H_FRAME))
    D_FAN = min(W_BUNDLE * 0.78, max(750.0, float(D_FAN)))
    D_NOZ = max(60.3, float(D_NOZ))

    r_fan = D_FAN / 2.0
    r_noz = D_NOZ / 2.0
    r_fl = r_noz + 55.0
    t_fl = 24.0
    h_bun = 280.0
    h_plenum = 380.0

    # 1. 上部水平矩形翅片管束框架 + 两端加厚丝堵管箱 (Header Boxes at +/-X)
    z_bun_c = H_FRAME + h_bun * 0.5
    o_m = BOX(s, L=W_BUNDLE, W=h_bun, H=L_BUNDLE - 360.0).translate((0.0, 0.0, z_bun_c))
    for sx in (-1.0, 1.0):
        xh = sx * (L_BUNDLE * 0.5 - 110.0)
        hdr = BOX(s, L=W_BUNDLE * 1.04, W=h_bun * 1.25, H=220.0).translate((xh, 0.0, z_bun_c))
        o_m.uniteWith(hdr); hdr.erase()

    # 2. 管束下方风箱过渡室 (Plenum) + 前后两台大口径轴流风机风筒、轮毂叶轮与下部悬吊电机
    z_plen_c = H_FRAME - h_plenum * 0.5
    o_plen = BOX(s, L=W_BUNDLE * 0.94, W=h_plenum, H=L_BUNDLE * 0.88).translate((0.0, 0.0, z_plen_c))
    o_m.uniteWith(o_plen); o_plen.erase()

    z_ring_bot = H_FRAME - h_plenum - 240.0
    for sx in (-0.25, 0.25):
        xf = sx * L_BUNDLE
        f_ring = CYLINDER(s, R=r_fan, H=250.0, O=r_fan * 0.92).translate((xf, 0.0, z_ring_bot))
        f_hub = CYLINDER(s, R=r_fan * 0.24, H=160.0, O=0.0).translate((xf, 0.0, z_ring_bot + 70.0))
        f_mot = CYLINDER(s, R=135.0, H=340.0, O=0.0).translate((xf, 0.0, z_ring_bot - 260.0))
        m_beam = BOX(s, L=W_BUNDLE * 0.96, W=65.0, H=90.0).translate((xf, 0.0, z_ring_bot - 20.0))
        for p in (f_ring, f_hub, f_mot, m_beam):
            o_m.uniteWith(p); p.erase()
        for k in range(4):
            bl = BOX(s, L=110.0, W=18.0, H=r_fan * 1.82).rotateZ(k * 45.0).translate((xf, 0.0, z_ring_bot + 130.0))
            o_m.uniteWith(bl); bl.erase()

    # 3. 四角 H 型钢支承立柱 + 纵向连系梁 + 4块地面锚固底板 (Z=0)
    dx_col = L_BUNDLE * 0.44
    dy_col = W_BUNDLE * 0.45
    for sx in (-1.0, 1.0):
        s_beam = BOX(s, L=110.0, W=140.0, H=L_BUNDLE * 0.92).translate((0.0, sx * dy_col, H_FRAME * 0.48))
        o_m.uniteWith(s_beam); s_beam.erase()
        for sy in (-1.0, 1.0):
            xc, yc = sx * dx_col, sy * dy_col
            col = BOX(s, L=150.0, W=H_FRAME, H=150.0).translate((xc, yc, H_FRAME * 0.5))
            bp = BOX(s, L=320.0, W=28.0, H=320.0).translate((xc, yc, 14.0))
            o_m.uniteWith(col); col.erase()
            o_m.uniteWith(bp); bp.erase()

    # 4. 前管箱顶部热流进口 (Port 1, +Z) 与后管箱底部冷流出口 (Port 2, -Z)
    x_in = -(L_BUNDLE * 0.5 - 110.0)
    z_in = H_FRAME + h_bun + 220.0
    n_in = CYLINDER(s, R=r_noz, H=240.0, O=0.0).translate((x_in, 0.0, H_FRAME + h_bun - 20.0))
    f_in = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((x_in, 0.0, z_in - t_fl))

    x_out = L_BUNDLE * 0.5 - 110.0
    z_out = H_FRAME - 220.0
    n_out = CYLINDER(s, R=r_noz, H=240.0, O=0.0).translate((x_out, 0.0, z_out))
    f_out = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((x_out, 0.0, z_out))
    for p in (n_in, f_in, n_out, f_out):
        o_m.uniteWith(p); p.erase()

    s.setPoint((x_in, 0.0, z_in), (0.0, 0.0, 1.0))
    s.setPoint((x_out, 0.0, z_out), (0.0, 0.0, -1.0))
    s.setLinearDimension("L_BUNDLE", (-L_BUNDLE / 2.0, 0.0, 0.0), (L_BUNDLE / 2.0, 0.0, 0.0))
    s.setLinearDimension("W_BUNDLE", (0.0, -W_BUNDLE / 2.0, 0.0), (0.0, W_BUNDLE / 2.0, 0.0))
    s.setLinearDimension("H_FRAME", (-dx_col, -dy_col, 0.0), (-dx_col, -dy_col, H_FRAME))
