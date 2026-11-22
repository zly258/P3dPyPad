# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *


@activate(
    Group="Valve",
    FirstPortEndtypes="FL",
    Ports="2",
    TooltipShort=u"波纹管密封零泄漏截止阀",
    TooltipLong=u"化工剧毒/易燃/导热油管线用金属波纹管双层密封法兰截止阀 (WJ41H / HG/T 4086，含球形Z型流道阀体、加高波纹管密封圆筒中腔、双法兰螺栓连接盘、副填料函、防转支架与手轮)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"阀门连接管道外径 (mm)")
@param(L=LENGTH, TooltipShort=u"结构长度", TooltipLong=u"两端法兰密封面间距 (mm)")
@param(FL_OD=LENGTH, TooltipShort=u"法兰外径", TooltipLong=u"两端连接法兰外径 (mm)")
@param(FL_T=LENGTH, TooltipShort=u"法兰厚度", TooltipLong=u"连接法兰厚度 (mm)")
@param(H=LENGTH, TooltipShort=u"中心至顶高", TooltipLong=u"流道中心至手轮顶面总高度 (mm)")
@param(W_DIA=LENGTH, TooltipShort=u"手轮直径", TooltipLong=u"顶部操作手轮直径 (mm)")
@param(NBOLTS=INT, TooltipShort=u"螺栓孔数", TooltipLong=u"单侧法兰螺栓孔数")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"型号编码", TooltipLong=u"波纹管截止阀图集型号编码")
def VALVE_BELLOWS_GLOBE(s, D=88.9, L=310.0, FL_OD=200.0, FL_T=22.0, H=485.0, W_DIA=240.0, NBOLTS=8, ID=u"WJ41H-DN80", **kw):
    D = max(20.0, float(D))
    L = max(150.0, float(L))
    FL_OD = max(D + 55.0, float(FL_OD))
    FL_T = max(14.0, float(FL_T))
    H = max(280.0, float(H))
    W_DIA = max(140.0, float(W_DIA))
    NBOLTS = max(4, int(NBOLTS))

    r_pipe = D / 2.0
    r_bore = r_pipe * 0.84
    r_fl = FL_OD / 2.0
    r_globe = r_pipe * 1.48

    # 1. 球形截止阀肚 + 左右接管颈 + 两端法兰
    o_m = SPHERE(s, R=r_globe)
    o_neck = CYLINDER(s, R=r_pipe * 1.08, H=L - 2.0 * FL_T, O=0.0).rotateY(90.0).translate((-(L * 0.5 - FL_T), 0.0, 0.0))
    fl_l = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((-L * 0.5, 0.0, 0.0))
    fl_r = CYLINDER(s, R=r_fl, H=FL_T, O=0.0).rotateY(90.0).translate((L * 0.5 - FL_T, 0.0, 0.0))
    for p in (o_neck, fl_l, fl_r):
        o_m.uniteWith(p); p.erase()

    # 2. 加高金属波纹管密封圆筒腔 + 上下对夹连接法兰盘 + 8颗中腔螺柱
    z_bfl = r_globe * 0.78
    h_bellows = (H - z_bfl) * 0.48
    o_bfl1 = CYLINDER(s, R=r_globe * 0.96, H=34.0, O=0.0).translate((0.0, 0.0, z_bfl))
    o_bel_cyl = CYLINDER(s, R=r_pipe * 0.92, H=h_bellows, O=0.0).translate((0.0, 0.0, z_bfl + 28.0))
    z_bfl2 = z_bfl + 24.0 + h_bellows
    o_bfl2 = CYLINDER(s, R=r_pipe * 1.25, H=26.0, O=0.0).translate((0.0, 0.0, z_bfl2))
    for p in (o_bfl1, o_bel_cyl, o_bfl2):
        o_m.uniteWith(p); p.erase()

    for k in range(8):
        ang = math.radians(45.0 * k)
        bt = CYLINDER(s, R=6.5, H=44.0, O=0.0).translate((r_globe * 0.80 * math.cos(ang), r_globe * 0.80 * math.sin(ang), z_bfl - 5.0))
        o_m.uniteWith(bt); bt.erase()

    # 波纹管筒外壁识别环槽与黄油嘴
    for zf in (0.3, 0.55, 0.8):
        rg = CYLINDER(s, R=r_pipe * 1.02, H=8.0, O=0.0).translate((0.0, 0.0, z_bfl + 28.0 + h_bellows * zf))
        o_m.uniteWith(rg); rg.erase()

    # 3. 上部门型支架 + 副填料压盖 + 升降阀杆 + 顶部手轮
    z_yoke0 = z_bfl2 + 24.0
    z_wheel = H - 28.0
    h_yoke = max(75.0, z_wheel - z_yoke0)
    o_gland = BOX(s, L=r_pipe * 1.5, W=20.0, H=r_pipe * 1.1).translate((0.0, 0.0, z_yoke0 + 18.0))
    o_stem = CYLINDER(s, R=max(12.0, D * 0.14), H=H - z_yoke0, O=0.0).translate((0.0, 0.0, z_yoke0))
    o_ytop = CYLINDER(s, R=r_pipe * 0.72, H=28.0, O=0.0).translate((0.0, 0.0, z_wheel - 22.0))
    for p in (o_gland, o_stem, o_ytop):
        o_m.uniteWith(p); p.erase()

    for sy in (-1.0, 1.0):
        arm = BOX(s, L=16.0, W=h_yoke, H=28.0).translate((0.0, sy * r_pipe * 0.82, z_yoke0 + h_yoke * 0.5))
        o_m.uniteWith(arm); arm.erase()

    r_w = W_DIA / 2.0
    w_thk = 16.0
    o_rim = TORUS(s, R1=r_w - w_thk * 0.5, R2=w_thk * 0.5).translate((0.0, 0.0, z_wheel))
    o_hub = CYLINDER(s, R=24.0, H=22.0, O=0.0).translate((0.0, 0.0, z_wheel - 11.0))
    o_m.uniteWith(o_rim); o_rim.erase()
    o_m.uniteWith(o_hub); o_hub.erase()
    for k in range(4):
        spk = BOX(s, L=14.0, W=12.0, H=r_w * 1.85).rotateZ(k * 45.0).translate((0.0, 0.0, z_wheel))
        o_m.uniteWith(spk); spk.erase()

    # 法兰螺栓孔与内流道切除
    r_bcd = (r_pipe + r_fl) * 0.54
    r_hole = max(5.5, (r_fl - r_pipe) * 0.16)
    for i in range(NBOLTS):
        ang = (2.0 * math.pi * i) / NBOLTS + math.pi / NBOLTS
        for x_pos in (-L * 0.5 - 2.0, L * 0.5 - FL_T - 2.0):
            h_cyl = CYLINDER(s, R=r_hole, H=FL_T + 4.0, O=0.0).rotateY(90.0).translate((x_pos, r_bcd * math.cos(ang), r_bcd * math.sin(ang)))
            o_m.subtractFrom(h_cyl); h_cyl.erase()

    o_bore = CYLINDER(s, R=r_bore, H=L + 10.0, O=0.0).rotateY(90.0).translate((-(L * 0.5 + 5.0), 0.0, 0.0))
    o_m.subtractFrom(o_bore); o_bore.erase()

    s.setPoint((-L / 2.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setPoint((L / 2.0, 0.0, 0.0), (1.0, 0.0, 0.0))
    s.setLinearDimension("L", (-L / 2.0, 0.0, -r_fl), (L / 2.0, 0.0, -r_fl))
    s.setLinearDimension("H", (0.0, 0.0, 0.0), (0.0, 0.0, H))
    s.setLinearDimension("W_DIA", (-r_w, 0.0, z_wheel), (r_w, 0.0, z_wheel))
