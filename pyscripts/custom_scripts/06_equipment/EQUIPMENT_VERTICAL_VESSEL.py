# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="3",
    TooltipShort=u"立式裙座化工工艺容器",
    TooltipLong=u"化工装置立式裙座支承气液分离罐/回流罐/缓冲容器 (符合 NB/T 47041，含带地脚螺栓座的圆筒裙座、裙座检查孔、上下椭球封头、侧向带旋臂吊杆人孔、液位计上下法兰口与工艺进出料口)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D_BODY=LENGTH, TooltipShort=u"筒体外径", TooltipLong=u"立式容器圆筒壳体公称外径 (mm)")
@param(H_SHELL=LENGTH, TooltipShort=u"直筒高度", TooltipLong=u"上下封头切线间直筒高度 (mm)")
@param(H_SKIRT=LENGTH, TooltipShort=u"裙座高度", TooltipLong=u"基础面至下封头切线的裙座高度 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"进出料管径", TooltipLong=u"主工艺进出料法兰管口外径 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"管口法兰径", TooltipLong=u"主工艺管口配对法兰外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"立式工艺容器位号编码")
def EQUIPMENT_VERTICAL_VESSEL(s, D_BODY=800.0, H_SHELL=1400.0, H_SKIRT=600.0, D_NOZ=88.9, FL_OD=200.0, ID=u"V-102-DN800", **kw):
    D_BODY = max(400.0, float(D_BODY))
    H_SHELL = max(800.0, float(H_SHELL))
    H_SKIRT = max(400.0, float(H_SKIRT))
    D_NOZ = max(42.0, float(D_NOZ))
    FL_OD = max(D_NOZ + 65.0, float(FL_OD))

    r_body = D_BODY / 2.0
    h_head = r_body * 0.5
    r_noz = D_NOZ / 2.0
    r_fl = FL_OD / 2.0
    t_base = 24.0
    t_fl = 22.0

    z_tan_bot = H_SKIRT
    z_tan_top = H_SKIRT + H_SHELL

    # 1. 裙座基础环板 + 地脚筋板 + 裙座圆筒 + 主容器筒体 + 上下标准椭球封头
    o_m = CYLINDER(s, R=r_body + 65.0, H=t_base, O=0.0)
    o_skirt = CYLINDER(s, R=r_body, H=H_SKIRT + H_SHELL, O=0.0).translate((0.0, 0.0, t_base))
    o_top_hd = ELLIPSOIDHEAD(s, R=r_body, H=h_head).translate((0.0, 0.0, z_tan_top))
    o_bot_hd = ELLIPSOIDHEAD(s, R=r_body, H=h_head).rotateY(180.0).translate((0.0, 0.0, z_tan_bot))
    o_weld_ring = CYLINDER(s, R=r_body + 16.0, H=24.0, O=0.0).translate((0.0, 0.0, z_tan_bot - 12.0))
    for p in (o_skirt, o_top_hd, o_bot_hd, o_weld_ring):
        o_m.uniteWith(p); p.erase()

    for i in range(8):
        ang = 45.0 * i
        rib = BOX(s, L=14.0, W=110.0, H=65.0).translate((r_body + 25.0, 0.0, t_base + 55.0)).rotateZ(ang)
        o_m.uniteWith(rib); rib.erase()

    # 2. 侧向人孔 (+Y) 与侧向磁翻板液位计上下配对法兰管嘴 (-Y)
    zm = z_tan_bot + H_SHELL * 0.45
    o_mh = CYLINDER(s, R=180.0, H=r_body + 140.0, O=0.0).rotateX(-90.0).translate((0.0, 0.0, zm))
    o_mfl = CYLINDER(s, R=235.0, H=38.0, O=0.0).rotateX(-90.0).translate((0.0, r_body + 115.0, zm))
    o_m.uniteWith(o_mh); o_mh.erase()
    o_m.uniteWith(o_mfl); o_mfl.erase()

    for zf in (0.22, 0.78):
        zl = z_tan_bot + H_SHELL * zf
        ln = CYLINDER(s, R=24.0, H=r_body + 110.0, O=0.0).rotateX(90.0).translate((0.0, 0.0, zl))
        lf = CYLINDER(s, R=58.0, H=18.0, O=0.0).rotateX(90.0).translate((0.0, -(r_body + 92.0), zl))
        o_m.uniteWith(ln); ln.erase()
        o_m.uniteWith(lf); lf.erase()

    # 3. 三个主工艺端口: Port 1 进料 (-X, 上部), Port 2 气相出口 (+Z, 顶部), Port 3 液相出口 (+X, 下部)
    ext_x = r_body + 140.0
    z_in = z_tan_bot + H_SHELL * 0.72
    z_out = z_tan_bot + H_SHELL * 0.22
    z_top = z_tan_top + h_head + 125.0

    n_in = CYLINDER(s, R=r_noz, H=ext_x, O=0.0).rotateY(-90.0).translate((0.0, 0.0, z_in))
    f_in = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).rotateY(-90.0).translate((-(ext_x - t_fl), 0.0, z_in))
    n_out = CYLINDER(s, R=r_noz, H=ext_x, O=0.0).rotateY(90.0).translate((0.0, 0.0, z_out))
    f_out = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).rotateY(90.0).translate((ext_x - t_fl, 0.0, z_out))
    n_top = CYLINDER(s, R=r_noz, H=h_head + 160.0, O=0.0).translate((0.0, 0.0, z_tan_top - 35.0))
    f_top = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((0.0, 0.0, z_top - t_fl))
    for p in (n_in, f_in, n_out, f_out, n_top, f_top):
        o_m.uniteWith(p); p.erase()

    s.setPoint((-ext_x, 0.0, z_in), (-1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, z_top), (0.0, 0.0, 1.0))
    s.setPoint((ext_x, 0.0, z_out), (1.0, 0.0, 0.0))
    s.setLinearDimension("D_BODY", (-r_body, 0.0, z_tan_bot), (r_body, 0.0, z_tan_bot))
    s.setLinearDimension("H_SHELL", (r_body, 0.0, z_tan_bot), (r_body, 0.0, z_tan_top))
    s.setLinearDimension("H_SKIRT", (-r_body, 0.0, 0.0), (-r_body, 0.0, z_tan_bot))
