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
          TooltipShort=u"平盖搅拌配料槽",
          TooltipLong=u"常压平盖搅拌配料槽参数化模型，含立式筒体、锥形排净底、顶部法兰平盖与半开检查口、顶部机架与搅拌电机减速机、4支腿底板及3个工艺接管",
          LengthUnit="mm",
          Ports="3")
@group("MainDimensions", TooltipLong=u"平盖搅拌配料槽主要尺寸参数")
@param(D=LENGTH, TooltipShort=u"槽体公称直径", TooltipLong=u"搅拌配料槽筒体公称直径 D (mm)")
@param(H_SHELL=LENGTH, TooltipShort=u"筒体直段高", TooltipLong=u"配料槽圆筒直段高度 H (mm)", Ask4Dist=True)
@param(H_CONE=LENGTH, TooltipShort=u"锥底高度", TooltipLong=u"下部锥形排净底高度 (mm)")
@param(H_LEG=LENGTH, TooltipShort=u"支腿净高", TooltipLong=u"底板底面至圆筒下切线高度 (mm)", Ask4Dist=True)
@param(H_MOTOR=LENGTH, TooltipShort=u"搅拌驱动总高", TooltipLong=u"顶部搅拌机架、减速机及立式电机总高 (mm)")
@param(NOZ_IN=LENGTH, TooltipShort=u"顶进料口径", TooltipLong=u"顶部进料接管公称通径 DN (mm)")
@param(NOZ_SIDE=LENGTH, TooltipShort=u"侧溢流口径", TooltipLong=u"上部侧面溢流/加料口公称通径 DN (mm)")
@param(NOZ_OUT=LENGTH, TooltipShort=u"底出料口径", TooltipLong=u"底部中心排料口公称通径 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出高", TooltipLong=u"接管法兰面伸出外壁高度 (mm)")
def EQ_MIXING_TANK_OPEN(
    s,
    D=1400.0,
    H_SHELL=1800.0,
    H_CONE=320.0,
    H_LEG=750.0,
    H_MOTOR=720.0,
    NOZ_IN=80.0,
    NOZ_SIDE=80.0,
    NOZ_OUT=100.0,
    NOZ_EXT=200.0,
    ID=u"EQ_MIXING_TANK_OPEN",
    **kw
):
    u"""平盖搅拌配料槽 (筒体下切线为 Z=0，支腿底板底面 Z=-H_LEG，+Z 向上)。"""
    D = float(D)
    if D < 1.0:
        D = 1.0
    R_V = D / 2.0
    H_SHELL = float(H_SHELL)
    if H_SHELL < 1.0:
        H_SHELL = 1.0
    H_CONE = max(120.0, float(H_CONE))
    H_LEG = float(H_LEG)
    if H_LEG < 1.0:
        H_LEG = 1.0
    H_MOTOR = max(400.0, float(H_MOTOR))
    NOZ_IN = max(40.0, float(NOZ_IN))
    NOZ_SIDE = max(40.0, float(NOZ_SIDE))
    NOZ_OUT = max(50.0, float(NOZ_OUT))
    NOZ_EXT = max(120.0, float(NOZ_EXT))

    z_gnd = -H_LEG
    lid_t = max(24.0, D * 0.02)
    r_lid = R_V + max(55.0, D * 0.045)

    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    r_po, r_fo, t_fo = _fl_dims(NOZ_OUT)

    # 1. 主圆筒体 + 底部排净锥底
    o_main = CYLINDER(s, R=R_V, H=H_SHELL, O=0.0)
    o_cone = CONE(s, R1=max(r_po + 15.0, R_V * 0.14), R2=R_V, H=H_CONE + 4.0).translate((0.0, 0.0, -H_CONE))
    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 2. 顶部平盖法兰边 + 平盖板 + 半开投料检查盖
    o_rim = CYLINDER(s, R=r_lid, H=lid_t * 1.6, O=0.0).translate((0.0, 0.0, H_SHELL - lid_t * 0.6))
    o_main.uniteWith(o_rim)
    o_rim.erase()

    # 顶部投料口半圆盖凸台 (位于 -X 侧)
    hatch_r = max(140.0, R_V * 0.24)
    o_ht = CYLINDER(s, R=hatch_r, H=90.0, O=0.0).translate((-R_V * 0.52, 0.0, H_SHELL + lid_t - 4.0))
    o_main.uniteWith(o_ht)
    o_ht.erase()

    # 3. 顶部搅拌机架横梁 + 机架底座 + 减速机 + 立式电机
    z_top = H_SHELL + lid_t
    beam_w = max(160.0, D * 0.14)
    beam_h = max(100.0, D * 0.08)
    o_beam = CORNERBOX(s, L=D * 0.96, W=beam_w, H=beam_h).translate((-D * 0.48, -beam_w * 0.5, z_top - 4.0))
    o_main.uniteWith(o_beam)
    o_beam.erase()

    h_st = H_MOTOR * 0.30
    h_gb = H_MOTOR * 0.28
    h_mt = H_MOTOR * 0.42
    r_st = max(95.0, D * 0.095)
    r_gb = max(120.0, D * 0.12)
    r_mt = max(110.0, D * 0.11)
    o_st = CYLINDER(s, R=r_st, H=h_st + 10.0, O=0.0).translate((0.0, 0.0, z_top + beam_h - 8.0))
    o_gb = CYLINDER(s, R=r_gb, H=h_gb + 6.0, O=0.0).translate((0.0, 0.0, z_top + beam_h + h_st - 4.0))
    o_mt = CYLINDER(s, R=r_mt, H=h_mt, O=0.0).translate((0.0, 0.0, z_top + beam_h + h_st + h_gb - 2.0))
    o_tbox = CORNERBOX(s, L=r_mt * 0.65, W=r_mt * 0.65, H=h_mt * 0.45).translate(
        (r_mt * 0.75, -r_mt * 0.325, z_top + beam_h + h_st + h_gb + h_mt * 0.25)
    )
    for ob in (o_st, o_gb, o_mt, o_tbox):
        o_main.uniteWith(ob)
        ob.erase()

    # 4. 4 根圆管支腿与底板 (均匀分布于 45/135/225/315 度)
    r_leg = max(48.0, D * 0.045)
    pcd_r = R_V * 0.88
    bp_w = r_leg * 3.4
    bp_t = 16.0
    leg_top = H_SHELL * 0.16
    for i in range(4):
        ang = math.radians(45.0 + i * 90.0)
        lx = pcd_r * math.cos(ang)
        ly = pcd_r * math.sin(ang)
        o_lg = CYLINDER(s, R=r_leg, H=leg_top - (z_gnd + bp_t) + 4.0, O=0.0).translate((lx, ly, z_gnd + bp_t - 2.0))
        o_bp = CORNERBOX(s, L=bp_w, W=bp_w, H=bp_t).translate((lx - bp_w * 0.5, ly - bp_w * 0.5, z_gnd))
        o_main.uniteWith(o_lg)
        o_lg.erase()
        o_main.uniteWith(o_bp)
        o_bp.erase()

    # 5. 3 个工艺接管
    # Port 1: 顶部进料口 (+Z, 位于 +Y 侧)
    r_pi, r_fi, t_fi = _fl_dims(NOZ_IN)
    y_in = R_V * 0.54
    z_in_face = z_top + NOZ_EXT
    o_p1 = CYLINDER(s, R=r_pi, H=NOZ_EXT - t_fi + 30.0, O=0.0).translate((0.0, y_in, z_top - 25.0))
    o_f1 = CYLINDER(s, R=r_fi, H=t_fi, O=0.0).translate((0.0, y_in, z_in_face - t_fi))
    o_main.uniteWith(o_p1)
    o_p1.erase()
    o_main.uniteWith(o_f1)
    o_f1.erase()
    p_in = (0.0, y_in, z_in_face)

    # Port 2: 上部侧面溢流口 (+X)
    r_ps, r_fs, t_fs = _fl_dims(NOZ_SIDE)
    z_side = H_SHELL * 0.80
    x_side_face = R_V + NOZ_EXT
    o_p2 = CYLINDER(s, R=r_ps, H=NOZ_EXT - t_fs + R_V * 0.25, O=0.0).rotateY(90.0).translate((R_V * 0.75, 0.0, z_side))
    o_f2 = CYLINDER(s, R=r_fs, H=t_fs, O=0.0).rotateY(90.0).translate((x_side_face - t_fs, 0.0, z_side))
    o_main.uniteWith(o_p2)
    o_p2.erase()
    o_main.uniteWith(o_f2)
    o_f2.erase()
    p_side = (x_side_face, 0.0, z_side)

    # Port 3: 底部中心排料口 (-Z)
    z_out_face = max(z_gnd + 80.0, -H_CONE - NOZ_EXT)
    o_p3 = CYLINDER(s, R=r_po, H=(-H_CONE + 30.0) - (z_out_face + t_fo), O=0.0).translate((0.0, 0.0, z_out_face + t_fo - 2.0))
    o_f3 = CYLINDER(s, R=r_fo, H=t_fo, O=0.0).translate((0.0, 0.0, z_out_face))
    o_main.uniteWith(o_p3)
    o_p3.erase()
    o_main.uniteWith(o_f3)
    o_f3.erase()
    p_out = (0.0, 0.0, z_out_face)

    # 6. 注册 3 个工艺端口
    s.setPoint(p_in, (0.0, 0.0, 1.0))
    s.setPoint(p_side, (1.0, 0.0, 0.0))
    s.setPoint(p_out, (0.0, 0.0, -1.0))

    # 7. 注册线性标注
    s.setLinearDimension('D', (-R_V, 0.0, 0.0), (R_V, 0.0, 0.0))
    s.setLinearDimension('H_SHELL', (-R_V, 0.0, 0.0), (-R_V, 0.0, H_SHELL))
    s.setLinearDimension('H_LEG', (-R_V, 0.0, z_gnd), (-R_V, 0.0, 0.0))
