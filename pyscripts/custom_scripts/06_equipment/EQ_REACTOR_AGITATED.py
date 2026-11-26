# -*- coding: utf-8 -*-
import math
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except (NameError, AttributeError):
    pass

from aqa.math import *
from varmain.primitiv import *
from varmain.var_basic import *
from varmain.custom import *

_HGT20592_PN16_A = {
    10: (17.2, 90.0, 16.0),
    15: (21.3, 95.0, 16.0),
    20: (26.9, 105.0, 18.0),
    25: (33.7, 115.0, 18.0),
    32: (42.4, 140.0, 18.0),
    40: (48.3, 150.0, 18.0),
    50: (60.3, 165.0, 18.0),
    65: (76.1, 185.0, 18.0),
    80: (88.9, 200.0, 20.0),
    100: (114.3, 220.0, 20.0),
    125: (139.7, 250.0, 22.0),
    150: (168.3, 285.0, 22.0),
    200: (219.1, 340.0, 24.0),
    250: (273.0, 405.0, 26.0),
    300: (323.9, 460.0, 28.0),
    350: (355.6, 520.0, 30.0),
    400: (406.4, 580.0, 32.0),
    450: (457.0, 640.0, 40.0),
    500: (508.0, 715.0, 44.0),
    600: (610.0, 840.0, 54.0),
    700: (711.0, 910.0, 36.0),
    800: (813.0, 1025.0, 38.0),
    900: (914.0, 1125.0, 40.0),
}

def _std_noz_dims(dn_val):
    dn_i = int(round(float(dn_val)))
    if dn_i in _HGT20592_PN16_A:
        od, d_fl, t_fl = _HGT20592_PN16_A[dn_i]
        return od / 2.0, d_fl / 2.0, t_fl
    keys = sorted(_HGT20592_PN16_A.keys())
    if dn_i < keys[0]:
        od, d_fl, t_fl = _HGT20592_PN16_A[keys[0]]
        return od / 2.0, d_fl / 2.0, t_fl
    if dn_i > keys[-1]:
        od = float(dn_val) * 1.016
        return od / 2.0, (od + 210.0) / 2.0, 42.0
    for k0, k1 in zip(keys, keys[1:]):
        if k0 <= dn_i <= k1:
            t = (dn_i - k0) / float(k1 - k0)
            v0, v1 = _HGT20592_PN16_A[k0], _HGT20592_PN16_A[k1]
            od = v0[0] + t * (v1[0] - v0[0])
            d_fl = v0[1] + t * (v1[1] - v0[1])
            t_fl = v0[2] + t * (v1[2] - v0[2])
            return od / 2.0, d_fl / 2.0, t_fl
    return float(dn_val) * 0.54, float(dn_val) * 0.54 + 55.0, 22.0

@activate(Group="Equipment",
          TooltipShort=u"夹套搅拌反应釜 (GB/T 150)",
          TooltipLong=u"GB/T 150 夹套搅拌反应釜参数化模型，含釜体、外部 U 形夹套、4×管式支腿、顶部机架/减速机/立式电机及 6 个工艺接管",
          LengthUnit="mm",
          Ports="6")
