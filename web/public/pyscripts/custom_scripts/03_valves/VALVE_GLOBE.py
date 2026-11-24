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

def _hex_z(s, af, h):
    rc = float(af) / math.sqrt(3.0)
    b0 = BOX(s, L=af, W=h, H=rc).translate((0.0, 0.0, h * 0.5))
    b1 = BOX(s, L=af, W=h, H=rc).rotateZ(60.0).translate((0.0, 0.0, h * 0.5))
    b2 = BOX(s, L=af, W=h, H=rc).rotateZ(120.0).translate((0.0, 0.0, h * 0.5))
    b0.uniteWith(b1); b1.erase()
    b0.uniteWith(b2); b2.erase()
    return b0

@activate(Group="Valve", Ports=2, TooltipShort=u"直通式法兰截止阀 (J41H / BS 1873)", TooltipLong=u"化工标准 GB/T 12235 / BS 1873 直通式球形阀体法兰截止阀 (Globe Valve)，带典型球肚阀腔、中法兰螺栓圈、填料函、双臂支架与手轮", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"阀门主要结构尺寸：结构长度、中心高与法兰规格")
@param(D=LENGTH, TooltipShort=u"管道外径 OD", Ask4Dist=True, TooltipLong=u"管道外径 OD")
@param(L=LENGTH, TooltipShort=u"结构长度 L (GB/T 12221)", Ask4Dist=True, TooltipLong=u"结构长度 L (GB/T 12221)")
@param(H=LENGTH, TooltipShort=u"中心至手轮高 H", Ask4Dist=True, TooltipLong=u"中心至手轮高 H")
@param(W_DIA=LENGTH, TooltipShort=u"手轮外径 W", TooltipLong=u"手轮外径 W")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰密封面外圆直径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓孔数", TooltipLong=u"法兰螺栓孔总数，需与法兰外径/厚度配套")
@param(ID=STRING, TooltipShort=u"阀门位号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def VALVE_GLOBE(s, D=114.3, L=350.0, H=410.0, W_DIA=250.0, FL_OD=220.0, FL_T=22.0, NBOLTS=8, ID="J41H-16C", **kw):
    D = max(20.0, float(D))
    L = max(150.0, float(L))
    H = max(180.0, float(H))
    W_DIA = max(100.0, float(W_DIA))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.85
    r_fl = FL_OD / 2.0
    rf_r = r_pipe + (r_fl - r_pipe) * 0.36
    rf_t = 2.5

    # 1. 流道连接颈 + 两端 RF 法兰
    o_valve = CYLINDER(s, R=r_pipe * 1.06, H=L - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(L * 0.5 - rf_t), 0.0, 0.0))
    for sx in (-1.0, 1.0):
        x_rf = -L * 0.5 if sx < 0 else (L * 0.5 - rf_t - 1.0)
        c_rf = CYLINDER(s, R=rf_r, H=rf_t + 1.0, O=0.0).rotateY(90.0).translate((x_rf, 0.0, 0.0))
        o_valve.uniteWith(c_rf); c_rf.erase()
        x_fl = (-L * 0.5 + rf_t) if sx < 0 else (L * 0.5 - rf_t - FL_T)
        c_fl = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_valve.uniteWith(c_fl); c_fl.erase()

    # 2. 截止阀标志性鼓形球肚阀腔 (Globular Spherical Body) + 左右流道变径过渡锥
    r_globe = r_pipe * 1.62
    o_top_hem = ELLIPSOIDHEAD(s, R=r_globe * 1.05, H=r_globe * 0.92)
    o_bot_hem = ELLIPSOIDHEAD(s, R=r_globe * 1.05, H=r_globe * 0.88).rotateX(180.0)
    o_valve.uniteWith(o_top_hem); o_top_hem.erase()
    o_valve.uniteWith(o_bot_hem); o_bot_hem.erase()

    # 3. 阀体上口圆颈 + 圆形中法兰 + 8 颗六角中法兰螺栓
    z_bfl = r_globe * 0.78
    r_neck = r_globe * 0.72
    o_neck = CYLINDER(s, R=r_neck, H=z_bfl, O=0.0)
    o_valve.uniteWith(o_neck); o_neck.erase()

    r_bfl = r_neck * 1.38
    t_bfl = FL_T * 0.88
    o_bfl = CYLINDER(s, R=r_bfl, H=2.0 * t_bfl, O=0.0).translate((0.0, 0.0, z_bfl))
    o_valve.uniteWith(o_bfl); o_bfl.erase()

    r_bbcd = r_neck + (r_bfl - r_neck) * 0.58
    bolt_af = max(12.0, (r_bfl - r_neck) * 0.48)
    for i in range(8):
        ang = math.radians(i * 45.0 + 22.5)
        hb = _hex_z(s, bolt_af, t_bfl * 0.55).translate((r_bbcd * math.cos(ang), r_bbcd * math.sin(ang), z_bfl + 1.95 * t_bfl))
        o_valve.uniteWith(hb); hb.erase()

    # 4. 阶梯锥形阀盖 + 填料函 + 填料压盖法兰
    z_bfl_top = z_bfl + 1.95 * t_bfl
    h_bon = (H - z_bfl_top) * 0.30
    r_stuff = r_neck * 0.52
    o_bon = CONE(s, R1=r_neck * 1.02, R2=r_stuff, H=h_bon, E=0.0).translate((0.0, 0.0, z_bfl_top - 1.0))
    o_valve.uniteWith(o_bon); o_bon.erase()

    z_stuff_top = z_bfl_top + h_bon + H * 0.08
    o_stuff = CYLINDER(s, R=r_stuff, H=z_stuff_top - (z_bfl_top + h_bon) + 2.0, O=0.0).translate((0.0, 0.0, z_bfl_top + h_bon - 2.0))
    o_valve.uniteWith(o_stuff); o_stuff.erase()
    o_gland = BOX(s, L=r_stuff * 2.5, W=t_bfl * 0.6, H=r_stuff * 1.4).translate((0.0, 0.0, z_stuff_top))
    o_valve.uniteWith(o_gland); o_gland.erase()

    # 5. 双立柱支架 + 顶部横梁 + 旋转上升阀杆 + 四辐条手轮
    z_yoke_top = H - 16.0
    r_arm = max(8.0, r_pipe * 0.16)
    y_arm = r_stuff * 0.85
    for sy in (-1.0, 1.0):
        arm = CYLINDER(s, R=r_arm, H=max(30.0, z_yoke_top - z_stuff_top + 4.0), O=0.0).translate((0.0, sy * y_arm, z_stuff_top - 2.0))
        o_valve.uniteWith(arm); arm.erase()
    o_top_b = BOX(s, L=2.0 * y_arm + 2.0 * r_arm, W=20.0, H=r_stuff * 1.2).translate((0.0, 0.0, z_yoke_top - 6.0))
    o_valve.uniteWith(o_top_b); o_top_b.erase()

    r_stem = max(7.5, r_pipe * 0.16)
    stem_top = H + max(32.0, D * 0.28)
    o_stem = CYLINDER(s, R=r_stem, H=stem_top - z_bfl, O=0.0).translate((0.0, 0.0, z_bfl))
    o_valve.uniteWith(o_stem); o_stem.erase()

    r_hw = W_DIA / 2.0
    r_rim = max(6.5, W_DIA * 0.042)
    o_rim = TORUS(s, R1=r_hw - r_rim, R2=r_rim, A=360.0).translate((0.0, 0.0, H))
    o_valve.uniteWith(o_rim); o_rim.erase()
    o_hub = CYLINDER(s, R=r_stem * 2.1, H=r_rim * 2.4, O=0.0).translate((0.0, 0.0, H - r_rim * 1.2))
    o_valve.uniteWith(o_hub); o_hub.erase()
    for i in range(4):
        ang_deg = i * 90.0 + 45.0
        ang_rad = math.radians(ang_deg)
        spoke_len = (r_hw - r_rim) - r_stem * 1.5
        rm = r_stem * 1.5 + spoke_len * 0.5
        sp = CYLINDER(s, R=r_rim * 0.62, H=spoke_len, O=0.0).rotateY(90.0).translate((-spoke_len * 0.5, 0.0, 0.0))
        sp.rotateZ(ang_deg).translate((rm * math.cos(ang_rad), rm * math.sin(ang_rad), H))
        o_valve.uniteWith(sp); sp.erase()

    # 6. 流道内孔与两端法兰螺栓孔
    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_valve.subtractFrom(o_bore); o_bore.erase()
    r_bcd = r_pipe + (r_fl - r_pipe) * 0.66
    r_hole = max(5.0, min(13.0, (r_fl - r_pipe) * 0.14))
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        by, bz = r_bcd * math.cos(ang), r_bcd * math.sin(ang)
        hl = CYLINDER(s, R=r_hole, H=FL_T + rf_t + 6.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 2.0), by, bz))
        o_valve.subtractFrom(hl); hl.erase()
        hr = CYLINDER(s, R=r_hole, H=FL_T + rf_t + 6.0, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T - rf_t - 4.0, by, bz))
        o_valve.subtractFrom(hr); hr.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))

    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_fl), (L / 2.0, 0.0, -r_fl))
    s.setLinearDimension("H", (-L / 2.0, 0.0, 0.0), (-L / 2.0, 0.0, H))
    s.setLinearDimension("W_DIA", (-r_hw, 0.0, stem_top), (r_hw, 0.0, stem_top))
