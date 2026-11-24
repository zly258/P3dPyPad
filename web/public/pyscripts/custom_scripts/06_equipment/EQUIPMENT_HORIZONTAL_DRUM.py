# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *
import math

@activate(Group="Equipment", Ports=3, TooltipShort=u"化工卧式双鞍座储罐 (NB/T 47042)", TooltipLong=u"化工行业标准 NB/T 47042 / JB/T 4712.1 卧式双鞍座压力容器/回流罐 (Horizontal Saddle-Supported Drum)，含圆筒体、左右2:1标准椭圆封头、双鞍式支座(带弧形垫板与加劲肋)、顶部人孔及进出料法兰管口", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"设备主要结构尺寸：筒体、封头、接管与支承高度")
@param(D_DRUM=LENGTH, TooltipShort=u"储罐筒体外径 D", Ask4Dist=True, TooltipLong=u"储罐筒体外径 D")
@param(L_SHELL=LENGTH, TooltipShort=u"筒体切线长 L", Ask4Dist=True, TooltipLong=u"筒体切线长 L")
@param(H_CENTER=LENGTH, TooltipShort=u"中心线至底座高 H", Ask4Dist=True, TooltipLong=u"中心线至底座高 H")
@param(L_SADDLE=LENGTH, TooltipShort=u"两鞍座中心距 S", Ask4Dist=True, TooltipLong=u"两鞍座中心距 S")
@param(DN_NOZZLE=LENGTH, TooltipShort=u"进出料管口外径", TooltipLong=u"进出料管口外径")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def EQUIPMENT_HORIZONTAL_DRUM(s, D_DRUM=1200.0, L_SHELL=3200.0, H_CENTER=850.0, L_SADDLE=2000.0, DN_NOZZLE=114.3, ID="V-201", **kw):
    D_DRUM = max(500.0, float(D_DRUM))
    L_SHELL = max(1200.0, float(L_SHELL))
    r_drum = D_DRUM / 2.0
    H_CENTER = max(r_drum + 180.0, float(H_CENTER))
    L_SADDLE = max(L_SHELL * 0.4, min(L_SHELL * 0.82, float(L_SADDLE)))
    DN_NOZZLE = max(40.0, float(DN_NOZZLE))

    r_noz = DN_NOZZLE / 2.0
    head_len = r_drum * 0.5  # 2:1 椭圆封头深度

    # 1. 卧式圆筒体 (沿 X 轴 [-L_SHELL/2, +L_SHELL/2]，中心线在 z = 0) + 左右 2:1 标准椭圆封头
    o_drum = CYLINDER(s, R=r_drum, H=L_SHELL, O=0.0).rotateY(90.0).translate((-L_SHELL * 0.5, 0.0, 0.0))
    o_head_r = ELLIPSOIDHEAD(s, R=r_drum, H=head_len).rotateY(90.0).translate((L_SHELL * 0.5, 0.0, 0.0))
    o_head_l = ELLIPSOIDHEAD(s, R=r_drum, H=head_len).rotateY(-90.0).translate((-L_SHELL * 0.5, 0.0, 0.0))
    o_drum.uniteWith(o_head_r); o_head_r.erase()
    o_drum.uniteWith(o_head_l); o_head_l.erase()

    # 2. 两座 JB/T 4712.1 标准鞍式支座 (位于 x = ±L_SADDLE/2，底面在 z = -H_CENTER)
    w_sad_y = D_DRUM * 0.88
    l_sad_x = max(180.0, D_DRUM * 0.18)
    t_base = 24.0
    t_web = 16.0
    r_pad = r_drum + 14.0

    for sx in (-1.0, 1.0):
        xs = sx * L_SADDLE * 0.5
        # 鞍座底板
        base = BOX(s, L=w_sad_y, W=t_base, H=l_sad_x).translate((xs, 0.0, -H_CENTER + t_base * 0.5))
        o_drum.uniteWith(base); base.erase()
        # 鞍座中心腹板 + 前后两翼斜肋板
        h_web = H_CENTER - t_base - r_drum * 0.35
        web = BOX(s, L=w_sad_y * 0.92, W=h_web, H=t_web).translate((xs, 0.0, -H_CENTER + t_base + h_web * 0.5))
        o_drum.uniteWith(web); web.erase()
        for sy in (-1.0, 0.0, 1.0):
            rib = BOX(s, L=t_web, W=h_web, H=l_sad_x * 0.86).translate((xs, sy * w_sad_y * 0.38, -H_CENTER + t_base + h_web * 0.5))
            o_drum.uniteWith(rib); rib.erase()
        # 120° 弧形鞍座护板
        pad = CYLINDER(s, R=r_pad, H=l_sad_x * 1.15, O=0.0).rotateY(90.0).translate((xs - l_sad_x * 0.575, 0.0, 0.0))
        cut_top = BOX(s, L=2.0 * r_pad + 20.0, W=2.0 * r_pad, H=l_sad_x * 1.3).translate((xs, 0.0, r_pad * 0.55))
        pad.subtractFrom(cut_top); cut_top.erase()
        o_drum.uniteWith(pad); pad.erase()

    # 3. 顶部中央法兰人孔 (Manhole at x = 0, z = r_drum + 180)
    r_mh = min(250.0, r_drum * 0.38)
    z_mh = r_drum + 170.0
    o_mh = CYLINDER(s, R=r_mh, H=190.0, O=0.0).translate((0.0, 0.0, r_drum - 20.0))
    o_mh_fl = CYLINDER(s, R=r_mh + 55.0, H=48.0, O=0.0).translate((0.0, 0.0, z_mh - 24.0))
    o_drum.uniteWith(o_mh); o_mh.erase()
    o_drum.uniteWith(o_mh_fl); o_mh_fl.erase()

    # 4. 三个工艺管口: Port 1 (顶部左进料口), Port 2 (顶部右气相口), Port 3 (底部右液相出口)
    z_top_noz = r_drum + 180.0
    z_bot_noz = -(r_drum + 180.0)
    x_p1 = -L_SHELL * 0.32
    x_p2 = L_SHELL * 0.32
    x_p3 = L_SHELL * 0.28
    r_fl = r_noz + 50.0
    fl_t = 22.0

    for xp in (x_p1, x_p2):
        np_c = CYLINDER(s, R=r_noz, H=200.0, O=0.0).translate((xp, 0.0, r_drum - 20.0))
        nf_c = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).translate((xp, 0.0, z_top_noz - fl_t))
        nb_c = CYLINDER(s, R=r_noz * 0.85, H=160.0, O=0.0).translate((xp, 0.0, z_top_noz - 155.0))
        o_drum.uniteWith(np_c); np_c.erase()
        o_drum.uniteWith(nf_c); nf_c.erase()
        o_drum.subtractFrom(nb_c); nb_c.erase()

    np_b = CYLINDER(s, R=r_noz, H=200.0, O=0.0).translate((x_p3, 0.0, z_bot_noz))
    nf_b = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).translate((x_p3, 0.0, z_bot_noz))
    nb_b = CYLINDER(s, R=r_noz * 0.85, H=160.0, O=0.0).translate((x_p3, 0.0, z_bot_noz - 5.0))
    o_drum.uniteWith(np_b); np_b.erase()
    o_drum.uniteWith(nf_b); nf_b.erase()
    o_drum.subtractFrom(nb_b); nb_b.erase()

    s.setPoint((x_p1, 0.0, z_top_noz), (0.0, 0.0, 1.0))
    s.setPoint((x_p2, 0.0, z_top_noz), (0.0, 0.0, 1.0))
    s.setPoint((x_p3, 0.0, z_bot_noz), (0.0, 0.0, -1.0))

    s.setLinearDimension("L_SHELL", (-L_SHELL * 0.5, 0.0, r_drum), (L_SHELL * 0.5, 0.0, r_drum))
    s.setLinearDimension("L_SADDLE", (-L_SADDLE * 0.5, 0.0, -H_CENTER), (L_SADDLE * 0.5, 0.0, -H_CENTER))
    s.setLinearDimension("H_CENTER", (-L_SHELL * 0.5, 0.0, -H_CENTER), (-L_SHELL * 0.5, 0.0, 0.0))
    s.setLinearDimension("D_DRUM", (-L_SHELL * 0.5 - head_len, -r_drum, 0.0), (-L_SHELL * 0.5 - head_len, r_drum, 0.0))
