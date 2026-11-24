# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="3",
    TooltipShort=u"立式平底锥顶常压储罐",
    TooltipLong=u"化工罐区立式圆筒形平底固定锥顶常压储罐 (符合 GB 50341 / API 650 / HG/T 21502，含边缘环形底板、带抗风圈罐壁筒体、罐顶环形安全栏杆、侧向护笼爬梯、消防泡沫室鹅颈管、自支承锥顶与下部进出料口)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D_TANK=LENGTH, TooltipShort=u"储罐直径", TooltipLong=u"储罐圆筒壁板公称外径 (mm)")
@param(H_WALL=LENGTH, TooltipShort=u"罐壁高度", TooltipLong=u"储罐底板顶面至罐壁上沿的高度 (mm)")
@param(H_ROOF=LENGTH, TooltipShort=u"锥顶高度", TooltipLong=u"圆锥形固定罐顶中心拱高 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"进出料管径", TooltipLong=u"下部侧向进出料管口外径 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"进出料管口法兰外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"储罐位号", TooltipLong=u"常压储罐设备位号与容积编码")
def EQUIPMENT_CONICAL_STORAGE_TANK(s, D_TANK=2600.0, H_WALL=2800.0, H_ROOF=480.0, D_NOZ=168.3, FL_OD=285.0, ID=u"V-201-15m3", **kw):
    D_TANK = max(1000.0, float(D_TANK))
    H_WALL = max(1200.0, float(H_WALL))
    H_ROOF = max(220.0, float(H_ROOF))
    D_NOZ = max(60.3, float(D_NOZ))
    FL_OD = max(D_NOZ + 75.0, float(FL_OD))

    r_tank = D_TANK / 2.0
    r_noz = D_NOZ / 2.0
    r_fl = FL_OD / 2.0
    t_base = 24.0
    t_fl = 24.0

    # 1. 底部边缘环形底板 + 地脚抗风锚固座 (8个) + 主圆筒罐壁 + 抗风圈
    o_m = CYLINDER(s, R=r_tank + 75.0, H=t_base, O=0.0)
    o_wall = CYLINDER(s, R=r_tank, H=H_WALL, O=0.0).translate((0.0, 0.0, t_base))
    o_wind = CYLINDER(s, R=r_tank + 65.0, H=32.0, O=0.0).translate((0.0, 0.0, t_base + H_WALL * 0.82))
    o_curb = CYLINDER(s, R=r_tank + 45.0, H=32.0, O=0.0).translate((0.0, 0.0, t_base + H_WALL - 30.0))
    for p in (o_wall, o_wind, o_curb):
        o_m.uniteWith(p); p.erase()

    for i in range(8):
        ang = 45.0 * i
        chair = BOX(s, L=65.0, W=140.0, H=90.0).translate((r_tank + 25.0, 0.0, t_base + 70.0)).rotateZ(ang)
        o_m.uniteWith(chair); chair.erase()

    # 2. 自支承圆锥形罐顶 + 罐顶周向安全栏杆环 + 顶部中心呼吸阀安装管口 (Port 3)
    z_roof_base = t_base + H_WALL
    o_roof = CONE(s, R1=r_tank + 40.0, R2=r_fl * 1.15, H=H_ROOF, E=0.0).translate((0.0, 0.0, z_roof_base))
    o_rail_top = TORUS(s, R1=r_tank + 20.0, R2=18.0).translate((0.0, 0.0, z_roof_base + 220.0))
    o_rail_mid = TORUS(s, R1=r_tank + 20.0, R2=14.0).translate((0.0, 0.0, z_roof_base + 110.0))
    z_top_port = z_roof_base + H_ROOF + 160.0
    n_top = CYLINDER(s, R=r_noz, H=220.0, O=0.0).translate((0.0, 0.0, z_roof_base + H_ROOF - 60.0))
    f_top = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((0.0, 0.0, z_top_port - t_fl))
    for p in (o_roof, o_rail_top, o_rail_mid, n_top, f_top):
        o_m.uniteWith(p); p.erase()

    for i in range(12):
        ang_rad = math.radians(30.0 * i)
        post = CYLINDER(s, R=16.0, H=235.0, O=0.0).translate(((r_tank + 20.0) * math.cos(ang_rad), (r_tank + 20.0) * math.sin(ang_rad), z_roof_base - 10.0))
        o_m.uniteWith(post); post.erase()

    # 罐壁外侧直爬梯与安全护笼 (-Y 侧) + 罐顶量油孔/透光孔 + 下部罐壁人孔 (+Y 侧)
    y_lad = -(r_tank + 110.0)
    for sx in (-110.0, 110.0):
        rail = CYLINDER(s, R=16.0, H=H_WALL + 220.0, O=0.0).translate((sx, y_lad, t_base))
        o_m.uniteWith(rail); rail.erase()
    for zf in (0.18, 0.36, 0.54, 0.72, 0.90):
        zn = t_base + H_WALL * zf
        hoop = CYLINDER(s, R=175.0, H=22.0, O=145.0).translate((0.0, y_lad - 45.0, zn))
        brk = BOX(s, L=140.0, W=24.0, H=240.0).translate((0.0, -(r_tank + 55.0), zn))
        o_m.uniteWith(hoop); hoop.erase()
        o_m.uniteWith(brk); brk.erase()

    o_sky = CYLINDER(s, R=240.0, H=180.0, O=0.0).translate((0.0, r_tank * 0.55, z_roof_base + H_ROOF * 0.35))
    o_sky_fl = CYLINDER(s, R=295.0, H=24.0, O=0.0).translate((0.0, r_tank * 0.55, z_roof_base + H_ROOF * 0.35 + 160.0))
    o_mh = CYLINDER(s, R=280.0, H=r_tank + 220.0, O=0.0).rotateX(-90.0).translate((0.0, 0.0, t_base + 520.0))
    o_mh_fl = CYLINDER(s, R=350.0, H=36.0, O=0.0).rotateX(-90.0).translate((0.0, r_tank + 190.0, t_base + 520.0))
    for p in (o_sky, o_sky_fl, o_mh, o_mh_fl):
        o_m.uniteWith(p); p.erase()

    # 3. 两侧下部进出料法兰管口 (Port 1 at -X, Port 2 at +X)
    ext_x = r_tank + 220.0
    z_noz1 = t_base + 320.0
    z_noz2 = t_base + 320.0
    n1 = CYLINDER(s, R=r_noz, H=ext_x, O=0.0).rotateY(-90.0).translate((0.0, 0.0, z_noz1))
    f1 = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).rotateY(-90.0).translate((-(ext_x - t_fl), 0.0, z_noz1))
    n2 = CYLINDER(s, R=r_noz, H=ext_x, O=0.0).rotateY(90.0).translate((0.0, 0.0, z_noz2))
    f2 = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).rotateY(90.0).translate((ext_x - t_fl, 0.0, z_noz2))
    for p in (n1, f1, n2, f2):
        o_m.uniteWith(p); p.erase()

    s.setPoint((-ext_x, 0.0, z_noz1), (-1.0, 0.0, 0.0))
    s.setPoint((ext_x, 0.0, z_noz2), (1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, z_top_port), (0.0, 0.0, 1.0))
    s.setLinearDimension("D_TANK", (-r_tank, 0.0, t_base), (r_tank, 0.0, t_base))
    s.setLinearDimension("H_WALL", (r_tank, 0.0, t_base), (r_tank, 0.0, z_roof_base))
    s.setLinearDimension("H_ROOF", (0.0, 0.0, z_roof_base), (0.0, 0.0, z_roof_base + H_ROOF))
