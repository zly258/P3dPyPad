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

@activate(Group="Equipment", Ports=4, TooltipShort=u"化工固定管板列管换热器 (GB/T 151 BEM)", TooltipLong=u"化工行业标准 GB/T 151 BEM型固定管板式列管热交换器 (Shell-and-Tube Heat Exchanger)，含壳程圆筒、前后管板设备大法兰与紧固螺柱、前后端管箱与椭圆封头、双鞍式支座及管程/壳程4个法兰接管嘴", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"设备主要结构尺寸：筒体、封头、接管与支承高度")
@param(D_SHELL=LENGTH, TooltipShort=u"壳体公称外径 D", Ask4Dist=True, TooltipLong=u"壳体公称外径 D")
@param(L_SHELL=LENGTH, TooltipShort=u"壳程管板间距 L", Ask4Dist=True, TooltipLong=u"壳程管板间距 L")
@param(L_CHAN=LENGTH, TooltipShort=u"两端管箱短节长", TooltipLong=u"两端管箱短节长")
@param(H_CENTER=LENGTH, TooltipShort=u"中心至鞍座底高 H", Ask4Dist=True, TooltipLong=u"中心至鞍座底高 H")
@param(DN_SHELL=LENGTH, TooltipShort=u"壳程接管外径", TooltipLong=u"壳程接管外径")
@param(DN_TUBE=LENGTH, TooltipShort=u"管程接管外径", TooltipLong=u"管程接管外径")
@param(ID=STRING, TooltipShort=u"换热器位号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def EQUIPMENT_SHELL_TUBE_EXCHANGER(s, D_SHELL=700.0, L_SHELL=3000.0, L_CHAN=420.0, H_CENTER=620.0, DN_SHELL=168.3, DN_TUBE=114.3, ID="E-101", **kw):
    D_SHELL = max(325.0, float(D_SHELL))
    L_SHELL = max(1400.0, float(L_SHELL))
    L_CHAN = max(240.0, float(L_CHAN))
    r_sh = D_SHELL / 2.0
    H_CENTER = max(r_sh + 160.0, float(H_CENTER))
    r_s_noz = max(30.0, float(DN_SHELL)) / 2.0
    r_t_noz = max(25.0, float(DN_TUBE)) / 2.0

    # 1. 壳程主筒体 (x in [-L_SHELL/2, +L_SHELL/2]) + 前后管箱筒体 + 左右 2:1 椭圆封头
    total_cyl = L_SHELL + 2.0 * L_CHAN
    o_ex = CYLINDER(s, R=r_sh, H=total_cyl, O=0.0).rotateY(90.0).translate((-total_cyl * 0.5, 0.0, 0.0))

    x_end = total_cyl * 0.5
    head_h = r_sh * 0.5
    o_hr = ELLIPSOIDHEAD(s, R=r_sh, H=head_h).rotateY(90.0).translate((x_end, 0.0, 0.0))
    o_hl = ELLIPSOIDHEAD(s, R=r_sh, H=head_h).rotateY(-90.0).translate((-x_end, 0.0, 0.0))
    o_ex.uniteWith(o_hr); o_hr.erase()
    o_ex.uniteWith(o_hl); o_hl.erase()

    # 2. 前后管板-管箱成对设备大法兰 (NB/T 47020) + 12 颗周向穿心紧固螺柱
    r_ts_fl = r_sh + 75.0
    w_ts_fl = 110.0
    r_bcd = r_sh + 42.0
    for sx in (-1.0, 1.0):
        xf = sx * L_SHELL * 0.5
        fl = CYLINDER(s, R=r_ts_fl, H=w_ts_fl, O=0.0).rotateY(90.0).translate((xf - w_ts_fl * 0.5, 0.0, 0.0))
        o_ex.uniteWith(fl); fl.erase()
        for i in range(12):
            ang = math.radians(i * 30.0 + 15.0)
            st = CYLINDER(s, R=12.0, H=w_ts_fl + 36.0, O=0.0).rotateY(90.0).translate((xf - (w_ts_fl + 36.0) * 0.5, r_bcd * math.cos(ang), r_bcd * math.sin(ang)))
            o_ex.uniteWith(st); st.erase()

    # 3. 两座 JB/T 4712 鞍式支座 (位于 x = ±L_SHELL * 0.34)
    w_sad = D_SHELL * 0.90
    l_sad = 160.0
    t_b = 20.0
    for sx in (-1.0, 1.0):
        xs = sx * L_SHELL * 0.34
        base = BOX(s, L=w_sad, W=t_b, H=l_sad).translate((xs, 0.0, -H_CENTER + t_b * 0.5))
        h_w = H_CENTER - t_b - r_sh * 0.3
        web = BOX(s, L=w_sad * 0.92, W=h_w, H=14.0).translate((xs, 0.0, -H_CENTER + t_b + h_w * 0.5))
        rib_l = BOX(s, L=14.0, W=h_w, H=l_sad * 0.85).translate((xs, -w_sad * 0.38, -H_CENTER + t_b + h_w * 0.5))
        rib_r = BOX(s, L=14.0, W=h_w, H=l_sad * 0.85).translate((xs, w_sad * 0.38, -H_CENTER + t_b + h_w * 0.5))
        o_ex.uniteWith(base); base.erase()
        o_ex.uniteWith(web); web.erase()
        o_ex.uniteWith(rib_l); rib_l.erase()
        o_ex.uniteWith(rib_r); rib_r.erase()

    # 4. 四个工艺法兰管口 (壳程上进下出 + 管程前下进后上出)
    z_sh_top = r_sh + 165.0
    z_sh_bot = -(r_sh + 165.0)
    z_tu_top = r_sh + 155.0
    z_tu_bot = -(r_sh + 155.0)
    x_s_in = -L_SHELL * 0.36
    x_s_out = L_SHELL * 0.36
    x_t_in = -(L_SHELL * 0.5 + L_CHAN * 0.52)
    x_t_out = L_SHELL * 0.5 + L_CHAN * 0.52

    for xp, zp, rn, is_top in (
        (x_s_in, z_sh_top, r_s_noz, True),
        (x_s_out, z_sh_bot, r_s_noz, False),
        (x_t_in, z_tu_bot, r_t_noz, False),
        (x_t_out, z_tu_top, r_t_noz, True),
    ):
        r_fl = rn + 48.0
        fl_t = 22.0
        z_cyl = (r_sh - 20.0) if is_top else zp
        z_fl = (zp - fl_t) if is_top else zp
        z_bore = (zp - 140.0) if is_top else (zp - 5.0)
        nc = CYLINDER(s, R=rn, H=abs(zp) - r_sh + 20.0, O=0.0).translate((xp, 0.0, z_cyl))
        nf = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).translate((xp, 0.0, z_fl))
        nb = CYLINDER(s, R=rn * 0.85, H=145.0, O=0.0).translate((xp, 0.0, z_bore))
        o_ex.uniteWith(nc); nc.erase()
        o_ex.uniteWith(nf); nf.erase()
        o_ex.subtractFrom(nb); nb.erase()

    s.setPoint((x_t_in, 0.0, z_tu_bot), (0.0, 0.0, -1.0))
    s.setPoint((x_t_out, 0.0, z_tu_top), (0.0, 0.0, 1.0))
    s.setPoint((x_s_in, 0.0, z_sh_top), (0.0, 0.0, 1.0))
    s.setPoint((x_s_out, 0.0, z_sh_bot), (0.0, 0.0, -1.0))

    s.setLinearDimension("L_SHELL", (-L_SHELL * 0.5, 0.0, r_ts_fl), (L_SHELL * 0.5, 0.0, r_ts_fl))
    s.setLinearDimension("H_CENTER", (-x_end, 0.0, -H_CENTER), (-x_end, 0.0, 0.0))
    s.setLinearDimension("D_SHELL", (-x_end - r_sh * 0.5, -r_sh, 0.0), (-x_end - r_sh * 0.5, r_sh, 0.0))
