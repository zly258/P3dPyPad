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

@activate(Group="Valve", Ports=2, TooltipShort=u"蜗轮传动双法兰蝶阀 (D341H / API 609)", TooltipLong=u"化工标准 GB/T 12238 / API 609 蜗轮蜗杆传动双法兰/凸耳式蝶阀 (Gear-Operated Butterfly Valve)，带薄型阀体、微开蝶板、加长保温颈、蜗轮减速箱与侧向手轮", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"阀门主要结构尺寸：结构长度、中心高与法兰规格")
@param(D=LENGTH, TooltipShort=u"管道外径 OD", Ask4Dist=True, TooltipLong=u"管道外径 OD")
@param(L=LENGTH, TooltipShort=u"蝶阀结构长度 L", Ask4Dist=True, TooltipLong=u"蝶阀结构长度 L")
@param(H1=LENGTH, TooltipShort=u"底部轴座长 H1", TooltipLong=u"底部轴座长 H1")
@param(H2=LENGTH, TooltipShort=u"中心至蜗轮箱高 H2", Ask4Dist=True, TooltipLong=u"中心至蜗轮箱高 H2")
@param(W_DIA=LENGTH, TooltipShort=u"侧向手轮外径", TooltipLong=u"侧向手轮外径")
@param(FL_OD=LENGTH, TooltipShort=u"外缘法兰外径", TooltipLong=u"法兰密封面外圆直径")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓孔数", TooltipLong=u"法兰螺栓孔总数，需与法兰外径/厚度配套")
@param(ID=STRING, TooltipShort=u"阀门位号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def VALVE_BUTTERFLY(s, D=219.1, L=152.0, H1=195.0, H2=310.0, W_DIA=220.0, FL_OD=340.0, NBOLTS=12, ID="D341H-16C", **kw):
    D = max(50.0, float(D))
    L = max(46.0, float(L))
    H1 = max(D * 0.65, float(H1))
    H2 = max(D * 0.95, float(H2))
    W_DIA = max(120.0, float(W_DIA))
    FL_OD = max(D + 70.0, float(FL_OD))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.90
    r_fl = FL_OD / 2.0
    fl_t = max(18.0, L * 0.22)

    # 1. 窄型双法兰阀体 (两端法兰盘 + 中间腰形凹槽短筒)
    o_valve = CYLINDER(s, R=r_pipe * 1.15, H=L, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    o_valve.uniteWith(fl_l); fl_l.erase()
    fl_r = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).rotateY(90.0).translate((L * 0.5 - fl_t, 0.0, 0.0))
    o_valve.uniteWith(fl_r); fl_r.erase()

    # 钻削两端法兰螺栓通孔并挖出流道孔
    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_valve.subtractFrom(o_bore); o_bore.erase()
    r_bcd = r_pipe + (r_fl - r_pipe) * 0.66
    r_hole = max(6.0, min(14.0, (r_fl - r_pipe) * 0.15))
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        by, bz = r_bcd * math.cos(ang), r_bcd * math.sin(ang)
        hl = CYLINDER(s, R=r_hole, H=fl_t + 6.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 2.0), by, bz))
        o_valve.subtractFrom(hl); hl.erase()
        hr = CYLINDER(s, R=r_hole, H=fl_t + 6.0, O=0.0).rotateY(90.0).translate((L * 0.5 - fl_t - 4.0, by, bz))
        o_valve.subtractFrom(hr); hr.erase()

    # 2. 通道内部真实蝶板 (微开 28° 倾斜圆盘 + 中心立轴加强筋毂，从四视图均清晰可见)
    disc_t = max(12.0, r_bore * 0.14)
    o_disc = CYLINDER(s, R=r_bore * 0.94, H=disc_t, O=0.0).rotateY(90.0).translate((-disc_t * 0.5, 0.0, 0.0)).rotateZ(28.0)
    o_valve.uniteWith(o_disc); o_disc.erase()
    o_shaft_in = CYLINDER(s, R=max(10.0, r_bore * 0.16), H=2.0 * r_bore + 20.0, O=0.0).translate((0.0, 0.0, -(r_bore + 10.0)))
    o_valve.uniteWith(o_shaft_in); o_shaft_in.erase()

    # 3. 底部下轴座盲盖 (Bottom Trunnion Boss) + 顶部加长保温脖颈 (Extended Neck)
    r_neck = max(24.0, r_pipe * 0.32)
    o_bot_boss = CYLINDER(s, R=r_neck * 0.92, H=H1 - r_pipe, O=0.0).translate((0.0, 0.0, -H1))
    o_valve.uniteWith(o_bot_boss); o_bot_boss.erase()
    o_bot_cap = CYLINDER(s, R=r_neck * 1.25, H=14.0, O=0.0).translate((0.0, 0.0, -H1))
    o_valve.uniteWith(o_bot_cap); o_bot_cap.erase()

    z_gear_bot = H2 - 36.0
    o_top_neck = CYLINDER(s, R=r_neck, H=z_gear_bot - r_pipe + 10.0, O=0.0).translate((0.0, 0.0, r_pipe - 10.0))
    o_valve.uniteWith(o_top_neck); o_top_neck.erase()
    o_top_fl = CYLINDER(s, R=r_neck * 1.55, H=14.0, O=0.0).translate((0.0, 0.0, z_gear_bot - 14.0))
    o_valve.uniteWith(o_top_fl); o_top_fl.erase()

    # 4. 顶部蜗轮减速箱体 (Worm-Gear Operator Box) + 顶部开度指示圆盘
    r_gear = max(55.0, r_neck * 2.15)
    h_gear = 68.0
    o_gear = CYLINDER(s, R=r_gear, H=h_gear, O=0.0).translate((0.0, 0.0, z_gear_bot))
    o_valve.uniteWith(o_gear); o_gear.erase()
    o_worm_housing = BOX(s, L=r_gear * 1.6, W=h_gear * 0.82, H=r_gear * 1.35).translate((-r_gear * 0.45, -r_gear * 0.35, z_gear_bot + h_gear * 0.5))
    o_valve.uniteWith(o_worm_housing); o_worm_housing.erase()
    o_ind = CYLINDER(s, R=r_gear * 0.52, H=12.0, O=0.0).translate((0.0, 0.0, z_gear_bot + h_gear))
    o_valve.uniteWith(o_ind); o_ind.erase()

    # 5. 侧向水平蜗杆输入轴 (沿 -Y 伸出) + 侧向竖直手轮 (位于 XZ 平面)
    z_shaft = z_gear_bot + h_gear * 0.5
    x_shaft = -r_gear * 0.55
    y_hw = -(r_gear + 85.0)
    o_in_shaft = CYLINDER(s, R=12.0, H=abs(y_hw) + 10.0, O=0.0).rotateX(90.0).translate((x_shaft, 0.0, z_shaft))
    o_valve.uniteWith(o_in_shaft); o_in_shaft.erase()

    r_hw = W_DIA / 2.0
    r_rim = max(6.5, W_DIA * 0.042)
    o_rim = TORUS(s, R1=r_hw - r_rim, R2=r_rim, A=360.0).rotateX(90.0).translate((x_shaft, y_hw, z_shaft))
    o_valve.uniteWith(o_rim); o_rim.erase()
    o_hw_hub = CYLINDER(s, R=24.0, H=24.0, O=0.0).rotateX(90.0).translate((x_shaft, y_hw + 12.0, z_shaft))
    o_valve.uniteWith(o_hw_hub); o_hw_hub.erase()
    for ang_deg in (0.0, 90.0, 180.0, 270.0):
        ang_rad = math.radians(ang_deg)
        sp_len = r_hw - r_rim - 18.0
        rm = 18.0 + sp_len * 0.5
        sp = CYLINDER(s, R=r_rim * 0.62, H=sp_len, O=0.0).translate((0.0, 0.0, -sp_len * 0.5)).rotateY(ang_deg)
        sp.translate((x_shaft + rm * math.sin(ang_rad), y_hw, z_shaft + rm * math.cos(ang_rad)))
        o_valve.uniteWith(sp); sp.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))

    s.setLinearDimension("L", (-L / 2.0, 0.0, -H1), (L / 2.0, 0.0, -H1))
    s.setLinearDimension("H2", (-r_fl, 0.0, 0.0), (-r_fl, 0.0, z_gear_bot + h_gear))
    s.setLinearDimension("H1", (-r_fl, 0.0, -H1), (-r_fl, 0.0, 0.0))
    s.setLinearDimension("W_DIA", (x_shaft - r_hw, y_hw, z_shaft + r_hw), (x_shaft + r_hw, y_hw, z_shaft + r_hw))