@group("MainDimensions", TooltipLong=u"夹套搅拌反应釜釜体、夹套、搅拌传动与接管尺寸参数")
@param(D=LENGTH, TooltipShort=u"釜体内径", TooltipLong=u"反应釜主体公称直径 DN (mm)")
@param(H_SHELL=LENGTH, TooltipShort=u"釜体直段高", TooltipLong=u"上下封头切线间釜体直段长度 (mm)", Ask4Dist=True)
@param(D_JACKET=LENGTH, TooltipShort=u"夹套外径", TooltipLong=u"外部 U 形夹套外径 (mm)")
@param(H_JACKET=LENGTH, TooltipShort=u"夹套直段高", TooltipLong=u"夹套筒体直段高度 (mm)")
@param(H_LEG=LENGTH, TooltipShort=u"支腿高度", TooltipLong=u"支腿底面至釜体下切线 EL 0 高度 (mm)", Ask4Dist=True)
@param(H_DRIVE=LENGTH, TooltipShort=u"搅拌传动总高", TooltipLong=u"顶部机架、减速机与立式电机总高度 (mm)", Ask4Dist=True)
@param(N_FEED=LENGTH, TooltipShort=u"进料口通径", TooltipLong=u"顶部进料口公称通径 DN (mm)")
@param(N_VENT=LENGTH, TooltipShort=u"放空口通径", TooltipLong=u"顶部放空/冷凝口公称通径 DN (mm)")
@param(N_MH=LENGTH, TooltipShort=u"人孔通径", TooltipLong=u"顶部人孔/加料口公称通径 DN (mm)")
@param(N_BOT=LENGTH, TooltipShort=u"釜底出料口", TooltipLong=u"釜底放料口公称通径 DN (mm)")
@param(N_JK=LENGTH, TooltipShort=u"夹套进出口", TooltipLong=u"夹套介质进出口公称通径 DN (mm)")
def EQ_REACTOR_AGITATED(
    s,
    D=1400.0,
    H_SHELL=1600.0,
    D_JACKET=1560.0,
    H_JACKET=1250.0,
    H_LEG=850.0,
    H_DRIVE=1150.0,
    N_FEED=80.0,
    N_VENT=100.0,
    N_MH=300.0,
    N_BOT=80.0,
    N_JK=65.0,
    ID=u"EQ_REACTOR_AGITATED",
    **kw
):
    u"""GB/T 150 夹套搅拌反应釜 (EL 0 = 釜体下封头切线，支腿底面 Z = -H_LEG，+Z 向上)。"""
    D = float(D)
    if D < 1.0:
        D = 1.0
    R_V = D / 2.0
    H_SHELL = float(H_SHELL)
    if H_SHELL < 1.0:
        H_SHELL = 1.0
    H_HEAD = R_V * 0.5
    D_JACKET = float(D_JACKET)
    if D_JACKET < 1.0:
        D_JACKET = 1.0
    R_JK = D_JACKET / 2.0
    H_JACKET = min(H_SHELL - 120.0, max(400.0, float(H_JACKET)))
    H_HEAD_JK = R_JK * 0.5
    H_LEG = float(H_LEG)
    if H_LEG < 1.0:
        H_LEG = 1.0
    H_DRIVE = max(600.0, float(H_DRIVE))

    z_gnd = -H_LEG

    # 1. 釜体直段 + 上下 EHA 2:1 封头 + 设备主法兰
    o_main = CYLINDER(s, R=R_V, H=H_SHELL, O=0.0)
    o_th = ELLIPSOIDHEAD(s, R=R_V).translate((0.0, 0.0, H_SHELL - 2.0))
    o_main.uniteWith(o_th)
    o_th.erase()

    o_bh = ELLIPSOIDHEAD(s, R=R_V).rotateX(180.0).translate((0.0, 0.0, 2.0))
    o_main.uniteWith(o_bh)
    o_bh.erase()

    # 釜盖主法兰环
    o_mfl = CYLINDER(s, R=R_V + 75.0, H=56.0, O=0.0).translate((0.0, 0.0, H_SHELL - 28.0))
    o_main.uniteWith(o_mfl)
    o_mfl.erase()

    # 2. 外部 U 形夹套 (夹套筒段 + 夹套下封头 + 顶封环)
    o_jk = CYLINDER(s, R=R_JK, H=H_JACKET, O=0.0)
    o_main.uniteWith(o_jk)
    o_jk.erase()

    o_jkh = ELLIPSOIDHEAD(s, R=R_JK).rotateX(180.0).translate((0.0, 0.0, 2.0))
    o_main.uniteWith(o_jkh)
    o_jkh.erase()

    # 3. 4×管式支腿 (45°, 135°, 225°, 315°)
    r_pcd = R_JK - 75.0
    r_leg = max(45.0, D * 0.05)
    base_w = r_leg * 3.4
    base_t = 18.0
    for deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(deg)
        lx = r_pcd * math.cos(rad)
        ly = r_pcd * math.sin(rad)
        o_leg = CYLINDER(s, R=r_leg, H=H_LEG - base_t + 30.0, O=0.0).translate((lx, ly, z_gnd + base_t))
        o_base = CORNERBOX(s, L=base_w, W=base_w, H=base_t).translate(
            (lx - base_w / 2.0, ly - base_w / 2.0, z_gnd)
        )
        o_main.uniteWith(o_leg)
        o_leg.erase()
        o_main.uniteWith(o_base)
        o_base.erase()

    # 4. 顶部搅拌传动装置 (机封法兰 + 机架灯笼柱 + 摆线/齿轮减速机 + 立式防爆电机)
    z_top_crown = H_SHELL + H_HEAD
    h_stool = H_DRIVE * 0.34
    h_gear = H_DRIVE * 0.24
    h_motor = H_DRIVE * 0.42

    # 中心安装法兰底座
    r_mnt = max(140.0, D * 0.13)
    o_mnt = CYLINDER(s, R=r_mnt, H=80.0, O=0.0).translate((0.0, 0.0, z_top_crown - 40.0))
    o_main.uniteWith(o_mnt)
    o_mnt.erase()

    # 机架下/上法兰 + 4 根机架立柱 + 中心搅拌轴
    z_st0 = z_top_crown + 35.0
    o_st_bot = CYLINDER(s, R=r_mnt * 0.92, H=24.0, O=0.0).translate((0.0, 0.0, z_st0))
    o_st_top = CYLINDER(s, R=r_mnt * 0.95, H=26.0, O=0.0).translate((0.0, 0.0, z_st0 + h_stool - 26.0))
    o_shaft = CYLINDER(s, R=max(26.0, D * 0.022), H=h_stool + 40.0, O=0.0).translate((0.0, 0.0, z_st0 - 20.0))
    o_main.uniteWith(o_st_bot)
    o_st_bot.erase()
    o_main.uniteWith(o_st_top)
    o_st_top.erase()
    o_main.uniteWith(o_shaft)
    o_shaft.erase()

    for deg in (0.0, 90.0, 180.0, 270.0):
        rad = math.radians(deg)
        pr = r_mnt * 0.72
        o_col = CYLINDER(s, R=max(16.0, r_mnt * 0.11), H=h_stool, O=0.0).translate(
            (pr * math.cos(rad), pr * math.sin(rad), z_st0)
        )
        o_main.uniteWith(o_col)
        o_col.erase()

    # 减速机壳体
    z_g0 = z_st0 + h_stool - 4.0
    r_gear = r_mnt * 1.15
    o_gear = CYLINDER(s, R=r_gear, H=h_gear + 4.0, O=0.0).translate((0.0, 0.0, z_g0))
    o_main.uniteWith(o_gear)
    o_gear.erase()

    # 立式电机主体 + 接线盒
    z_m0 = z_g0 + h_gear
    r_mot = r_mnt * 0.95
    o_mot = CYLINDER(s, R=r_mot, H=h_motor, O=0.0).translate((0.0, 0.0, z_m0 - 4.0))
    o_tbox = CORNERBOX(s, L=r_mot * 0.65, W=r_mot * 0.60, H=h_motor * 0.35).translate(
        (r_mot * 0.75, -r_mot * 0.30, z_m0 + h_motor * 0.32)
    )
    o_main.uniteWith(o_mot)
    o_mot.erase()
    o_main.uniteWith(o_tbox)
    o_tbox.erase()

    # 5. 6 个工艺接管
    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    def _add_top_noz(r_ecc, deg, dn_val, z_face):
        r_p, r_f, t_f = _fl_dims(dn_val)
        rad = math.radians(deg)
        nx = r_ecc * math.cos(rad)
        ny = r_ecc * math.sin(rad)
        z_start = H_SHELL + H_HEAD * 0.25
        o_p = CYLINDER(s, R=r_p, H=z_face - t_f - z_start + 2.0, O=0.0).translate((nx, ny, z_start))
        o_f = CYLINDER(s, R=r_f, H=t_f, O=0.0).translate((nx, ny, z_face - t_f))
        o_main.uniteWith(o_p)
        o_p.erase()
        o_main.uniteWith(o_f)
        o_f.erase()
        return (nx, ny, z_face)

    z_top_noz = z_top_crown + 220.0
    p_feed = _add_top_noz(R_V * 0.56, 180.0, N_FEED, z_top_noz)
    p_vent = _add_top_noz(R_V * 0.56, 90.0, N_VENT, z_top_noz)
    p_mh = _add_top_noz(R_V * 0.54, 0.0, N_MH, z_top_noz + 40.0)

    # 釜底出料口 (中心向下)
    r_pb, r_fb, t_fb = _fl_dims(N_BOT)
    z_bot_face = -(H_HEAD_JK + 180.0)
    z_bot_start = -H_HEAD * 0.55
    o_nb_p = CYLINDER(s, R=r_pb, H=abs(z_bot_face) - t_fb - abs(z_bot_start) + 2.0, O=0.0).rotateX(180.0).translate((0.0, 0.0, z_bot_start))
    o_nb_f = CYLINDER(s, R=r_fb, H=t_fb, O=0.0).rotateX(180.0).translate((0.0, 0.0, z_bot_face + t_fb))
    o_main.uniteWith(o_nb_p)
    o_nb_p.erase()
    o_main.uniteWith(o_nb_f)
    o_nb_f.erase()
    p_bot = (0.0, 0.0, z_bot_face)

    # 夹套进口 (下部 +X) 与夹套出口 (上部 -X)
    r_pj, r_fj, t_fj = _fl_dims(N_JK)
    jk_ext = 200.0
    x_jk_face = R_JK + jk_ext
    pipe_jl = jk_ext + 80.0 - t_fj

    z_jk1 = 220.0
    o_jk1_p = CYLINDER(s, R=r_pj, H=pipe_jl + 2.0, O=0.0).rotateY(90.0).translate((R_JK - 80.0, 0.0, z_jk1))
    o_jk1_f = CYLINDER(s, R=r_fj, H=t_fj, O=0.0).rotateY(90.0).translate((x_jk_face - t_fj, 0.0, z_jk1))
    o_main.uniteWith(o_jk1_p)
    o_jk1_p.erase()
    o_main.uniteWith(o_jk1_f)
    o_jk1_f.erase()
    p_jk_in = (x_jk_face, 0.0, z_jk1)

    z_jk2 = H_JACKET - 180.0
    o_jk2_p = CYLINDER(s, R=r_pj, H=pipe_jl + 2.0, O=0.0).rotateY(-90.0).translate((-(R_JK - 80.0), 0.0, z_jk2))
    o_jk2_f = CYLINDER(s, R=r_fj, H=t_fj, O=0.0).rotateY(-90.0).translate((-x_jk_face + t_fj, 0.0, z_jk2))
    o_main.uniteWith(o_jk2_p)
    o_jk2_p.erase()
    o_main.uniteWith(o_jk2_f)
    o_jk2_f.erase()
    p_jk_out = (-x_jk_face, 0.0, z_jk2)

    # 6. 注册 6 个端口
    s.setPoint(p_feed, (0.0, 0.0, 1.0))
    s.setPoint(p_vent, (0.0, 0.0, 1.0))
    s.setPoint(p_mh, (0.0, 0.0, 1.0))
    s.setPoint(p_bot, (0.0, 0.0, -1.0))
    s.setPoint(p_jk_in, (1.0, 0.0, 0.0))
    s.setPoint(p_jk_out, (-1.0, 0.0, 0.0))

    # 7. 注册线性标注
    s.setLinearDimension('D', (-R_V, 0.0, H_SHELL), (R_V, 0.0, H_SHELL))
    s.setLinearDimension('D_JACKET', (-R_JK, 0.0, H_JACKET * 0.5), (R_JK, 0.0, H_JACKET * 0.5))
    s.setLinearDimension('H_SHELL', (-R_JK, 0.0, 0.0), (-R_JK, 0.0, H_SHELL))
    s.setLinearDimension('H_LEG', (-R_JK, 0.0, z_gnd), (-R_JK, 0.0, 0.0))
