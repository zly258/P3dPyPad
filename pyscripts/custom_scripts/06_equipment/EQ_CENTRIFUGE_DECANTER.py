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
          TooltipShort=u"卧螺沉降离心机",
          TooltipLong=u"卧式螺旋卸料沉降离心机，含重型减振机座、圆柱+圆锥转鼓分箱保护罩、主副双驱动电机、差速器端壳体及进料/液相/固相 3 个工艺接口",
          LengthUnit="mm",
          Ports="3")
@group("MainDimensions", TooltipLong=u"卧螺沉降离心机主要几何尺寸参数")
@param(DN_FEED=LENGTH, TooltipShort=u"进料口通径", TooltipLong=u"轴向中心进料口 DN (mm)")
@param(DN_LIQ=LENGTH, TooltipShort=u"清液出口", TooltipLong=u"液相清液排出口 DN (mm)")
@param(DN_SOL=LENGTH, TooltipShort=u"排渣口", TooltipLong=u"固相排渣口 DN (mm)")
@param(L_BASE=LENGTH, TooltipShort=u"机座总长", TooltipLong=u"离心机整体机座长度 (mm)", Ask4Dist=True)
@param(W_BASE=LENGTH, TooltipShort=u"机座总宽", TooltipLong=u"离心机机座宽度 (mm)")
@param(H_CL=LENGTH, TooltipShort=u"主轴中心高", TooltipLong=u"地面至转鼓中心线高度 (mm)")
@param(D_BOWL=LENGTH, TooltipShort=u"转鼓罩外径", TooltipLong=u"圆柱段转鼓外保护罩直径 (mm)")
def EQ_CENTRIFUGE_DECANTER(
    s,
    DN_FEED=80.0,
    DN_LIQ=150.0,
    DN_SOL=200.0,
    L_BASE=3200.0,
    W_BASE=1250.0,
    H_CL=860.0,
    D_BOWL=760.0,
    ID=u"EQ_CENTRIFUGE_DECANTER",
    **kw
):
    u"""卧螺沉降离心机 (底面 Z=0, 转鼓沿 X 轴)。"""
    L_BASE = float(L_BASE)
    if L_BASE < 1.0:
        L_BASE = 1.0
    W_BASE = max(900.0, float(W_BASE))
    D_BOWL = max(480.0, float(D_BOWL))
    R_BW = D_BOWL / 2.0
    H_CL = float(H_CL)
    if H_CL < 1.0:
        H_CL = 1.0

    # 1. 重型减振机座
    h_base = 220.0
    o_main = CORNERBOX(s, L=L_BASE, W=W_BASE, H=h_base).translate((-L_BASE / 2.0, -W_BASE / 2.0, 0.0))

    # 2. 圆柱段 + 圆锥段转鼓保护罩
    l_cyl = L_BASE * 0.44
    l_cone = L_BASE * 0.24
    x_cyl0 = -L_BASE * 0.24
    o_cyl = CYLINDER(s, R=R_BW, H=l_cyl, O=0.0).rotateY(90.0).translate((x_cyl0, 0.0, H_CL))
    o_cone = CONE(s, R1=R_BW * 0.56, R2=R_BW, H=l_cone).rotateY(90.0).translate((x_cyl0 - l_cone, 0.0, H_CL))
    # 罩体水平分箱凸缘
    o_split = CORNERBOX(s, L=l_cyl + l_cone * 0.85, W=D_BOWL + 90.0, H=38.0).translate((x_cyl0 - l_cone * 0.85, -(D_BOWL + 90.0) / 2.0, H_CL - 19.0))
    o_main.uniteWith(o_cyl); o_cyl.erase()
    o_main.uniteWith(o_cone); o_cone.erase()
    o_main.uniteWith(o_split); o_split.erase()

    # 前后轴承座支撑
    for xb in (x_cyl0 - l_cone - 90.0, x_cyl0 + l_cyl + 90.0):
        o_bsup = CORNERBOX(s, L=180.0, W=D_BOWL * 0.65, H=H_CL - h_base).translate((xb - 90.0, -D_BOWL * 0.325, h_base))
        o_brg = CYLINDER(s, R=R_BW * 0.36, H=200.0, O=0.0).rotateY(90.0).translate((xb - 100.0, 0.0, H_CL))
        o_main.uniteWith(o_bsup); o_bsup.erase()
        o_main.uniteWith(o_brg); o_brg.erase()

    # 3. 差速器壳体 (+X 端) 与 主/副驱动电机 (侧面 +Y)
    x_diff = x_cyl0 + l_cyl + 190.0
    o_diff = CYLINDER(s, R=R_BW * 0.48, H=240.0, O=0.0).rotateY(90.0).translate((x_diff, 0.0, H_CL))
    o_main.uniteWith(o_diff); o_diff.erase()

    # 主电机 (+Y 侧)
    r_m1 = R_BW * 0.44
    l_m1 = L_BASE * 0.24
    y_m1 = W_BASE * 0.32
    o_m1 = CYLINDER(s, R=r_m1, H=l_m1, O=0.0).rotateY(90.0).translate((x_cyl0 + l_cyl * 0.25, y_m1, h_base + r_m1 + 80.0))
    o_m1s = CORNERBOX(s, L=l_m1 * 0.85, W=r_m1 * 1.8, H=100.0).translate((x_cyl0 + l_cyl * 0.25 + l_m1 * 0.075, y_m1 - r_m1 * 0.9, h_base))
    o_belt1 = CORNERBOX(s, L=140.0, W=y_m1 + 60.0, H=H_CL - h_base + 80.0).translate((x_cyl0 + l_cyl + 40.0, -30.0, h_base + 40.0))
    o_main.uniteWith(o_m1); o_m1.erase()
    o_main.uniteWith(o_m1s); o_m1s.erase()
    o_main.uniteWith(o_belt1); o_belt1.erase()

    # 副电机 (-Y 侧)
    r_m2 = R_BW * 0.30
    l_m2 = L_BASE * 0.16
    y_m2 = -W_BASE * 0.32
    o_m2 = CYLINDER(s, R=r_m2, H=l_m2, O=0.0).rotateY(90.0).translate((x_cyl0 + l_cyl * 0.35, y_m2, h_base + r_m2 + 60.0))
    o_m2s = CORNERBOX(s, L=l_m2 * 0.85, W=r_m2 * 1.8, H=80.0).translate((x_cyl0 + l_cyl * 0.35 + l_m2 * 0.075, y_m2 - r_m2 * 0.9, h_base))
    o_main.uniteWith(o_m2); o_m2.erase()
    o_main.uniteWith(o_m2s); o_m2s.erase()

    # 4. 三个工艺接管法兰: 轴向进料口 (+X), 底部清液出口 (-Z), 底部固相排渣口 (-Z)
    r_pf, r_ff, t_ff = _std_noz_dims(DN_FEED)
    x_feed = x_diff + 240.0 + 180.0
    o_fp = CYLINDER(s, R=r_pf, H=x_feed - t_ff - x_diff, O=0.0).rotateY(90.0).translate((x_diff, 0.0, H_CL))
    o_ff = CYLINDER(s, R=r_ff, H=t_ff, O=0.0).rotateY(90.0).translate((x_feed - t_ff, 0.0, H_CL))
    o_main.uniteWith(o_fp); o_fp.erase()
    o_main.uniteWith(o_ff); o_ff.erase()

    r_pl, r_fl, t_fl = _std_noz_dims(DN_LIQ)
    x_liq = x_cyl0 + l_cyl * 0.72
    z_liq = h_base + 110.0
    o_lp = CYLINDER(s, R=r_pl, H=H_CL - z_liq, O=0.0).translate((x_liq, 0.0, z_liq))
    o_lf = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).translate((x_liq, 0.0, z_liq))
    o_main.uniteWith(o_lp); o_lp.erase()
    o_main.uniteWith(o_lf); o_lf.erase()

    r_ps, r_fs, t_fs = _std_noz_dims(DN_SOL)
    x_sol = x_cyl0 - l_cone * 0.75
    z_sol = h_base + 110.0
    o_sp = CYLINDER(s, R=r_ps, H=H_CL - z_sol, O=0.0).translate((x_sol, 0.0, z_sol))
    o_sf = CYLINDER(s, R=r_fs, H=t_fs, O=0.0).translate((x_sol, 0.0, z_sol))
    o_main.uniteWith(o_sp); o_sp.erase()
    o_main.uniteWith(o_sf); o_sf.erase()

    s.setPoint((x_feed, 0.0, H_CL), (1.0, 0.0, 0.0))
    s.setPoint((x_liq, 0.0, z_liq), (0.0, 0.0, -1.0))
    s.setPoint((x_sol, 0.0, z_sol), (0.0, 0.0, -1.0))

    s.setLinearDimension('L_BASE', (-L_BASE / 2.0, -W_BASE / 2.0, 0.0), (L_BASE / 2.0, -W_BASE / 2.0, 0.0))
    s.setLinearDimension('H_CL', (0.0, 0.0, 0.0), (0.0, 0.0, H_CL))
