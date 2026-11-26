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
          TooltipShort=u"立式夹套缓冲/储罐",
          TooltipLong=u"立式带外部传热夹套压力容器，含上下 2:1 椭圆封头、4 根管式支腿、外部夹套、顶部人孔及 5 个工艺/夹套接管法兰",
          LengthUnit="mm",
          Ports="5")
@group("MainDimensions", TooltipLong=u"立式夹套缓冲/储罐主要几何尺寸参数")
@param(D=LENGTH, TooltipShort=u"内筒公称直径", TooltipLong=u"内筒体公称直径 DN (mm)")
@param(H_SHELL=LENGTH, TooltipShort=u"内筒直边高", TooltipLong=u"内筒体圆柱段高度 (mm)", Ask4Dist=True)
@param(D_JACKET=LENGTH, TooltipShort=u"夹套外径", TooltipLong=u"外部加热/冷却夹套外径 (mm)")
@param(H_JACKET=LENGTH, TooltipShort=u"夹套高度", TooltipLong=u"外部夹套包覆高度 (mm)")
@param(H_LEG=LENGTH, TooltipShort=u"支腿高度", TooltipLong=u"底封头下切线至地面支腿基础高度 (mm)", Ask4Dist=True)
@param(N_TOP=LENGTH, TooltipShort=u"顶气相口", TooltipLong=u"顶部气相/放空口 DN (mm)")
@param(N_IN=LENGTH, TooltipShort=u"顶进料口", TooltipLong=u"顶部进料口 DN (mm)")
@param(N_BOT=LENGTH, TooltipShort=u"底出料口", TooltipLong=u"底部中心排料口 DN (mm)")
@param(N_JK=LENGTH, TooltipShort=u"夹套进出口", TooltipLong=u"夹套介质进出口 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出高", TooltipLong=u"接管法兰面伸出高度 (mm)")
def EQ_VESSEL_JACKETED_V(
    s,
    D=1200.0,
    H_SHELL=2200.0,
    D_JACKET=1360.0,
    H_JACKET=1650.0,
    H_LEG=750.0,
    N_TOP=100.0,
    N_IN=80.0,
    N_BOT=100.0,
    N_JK=50.0,
    NOZ_EXT=240.0,
    ID=u"EQ_VESSEL_JACKETED_V",
    **kw
):
    u"""立式夹套缓冲/储罐 (下封头切线 Z=0, 地面 Z=-H_LEG)。"""
    D = float(D)
    if D < 1.0:
        D = 1.0
    R_V = D / 2.0
    H_SHELL = float(H_SHELL)
    if H_SHELL < 1.0:
        H_SHELL = 1.0
    D_JACKET = max(D + 80.0, float(D_JACKET))
    R_JK = D_JACKET / 2.0
    H_JACKET = min(H_SHELL - 120.0, max(400.0, float(H_JACKET)))
    H_LEG = float(H_LEG)
    if H_LEG < 1.0:
        H_LEG = 1.0
    NOZ_EXT = max(140.0, float(NOZ_EXT))
    h_head = D * 0.25
    z_gnd = -H_LEG

    # 1. 内筒体 + 上下2:1椭圆封头
    o_main = CYLINDER(s, R=R_V, H=H_SHELL, O=0.0)
    o_top = ELLIPSOIDHEAD(s, R=R_V).translate((0.0, 0.0, H_SHELL))
    o_bot = ELLIPSOIDHEAD(s, R=R_V).rotateX(180.0)
    o_main.uniteWith(o_top); o_top.erase()
    o_main.uniteWith(o_bot); o_bot.erase()

    # 2. 外部夹套筒体 + 上下封头过渡环
    z_jk0 = 120.0
    o_jk = CYLINDER(s, R=R_JK, H=H_JACKET, O=0.0).translate((0.0, 0.0, z_jk0))
    o_jk_top = CONE(s, R1=R_JK, R2=R_V, H=55.0).translate((0.0, 0.0, z_jk0 + H_JACKET))
    o_jk_bot = CONE(s, R1=R_V, R2=R_JK, H=55.0).translate((0.0, 0.0, z_jk0 - 55.0))
    o_main.uniteWith(o_jk); o_jk.erase()
    o_main.uniteWith(o_jk_top); o_jk_top.erase()
    o_main.uniteWith(o_jk_bot); o_jk_bot.erase()

    # 3. 4 根管式支腿 + 加强垫板 + 地脚底板
    r_pcd = R_V * 0.88
    r_leg = max(45.0, D * 0.055)
    base_w = r_leg * 3.2
    base_t = 18.0
    z_leg_top = R_V * 0.35
    for ang_deg in (45.0, 135.0, 225.0, 315.0):
        rad = math.radians(ang_deg)
        lx, ly = r_pcd * math.cos(rad), r_pcd * math.sin(rad)
        o_leg = CYLINDER(s, R=r_leg, H=z_leg_top - (z_gnd + base_t), O=0.0).translate((lx, ly, z_gnd + base_t))
        o_bp = CORNERBOX(s, L=base_w, W=base_w, H=base_t).translate((lx - base_w / 2.0, ly - base_w / 2.0, z_gnd))
        o_main.uniteWith(o_leg); o_leg.erase()
        o_main.uniteWith(o_bp); o_bp.erase()

    # 4. 顶部人孔 (DN400 带盲盖, 非连接端口)
    r_pm, r_fm, t_fm = _std_noz_dims(400.0)
    z_mh_top = H_SHELL + h_head + NOZ_EXT * 0.85
    o_mhp = CYLINDER(s, R=r_pm, H=z_mh_top - (H_SHELL + h_head * 0.4), O=0.0).translate((R_V * 0.48, 0.0, H_SHELL + h_head * 0.4))
    o_mhf = CYLINDER(s, R=r_fm, H=t_fm * 1.6, O=0.0).translate((R_V * 0.48, 0.0, z_mh_top - t_fm))
    o_main.uniteWith(o_mhp); o_mhp.erase()
    o_main.uniteWith(o_mhf); o_mhf.erase()

    # 5. 五个工艺与夹套接口
    # Port 1: 顶部中心气相口
    r_p1, r_f1, t_f1 = _std_noz_dims(N_TOP)
    z_p1 = H_SHELL + h_head + NOZ_EXT
    o_p1 = CYLINDER(s, R=r_p1, H=z_p1 - t_f1 - (H_SHELL + h_head * 0.5), O=0.0).translate((0.0, 0.0, H_SHELL + h_head * 0.5))
    o_f1 = CYLINDER(s, R=r_f1, H=t_f1, O=0.0).translate((0.0, 0.0, z_p1 - t_f1))
    o_main.uniteWith(o_p1); o_p1.erase()
    o_main.uniteWith(o_f1); o_f1.erase()

    # Port 2: 顶部偏心进料口 (-X)
    r_p2, r_f2, t_f2 = _std_noz_dims(N_IN)
    z_p2 = H_SHELL + h_head + NOZ_EXT
    x_p2 = -R_V * 0.52
    o_p2 = CYLINDER(s, R=r_p2, H=z_p2 - t_f2 - (H_SHELL + h_head * 0.35), O=0.0).translate((x_p2, 0.0, H_SHELL + h_head * 0.35))
    o_f2 = CYLINDER(s, R=r_f2, H=t_f2, O=0.0).translate((x_p2, 0.0, z_p2 - t_f2))
    o_main.uniteWith(o_p2); o_p2.erase()
    o_main.uniteWith(o_f2); o_f2.erase()

    # Port 3 & 4: 夹套上部出口 (+X) 与 夹套下部进口 (-X)
    r_pj, r_fj, t_fj = _std_noz_dims(N_JK)
    x_jk_face = R_JK + NOZ_EXT * 0.85
    z_jk_hi = z_jk0 + H_JACKET - 180.0
    z_jk_lo = z_jk0 + 180.0
    o_p3 = CYLINDER(s, R=r_pj, H=x_jk_face - t_fj - R_JK * 0.85, O=0.0).rotateY(90.0).translate((R_JK * 0.85, 0.0, z_jk_hi))
    o_f3 = CYLINDER(s, R=r_fj, H=t_fj, O=0.0).rotateY(90.0).translate((x_jk_face - t_fj, 0.0, z_jk_hi))
    o_main.uniteWith(o_p3); o_p3.erase()
    o_main.uniteWith(o_f3); o_f3.erase()

    o_p4 = CYLINDER(s, R=r_pj, H=x_jk_face - t_fj - R_JK * 0.85, O=0.0).rotateY(-90.0).translate((-R_JK * 0.85, 0.0, z_jk_lo))
    o_f4 = CYLINDER(s, R=r_fj, H=t_fj, O=0.0).rotateY(-90.0).translate((-x_jk_face + t_fj, 0.0, z_jk_lo))
    o_main.uniteWith(o_p4); o_p4.erase()
    o_main.uniteWith(o_f4); o_f4.erase()

    # Port 5: 底部中心排料口 (-Z)
    r_p5, r_f5, t_f5 = _std_noz_dims(N_BOT)
    z_p5 = max(z_gnd + 110.0, -(h_head + NOZ_EXT * 0.85))
    o_p5 = CYLINDER(s, R=r_p5, H=(-h_head * 0.5) - (z_p5 + t_f5), O=0.0).translate((0.0, 0.0, z_p5 + t_f5))
    o_f5 = CYLINDER(s, R=r_f5, H=t_f5, O=0.0).translate((0.0, 0.0, z_p5))
    o_main.uniteWith(o_p5); o_p5.erase()
    o_main.uniteWith(o_f5); o_f5.erase()

    s.setPoint((0.0, 0.0, z_p1), (0.0, 0.0, 1.0))
    s.setPoint((x_p2, 0.0, z_p2), (0.0, 0.0, 1.0))
    s.setPoint((x_jk_face, 0.0, z_jk_hi), (1.0, 0.0, 0.0))
    s.setPoint((-x_jk_face, 0.0, z_jk_lo), (-1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, z_p5), (0.0, 0.0, -1.0))

    s.setLinearDimension('D', (-R_V, 0.0, H_SHELL * 0.5), (R_V, 0.0, H_SHELL * 0.5))
    s.setLinearDimension('H_SHELL', (R_JK + 120.0, 0.0, 0.0), (R_JK + 120.0, 0.0, H_SHELL))
    s.setLinearDimension('H_LEG', (R_V, 0.0, z_gnd), (R_V, 0.0, 0.0))
