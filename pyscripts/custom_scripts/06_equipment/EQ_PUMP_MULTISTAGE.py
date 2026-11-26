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
          TooltipShort=u"卧式多级离心泵总成",
          TooltipLong=u"卧式节段式多级高压离心泵总成，含公共底座、吸入段、多级节段式泵体与拉紧凸缘环、吐出段、两端独立轴承箱、联轴器护罩、大功率电机及 2 个标准接管法兰",
          LengthUnit="mm",
          Ports="2")
@group("MainDimensions", TooltipLong=u"卧式多级离心泵主要几何尺寸参数")
@param(DN_SUC=LENGTH, TooltipShort=u"吸入口通径", TooltipLong=u"吸入法兰 DN (mm)")
@param(DN_DIS=LENGTH, TooltipShort=u"排出口通径", TooltipLong=u"吐出法兰 DN (mm)")
@param(L_BASE=LENGTH, TooltipShort=u"底座长度", TooltipLong=u"公共底座总长 (mm)", Ask4Dist=True)
@param(W_BASE=LENGTH, TooltipShort=u"底座宽度", TooltipLong=u"公共底座总宽 (mm)")
@param(H_BASE=LENGTH, TooltipShort=u"底座高度", TooltipLong=u"底座高度 (mm)")
@param(H_CL=LENGTH, TooltipShort=u"泵轴中心高", TooltipLong=u"地面至泵轴中心线高度 (mm)")
@param(D_STAGE=LENGTH, TooltipShort=u"中段外径", TooltipLong=u"多级泵节段外壳外径 (mm)")
@param(N_STAGES=INT, TooltipShort=u"泵级数", TooltipLong=u"多级节段数 (节)")
@param(D_MOTOR=LENGTH, TooltipShort=u"电机外径", TooltipLong=u"主驱动电机机座外径 (mm)")
@param(L_MOTOR=LENGTH, TooltipShort=u"电机长度", TooltipLong=u"电机总长 (mm)")
def EQ_PUMP_MULTISTAGE(
    s,
    DN_SUC=100.0,
    DN_DIS=80.0,
    L_BASE=2200.0,
    W_BASE=720.0,
    H_BASE=140.0,
    H_CL=460.0,
    D_STAGE=380.0,
    N_STAGES=6,
    D_MOTOR=480.0,
    L_MOTOR=760.0,
    ID=u"EQ_PUMP_MULTISTAGE",
    **kw
):
    u"""卧式多级离心泵总成 (底面 Z=0, 泵轴沿 X 轴)。"""
    L_BASE = float(L_BASE)
    if L_BASE < 1.0:
        L_BASE = 1.0
    W_BASE = max(460.0, float(W_BASE))
    H_BASE = max(100.0, float(H_BASE))
    D_STAGE = max(240.0, float(D_STAGE))
    N_STAGES = max(3, min(12, int(N_STAGES)))
    D_MOTOR = max(280.0, float(D_MOTOR))
    L_MOTOR = max(420.0, float(L_MOTOR))
    H_CL = float(H_CL)
    if H_CL < 1.0:
        H_CL = 1.0

    r_st = D_STAGE / 2.0
    r_mot = D_MOTOR / 2.0

    # 1. 公共底座
    o_main = CORNERBOX(s, L=L_BASE, W=W_BASE, H=H_BASE).translate((-L_BASE / 2.0, -W_BASE / 2.0, 0.0))

    # 2. 泵体布置 (-X 侧): 前轴承箱 + 吸入段 + 多级节段 + 吐出段 + 后轴承箱
    l_pump_stack = L_BASE * 0.40
    x_p_start = -L_BASE * 0.42
    l_brg = 150.0
    l_end = 130.0
    l_mid = max(240.0, l_pump_stack - 2.0 * l_brg - 2.0 * l_end)

    # 前轴承箱
    o_brg1 = CYLINDER(s, R=r_st * 0.45, H=l_brg, O=0.0).rotateY(90.0).translate((x_p_start, 0.0, H_CL))
    o_bs1 = CORNERBOX(s, L=l_brg * 0.8, W=r_st * 0.9, H=H_CL - H_BASE).translate((x_p_start + l_brg * 0.1, -r_st * 0.45, H_BASE))
    o_main.uniteWith(o_brg1); o_brg1.erase()
    o_main.uniteWith(o_bs1); o_bs1.erase()

    # 吸入段 + 多级中段 + 吐出段
    x_suc = x_p_start + l_brg
    o_suc_cas = CYLINDER(s, R=r_st * 1.05, H=l_end, O=0.0).rotateY(90.0).translate((x_suc, 0.0, H_CL))
    o_main.uniteWith(o_suc_cas); o_suc_cas.erase()

    x_mid0 = x_suc + l_end
    stage_l = l_mid / float(N_STAGES)
    for idx in range(N_STAGES):
        xs = x_mid0 + idx * stage_l
        o_seg = CYLINDER(s, R=r_st, H=stage_l * 0.82, O=0.0).rotateY(90.0).translate((xs, 0.0, H_CL))
        o_rib = CYLINDER(s, R=r_st * 1.08, H=stage_l * 0.22, O=0.0).rotateY(90.0).translate((xs + stage_l * 0.78, 0.0, H_CL))
        o_main.uniteWith(o_seg); o_seg.erase()
        o_main.uniteWith(o_rib); o_rib.erase()

    x_dis = x_mid0 + l_mid
    o_dis_cas = CYLINDER(s, R=r_st * 1.05, H=l_end, O=0.0).rotateY(90.0).translate((x_dis, 0.0, H_CL))
    o_brg2 = CYLINDER(s, R=r_st * 0.45, H=l_brg, O=0.0).rotateY(90.0).translate((x_dis + l_end, 0.0, H_CL))
    o_bs2 = CORNERBOX(s, L=l_brg * 0.8, W=r_st * 0.9, H=H_CL - H_BASE).translate((x_dis + l_end + l_brg * 0.1, -r_st * 0.45, H_BASE))
    o_main.uniteWith(o_dis_cas); o_dis_cas.erase()
    o_main.uniteWith(o_brg2); o_brg2.erase()
    o_main.uniteWith(o_bs2); o_bs2.erase()

    # 泵体双侧支撑脚
    for xp in (x_suc + l_end * 0.5, x_dis + l_end * 0.5):
        o_psup = CORNERBOX(s, L=110.0, W=D_STAGE * 1.1, H=H_CL - H_BASE).translate((xp - 55.0, -D_STAGE * 0.55, H_BASE))
        o_main.uniteWith(o_psup); o_psup.erase()

    # 3. 联轴器护罩 + 大电机 (+X 侧)
    x_mot0 = L_BASE * 0.46 - L_MOTOR
    x_brg2_end = x_dis + l_end + l_brg
    o_cpl = CYLINDER(s, R=r_st * 0.42, H=max(80.0, x_mot0 - x_brg2_end + 30.0), O=0.0).rotateY(90.0).translate((x_brg2_end - 15.0, 0.0, H_CL))
    o_mbase = CORNERBOX(s, L=L_MOTOR * 0.8, W=D_MOTOR * 0.86, H=H_CL - H_BASE).translate((x_mot0 + L_MOTOR * 0.1, -D_MOTOR * 0.43, H_BASE))
    o_mot = CYLINDER(s, R=r_mot, H=L_MOTOR, O=0.0).rotateY(90.0).translate((x_mot0, 0.0, H_CL))
    o_tbox = CORNERBOX(s, L=180.0, W=160.0, H=180.0).translate((x_mot0 + L_MOTOR * 0.35, r_mot * 0.65, H_CL + r_mot * 0.35))
    o_main.uniteWith(o_cpl); o_cpl.erase()
    o_main.uniteWith(o_mbase); o_mbase.erase()
    o_main.uniteWith(o_mot); o_mot.erase()
    o_main.uniteWith(o_tbox); o_tbox.erase()

    # 4. 吸入口 (顶部 +Z 或 侧向) 与 吐出口 (顶部 +Z)
    r_ps, r_fs, t_fs = _std_noz_dims(DN_SUC)
    x_s_noz = x_suc + l_end * 0.5
    z_s_face = H_CL + r_st * 1.05 + 190.0
    o_sp = CYLINDER(s, R=r_ps, H=z_s_face - t_fs - H_CL, O=0.0).translate((x_s_noz, 0.0, H_CL))
    o_sf = CYLINDER(s, R=r_fs, H=t_fs, O=0.0).translate((x_s_noz, 0.0, z_s_face - t_fs))
    o_main.uniteWith(o_sp); o_sp.erase()
    o_main.uniteWith(o_sf); o_sf.erase()

    r_pd, r_fd, t_fd = _std_noz_dims(DN_DIS)
    x_d_noz = x_dis + l_end * 0.5
    z_d_face = H_CL + r_st * 1.05 + 190.0
    o_dp = CYLINDER(s, R=r_pd, H=z_d_face - t_fd - H_CL, O=0.0).translate((x_d_noz, 0.0, H_CL))
    o_df = CYLINDER(s, R=r_fd, H=t_fd, O=0.0).translate((x_d_noz, 0.0, z_d_face - t_fd))
    o_main.uniteWith(o_dp); o_dp.erase()
    o_main.uniteWith(o_df); o_df.erase()

    s.setPoint((x_s_noz, 0.0, z_s_face), (0.0, 0.0, 1.0))
    s.setPoint((x_d_noz, 0.0, z_d_face), (0.0, 0.0, 1.0))

    s.setLinearDimension('L_BASE', (-L_BASE / 2.0, -W_BASE / 2.0, 0.0), (L_BASE / 2.0, -W_BASE / 2.0, 0.0))
    s.setLinearDimension('H_CL', (0.0, 0.0, 0.0), (0.0, 0.0, H_CL))
