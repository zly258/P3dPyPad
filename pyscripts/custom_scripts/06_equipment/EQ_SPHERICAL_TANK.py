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
          TooltipShort=u"球形储罐 (GB/T 12337)",
          TooltipLong=u"GB/T 12337 钢制球形储罐参数化模型，含大直径球壳、6根赤道支柱与基础环底板、中部拉杆环、顶部人孔及3个工艺进出口法兰",
          LengthUnit="mm",
          Ports="3")
@group("MainDimensions", TooltipLong=u"球形储罐主要尺寸参数")
@param(D_SPHERE=LENGTH, TooltipShort=u"球壳公称直径", TooltipLong=u"球形储罐球体内径/公称直径 D (mm)")
@param(H_CLEAR=LENGTH, TooltipShort=u"球底净空高", TooltipLong=u"基础底面至球壳最低点净空高度 (mm)", Ask4Dist=True)
@param(D_LEG=LENGTH, TooltipShort=u"赤道支柱直径", TooltipLong=u"6根赤道圆管支柱外径 (mm)")
@param(NOZ_TOP=LENGTH, TooltipShort=u"顶部气相口", TooltipLong=u"球顶气相/安全阀口公称通径 DN (mm)")
@param(NOZ_IN=LENGTH, TooltipShort=u"底部进口口径", TooltipLong=u"球底液相进口公称通径 DN (mm)")
@param(NOZ_OUT=LENGTH, TooltipShort=u"底部出口口径", TooltipLong=u"球底液相出口公称通径 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出高", TooltipLong=u"接管法兰面伸出球壳外壁高度 (mm)")
def EQ_SPHERICAL_TANK(
    s,
    D_SPHERE=8000.0,
    H_CLEAR=1800.0,
    D_LEG=400.0,
    NOZ_TOP=150.0,
    NOZ_IN=150.0,
    NOZ_OUT=200.0,
    NOZ_EXT=450.0,
    ID=u"EQ_SPHERICAL_TANK",
    **kw
):
    u"""GB/T 12337 球形储罐 (基础环底面 Z=0，球心位于 Z=R_S+H_CLEAR，6 根赤道支柱均布)。"""
    D_SPHERE = float(D_SPHERE)
    if D_SPHERE < 1.0:
        D_SPHERE = 1.0
    R_S = D_SPHERE / 2.0
    H_CLEAR = float(H_CLEAR)
    if H_CLEAR < 1.0:
        H_CLEAR = 1.0
    D_LEG = max(200.0, float(D_LEG))
    R_LEG = D_LEG / 2.0
    NOZ_TOP = max(80.0, float(NOZ_TOP))
    NOZ_IN = max(80.0, float(NOZ_IN))
    NOZ_OUT = max(100.0, float(NOZ_OUT))
    NOZ_EXT = max(250.0, float(NOZ_EXT))

    z_cl = R_S + H_CLEAR

    # 1. 大球体主壳
    o_main = SPHERE(s, R=R_S).translate((0.0, 0.0, z_cl))

    # 2. 6 根赤道支柱 + 支柱底板 + 底部基础环 + 支柱中部环向拉杆
    r_pcd = R_S + R_LEG * 0.25
    bp_w = D_LEG * 2.1
    bp_t = max(36.0, D_LEG * 0.1)
    ring_h = max(120.0, D_LEG * 0.35)
    ring_w = max(240.0, D_LEG * 0.75)

    # 底部连续基础环 (空心圆环)
    o_fring = CYLINDER(s, R=r_pcd + ring_w * 0.5, H=ring_h, O=r_pcd - ring_w * 0.5)
    o_main.uniteWith(o_fring)
    o_fring.erase()

    # 支柱中部水平拉杆环 (位于 Z = z_cl * 0.45)
    z_tie = z_cl * 0.44
    r_tie = max(45.0, D_LEG * 0.14)
    for i in range(6):
        a0 = math.radians(i * 60.0)
        a1 = math.radians((i + 1) * 60.0)
        x0, y0 = r_pcd * math.cos(a0), r_pcd * math.sin(a0)
        x1, y1 = r_pcd * math.cos(a1), r_pcd * math.sin(a1)
        chord = math.hypot(x1 - x0, y1 - y0)
        ang_deg = math.degrees(math.atan2(y1 - y0, x1 - x0))
        o_tr = CYLINDER(s, R=r_tie, H=chord + 20.0, O=0.0).rotateY(90.0).rotateZ(ang_deg).translate((x0, y0, z_tie))
        o_main.uniteWith(o_tr)
        o_tr.erase()

    for i in range(6):
        ang = math.radians(i * 60.0)
        lx = r_pcd * math.cos(ang)
        ly = r_pcd * math.sin(ang)
        # 支柱延伸至赤道以上 R_LEG*1.4 处确保与球壳可靠相贯
        h_col = z_cl + R_LEG * 1.4
        o_col = CYLINDER(s, R=R_LEG, H=h_col, O=0.0).translate((lx, ly, 0.0))
        o_main.uniteWith(o_col)
        o_col.erase()
        # 支柱顶封头帽
        o_cap = HALFSPHERE(s, R=R_LEG).translate((lx, ly, h_col - 2.0))
        o_main.uniteWith(o_cap)
        o_cap.erase()
        # 支柱底板
        o_bp = CORNERBOX(s, L=bp_w, W=bp_w, H=bp_t).translate((lx - bp_w * 0.5, ly - bp_w * 0.5, 0.0))
        o_main.uniteWith(o_bp)
        o_bp.erase()

    # 3. 接管构造函数
    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    # 4. 顶部人孔 (带盲盖，非端口，位于 +X 偏置)
    r_pm, r_fm, t_fm = _fl_dims(500.0)
    x_mh = R_S * 0.22
    z_mh_top = z_cl + R_S + NOZ_EXT * 0.9
    o_mhp = CYLINDER(s, R=r_pm, H=z_mh_top - (z_cl + R_S * 0.78), O=0.0).translate((x_mh, 0.0, z_cl + R_S * 0.78))
    o_mhf = CYLINDER(s, R=r_fm, H=t_fm * 1.85, O=0.0).translate((x_mh, 0.0, z_mh_top - t_fm))
    o_main.uniteWith(o_mhp)
    o_mhp.erase()
    o_main.uniteWith(o_mhf)
    o_mhf.erase()

    # 5. 3 个工艺法兰口
    # Port 1: 顶部气相/安全阀口 (+Z, 位于 -X 偏置)
    r_p1, r_f1, t_f1 = _fl_dims(NOZ_TOP)
    x_top = -R_S * 0.20
    z_top_face = z_cl + R_S + NOZ_EXT
    o_p1 = CYLINDER(s, R=r_p1, H=z_top_face - t_f1 - (z_cl + R_S * 0.78) + 2.0, O=0.0).translate((x_top, 0.0, z_cl + R_S * 0.78))
    o_f1 = CYLINDER(s, R=r_f1, H=t_f1, O=0.0).translate((x_top, 0.0, z_top_face - t_f1))
    o_main.uniteWith(o_p1)
    o_p1.erase()
    o_main.uniteWith(o_f1)
    o_f1.erase()
    p_top = (x_top, 0.0, z_top_face)

    # Port 2: 底部液相进口 (-Z, 位于 -X 偏置)
    r_p2, r_f2, t_f2 = _fl_dims(NOZ_IN)
    x_in = -R_S * 0.18
    z_in_face = max(350.0, H_CLEAR - NOZ_EXT)
    o_p2 = CYLINDER(s, R=r_p2, H=(z_cl - R_S * 0.78) - (z_in_face + t_f2) + 2.0, O=0.0).translate((x_in, 0.0, z_in_face + t_f2 - 2.0))
    o_f2 = CYLINDER(s, R=r_f2, H=t_f2, O=0.0).translate((x_in, 0.0, z_in_face))
    o_main.uniteWith(o_p2)
    o_p2.erase()
    o_main.uniteWith(o_f2)
    o_f2.erase()
    p_in = (x_in, 0.0, z_in_face)

    # Port 3: 底部液相出口 (-Z, 位于 +X 偏置)
    r_p3, r_f3, t_f3 = _fl_dims(NOZ_OUT)
    x_out = R_S * 0.18
    z_out_face = max(350.0, H_CLEAR - NOZ_EXT)
    o_p3 = CYLINDER(s, R=r_p3, H=(z_cl - R_S * 0.78) - (z_out_face + t_f3) + 2.0, O=0.0).translate((x_out, 0.0, z_out_face + t_f3 - 2.0))
    o_f3 = CYLINDER(s, R=r_f3, H=t_f3, O=0.0).translate((x_out, 0.0, z_out_face))
    o_main.uniteWith(o_p3)
    o_p3.erase()
    o_main.uniteWith(o_f3)
    o_f3.erase()
    p_out = (x_out, 0.0, z_out_face)

    # 6. 注册 3 个工艺端口
    s.setPoint(p_top, (0.0, 0.0, 1.0))
    s.setPoint(p_in, (0.0, 0.0, -1.0))
    s.setPoint(p_out, (0.0, 0.0, -1.0))

    # 7. 注册线性标注
    s.setLinearDimension('D_SPHERE', (-R_S, 0.0, z_cl), (R_S, 0.0, z_cl))
    s.setLinearDimension('H_CLEAR', (0.0, 0.0, 0.0), (0.0, 0.0, H_CLEAR))
