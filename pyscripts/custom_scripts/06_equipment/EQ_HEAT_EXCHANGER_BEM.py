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
    10: (17.2, 90.0, 16.0), 15: (21.3, 95.0, 16.0), 20: (26.9, 105.0, 18.0),
    25: (33.7, 115.0, 18.0), 32: (42.4, 140.0, 18.0), 40: (48.3, 150.0, 18.0),
    50: (60.3, 165.0, 18.0), 65: (76.1, 185.0, 18.0), 80: (88.9, 200.0, 20.0),
    100: (114.3, 220.0, 20.0), 125: (139.7, 250.0, 22.0), 150: (168.3, 285.0, 22.0),
    200: (219.1, 340.0, 24.0), 250: (273.0, 405.0, 26.0), 300: (323.9, 460.0, 28.0),
    350: (355.6, 520.0, 30.0), 400: (406.4, 580.0, 32.0), 450: (457.0, 640.0, 40.0),
    500: (508.0, 715.0, 44.0), 600: (610.0, 840.0, 54.0),
}

def _std_noz_dims(dn_val):
    dn_i = int(round(float(dn_val)))
    if dn_i in _HGT20592_PN16_A:
        od, d_fl, t_fl = _HGT20592_PN16_A[dn_i]
        return od / 2.0, d_fl / 2.0, t_fl
    od = float(dn_val) * 1.05
    return od / 2.0, (od + 120.0) / 2.0, 24.0

@activate(Group="Equipment",
          TooltipShort=u"固定管板列管换热器 (GB/T 151 BEM)",
          TooltipLong=u"GB/T 151 BEM 型卧式固定管板热交换器，含两端等径整体B/M型封头管箱、轴向端头管程接管、壳体中部波纹膨胀节、双鞍座及壳程上下接管",
          LengthUnit="mm",
          Ports="4")
