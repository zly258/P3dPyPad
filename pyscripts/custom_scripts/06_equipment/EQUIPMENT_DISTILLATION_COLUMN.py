# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="3",
    TooltipShort=u"化工板式填料精馏塔器",
    TooltipLong=u"化工装置立式裙座支承精馏塔/吸收塔设备 (符合 NB/T 47041 / HG/T 20592，含喇叭形裙座与检查人孔、双层环形操作平台与护栏、上下椭圆形封头、分段塔盘加强圈、双人孔与进出料口)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D_BODY=LENGTH, TooltipShort=u"塔体外径", TooltipLong=u"精馏塔圆筒壳体公称外径 (mm)")
@param(H_SHELL=LENGTH, TooltipShort=u"直筒段高", TooltipLong=u"塔体上下切线间直筒段高度 (mm)")
@param(H_SKIRT=LENGTH, TooltipShort=u"裙座高度", TooltipLong=u"地面基础面至下封头切线的裙座高度 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"进出料管径", TooltipLong=u"主要工艺进出料管口外径 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"管口法兰径", TooltipLong=u"工艺管口配对法兰外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"精馏塔设备位号与规格编码")
def EQUIPMENT_DISTILLATION_COLUMN(s, D_BODY=1600.0, H_SHELL=4800.0, H_SKIRT=1400.0, D_NOZ=219.1, FL_OD=340.0, ID=u"T-101-DN1600", **kw):
    D_BODY = max(600.0, float(D_BODY))
    H_SHELL = max(2000.0, float(H_SHELL))
    H_SKIRT = max(800.0, float(H_SKIRT))
    D_NOZ = max(88.9, float(D_NOZ))
    FL_OD = max(D_NOZ + 80.0, float(FL_OD))

    r_body = D_BODY / 2.0
    h_head = r_body * 0.5
    r_noz = D_NOZ / 2.0
    r_fl = FL_OD / 2.0
    t_fl = 28.0

    # 1. 底部微锥形裙座 + 地脚螺栓基础环板 + 裙座检查人孔圈 (+Y)
    r_skirt_bot = r_body * 1.06
    t_base = 36.0
    o_m = CYLINDER(s, R=r_skirt_bot + 95.0, H=t_base, O=0.0)
    o_chair = CYLINDER(s, R=r_skirt_bot + 75.0, H=160.0, O=r_skirt_bot - 10.0).translate((0.0, 0.0, t_base))
    o_skirt = CONE(s, R1=r_skirt_bot, R2=r_body, H=H_SKIRT, E=0.0).translate((0.0, 0.0, t_base))
    o_sk_mh = CYLINDER(s, R=240.0, H=r_skirt_bot + 90.0, O=0.0).rotateX(-90.0).translate((0.0, 0.0, H_SKIRT * 0.48))
    for p in (o_chair, o_skirt, o_sk_mh):
        o_m.uniteWith(p); p.erase()

    for i in range(12):
        ang = 30.0 * i
        rib = BOX(s, L=18.0, W=160.0, H=85.0).translate((r_skirt_bot + 40.0, 0.0, t_base + 80.0)).rotateZ(ang)
        o_m.uniteWith(rib); rib.erase()

    # 2. 主塔体直筒段 + 上下 2:1 椭圆形封头 + 分段加强圈 + 两层环形操作平台托架
    z_tan_bot = H_SKIRT
    z_tan_top = H_SKIRT + H_SHELL
    o_shell = CYLINDER(s, R=r_body, H=H_SHELL, O=0.0).translate((0.0, 0.0, z_tan_bot))
    o_head_top = ELLIPSOIDHEAD(s, R=r_body, H=h_head).translate((0.0, 0.0, z_tan_top))
    o_head_bot = ELLIPSOIDHEAD(s, R=r_body, H=h_head).rotateY(180.0).translate((0.0, 0.0, z_tan_bot))
    for p in (o_shell, o_head_top, o_head_bot):
        o_m.uniteWith(p); p.erase()

    for frac in (0.20, 0.40, 0.60, 0.80):
        zr = z_tan_bot + H_SHELL * frac
        ring = CYLINDER(s, R=r_body + 48.0, H=28.0, O=0.0).translate((0.0, 0.0, zr - 14.0))
        o_m.uniteWith(ring); ring.erase()

    # 两层半圆弧形检修平台与栏杆环 (位于人孔下方)
    for frac in (0.16, 0.66):
        zp = z_tan_bot + H_SHELL * frac
        plat = CYLINDER(s, R=r_body + 360.0, H=32.0, O=r_body - 10.0).translate((0.0, 0.0, zp))
        cut_p = BOX(s, L=(r_body + 400.0) * 1.2, W=80.0, H=(r_body + 400.0) * 2.2).translate((0.0, -(r_body + 400.0) * 0.55, zp + 16.0))
        plat.subtractFrom(cut_p); cut_p.erase()
        o_m.uniteWith(plat); plat.erase()

    # 3. 2 个带回转盖铰链的侧向人孔 (+Y 方向 DN500)
    for frac in (0.24, 0.74):
        zm = z_tan_bot + H_SHELL * frac
        mh_n = CYLINDER(s, R=265.0, H=r_body + 240.0, O=0.0).rotateX(-90.0).translate((0.0, 0.0, zm))
        mh_f = CYLINDER(s, R=335.0, H=32.0, O=0.0).rotateX(-90.0).translate((0.0, r_body + 210.0, zm))
        mh_c = CYLINDER(s, R=335.0, H=28.0, O=0.0).rotateX(-90.0).translate((0.0, r_body + 242.0, zm))
        for p in (mh_n, mh_f, mh_c):
            o_m.uniteWith(p); p.erase()

    # 4. 工艺管口: Port 1 中部进料口 (-X), Port 2 塔顶气相出料口 (+Z), Port 3 下部回流/塔釜采出口 (+X)
    ext_noz = r_body + 260.0
    z_feed = z_tan_bot + H_SHELL * 0.48
    n_feed = CYLINDER(s, R=r_noz, H=ext_noz, O=0.0).rotateY(-90.0).translate((0.0, 0.0, z_feed))
    f_feed = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).rotateY(-90.0).translate((-(ext_noz - t_fl), 0.0, z_feed))

    z_top_port = z_tan_top + h_head + 220.0
    n_top = CYLINDER(s, R=r_noz, H=h_head + 260.0, O=0.0).translate((0.0, 0.0, z_tan_top - 40.0))
    f_top = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((0.0, 0.0, z_top_port - t_fl))

    z_bot_port = z_tan_bot + H_SHELL * 0.10
    n_bot = CYLINDER(s, R=r_noz, H=ext_noz, O=0.0).rotateY(90.0).translate((0.0, 0.0, z_bot_port))
    f_bot = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).rotateY(90.0).translate((ext_noz - t_fl, 0.0, z_bot_port))

    z_ref = z_tan_bot + H_SHELL * 0.88
    n_ref = CYLINDER(s, R=r_noz * 0.8, H=ext_noz, O=0.0).rotateY(90.0).translate((0.0, 0.0, z_ref))
    f_ref = CYLINDER(s, R=r_fl * 0.85, H=t_fl, O=0.0).rotateY(90.0).translate((ext_noz - t_fl, 0.0, z_ref))

    for p in (n_feed, f_feed, n_top, f_top, n_bot, f_bot, n_ref, f_ref):
        o_m.uniteWith(p); p.erase()

    s.setPoint((-ext_noz, 0.0, z_feed), (-1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, z_top_port), (0.0, 0.0, 1.0))
    s.setPoint((ext_noz, 0.0, z_bot_port), (1.0, 0.0, 0.0))
    s.setLinearDimension("D_BODY", (-r_body, 0.0, z_tan_bot), (r_body, 0.0, z_tan_bot))
    s.setLinearDimension("H_SHELL", (r_body, 0.0, z_tan_bot), (r_body, 0.0, z_tan_top))
    s.setLinearDimension("H_SKIRT", (-r_body, 0.0, 0.0), (-r_body, 0.0, z_tan_bot))
