# -*- coding: utf-8 -*-
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
          TooltipShort=u"干式翅片管空冷器 (API 661)",
          TooltipLong=u"API 661 / NB/T 47007 干式鼓风翅片管空气冷却器参数化模型，含顶部翅片管束箱、两端丝堵式管箱、下部风箱、双风机筒与风机毂、4根钢构支柱及进出口法兰",
          LengthUnit="mm",
          Ports="2")
@group("MainDimensions", TooltipLong=u"干式翅片管空冷器主要尺寸参数")
@param(L_BUNDLE=LENGTH, TooltipShort=u"管束长度", TooltipLong=u"翅片管束有效长度 L (mm)", Ask4Dist=True)
@param(W_BUNDLE=LENGTH, TooltipShort=u"管束宽度", TooltipLong=u"空冷器管束箱总宽 W (mm)", Ask4Dist=True)
@param(H_BUNDLE=LENGTH, TooltipShort=u"管束箱高", TooltipLong=u"顶部翅片管束及管箱高度 (mm)")
@param(H_PLENUM=LENGTH, TooltipShort=u"风箱高度", TooltipLong=u"管束箱下方过渡风箱高度 (mm)")
@param(D_FAN=LENGTH, TooltipShort=u"风机筒直径", TooltipLong=u"下部双风机护筒外径 (mm)")
@param(H_LEG=LENGTH, TooltipShort=u"支柱高度", TooltipLong=u"底板底面至风箱底面净空高度 (mm)", Ask4Dist=True)
@param(NOZ_IN=LENGTH, TooltipShort=u"进口口径", TooltipLong=u"工艺介质进口接管公称通径 DN (mm)")
@param(NOZ_OUT=LENGTH, TooltipShort=u"出口口径", TooltipLong=u"工艺介质出口接管公称通径 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出高", TooltipLong=u"接管法兰面伸出管箱外壁高度 (mm)")
def EQ_AIR_COOLER_FIN(
    s,
    L_BUNDLE=6000.0,
    W_BUNDLE=2400.0,
    H_BUNDLE=420.0,
    H_PLENUM=680.0,
    D_FAN=1800.0,
    H_LEG=2200.0,
    NOZ_IN=200.0,
    NOZ_OUT=200.0,
    NOZ_EXT=260.0,
    ID=u"EQ_AIR_COOLER_FIN",
    **kw
):
    u"""API 661 干式翅片管空冷器 (沿 X 轴布置，4 根支柱底面 Z=0，顶部为翅片管束箱与两端管箱，下部为风箱及双风机筒)。"""
    L_BUNDLE = float(L_BUNDLE)
    if L_BUNDLE < 1.0:
        L_BUNDLE = 1.0
    W_BUNDLE = float(W_BUNDLE)
    if W_BUNDLE < 1.0:
        W_BUNDLE = 1.0
    H_BUNDLE = max(280.0, float(H_BUNDLE))
    H_PLENUM = max(400.0, float(H_PLENUM))
    D_FAN = min(W_BUNDLE * 0.88, L_BUNDLE * 0.42, max(900.0, float(D_FAN)))
    H_LEG = float(H_LEG)
    if H_LEG < 1.0:
        H_LEG = 1.0
    NOZ_IN = max(80.0, float(NOZ_IN))
    NOZ_OUT = max(80.0, float(NOZ_OUT))
    NOZ_EXT = max(160.0, float(NOZ_EXT))

    half_l = L_BUNDLE * 0.5
    half_w = W_BUNDLE * 0.5
    hdr_l = max(320.0, H_BUNDLE * 0.85)
    z_pl_bot = H_LEG
    z_pl_top = H_LEG + H_PLENUM
    z_bd_top = z_pl_top + H_BUNDLE

    # 1. 下部风箱 (Plenum Chamber)
    o_main = CORNERBOX(s, L=L_BUNDLE - hdr_l * 1.4, W=W_BUNDLE * 0.94, H=H_PLENUM + 10.0).translate(
        (-(L_BUNDLE - hdr_l * 1.4) * 0.5, -W_BUNDLE * 0.47, z_pl_bot)
    )

    # 2. 顶部翅片管束箱 (两侧边框 + 底层托板 + 纵向翅片管束肋条)
    o_bd_base = CORNERBOX(s, L=L_BUNDLE - hdr_l * 1.6, W=W_BUNDLE, H=H_BUNDLE * 0.48).translate(
        (-(L_BUNDLE - hdr_l * 1.6) * 0.5, -half_w, z_pl_top)
    )
    o_main.uniteWith(o_bd_base)
    o_bd_base.erase()

    side_t = max(70.0, W_BUNDLE * 0.04)
    for sy in (-1.0, 1.0):
        ys = -half_w if sy < 0 else half_w - side_t
        o_sb = CORNERBOX(s, L=L_BUNDLE - hdr_l * 1.4, W=side_t, H=H_BUNDLE).translate(
            (-(L_BUNDLE - hdr_l * 1.4) * 0.5, ys, z_pl_top)
        )
        o_main.uniteWith(o_sb)
        o_sb.erase()

    # 顶部纵向翅片管肋条 (6 组清晰工业纹理)
    n_ribs = 6
    span_y = W_BUNDLE - side_t * 2.6
    rib_w = span_y / float(n_ribs * 2 - 1)
    for i in range(n_ribs):
        yr = -span_y * 0.5 + i * rib_w * 2.0
        o_rb = CORNERBOX(s, L=L_BUNDLE - hdr_l * 1.6, W=rib_w, H=H_BUNDLE * 0.48).translate(
            (-(L_BUNDLE - hdr_l * 1.6) * 0.5, yr, z_pl_top + H_BUNDLE * 0.46)
        )
        o_main.uniteWith(o_rb)
        o_rb.erase()

    # 3. 两端丝堵式管箱 (Header Boxes)
    for sx in (-1.0, 1.0):
        xh = -half_l if sx < 0 else half_l - hdr_l
        o_hd = CORNERBOX(s, L=hdr_l, W=W_BUNDLE + 60.0, H=H_BUNDLE + 40.0).translate(
            (xh, -(W_BUNDLE + 60.0) * 0.5, z_pl_top - 20.0)
        )
        o_main.uniteWith(o_hd)
        o_hd.erase()

    # 4. 下部双风机筒 + 风机轮毂与驱动电机
    r_fan = D_FAN * 0.5
    h_shroud = max(380.0, D_FAN * 0.28)
    for xf in (-L_BUNDLE * 0.24, L_BUNDLE * 0.24):
        o_sh = CYLINDER(s, R=r_fan, H=h_shroud + 20.0, O=0.0).translate((xf, 0.0, z_pl_bot - h_shroud))
        o_main.uniteWith(o_sh)
        o_sh.erase()
        # 风机底部扩口环
        o_fr = CYLINDER(s, R=r_fan + 55.0, H=45.0, O=0.0).translate((xf, 0.0, z_pl_bot - h_shroud))
        o_main.uniteWith(o_fr)
        o_fr.erase()
        # 下悬风机电机
        o_fm = CYLINDER(s, R=r_fan * 0.22, H=h_shroud * 0.85, O=0.0).translate((xf, 0.0, z_pl_bot - h_shroud * 1.75))
        o_main.uniteWith(o_fm)
        o_fm.erase()

    # 5. 4 根钢结构支柱 + 底板 + 纵向联系梁
    col_s = max(180.0, W_BUNDLE * 0.085)
    bp_s = col_s + 140.0
    bp_t = 24.0
    x_col = half_l - hdr_l * 1.1
    y_col = half_w - col_s * 0.55
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            xc = sx * x_col
            yc = sy * y_col
            o_bp = CORNERBOX(s, L=bp_s, W=bp_s, H=bp_t).translate((xc - bp_s * 0.5, yc - bp_s * 0.5, 0.0))
            o_main.uniteWith(o_bp)
            o_bp.erase()
            o_col = CORNERBOX(s, L=col_s, W=col_s, H=z_pl_top - bp_t + 10.0).translate(
                (xc - col_s * 0.5, yc - col_s * 0.5, bp_t - 2.0)
            )
            o_main.uniteWith(o_col)
            o_col.erase()
    # 两侧纵向水平联系梁
    beam_h = col_s * 0.9
    for sy in (-1.0, 1.0):
        yc = sy * y_col
        o_lb = CORNERBOX(s, L=x_col * 2.0, W=col_s * 0.7, H=beam_h).translate(
            (-x_col, yc - col_s * 0.35, z_pl_bot - beam_h * 0.6)
        )
        o_main.uniteWith(o_lb)
        o_lb.erase()

    # 6. 2 个工艺法兰口 (进口在 -X 管箱顶部 +Z，出口在 +X 管箱底部 -Z)
    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    r_p1, r_f1, t_f1 = _fl_dims(NOZ_IN)
    x_in = -half_l + hdr_l * 0.5
    z_in_face = z_bd_top + 20.0 + NOZ_EXT
    o_p1 = CYLINDER(s, R=r_p1, H=NOZ_EXT - t_f1 + 40.0, O=0.0).translate((x_in, 0.0, z_bd_top - 15.0))
    o_f1 = CYLINDER(s, R=r_f1, H=t_f1, O=0.0).translate((x_in, 0.0, z_in_face - t_f1))
    o_main.uniteWith(o_p1)
    o_p1.erase()
    o_main.uniteWith(o_f1)
    o_f1.erase()
    p_in = (x_in, 0.0, z_in_face)

    r_p2, r_f2, t_f2 = _fl_dims(NOZ_OUT)
    x_out = half_l - hdr_l * 0.5
    z_out_face = z_pl_top - 20.0 - NOZ_EXT
    o_p2 = CYLINDER(s, R=r_p2, H=NOZ_EXT - t_f2 + 40.0, O=0.0).translate((x_out, 0.0, z_out_face + t_f2 - 2.0))
    o_f2 = CYLINDER(s, R=r_f2, H=t_f2, O=0.0).translate((x_out, 0.0, z_out_face))
    o_main.uniteWith(o_p2)
    o_p2.erase()
    o_main.uniteWith(o_f2)
    o_f2.erase()
    p_out = (x_out, 0.0, z_out_face)

    # 7. 注册 2 个工艺端口
    s.setPoint(p_in, (0.0, 0.0, 1.0))
    s.setPoint(p_out, (0.0, 0.0, -1.0))

    # 8. 注册线性标注
    s.setLinearDimension('L_BUNDLE', (-half_l, 0.0, z_bd_top), (half_l, 0.0, z_bd_top))
    s.setLinearDimension('W_BUNDLE', (0.0, -half_w, z_bd_top), (0.0, half_w, z_bd_top))
    s.setLinearDimension('H_LEG', (-x_col, -y_col, 0.0), (-x_col, -y_col, z_pl_bot))
