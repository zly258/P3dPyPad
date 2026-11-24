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

@activate(Group="Valve", Ports=2, TooltipShort=u"旋启式法兰止回阀 (H44H / BS 1868)", TooltipLong=u"化工标准 GB/T 12236 / BS 1868 旋启式钢制法兰止回阀 (Swing Check Valve)，带偏心鼓形阀腔、两侧摇杆销轴凸台、螺栓连接顶盖与中心环形吊耳", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"阀门主要结构尺寸：结构长度、中心高与法兰规格")
@param(D=LENGTH, TooltipShort=u"管道外径 OD", Ask4Dist=True, TooltipLong=u"管道外径 OD")
@param(L=LENGTH, TooltipShort=u"结构长度 L (GB/T 12221)", Ask4Dist=True, TooltipLong=u"结构长度 L (GB/T 12221)")
@param(H=LENGTH, TooltipShort=u"中心至阀盖吊环高 H", Ask4Dist=True, TooltipLong=u"中心至阀盖吊环高 H")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"法兰密封面外圆直径")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"法兰盘厚度")
@param(NBOLTS=INT, TooltipShort=u"法兰螺栓孔数", TooltipLong=u"法兰螺栓孔总数，需与法兰外径/厚度配套")
@param(ID=STRING, TooltipShort=u"阀门位号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def VALVE_CHECK_SWING(s, D=114.3, L=300.0, H=235.0, FL_OD=220.0, FL_T=22.0, NBOLTS=8, ID="H44H-16C", **kw):
    D = max(20.0, float(D))
    L = max(140.0, float(L))
    H = max(110.0, float(H))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(12.0, float(FL_T))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.86
    r_fl = FL_OD / 2.0
    rf_r = r_pipe + (r_fl - r_pipe) * 0.36
    rf_t = 2.5

    # 1. 水平通道 + 两端 RF 法兰
    o_valve = CYLINDER(s, R=r_pipe * 1.08, H=L - 2.0 * rf_t, O=0.0).rotateY(90.0).translate((-(L * 0.5 - rf_t), 0.0, 0.0))
    for sx in (-1.0, 1.0):
        x_rf = -L * 0.5 if sx < 0 else (L * 0.5 - rf_t - 1.0)
        c_rf = CYLINDER(s, R=rf_r, H=rf_t + 1.0, O=0.0).rotateY(90.0).translate((x_rf, 0.0, 0.0))
        o_valve.uniteWith(c_rf); c_rf.erase()
        x_fl = (-L * 0.5 + rf_t) if sx < 0 else (L * 0.5 - rf_t - FL_T)
        c_fl = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_valve.uniteWith(c_fl); c_fl.erase()

    # 2. 鼓形止回阀肚 + 上部两侧摇杆销轴耳座 (Hinge Pin Bosses)
    r_belly = r_pipe * 1.48
    o_top = ELLIPSOIDHEAD(s, R=r_belly * 1.08, H=r_belly * 0.95)
    o_bot = ELLIPSOIDHEAD(s, R=r_belly * 1.08, H=r_belly * 0.85).rotateX(180.0)
    o_valve.uniteWith(o_top); o_top.erase()
    o_valve.uniteWith(o_bot); o_bot.erase()

    # 进水侧上方 (-X 偏上) 两侧销轴凸台
    w_pin = r_belly * 2.25
    o_pin = CYLINDER(s, R=r_pipe * 0.32, H=w_pin, O=0.0).rotateX(90.0).translate((-r_pipe * 0.42, w_pin * 0.5, r_pipe * 0.65))
    o_valve.uniteWith(o_pin); o_pin.erase()

    # 3. 顶部螺栓连接阀盖法兰 + 8 颗六角螺栓 + 拱形顶盖 + 环形吊耳 (Lifting Eye Bolt)
    z_cov_fl = H * 0.55
    r_cneck = r_belly * 0.78
    o_cneck = CYLINDER(s, R=r_cneck, H=z_cov_fl, O=0.0)
    o_valve.uniteWith(o_cneck); o_cneck.erase()

    r_cfl = r_cneck * 1.36
    t_cfl = FL_T * 0.88
    o_cfl = CYLINDER(s, R=r_cfl, H=2.0 * t_cfl, O=0.0).translate((0.0, 0.0, z_cov_fl))
    o_valve.uniteWith(o_cfl); o_cfl.erase()

    r_cbcd = r_cneck + (r_cfl - r_cneck) * 0.58
    bolt_af = max(12.0, (r_cfl - r_cneck) * 0.48)
    for i in range(8):
        ang = math.radians(i * 45.0 + 22.5)
        hb = _hex_z(s, bolt_af, t_cfl * 0.55).translate((r_cbcd * math.cos(ang), r_cbcd * math.sin(ang), z_cov_fl + 1.95 * t_cfl))
        o_valve.uniteWith(hb); hb.erase()

    z_cap_top = z_cov_fl + 2.0 * t_cfl
    o_dome = ELLIPSOIDHEAD(s, R=r_cneck * 0.96, H=r_cneck * 0.96 * 0.38).translate((0.0, 0.0, z_cap_top - 1.0))
    o_valve.uniteWith(o_dome); o_dome.erase()

    # 顶部环形吊耳 (Lifting Eye)
    r_eye = max(18.0, (H - z_cap_top) * 0.42)
    z_eye_c = H - r_eye
    o_eye_stem = CYLINDER(s, R=r_eye * 0.35, H=max(12.0, z_eye_c - z_cap_top), O=0.0).translate((0.0, 0.0, z_cap_top))
    o_valve.uniteWith(o_eye_stem); o_eye_stem.erase()
    o_eye = TORUS(s, R1=r_eye * 0.72, R2=r_eye * 0.26, A=360.0).rotateX(90.0).translate((0.0, 0.0, z_eye_c))
    o_valve.uniteWith(o_eye); o_eye.erase()

    # 4. 流道内孔与两端法兰螺栓孔
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
    s.setLinearDimension("FL_OD", (-L / 2.0, 0.0, -r_fl), (-L / 2.0, 0.0, r_fl))
