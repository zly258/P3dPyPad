# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="3",
    TooltipShort=u"立式降膜蒸发器带分离器",
    TooltipLong=u"化工热敏性物料浓缩用立式长管降膜蒸发器与旁置气液分离室成套设备 (符合 HG/T 3188，含细长列管加热室、顶部布膜分布器封头、下部气液切向连通斜管、旁置大直径气液分离器、耳式支座与落地支腿)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D_HEATER=LENGTH, TooltipShort=u"加热室直径", TooltipLong=u"左侧降膜管束加热室圆筒外径 (mm)")
@param(H_HEATER=LENGTH, TooltipShort=u"加热室高度", TooltipLong=u"降膜加热室直筒段高度 (mm)")
@param(D_SEP=LENGTH, TooltipShort=u"分离室直径", TooltipLong=u"右侧气液分离器圆筒外径 (mm)")
@param(H_SEP=LENGTH, TooltipShort=u"分离室高度", TooltipLong=u"气液分离器直筒段高度 (mm)")
@param(SPAN_CC=LENGTH, TooltipShort=u"两筒中心距", TooltipLong=u"加热室与气液分离室轴线水平间距 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"工艺管口径", TooltipLong=u"进料、浓缩液与二次蒸汽管口外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"降膜蒸发器设备位号编码")
def EQUIPMENT_FALLING_FILM_EVAPORATOR(s, D_HEATER=650.0, H_HEATER=3600.0, D_SEP=1050.0, H_SEP=2100.0, SPAN_CC=1350.0, D_NOZ=168.3, ID=u"EV-101-FFE", **kw):
    D_HEATER = max(400.0, float(D_HEATER))
    H_HEATER = max(2200.0, float(H_HEATER))
    D_SEP = max(D_HEATER * 1.35, float(D_SEP))
    H_SEP = max(1400.0, float(H_SEP))
    SPAN_CC = max((D_HEATER + D_SEP) * 0.5 + 320.0, float(SPAN_CC))
    D_NOZ = max(60.3, float(D_NOZ))

    r_ht = D_HEATER / 2.0
    r_sep = D_SEP / 2.0
    r_noz = D_NOZ / 2.0
    r_fl = r_noz + 55.0
    t_fl = 24.0

    x_ht = -SPAN_CC * 0.45
    x_sep = x_ht + SPAN_CC
    z_ht_bot = 650.0
    z_ht_top = z_ht_bot + H_HEATER

    # 1. 左侧细长立式降膜加热室 + 上下管板大法兰与封头 + 顶部料液进料口 (Port 1, +Z)
    o_m = CYLINDER(s, R=r_ht, H=H_HEATER, O=0.0).translate((x_ht, 0.0, z_ht_bot))
    o_ht_fl_t = CYLINDER(s, R=r_ht + 55.0, H=75.0, O=0.0).translate((x_ht, 0.0, z_ht_top - 45.0))
    o_ht_fl_b = CYLINDER(s, R=r_ht + 55.0, H=75.0, O=0.0).translate((x_ht, 0.0, z_ht_bot - 30.0))
    o_ht_hd_t = ELLIPSOIDHEAD(s, R=r_ht, H=r_ht * 0.5).translate((x_ht, 0.0, z_ht_top + 30.0))
    o_ht_hd_b = CONE(s, R1=r_noz * 1.2, R2=r_ht, H=380.0, E=0.0).translate((x_ht, 0.0, z_ht_bot - 380.0))
    for p in (o_ht_fl_t, o_ht_fl_b, o_ht_hd_t, o_ht_hd_b):
        o_m.uniteWith(p); p.erase()

    z_feed = z_ht_top + 30.0 + r_ht * 0.5 + 160.0
    n_feed = CYLINDER(s, R=r_noz * 0.85, H=200.0, O=0.0).translate((x_ht, 0.0, z_feed - 200.0))
    f_feed = CYLINDER(s, R=r_fl * 0.88, H=t_fl, O=0.0).translate((x_ht, 0.0, z_feed - t_fl))
    o_m.uniteWith(n_feed); n_feed.erase()
    o_m.uniteWith(f_feed); f_feed.erase()

    # 加热室壳程生蒸汽进口与冷凝水出口 (-X)
    for zf in (0.18, 0.84):
        zs = z_ht_bot + H_HEATER * zf
        sn = CYLINDER(s, R=r_noz * 0.75, H=r_ht + 180.0, O=0.0).rotateY(-90.0).translate((x_ht, 0.0, zs))
        sf = CYLINDER(s, R=r_fl * 0.78, H=22.0, O=0.0).rotateY(-90.0).translate((x_ht - r_ht - 158.0, 0.0, zs))
        o_m.uniteWith(sn); sn.erase()
        o_m.uniteWith(sf); sf.erase()

    # 2. 右侧大直径气液分离室 + 上椭球封头 + 下锥形浓缩液底斗 + 连通大斜管 + 支承立腿 (落于 Z=0)
    z_sep_bot = 820.0
    z_sep_top = z_sep_bot + H_SEP
    o_sep = CYLINDER(s, R=r_sep, H=H_SEP, O=0.0).translate((x_sep, 0.0, z_sep_bot))
    o_sep_t = ELLIPSOIDHEAD(s, R=r_sep, H=r_sep * 0.5).translate((x_sep, 0.0, z_sep_top))
    o_sep_b = CONE(s, R1=r_noz, R2=r_sep, H=520.0, E=0.0).translate((x_sep, 0.0, z_sep_bot - 520.0))
    for p in (o_sep, o_sep_t, o_sep_b):
        o_m.uniteWith(p); p.erase()

    # 连接降膜加热室下部与气液分离室中下部的水平大口径气液过桥连通管 + 上部稳固连系横梁
    z_duct = z_sep_bot + H_SEP * 0.26
    o_duct = CYLINDER(s, R=r_noz * 1.45, H=SPAN_CC, O=0.0).rotateY(90.0).translate((x_ht, 0.0, z_duct))
    o_tie = BOX(s, L=120.0, W=140.0, H=SPAN_CC).translate(((x_ht + x_sep) * 0.5, 0.0, z_sep_top - 180.0))
    o_m.uniteWith(o_duct); o_duct.erase()
    o_m.uniteWith(o_tie); o_tie.erase()

    # 加热室与分离室共 6 根落地H型钢/圆管支腿 (底面 Z=0)
    for xc, rc, z_top_leg in ((x_ht, r_ht, z_ht_bot + 260.0), (x_sep, r_sep, z_sep_bot + 260.0)):
        for sy in (-1.0, 1.0):
            yl = sy * (rc + 45.0)
            leg = CYLINDER(s, R=58.0, H=z_top_leg, O=0.0).translate((xc, yl, 24.0))
            lug = BOX(s, L=140.0, W=180.0, H=140.0).translate((xc, sy * rc, z_top_leg - 60.0))
            bp = BOX(s, L=240.0, W=24.0, H=240.0).translate((xc, yl, 12.0))
            for p in (leg, lug, bp):
                o_m.uniteWith(p); p.erase()

    # 3. 分离室顶部二次蒸汽大口径出口 (Port 2, +Z) 与底部浓缩液出口 (Port 3, -Z)
    z_vap = z_sep_top + r_sep * 0.5 + 180.0
    n_vap = CYLINDER(s, R=r_noz * 1.25, H=240.0, O=0.0).translate((x_sep, 0.0, z_vap - 240.0))
    f_vap = CYLINDER(s, R=r_fl * 1.25, H=t_fl, O=0.0).translate((x_sep, 0.0, z_vap - t_fl))

    z_conc = z_sep_bot - 660.0
    n_conc = CYLINDER(s, R=r_noz, H=160.0, O=0.0).translate((x_sep, 0.0, z_conc))
    f_conc = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((x_sep, 0.0, z_conc))
    for p in (n_vap, f_vap, n_conc, f_conc):
        o_m.uniteWith(p); p.erase()

    s.setPoint((x_ht, 0.0, z_feed), (0.0, 0.0, 1.0))
    s.setPoint((x_sep, 0.0, z_vap), (0.0, 0.0, 1.0))
    s.setPoint((x_sep, 0.0, z_conc), (0.0, 0.0, -1.0))
    s.setLinearDimension("H_HEATER", (x_ht - r_ht, 0.0, z_ht_bot), (x_ht - r_ht, 0.0, z_ht_top))
    s.setLinearDimension("SPAN_CC", (x_ht, 0.0, 0.0), (x_sep, 0.0, 0.0))
