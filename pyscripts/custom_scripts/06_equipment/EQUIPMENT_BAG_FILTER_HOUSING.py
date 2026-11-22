# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"立式多袋式精密过滤器",
    TooltipLong=u"化工液相精密过滤用立式快开多袋式过滤器 (符合 HG/T 21637，含圆筒滤筒、快开环首螺栓法兰顶盖、旋臂吊杆机构、顶排气压力表口、三脚圆管支腿与高低错位进出料法兰口)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D_BODY=LENGTH, TooltipShort=u"滤筒外径", TooltipLong=u"多袋式过滤器筒体外径 (mm)")
@param(H_SHELL=LENGTH, TooltipShort=u"滤筒高度", TooltipLong=u"滤筒直筒段高度 (mm)")
@param(H_LEGS=LENGTH, TooltipShort=u"支腿高度", TooltipLong=u"地面至下封头底部的支腿高度 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"进出口管径", TooltipLong=u"进出液法兰接管外径 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"进出液接管法兰外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"多袋式过滤器设备位号编码")
def EQUIPMENT_BAG_FILTER_HOUSING(s, D_BODY=600.0, H_SHELL=1050.0, H_LEGS=520.0, D_NOZ=114.3, FL_OD=220.0, ID=u"FL-101-4BAG", **kw):
    D_BODY = max(325.0, float(D_BODY))
    H_SHELL = max(650.0, float(H_SHELL))
    H_LEGS = max(320.0, float(H_LEGS))
    D_NOZ = max(48.0, float(D_NOZ))
    FL_OD = max(D_NOZ + 65.0, float(FL_OD))

    r_body = D_BODY / 2.0
    h_head = r_body * 0.5
    r_noz = D_NOZ / 2.0
    r_fl = FL_OD / 2.0
    t_fl = 22.0

    z_tan_bot = H_LEGS + h_head
    z_tan_top = z_tan_bot + H_SHELL

    # 1. 滤筒圆筒段 + 下椭圆形封头 + 底部排污管口 + 顶部快开大法兰与顶盖封头
    o_m = CYLINDER(s, R=r_body, H=H_SHELL, O=0.0).translate((0.0, 0.0, z_tan_bot))
    o_bot_hd = ELLIPSOIDHEAD(s, R=r_body, H=h_head).rotateY(180.0).translate((0.0, 0.0, z_tan_bot))
    o_drain = CYLINDER(s, R=32.0, H=90.0, O=0.0).translate((0.0, 0.0, H_LEGS - 70.0))
    o_top_fl = CYLINDER(s, R=r_body + 52.0, H=68.0, O=0.0).translate((0.0, 0.0, z_tan_top - 34.0))
    o_top_hd = ELLIPSOIDHEAD(s, R=r_body, H=h_head).translate((0.0, 0.0, z_tan_top + 34.0))
    o_vent = CYLINDER(s, R=28.0, H=85.0, O=0.0).translate((0.0, 0.0, z_tan_top + 34.0 + h_head - 15.0))
    for p in (o_bot_hd, o_drain, o_top_fl, o_top_hd, o_vent):
        o_m.uniteWith(p); p.erase()

    # 快开环首摇臂螺栓 (8组) + 侧向旋臂顶盖提升吊臂 (Davit Arm at +Y)
    for i in range(8):
        ang = math.radians(45.0 * i)
        eb = CYLINDER(s, R=12.0, H=95.0, O=0.0).translate(((r_body + 32.0) * math.cos(ang), (r_body + 32.0) * math.sin(ang), z_tan_top - 42.0))
        o_m.uniteWith(eb); eb.erase()

    h_dav = h_head + 210.0
    o_dav_post = CYLINDER(s, R=28.0, H=h_dav + 140.0, O=0.0).translate((0.0, r_body + 65.0, z_tan_top - 120.0))
    o_dav_arm = BOX(s, L=r_body + 80.0, W=36.0, H=36.0).translate((0.0, (r_body + 65.0) * 0.5, z_tan_top + h_dav))
    o_dav_lug = BOX(s, L=80.0, W=70.0, H=40.0).translate((0.0, r_body + 30.0, z_tan_top - 80.0))
    for p in (o_dav_post, o_dav_arm, o_dav_lug):
        o_m.uniteWith(p); p.erase()

    # 2. 3 根可调圆管支腿與圆形地脚垫板 (底面 Z=0)
    for i in range(3):
        ang_deg = 120.0 * i + 30.0
        ang_rad = math.radians(ang_deg)
        xl = (r_body - 10.0) * math.cos(ang_rad)
        yl = (r_body - 10.0) * math.sin(ang_rad)
        leg = CYLINDER(s, R=38.0, H=z_tan_bot + 120.0, O=0.0).translate((xl, yl, 16.0))
        bp = CYLINDER(s, R=78.0, H=16.0, O=0.0).translate((xl, yl, 0.0))
        o_m.uniteWith(leg); leg.erase()
        o_m.uniteWith(bp); bp.erase()

    # 3. 高位进液法兰管口 (Port 1 at -X) 与低位出液法兰管口 (Port 2 at +X)
    ext_x = r_body + 180.0
    z_in = z_tan_bot + H_SHELL * 0.78
    z_out = z_tan_bot + H_SHELL * 0.22
    n_in = CYLINDER(s, R=r_noz, H=ext_x, O=0.0).rotateY(-90.0).translate((0.0, 0.0, z_in))
    f_in = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).rotateY(-90.0).translate((-(ext_x - t_fl), 0.0, z_in))
    n_out = CYLINDER(s, R=r_noz, H=ext_x, O=0.0).rotateY(90.0).translate((0.0, 0.0, z_out))
    f_out = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).rotateY(90.0).translate((ext_x - t_fl, 0.0, z_out))
    for p in (n_in, f_in, n_out, f_out):
        o_m.uniteWith(p); p.erase()

    s.setPoint((-ext_x, 0.0, z_in), (-1.0, 0.0, 0.0))
    s.setPoint((ext_x, 0.0, z_out), (1.0, 0.0, 0.0))
    s.setLinearDimension("D_BODY", (-r_body, 0.0, z_tan_bot), (r_body, 0.0, z_tan_bot))
    s.setLinearDimension("H_SHELL", (r_body, 0.0, z_tan_bot), (r_body, 0.0, z_tan_top))
    s.setLinearDimension("H_LEGS", (-r_body, 0.0, 0.0), (-r_body, 0.0, H_LEGS))
