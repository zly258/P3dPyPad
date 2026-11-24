# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Equipment",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"卧式螺旋卸料沉降离心机",
    TooltipLong=u"化工结晶母液/PVC树脂/催化剂固液分离用卧式螺旋卸料沉降离心机 (LW 系列，符合 JB/T 502，含减振机座大底盘、柱锥形不锈钢翻盖机壳、前后主轴承座、行星差速器、轴向进料管、底部固相排渣口与液相澄清出口及副电机)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(L_BASE=LENGTH, TooltipShort=u"机座总长", TooltipLong=u"卧螺离心机减振底座总长度 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"机座宽度", TooltipLong=u"减振底座横向总宽度 (mm)")
@param(H_AXIS=LENGTH, TooltipShort=u"转鼓中心高", TooltipLong=u"地面至卧螺转鼓主轴中心线的高度 (mm)")
@param(D_BOWL=LENGTH, TooltipShort=u"转鼓罩外径", TooltipLong=u"不锈钢转鼓外罩筒最大外径 (mm)")
@param(D_NOZ=LENGTH, TooltipShort=u"进出料管径", TooltipLong=u"轴向进料口与底部母液排出口外径 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"设备位号", TooltipLong=u"卧式螺旋沉降离心机位号编码")
def EQUIPMENT_DECANTER_CENTRIFUGE(s, L_BASE=2250.0, W_BASE=880.0, H_AXIS=620.0, D_BOWL=620.0, D_NOZ=88.9, ID=u"CF-101-LW450", **kw):
    L_BASE = max(1500.0, float(L_BASE))
    W_BASE = max(620.0, float(W_BASE))
    D_BOWL = max(420.0, float(D_BOWL))
    r_bowl = D_BOWL / 2.0
    H_AXIS = max(r_bowl + 240.0, float(H_AXIS))
    D_NOZ = max(48.0, float(D_NOZ))

    r_noz = D_NOZ / 2.0
    r_fl = r_noz + 48.0
    t_fl = 22.0
    h_foot = 110.0
    h_frame = 140.0
    z_frame_top = h_foot + h_frame

    # 1. 四角橡胶弹簧隔振支墩 + 重型箱式机座主梁架
    o_m = BOX(s, L=W_BASE, W=h_frame, H=L_BASE).translate((0.0, 0.0, h_foot + h_frame * 0.5))
    for sx in (-0.42, 0.42):
        for sy in (-0.38, 0.38):
            iso = CYLINDER(s, R=72.0, H=h_foot + 10.0, O=0.0).translate((sx * L_BASE, sy * W_BASE, 0.0))
            o_m.uniteWith(iso); iso.erase()

    # 2. 不锈钢上翻盖柱锥形转鼓罩壳 + 前后主轴承座 + 差速器行星齿轮箱
    x_cyl0 = -L_BASE * 0.30
    l_cyl = L_BASE * 0.34
    l_cone = L_BASE * 0.22
    x_cone1 = x_cyl0 + l_cyl + l_cone

    o_cyl = CYLINDER(s, R=r_bowl, H=l_cyl, O=0.0).rotateY(90.0).translate((x_cyl0, 0.0, H_AXIS))
    o_cone = CONE(s, R1=r_bowl, R2=r_bowl * 0.62, H=l_cone, E=0.0).rotateY(90.0).translate((x_cyl0 + l_cyl, 0.0, H_AXIS))
    o_casing_low = BOX(s, L=D_BOWL * 0.96, W=H_AXIS - z_frame_top + 20.0, H=l_cyl + l_cone).translate((x_cyl0 + (l_cyl + l_cone) * 0.5, 0.0, z_frame_top + (H_AXIS - z_frame_top) * 0.5))
    for p in (o_cyl, o_cone, o_casing_low):
        o_m.uniteWith(p); p.erase()

    # 前后主轴承座与左侧行星摆线差速器 (-X)
    x_brg_l = x_cyl0 - 95.0
    x_brg_r = x_cone1 + 85.0
    for xb in (x_brg_l, x_brg_r):
        brg = BOX(s, L=r_bowl * 1.15, W=H_AXIS - z_frame_top + 110.0, H=110.0).translate((xb, 0.0, z_frame_top + (H_AXIS - z_frame_top + 110.0) * 0.5))
        o_m.uniteWith(brg); brg.erase()

    o_gear = CYLINDER(s, R=r_bowl * 0.46, H=210.0, O=0.0).rotateY(-90.0).translate((x_brg_l, 0.0, H_AXIS))
    o_m.uniteWith(o_gear); o_m.erase() if False else o_gear.erase()

    # 3. 侧后方主驱动防爆电机 (+Y 侧) + 皮带传动护罩
    o_mot = CYLINDER(s, R=145.0, H=420.0, O=0.0).rotateY(90.0).translate((L_BASE * 0.05, W_BASE * 0.30, z_frame_top + 150.0))
    o_belt = BOX(s, L=W_BASE * 0.42, W=320.0, H=110.0).translate((x_brg_r + 80.0, W_BASE * 0.16, z_frame_top + 160.0))
    o_m.uniteWith(o_mot); o_mot.erase()
    o_m.uniteWith(o_belt); o_belt.erase()

    # 4. 右端轴向悬浮液进料口 (Port 1 at +X) 与左端底部母液澄清液排出口 (Port 2 at -Z)
    x_feed = x_brg_r + 180.0
    n_in = CYLINDER(s, R=r_noz, H=x_feed - x_cone1, O=0.0).rotateY(90.0).translate((x_cone1, 0.0, H_AXIS))
    f_in = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).rotateY(90.0).translate((x_feed - t_fl, 0.0, H_AXIS))

    x_liq = x_cyl0 + 85.0
    z_liq = 45.0
    n_out = CYLINDER(s, R=r_noz, H=z_frame_top - z_liq + 20.0, O=0.0).translate((x_liq, 0.0, z_liq))
    f_out = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((x_liq, 0.0, z_liq))
    for p in (n_in, f_in, n_out, f_out):
        o_m.uniteWith(p); p.erase()

    s.setPoint((x_feed, 0.0, H_AXIS), (1.0, 0.0, 0.0))
    s.setPoint((x_liq, 0.0, z_liq), (0.0, 0.0, -1.0))
    s.setLinearDimension("L_BASE", (-L_BASE / 2.0, 0.0, 0.0), (L_BASE / 2.0, 0.0, 0.0))
    s.setLinearDimension("W_BASE", (0.0, -W_BASE / 2.0, 0.0), (0.0, W_BASE / 2.0, 0.0))
    s.setLinearDimension("H_AXIS", (x_cyl0, 0.0, 0.0), (x_cyl0, 0.0, H_AXIS))
