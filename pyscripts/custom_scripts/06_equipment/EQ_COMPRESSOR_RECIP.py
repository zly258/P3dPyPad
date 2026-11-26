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
          TooltipShort=u"往复式活塞压缩机撬块",
          TooltipLong=u"往复式活塞压缩机撬装机组，含公共槽钢底座、中央曲轴箱、驱动电机、水平对称双气缸、顶部吸气与侧部排气缓冲罐及 2 个工艺接管法兰",
          LengthUnit="mm",
          Ports="2")
@group("MainDimensions", TooltipLong=u"往复式活塞压缩机撬块主要外形尺寸参数")
@param(DN_SUC=LENGTH, TooltipShort=u"吸气口通径", TooltipLong=u"压缩机进气缓冲罐吸气口 DN (mm)")
@param(DN_DIS=LENGTH, TooltipShort=u"排气口通径", TooltipLong=u"压缩机排气缓冲罐出口 DN (mm)")
@param(L_SKID=LENGTH, TooltipShort=u"撬块总长", TooltipLong=u"公共钢结构撬块长度 (mm)", Ask4Dist=True)
@param(W_SKID=LENGTH, TooltipShort=u"撬块总宽", TooltipLong=u"公共钢结构撬块宽度 (mm)", Ask4Dist=True)
@param(H_SKID=LENGTH, TooltipShort=u"底座高度", TooltipLong=u"槽钢底座高度 (mm)")
@param(H_CL=LENGTH, TooltipShort=u"曲轴中心高", TooltipLong=u"地面至曲轴中心线高度 (mm)")
@param(D_CYL=LENGTH, TooltipShort=u"气缸外径", TooltipLong=u"水平对置气缸外径 (mm)")
@param(D_MOTOR=LENGTH, TooltipShort=u"电机外径", TooltipLong=u"主驱动防爆电机机座外径 (mm)")
@param(L_MOTOR=LENGTH, TooltipShort=u"电机长度", TooltipLong=u"主驱动电机总长 (mm)")
def EQ_COMPRESSOR_RECIP(
    s,
    DN_SUC=150.0,
    DN_DIS=100.0,
    L_SKID=3800.0,
    W_SKID=2400.0,
    H_SKID=260.0,
    H_CL=920.0,
    D_CYL=460.0,
    D_MOTOR=680.0,
    L_MOTOR=1100.0,
    ID=u"EQ_COMPRESSOR_RECIP",
    **kw
):
    u"""往复式活塞压缩机撬块 (底面 Z=0, 曲轴沿 X 轴, 对称双气缸沿 Y 轴)。"""
    L_SKID = float(L_SKID)
    if L_SKID < 1.0:
        L_SKID = 1.0
    W_SKID = float(W_SKID)
    if W_SKID < 1.0:
        W_SKID = 1.0
    H_SKID = max(180.0, float(H_SKID))
    D_CYL = max(280.0, float(D_CYL))
    D_MOTOR = max(420.0, float(D_MOTOR))
    L_MOTOR = max(650.0, float(L_MOTOR))
    H_CL = max(H_SKID + D_MOTOR * 0.58, float(H_CL))

    # 1. 公共钢结构撬块底座 (纵梁 + 横梁 + 顶面板)
    o_main = CORNERBOX(s, L=L_SKID, W=W_SKID, H=H_SKID * 0.35).translate((-L_SKID / 2.0, -W_SKID / 2.0, H_SKID * 0.65))
    beam_w = 140.0
    for sy in (-1.0, 1.0):
        o_lb = CORNERBOX(s, L=L_SKID, W=beam_w, H=H_SKID * 0.7).translate((-L_SKID / 2.0, sy * (W_SKID / 2.0 - beam_w / 2.0) - beam_w / 2.0, 0.0))
        o_main.uniteWith(o_lb); o_lb.erase()
    for sx in (-0.45, -0.15, 0.15, 0.45):
        o_cb = CORNERBOX(s, L=beam_w, W=W_SKID - 60.0, H=H_SKID * 0.68).translate((sx * L_SKID - beam_w / 2.0, -(W_SKID - 60.0) / 2.0, 0.0))
        o_main.uniteWith(o_cb); o_cb.erase()

    # 2. 主驱动电机 (位于 -X 侧)
    x_mot_end = -L_SKID * 0.12
    x_mot_start = x_mot_end - L_MOTOR
    r_mot = D_MOTOR / 2.0
    o_mbase = CORNERBOX(s, L=L_MOTOR * 0.85, W=D_MOTOR * 0.9, H=H_CL - H_SKID).translate((x_mot_start + L_MOTOR * 0.075, -D_MOTOR * 0.45, H_SKID))
    o_mot = CYLINDER(s, R=r_mot, H=L_MOTOR, O=0.0).rotateY(90.0).translate((x_mot_start, 0.0, H_CL))
    o_main.uniteWith(o_mbase); o_mbase.erase()
    o_main.uniteWith(o_mot); o_mot.erase()
    # 电机散热筋 + 接线盒
    for k in range(6):
        ang = math.radians(k * 60.0 + 30.0)
        fy = (r_mot - 5.0) * math.cos(ang)
        fz = H_CL + (r_mot - 5.0) * math.sin(ang)
        o_fin = CORNERBOX(s, L=L_MOTOR * 0.72, W=26.0, H=26.0).translate((x_mot_start + L_MOTOR * 0.14, fy - 13.0, fz - 13.0))
        o_main.uniteWith(o_fin); o_fin.erase()
    o_tbox = CORNERBOX(s, L=240.0, W=220.0, H=240.0).translate((x_mot_start + L_MOTOR * 0.4, r_mot * 0.65, H_CL + r_mot * 0.35))
    o_main.uniteWith(o_tbox); o_tbox.erase()

    # 3. 联轴器护罩 + 中央曲轴箱 (+X 侧)
    x_crank_c = L_SKID * 0.16
    crank_l = L_SKID * 0.28
    crank_w = W_SKID * 0.28
    crank_h = D_CYL * 1.15
    o_cpl = CYLINDER(s, R=D_MOTOR * 0.32, H=(x_crank_c - crank_l / 2.0) - x_mot_end + 40.0, O=0.0).rotateY(90.0).translate((x_mot_end - 20.0, 0.0, H_CL))
    o_cped = CORNERBOX(s, L=crank_l, W=crank_w, H=H_CL - H_SKID).translate((x_crank_c - crank_l / 2.0, -crank_w / 2.0, H_SKID))
    o_crank = CORNERBOX(s, L=crank_l, W=crank_w, H=crank_h).translate((x_crank_c - crank_l / 2.0, -crank_w / 2.0, H_CL - crank_h * 0.45))
    o_main.uniteWith(o_cpl); o_cpl.erase()
    o_main.uniteWith(o_cped); o_cped.erase()
    o_main.uniteWith(o_crank); o_crank.erase()

    # 4. 水平对称双气缸 (沿 Y 轴伸出)
    r_cyl = D_CYL / 2.0
    cyl_len = W_SKID * 0.24
    neck_len = W_SKID * 0.12
    for sy in (-1.0, 1.0):
        y_n0 = sy * (crank_w / 2.0 - 15.0)
        y_c0 = sy * (crank_w / 2.0 + neck_len)
        rot = -90.0 if sy > 0 else 90.0
        o_neck = CYLINDER(s, R=r_cyl * 0.56, H=neck_len + 25.0, O=0.0).rotateX(rot).translate((x_crank_c, y_n0, H_CL))
        o_cyl = CYLINDER(s, R=r_cyl, H=cyl_len, O=0.0).rotateX(rot).translate((x_crank_c, y_c0, H_CL))
        o_head = CYLINDER(s, R=r_cyl * 1.12, H=48.0, O=0.0).rotateX(rot).translate((x_crank_c, y_c0 + sy * cyl_len, H_CL))
        o_sup = CORNERBOX(s, L=D_CYL * 0.6, W=cyl_len * 0.6, H=H_CL - r_cyl * 0.6 - H_SKID).translate((x_crank_c - D_CYL * 0.3, (y_c0 + sy * cyl_len * 0.5) - cyl_len * 0.3, H_SKID))
        o_main.uniteWith(o_neck); o_neck.erase()
        o_main.uniteWith(o_cyl); o_cyl.erase()
        o_main.uniteWith(o_head); o_head.erase()
        o_main.uniteWith(o_sup); o_sup.erase()

    # 5. 顶部吸气缓冲罐 + 侧旁排气缓冲罐
    r_buf = max(180.0, D_CYL * 0.48)
    l_buf = W_SKID * 0.72
    z_suc_buf = H_CL + r_cyl + r_buf + 160.0
    o_sbuf = CYLINDER(s, R=r_buf, H=l_buf, O=0.0).rotateX(-90.0).translate((x_crank_c, -l_buf / 2.0, z_suc_buf))
    for sy in (-1.0, 1.0):
        o_shd = ELLIPSOIDHEAD(s, R=r_buf).rotateX(-90.0 if sy > 0 else 90.0).translate((x_crank_c, sy * l_buf / 2.0, z_suc_buf))
        o_riser = CYLINDER(s, R=r_buf * 0.35, H=z_suc_buf - H_CL, O=0.0).translate((x_crank_c, sy * (crank_w / 2.0 + neck_len + cyl_len * 0.5), H_CL))
        o_main.uniteWith(o_shd); o_shd.erase()
        o_main.uniteWith(o_riser); o_riser.erase()
    o_main.uniteWith(o_sbuf); o_sbuf.erase()

    x_dbuf = L_SKID * 0.40
    z_dbuf = H_SKID + r_buf + 90.0
    o_dbuf = CYLINDER(s, R=r_buf * 0.92, H=l_buf, O=0.0).rotateX(-90.0).translate((x_dbuf, -l_buf / 2.0, z_dbuf))
    o_main.uniteWith(o_dbuf); o_dbuf.erase()
    for sy in (-1.0, 1.0):
        o_dhd = ELLIPSOIDHEAD(s, R=r_buf * 0.92).rotateX(-90.0 if sy > 0 else 90.0).translate((x_dbuf, sy * l_buf / 2.0, z_dbuf))
        o_dpipe = CYLINDER(s, R=r_buf * 0.32, H=x_dbuf - x_crank_c, O=0.0).rotateY(90.0).translate((x_crank_c, sy * (crank_w / 2.0 + neck_len + cyl_len * 0.5), z_dbuf))
        o_dv = CYLINDER(s, R=r_buf * 0.32, H=H_CL - z_dbuf + 20.0, O=0.0).translate((x_crank_c, sy * (crank_w / 2.0 + neck_len + cyl_len * 0.5), z_dbuf))
        o_dsup = CORNERBOX(s, L=r_buf, W=140.0, H=z_dbuf - H_SKID).translate((x_dbuf - r_buf / 2.0, sy * l_buf * 0.32 - 70.0, H_SKID))
        o_main.uniteWith(o_dhd); o_dhd.erase()
        o_main.uniteWith(o_dpipe); o_dpipe.erase()
        o_main.uniteWith(o_dv); o_dv.erase()
        o_main.uniteWith(o_dsup); o_dsup.erase()

    # 6. 吸气口 (Port 1: +Z) 与 排气口 (Port 2: +X)
    r_ps, r_fs, t_fs = _std_noz_dims(DN_SUC)
    z_suc_face = z_suc_buf + r_buf + 220.0
    o_sp = CYLINDER(s, R=r_ps, H=z_suc_face - t_fs - z_suc_buf, O=0.0).translate((x_crank_c, 0.0, z_suc_buf))
    o_sf = CYLINDER(s, R=r_fs, H=t_fs, O=0.0).translate((x_crank_c, 0.0, z_suc_face - t_fs))
    o_main.uniteWith(o_sp); o_sp.erase()
    o_main.uniteWith(o_sf); o_sf.erase()

    r_pd, r_fd, t_fd = _std_noz_dims(DN_DIS)
    x_dis_face = x_dbuf + r_buf * 0.92 + 220.0
    o_dp = CYLINDER(s, R=r_pd, H=x_dis_face - t_fd - x_dbuf, O=0.0).rotateY(90.0).translate((x_dbuf, 0.0, z_dbuf))
    o_df = CYLINDER(s, R=r_fd, H=t_fd, O=0.0).rotateY(90.0).translate((x_dis_face - t_fd, 0.0, z_dbuf))
    o_main.uniteWith(o_dp); o_dp.erase()
    o_main.uniteWith(o_df); o_df.erase()

    s.setPoint((x_crank_c, 0.0, z_suc_face), (0.0, 0.0, 1.0))
    s.setPoint((x_dis_face, 0.0, z_dbuf), (1.0, 0.0, 0.0))

    s.setLinearDimension('L_SKID', (-L_SKID / 2.0, -W_SKID / 2.0, 0.0), (L_SKID / 2.0, -W_SKID / 2.0, 0.0))
    s.setLinearDimension('W_SKID', (L_SKID / 2.0, -W_SKID / 2.0, 0.0), (L_SKID / 2.0, W_SKID / 2.0, 0.0))