@group("MainDimensions", TooltipLong=u"BEM 型列管换热器主要几何尺寸参数")
@param(D_SHELL=LENGTH, TooltipShort=u"壳体公称直径", TooltipLong=u"换热器壳体直径 DN (mm)")
@param(L_TUBE=LENGTH, TooltipShort=u"换热管长", TooltipLong=u"两管板间壳体公称长度 L (mm)", Ask4Dist=True)
@param(L_BOX=LENGTH, TooltipShort=u"管箱筒节长", TooltipLong=u"前后整体封头管箱直段长度 (mm)")
@param(H_SADDLE=LENGTH, TooltipShort=u"中心高", TooltipLong=u"鞍座底板至壳体中心线高度 H (mm)", Ask4Dist=True)
@param(A_SADDLE=LENGTH, TooltipShort=u"鞍座间距", TooltipLong=u"双鞍座中心距 A (mm)", Ask4Dist=True)
@param(NOZ_S=LENGTH, TooltipShort=u"壳程接管口径", TooltipLong=u"壳程进出口接管公称通径 DN (mm)")
@param(NOZ_T=LENGTH, TooltipShort=u"管程接管口径", TooltipLong=u"管程轴向进出口接管公称通径 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出高", TooltipLong=u"接管法兰面距壳体/封头外壁高度 (mm)")
def EQ_HEAT_EXCHANGER_BEM(
    s,
    D_SHELL=800.0,
    L_TUBE=4500.0,
    L_BOX=360.0,
    H_SADDLE=750.0,
    A_SADDLE=3200.0,
    NOZ_S=150.0,
    NOZ_T=150.0,
    NOZ_EXT=260.0,
    ID=u"EQ_HEAT_EXCHANGER_BEM",
    **kw
):
    u"""BEM 型卧式固定管板列管换热器 (两端整体曲面封头 + 轴向管程进出口 + 壳体中部波纹膨胀节)。"""
    D_SHELL = max(300.0, float(D_SHELL))
    R_S = D_SHELL / 2.0
    L_TUBE = float(L_TUBE)
    if L_TUBE < 1.0:
        L_TUBE = 1.0
    L_BOX = max(180.0, float(L_BOX))
    H_SADDLE = float(H_SADDLE)
    if H_SADDLE < 1.0:
        H_SADDLE = 1.0
    A_SADDLE = min(L_TUBE - 400.0, max(600.0, float(A_SADDLE)))
    NOZ_S = max(50.0, float(NOZ_S))
    NOZ_T = max(50.0, float(NOZ_T))
    NOZ_EXT = max(150.0, float(NOZ_EXT))

    half_l = L_TUBE / 2.0
    r_fl_main = R_S + 55.0
    fl_t = 42.0

    # 1. 主壳体 + 壳体中部固定管板波纹膨胀节 (3 道波纹凸环，固定管板典型特征)
    o_main = CYLINDER(s, R=R_S, H=L_TUBE, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))
    for dx in (-110.0, 0.0, 110.0):
        o_bel = CYLINDER(s, R=R_S + 68.0, H=56.0, O=0.0).rotateY(90.0).translate((dx - 28.0, 0.0, 0.0))
        o_main.uniteWith(o_bel); o_bel.erase()

    # 2. 两端等径固定管板焊颈法兰 + 整体 B/M 型曲面封头管箱
    for sx in (-1.0, 1.0):
        x_fl = sx * half_l - (fl_t / 2.0)
        o_mfl = CYLINDER(s, R=r_fl_main, H=fl_t, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_main.uniteWith(o_mfl); o_mfl.erase()

        if sx < 0:
            o_box = CYLINDER(s, R=R_S, H=L_BOX, O=0.0).rotateY(90.0).translate((-(half_l + L_BOX), 0.0, 0.0))
            o_hd = ELLIPSOIDHEAD(s, R=R_S).rotateY(-90.0).translate((-(half_l + L_BOX), 0.0, 0.0))
        else:
            o_box = CYLINDER(s, R=R_S, H=L_BOX, O=0.0).rotateY(90.0).translate((half_l, 0.0, 0.0))
            o_hd = ELLIPSOIDHEAD(s, R=R_S).rotateY(90.0).translate((half_l + L_BOX, 0.0, 0.0))
        o_main.uniteWith(o_box); o_box.erase()
        o_main.uniteWith(o_hd); o_hd.erase()

    # 3. 双鞍式支座
    sad_w = D_SHELL * 0.85
    sad_l = max(180.0, D_SHELL * 0.26)
    base_t = 20.0
    z_gnd = -H_SADDLE
    for sx in (-1.0, 1.0):
        xc = sx * (A_SADDLE / 2.0)
        o_web = CORNERBOX(s, L=sad_l * 0.55, W=sad_w * 0.82, H=H_SADDLE - base_t).translate((xc - sad_l * 0.275, -sad_w * 0.41, z_gnd + base_t))
        o_base = CORNERBOX(s, L=sad_l, W=sad_w, H=base_t).translate((xc - sad_l / 2.0, -sad_w / 2.0, z_gnd))
        o_main.uniteWith(o_web); o_web.erase()
        o_main.uniteWith(o_base); o_base.erase()

    # 4. 壳程上下对角接管 + 管程两端封头中心轴向接管 (单管程 BEM 典型布局)
    def _add_shell_nozzle(x_pos, z_sign, dn_val):
        r_n, r_nf, t_nf = _std_noz_dims(dn_val)
        z_face = z_sign * (R_S + NOZ_EXT)
        pipe_h = R_S * 0.35 + NOZ_EXT - t_nf
        if z_sign > 0:
            o_p = CYLINDER(s, R=r_n, H=pipe_h, O=0.0).translate((x_pos, 0.0, R_S * 0.65))
            o_f = CYLINDER(s, R=r_nf, H=t_nf, O=0.0).translate((x_pos, 0.0, z_face - t_nf))
        else:
            o_p = CYLINDER(s, R=r_n, H=pipe_h, O=0.0).rotateX(180.0).translate((x_pos, 0.0, -R_S * 0.65))
            o_f = CYLINDER(s, R=r_nf, H=t_nf, O=0.0).rotateX(180.0).translate((x_pos, 0.0, z_face + t_nf))
        o_main.uniteWith(o_p); o_p.erase()
        o_main.uniteWith(o_f); o_f.erase()
        return (x_pos, 0.0, z_face)

    def _add_axial_nozzle(x_sign, dn_val):
        r_n, r_nf, t_nf = _std_noz_dims(dn_val)
        head_tip = half_l + L_BOX + R_S * 0.50
        x_face = x_sign * (head_tip + NOZ_EXT)
        pipe_len = R_S * 0.35 + NOZ_EXT - t_nf
        if x_sign < 0:
            o_p = CYLINDER(s, R=r_n, H=pipe_len + 10.0, O=0.0).rotateY(90.0).translate((x_face + t_nf, 0.0, 0.0))
            o_f = CYLINDER(s, R=r_nf, H=t_nf, O=0.0).rotateY(90.0).translate((x_face, 0.0, 0.0))
        else:
            o_p = CYLINDER(s, R=r_n, H=pipe_len + 10.0, O=0.0).rotateY(90.0).translate((x_face - t_nf - pipe_len - 10.0, 0.0, 0.0))
            o_f = CYLINDER(s, R=r_nf, H=t_nf, O=0.0).rotateY(90.0).translate((x_face - t_nf, 0.0, 0.0))
        o_main.uniteWith(o_p); o_p.erase()
        o_main.uniteWith(o_f); o_f.erase()
        return (x_face, 0.0, 0.0)

    p_s1 = _add_shell_nozzle(-half_l + 420.0, 1.0, NOZ_S)
    p_s2 = _add_shell_nozzle(half_l - 420.0, -1.0, NOZ_S)
    p_t1 = _add_axial_nozzle(-1.0, NOZ_T)
    p_t2 = _add_axial_nozzle(1.0, NOZ_T)

    s.setPoint(p_s1, (0.0, 0.0, 1.0))
    s.setPoint(p_s2, (0.0, 0.0, -1.0))
    s.setPoint(p_t1, (-1.0, 0.0, 0.0))
    s.setPoint(p_t2, (1.0, 0.0, 0.0))

    s.setLinearDimension('L_TUBE', (-half_l, 0.0, R_S), (half_l, 0.0, R_S))
    s.setLinearDimension('A_SADDLE', (-A_SADDLE / 2.0, 0.0, z_gnd), (A_SADDLE / 2.0, 0.0, z_gnd))
    s.setLinearDimension('H_SADDLE', (0.0, 0.0, z_gnd), (0.0, 0.0, 0.0))
