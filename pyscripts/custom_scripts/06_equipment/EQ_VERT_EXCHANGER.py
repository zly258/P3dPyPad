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
          TooltipShort=u"立式热虹吸再沸器/冷凝器 (GB/T 151)",
          TooltipLong=u"GB/T 151 立式管壳热交换器/热虹吸再沸器参数化模型，含立式壳体、上下管箱封头、4×耳式支座及 4 个工艺接管",
          LengthUnit="mm",
          Ports="4")
@group("MainDimensions", TooltipLong=u"立式换热器主体、耳座与接管主要尺寸参数")
@param(D_SHELL=LENGTH, TooltipShort=u"壳体公称直径", TooltipLong=u"立式壳体公称直径 DN (mm)")
@param(L_TUBE=LENGTH, TooltipShort=u"换热管长", TooltipLong=u"两管板间壳体长度 L (mm)", Ask4Dist=True)
@param(L_BOX=LENGTH, TooltipShort=u"管箱筒节长", TooltipLong=u"上下管箱直段长度 (mm)")
@param(H_LUG=LENGTH, TooltipShort=u"耳座标高", TooltipLong=u"耳式支座底板底面距下管板 EL 0 高度 (mm)", Ask4Dist=True)
@param(LUG_EXT=LENGTH, TooltipShort=u"耳座伸出宽", TooltipLong=u"耳式支座底板外缘距壳体外壁伸出长度 (mm)")
@param(NOZ_S=LENGTH, TooltipShort=u"壳程接管口径", TooltipLong=u"壳程上下接管公称通径 DN (mm)")
@param(NOZ_T=LENGTH, TooltipShort=u"管程接管口径", TooltipLong=u"管程上下接管公称通径 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出长", TooltipLong=u"接管法兰面距壳体/封头外壁伸出长度 (mm)")
def EQ_VERT_EXCHANGER(
    s,
    D_SHELL=700.0,
    L_TUBE=3000.0,
    L_BOX=380.0,
    H_LUG=2000.0,
    LUG_EXT=180.0,
    NOZ_S=150.0,
    NOZ_T=200.0,
    NOZ_EXT=250.0,
    ID=u"EQ_VERT_EXCHANGER",
    **kw
):
    u"""GB/T 151 立式热虹吸再沸器/冷凝器 (EL 0 = 下管板中心面，+Z 向上)。"""
    D_SHELL = float(D_SHELL)
    if D_SHELL < 1.0:
        D_SHELL = 1.0
    R_S = D_SHELL / 2.0
    L_TUBE = float(L_TUBE)
    if L_TUBE < 1.0:
        L_TUBE = 1.0
    L_BOX = max(180.0, float(L_BOX))
    H_LUG = min(L_TUBE - 300.0, max(400.0, float(H_LUG)))
    LUG_EXT = max(100.0, float(LUG_EXT))
    NOZ_S = max(50.0, float(NOZ_S))
    NOZ_T = max(50.0, float(NOZ_T))
    NOZ_EXT = max(140.0, float(NOZ_EXT))

    r_fl = R_S + 65.0
    fl_t = 48.0
    h_head = R_S * 0.5

    # 1. 立式壳体 (Z: 0 -> L_TUBE)
    o_main = CYLINDER(s, R=R_S, H=L_TUBE, O=0.0)

    # 2. 上、下管板设备主法兰 + 管箱 + EHA 2:1 封头
    for z_fl in (0.0, L_TUBE):
        o_mfl = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).translate((0.0, 0.0, z_fl - fl_t / 2.0))
        o_main.uniteWith(o_mfl)
        o_mfl.erase()

    o_tbox = CYLINDER(s, R=R_S, H=L_BOX + 4.0, O=0.0).translate((0.0, 0.0, L_TUBE - 2.0))
    o_thd = ELLIPSOIDHEAD(s, R=R_S).translate((0.0, 0.0, L_TUBE + L_BOX - 2.0))
    o_main.uniteWith(o_tbox)
    o_tbox.erase()
    o_main.uniteWith(o_thd)
    o_thd.erase()

    o_bbox = CYLINDER(s, R=R_S, H=L_BOX + 4.0, O=0.0).translate((0.0, 0.0, -L_BOX - 2.0))
    o_bhd = ELLIPSOIDHEAD(s, R=R_S).rotateX(180.0).translate((0.0, 0.0, -L_BOX + 2.0))
    o_main.uniteWith(o_bbox)
    o_bbox.erase()
    o_main.uniteWith(o_bhd)
    o_bhd.erase()

    # 3. 4×耳式支座 (NB/T 47065.3 风格，45°, 135°, 225°, 315° 均布)
    lug_w = max(160.0, D_SHELL * 0.24)
    lug_h = max(240.0, LUG_EXT * 1.45)
    lug_bt = 20.0
    rib_t = 14.0
    for deg in (45.0, 135.0, 225.0, 315.0):
        # 水平底板
        o_lbase = CORNERBOX(s, L=LUG_EXT + 40.0, W=lug_w, H=lug_bt).translate(
            (R_S - 35.0, -lug_w / 2.0, H_LUG)
        ).rotateZ(deg)
        o_main.uniteWith(o_lbase)
        o_lbase.erase()
        # 双侧立筋板
        for sy in (-1.0, 1.0):
            o_lrib = CORNERBOX(s, L=LUG_EXT + 30.0, W=rib_t, H=lug_h).translate(
                (R_S - 35.0, sy * (lug_w * 0.36) - rib_t / 2.0, H_LUG + lug_bt - 4.0)
            ).rotateZ(deg)
            o_main.uniteWith(o_lrib)
            o_lrib.erase()

    # 4. 4 个工艺接管
    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    # 管程顶部出口 (+Z) 与底部进口 (-Z)
    r_pt, r_ft, t_ft = _fl_dims(NOZ_T)
    z_top_face = L_TUBE + L_BOX + h_head + NOZ_EXT
    z_top_start = L_TUBE + L_BOX + h_head * 0.60
    o_nt1_p = CYLINDER(s, R=r_pt, H=z_top_face - t_ft - z_top_start + 2.0, O=0.0).translate((0.0, 0.0, z_top_start))
    o_nt1_f = CYLINDER(s, R=r_ft, H=t_ft, O=0.0).translate((0.0, 0.0, z_top_face - t_ft))
    o_main.uniteWith(o_nt1_p)
    o_nt1_p.erase()
    o_main.uniteWith(o_nt1_f)
    o_nt1_f.erase()
    p_t1 = (0.0, 0.0, z_top_face)

    z_bot_face = -(L_BOX + h_head + NOZ_EXT)
    z_bot_start = -(L_BOX + h_head * 0.60)
    o_nt2_p = CYLINDER(s, R=r_pt, H=abs(z_bot_face) - t_ft - abs(z_bot_start) + 2.0, O=0.0).rotateX(180.0).translate((0.0, 0.0, z_bot_start))
    o_nt2_f = CYLINDER(s, R=r_ft, H=t_ft, O=0.0).rotateX(180.0).translate((0.0, 0.0, z_bot_face + t_ft))
    o_main.uniteWith(o_nt2_p)
    o_nt2_p.erase()
    o_main.uniteWith(o_nt2_f)
    o_nt2_f.erase()
    p_t2 = (0.0, 0.0, z_bot_face)

    # 壳程上部 (+X) 与下部 (-X) 接管
    r_ps, r_fs, t_fs = _fl_dims(NOZ_S)
    x_face = R_S + NOZ_EXT
    embed = R_S * 0.25
    pipe_l = NOZ_EXT + embed - t_fs

    z_s1 = L_TUBE - max(320.0, r_fs + 120.0)
    o_ns1_p = CYLINDER(s, R=r_ps, H=pipe_l + 2.0, O=0.0).rotateY(90.0).translate((R_S - embed, 0.0, z_s1))
    o_ns1_f = CYLINDER(s, R=r_fs, H=t_fs, O=0.0).rotateY(90.0).translate((x_face - t_fs, 0.0, z_s1))
    o_main.uniteWith(o_ns1_p)
    o_ns1_p.erase()
    o_main.uniteWith(o_ns1_f)
    o_ns1_f.erase()
    p_s1 = (x_face, 0.0, z_s1)

    z_s2 = max(320.0, r_fs + 120.0)
    o_ns2_p = CYLINDER(s, R=r_ps, H=pipe_l + 2.0, O=0.0).rotateY(-90.0).translate((-(R_S - embed), 0.0, z_s2))
    o_ns2_f = CYLINDER(s, R=r_fs, H=t_fs, O=0.0).rotateY(-90.0).translate((-x_face + t_fs, 0.0, z_s2))
    o_main.uniteWith(o_ns2_p)
    o_ns2_p.erase()
    o_main.uniteWith(o_ns2_f)
    o_ns2_f.erase()
    p_s2 = (-x_face, 0.0, z_s2)

    # 5. 注册 4 个端口
    s.setPoint(p_t1, (0.0, 0.0, 1.0))
    s.setPoint(p_t2, (0.0, 0.0, -1.0))
    s.setPoint(p_s1, (1.0, 0.0, 0.0))
    s.setPoint(p_s2, (-1.0, 0.0, 0.0))

    # 6. 注册线性标注
    s.setLinearDimension('D_SHELL', (-R_S, 0.0, 0.0), (R_S, 0.0, 0.0))
    s.setLinearDimension('L_TUBE', (-R_S, 0.0, 0.0), (-R_S, 0.0, L_TUBE))
    s.setLinearDimension('H_LUG', (R_S, 0.0, 0.0), (R_S, 0.0, H_LUG))
