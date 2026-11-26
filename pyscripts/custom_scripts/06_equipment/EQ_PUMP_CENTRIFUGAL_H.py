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
          TooltipShort=u"卧式单级离心泵总成 (GB/T 5662 / ISO 2858)",
          TooltipLong=u"GB/T 5662 / ISO 2858 卧式单级单吸离心泵总成，含公共槽钢底座、蜗壳、轴向吸入/顶部排出法兰、联轴器护罩及卧式电机",
          LengthUnit="mm",
          Ports="2")
@group("MainDimensions", TooltipLong=u"卧式单级离心泵总成底座、泵头与电机主要尺寸参数")
@param(DN_SUC=LENGTH, TooltipShort=u"吸入口通径", TooltipLong=u"轴向吸入法兰公称通径 DN (mm)")
@param(DN_DIS=LENGTH, TooltipShort=u"排出口通径", TooltipLong=u"顶部排出法兰公称通径 DN (mm)")
@param(L_BASE=LENGTH, TooltipShort=u"公共底座长", TooltipLong=u"公共槽钢底座总长 L (mm)", Ask4Dist=True)
@param(W_BASE=LENGTH, TooltipShort=u"公共底座宽", TooltipLong=u"公共槽钢底座总宽 W (mm)")
@param(H_BASE=LENGTH, TooltipShort=u"底座高度", TooltipLong=u"公共底座槽钢高度 (mm)")
@param(H_CL=LENGTH, TooltipShort=u"泵轴中心高", TooltipLong=u"底座底面至泵轴中心线高度 H (mm)", Ask4Dist=True)
@param(D_VOLUTE=LENGTH, TooltipShort=u"蜗壳外径", TooltipLong=u"离心泵蜗壳外径 (mm)")
@param(H_DIS=LENGTH, TooltipShort=u"排出口标高", TooltipLong=u"底座底面至顶部排出法兰面总高 (mm)", Ask4Dist=True)
@param(D_MOTOR=LENGTH, TooltipShort=u"电机机座外径", TooltipLong=u"卧式驱动电机外壳外径 (mm)")
@param(L_MOTOR=LENGTH, TooltipShort=u"电机总长", TooltipLong=u"卧式驱动电机机身长度 (mm)")
def EQ_PUMP_CENTRIFUGAL_H(
    s,
    DN_SUC=80.0,
    DN_DIS=65.0,
    L_BASE=1150.0,
    W_BASE=460.0,
    H_BASE=100.0,
    H_CL=280.0,
    D_VOLUTE=280.0,
    H_DIS=480.0,
    D_MOTOR=260.0,
    L_MOTOR=420.0,
    ID=u"EQ_PUMP_CENTRIFUGAL_H",
    **kw
):
    u"""GB/T 5662 卧式单级离心泵 (底座底面 Z=0，泵轴沿 X 轴，吸入口在 -X，电机在 +X，排出口朝 +Z)。"""
    DN_SUC = max(25.0, float(DN_SUC))
    DN_DIS = max(20.0, float(DN_DIS))
    L_BASE = float(L_BASE)
    if L_BASE < 1.0:
        L_BASE = 1.0
    W_BASE = float(W_BASE)
    if W_BASE < 1.0:
        W_BASE = 1.0
    H_BASE = max(60.0, float(H_BASE))
    D_VOLUTE = max(160.0, float(D_VOLUTE))
    R_VOL = D_VOLUTE / 2.0
    D_MOTOR = max(140.0, float(D_MOTOR))
    R_MOT = D_MOTOR / 2.0
    L_MOTOR = max(220.0, float(L_MOTOR))
    H_CL = float(H_CL)
    if H_CL < 1.0:
        H_CL = 1.0
    H_DIS = float(H_DIS)
    if H_DIS < 1.0:
        H_DIS = 1.0

    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    r_ps, r_fs, t_fs = _fl_dims(DN_SUC)
    r_pd, r_fd, t_fd = _fl_dims(DN_DIS)

    # X 坐标布局: 泵头中心在 x_vol, 底座从 x_base0 到 x_base0 + L_BASE
    x_vol = 0.0
    vol_w = max(90.0, D_VOLUTE * 0.36)
    suc_ext = max(110.0, D_VOLUTE * 0.42)
    x_suc_face = -(vol_w / 2.0 + suc_ext)
    x_base0 = x_suc_face + 40.0
    x_base1 = x_base0 + L_BASE

    # 1. 公共槽钢底座 (顶板 + 两侧纵梁 + 两端横梁)
    o_main = CORNERBOX(s, L=L_BASE, W=W_BASE, H=H_BASE * 0.35).translate(
        (x_base0, -W_BASE / 2.0, H_BASE * 0.65)
    )
    beam_w = max(35.0, W_BASE * 0.14)
    for sy in (-1.0, 1.0):
        o_rail = CORNERBOX(s, L=L_BASE, W=beam_w, H=H_BASE).translate(
            (x_base0, sy * (W_BASE / 2.0 - beam_w / 2.0) - beam_w / 2.0, 0.0)
        )
        o_main.uniteWith(o_rail)
        o_rail.erase()
    for sx_end in (x_base0, x_base1 - beam_w):
        o_end = CORNERBOX(s, L=beam_w, W=W_BASE, H=H_BASE).translate(
            (sx_end, -W_BASE / 2.0, 0.0)
        )
        o_main.uniteWith(o_end)
        o_end.erase()

    # 2. 泵体蜗壳 + 支脚
    o_vol = CYLINDER(s, R=R_VOL, H=vol_w, O=0.0).rotateY(90.0).translate((-vol_w / 2.0, 0.0, H_CL))
    o_main.uniteWith(o_vol)
    o_vol.erase()

    foot_w = W_BASE * 0.62
    o_pfoot = CORNERBOX(s, L=vol_w * 0.85, W=foot_w, H=H_CL - H_BASE + 20.0).translate(
        (-vol_w * 0.425, -foot_w / 2.0, H_BASE - 10.0)
    )
    o_main.uniteWith(o_pfoot)
    o_pfoot.erase()

    # 3. 轴向吸入接管与法兰 (Port 1, -X)
    o_sp = CYLINDER(s, R=r_ps, H=suc_ext + 20.0, O=0.0).rotateY(-90.0).translate((-vol_w / 2.0 + 15.0, 0.0, H_CL))
    o_sf = CYLINDER(s, R=r_fs, H=t_fs, O=0.0).rotateY(-90.0).translate((x_suc_face + t_fs, 0.0, H_CL))
    o_main.uniteWith(o_sp)
    o_sp.erase()
    o_main.uniteWith(o_sf)
    o_sf.erase()

    # 4. 顶部排出接管与法兰 (Port 2, +Z)
    dis_h = H_DIS - H_CL - t_fd
    o_dp = CYLINDER(s, R=r_pd, H=dis_h + 15.0, O=0.0).translate((0.0, 0.0, H_CL - 10.0))
    o_df = CYLINDER(s, R=r_fd, H=t_fd, O=0.0).translate((0.0, 0.0, H_DIS - t_fd))
    o_main.uniteWith(o_dp)
    o_dp.erase()
    o_main.uniteWith(o_df)
    o_df.erase()

    # 5. 轴承悬架体 + 支承脚
    x_brg0 = vol_w / 2.0 - 10.0
    l_brg = max(180.0, L_BASE * 0.22)
    r_brg = max(55.0, R_VOL * 0.44)
    o_brg = CYLINDER(s, R=r_brg, H=l_brg, O=0.0).rotateY(90.0).translate((x_brg0, 0.0, H_CL))
    o_bfoot = CORNERBOX(s, L=l_brg * 0.35, W=W_BASE * 0.45, H=H_CL - H_BASE + 15.0).translate(
        (x_brg0 + l_brg * 0.55, -W_BASE * 0.225, H_BASE - 10.0)
    )
    o_main.uniteWith(o_brg)
    o_brg.erase()
    o_main.uniteWith(o_bfoot)
    o_bfoot.erase()

    # 6. 联轴器护罩 (半圆顶矩形罩)
    x_cpl0 = x_brg0 + l_brg - 10.0
    l_cpl = max(130.0, L_BASE * 0.14)
    r_cpl = max(65.0, r_brg * 1.18)
    o_cpl = CYLINDER(s, R=r_cpl, H=l_cpl, O=0.0).rotateY(90.0).translate((x_cpl0, 0.0, H_CL))
    o_cpl_leg = CORNERBOX(s, L=l_cpl * 0.85, W=r_cpl * 1.6, H=H_CL - H_BASE + 15.0).translate(
        (x_cpl0 + l_cpl * 0.075, -r_cpl * 0.8, H_BASE - 10.0)
    )
    o_main.uniteWith(o_cpl)
    o_cpl.erase()
    o_main.uniteWith(o_cpl_leg)
    o_cpl_leg.erase()

    # 7. 卧式驱动电机 (机身 + 散热筋环 + 顶接线盒 + 电机底座支脚)
    x_mot0 = x_cpl0 + l_cpl - 10.0
    o_mot = CYLINDER(s, R=R_MOT, H=L_MOTOR, O=0.0).rotateY(90.0).translate((x_mot0, 0.0, H_CL))
    o_main.uniteWith(o_mot)
    o_mot.erase()

    # 电机后端风罩
    o_cowl = CYLINDER(s, R=R_MOT * 0.96, H=L_MOTOR * 0.18, O=0.0).rotateY(90.0).translate(
        (x_mot0 + L_MOTOR - 5.0, 0.0, H_CL)
    )
    o_main.uniteWith(o_cowl)
    o_cowl.erase()

    # 电机顶部接线盒
    tb_l = L_MOTOR * 0.28
    tb_w = D_MOTOR * 0.42
    tb_h = D_MOTOR * 0.28
    o_tbox = CORNERBOX(s, L=tb_l, W=tb_w, H=tb_h).translate(
        (x_mot0 + L_MOTOR * 0.22, -tb_w / 2.0, H_CL + R_MOT - 18.0)
    )
    o_main.uniteWith(o_tbox)
    o_tbox.erase()

    # 电机双侧支脚垫块 (落在底座上)
    mfoot_l = L_MOTOR * 0.72
    mfoot_w = W_BASE * 0.76
    o_mfoot = CORNERBOX(s, L=mfoot_l, W=mfoot_w, H=H_CL - H_BASE + 15.0).translate(
        (x_mot0 + L_MOTOR * 0.14, -mfoot_w / 2.0, H_BASE - 10.0)
    )
    o_main.uniteWith(o_mfoot)
    o_mfoot.erase()

    # 8. 注册 2 个端口
    s.setPoint((x_suc_face, 0.0, H_CL), (-1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, H_DIS), (0.0, 0.0, 1.0))

    # 9. 注册线性标注
    s.setLinearDimension('L_BASE', (x_base0, -W_BASE / 2.0, 0.0), (x_base1, -W_BASE / 2.0, 0.0))
    s.setLinearDimension('W_BASE', (x_base0, -W_BASE / 2.0, 0.0), (x_base0, W_BASE / 2.0, 0.0))
    s.setLinearDimension('H_CL', (x_suc_face, 0.0, 0.0), (x_suc_face, 0.0, H_CL))
    s.setLinearDimension('H_DIS', (0.0, 0.0, 0.0), (0.0, 0.0, H_DIS))
