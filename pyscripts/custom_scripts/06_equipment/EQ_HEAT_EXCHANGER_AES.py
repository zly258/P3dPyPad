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
          TooltipShort=u"浮头式列管换热器 (GB/T 151 AES)",
          TooltipLong=u"GB/T 151 AES 型卧式浮头式管壳换热器，前端带可拆螺栓平盖A型管箱与吊盖旋臂，后端带显著加大直径S型浮头外头盖与对夹主法兰",
          LengthUnit="mm",
          Ports="4")
@group("MainDimensions", TooltipLong=u"AES 型浮头式换热器主要尺寸参数")
@param(D_SHELL=LENGTH, TooltipShort=u"壳体公称直径", TooltipLong=u"换热器壳体公称直径 DN (mm)")
@param(L_TUBE=LENGTH, TooltipShort=u"换热管长", TooltipLong=u"壳体筒段有效长度 L (mm)", Ask4Dist=True)
@param(L_BOX=LENGTH, TooltipShort=u"前端管箱长", TooltipLong=u"前端 A 型管箱长度 (mm)")
@param(D_REAR=LENGTH, TooltipShort=u"后端外头盖直径", TooltipLong=u"后端浮头外头盖加大外径 (mm)")
@param(L_REAR=LENGTH, TooltipShort=u"外头盖直段长", TooltipLong=u"后端浮头外头盖直段长度 (mm)")
@param(H_SADDLE=LENGTH, TooltipShort=u"中心高", TooltipLong=u"鞍座底面至壳体中心线高度 H (mm)", Ask4Dist=True)
@param(A_SADDLE=LENGTH, TooltipShort=u"鞍座间距", TooltipLong=u"双鞍座中心距 A (mm)", Ask4Dist=True)
@param(NOZ_S=LENGTH, TooltipShort=u"壳程接管口径", TooltipLong=u"壳程进出口接管公称通径 DN (mm)")
@param(NOZ_T=LENGTH, TooltipShort=u"管程接管口径", TooltipLong=u"管程进出口接管公称通径 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出高", TooltipLong=u"接管法兰面距壳体外壁高度 (mm)")
def EQ_HEAT_EXCHANGER_AES(
    s,
    D_SHELL=800.0,
    L_TUBE=4500.0,
    L_BOX=580.0,
    D_REAR=1100.0,
    L_REAR=620.0,
    H_SADDLE=880.0,
    A_SADDLE=3100.0,
    NOZ_S=150.0,
    NOZ_T=150.0,
    NOZ_EXT=260.0,
    ID=u"EQ_HEAT_EXCHANGER_AES",
    **kw
):
    u"""GB/T 151 AES 型浮头式列管换热器 (前端 A 型平盖管箱在 -X，后端大幅加大 S 型外头盖在 +X)。"""
    D_SHELL = max(350.0, float(D_SHELL))
    R_S = D_SHELL / 2.0
    L_TUBE = float(L_TUBE)
    if L_TUBE < 1.0:
        L_TUBE = 1.0
    L_BOX = max(280.0, float(L_BOX))
    D_REAR = float(D_REAR)
    if D_REAR < 1.0:
        D_REAR = 1.0
    R_REAR = D_REAR / 2.0
    L_REAR = max(320.0, float(L_REAR))
    H_SADDLE = float(H_SADDLE)
    if H_SADDLE < 1.0:
        H_SADDLE = 1.0
    A_SADDLE = min(L_TUBE - 450.0, max(700.0, float(A_SADDLE)))
    NOZ_S = max(50.0, float(NOZ_S))
    NOZ_T = max(50.0, float(NOZ_T))
    NOZ_EXT = max(150.0, float(NOZ_EXT))

    half_l = L_TUBE / 2.0
    r_fl_front = R_S + 85.0
    fl_t = 65.0
    cover_t = 70.0
    r_fl_rear = R_REAR + 85.0
    z_gnd = -H_SADDLE

    # 1. E 型主壳体
    o_main = CYLINDER(s, R=R_S, H=L_TUBE, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))

    # 2. 前端 A 型可拆平盖管箱 (双主法兰 + 管箱筒体 + 厚螺栓平盖 + 管箱吊盖旋臂架)
    o_ffl1 = CYLINDER(s, R=r_fl_front, H=fl_t * 1.3, O=0.0).rotateY(90.0).translate((-half_l - fl_t * 0.65, 0.0, 0.0))
    o_main.uniteWith(o_ffl1); o_ffl1.erase()

    o_box = CYLINDER(s, R=R_S, H=L_BOX + 10.0, O=0.0).rotateY(90.0).translate((-(half_l + L_BOX), 0.0, 0.0))
    o_main.uniteWith(o_box); o_box.erase()

    x_fcap = -(half_l + L_BOX + fl_t * 0.5 + cover_t)
    o_ffl2 = CYLINDER(s, R=r_fl_front, H=fl_t + cover_t, O=0.0).rotateY(90.0).translate((x_fcap, 0.0, 0.0))
    o_main.uniteWith(o_ffl2); o_ffl2.erase()

    # 前端平盖吊盖旋臂（AES A型平盖典型特征）
    o_dv_post = CYLINDER(s, R=28.0, H=R_S * 0.65, O=0.0).translate((-(half_l + L_BOX * 0.72), 0.0, R_S * 0.85))
    o_dv_arm = CORNERBOX(s, L=L_BOX * 0.35 + fl_t + cover_t + 60.0, W=50.0, H=55.0).translate((x_fcap - 20.0, -25.0, R_S * 1.40))
    o_dv_drop = CYLINDER(s, R=22.0, H=R_S * 0.45, O=0.0).translate((x_fcap + cover_t * 0.5, 0.0, R_S * 1.00))
    for part in (o_dv_post, o_dv_arm, o_dv_drop):
        o_main.uniteWith(part); part.erase()

    # 3. 后端 S 型显著加大浮头外头盖 (台阶过渡锥 + 重型外头盖法兰 + 大直径筒节 + EHA 封头)
    o_rfl = CYLINDER(s, R=r_fl_rear, H=fl_t * 1.5, O=0.0).rotateY(90.0).translate((half_l - fl_t * 0.35, 0.0, 0.0))
    o_main.uniteWith(o_rfl); o_rfl.erase()

    o_rcyl = CYLINDER(s, R=R_REAR, H=L_REAR + 8.0, O=0.0).rotateY(90.0).translate((half_l + fl_t * 0.9, 0.0, 0.0))
    o_main.uniteWith(o_rcyl); o_rcyl.erase()

    o_rhd = ELLIPSOIDHEAD(s, R=R_REAR).rotateY(90.0).translate((half_l + fl_t * 0.9 + L_REAR, 0.0, 0.0))
    o_main.uniteWith(o_rhd); o_rhd.erase()

    # 4. 双鞍式支座
    sad_w = D_SHELL * 0.88
    sad_l = max(200.0, D_SHELL * 0.28)
    base_t = 24.0
    for sx in (-1.0, 1.0):
        xc = sx * (A_SADDLE / 2.0)
        o_base = CORNERBOX(s, L=sad_l, W=sad_w, H=base_t).translate((xc - sad_l / 2.0, -sad_w / 2.0, z_gnd))
        o_web = CORNERBOX(s, L=sad_l * 0.52, W=sad_w * 0.84, H=H_SADDLE - base_t).translate((xc - sad_l * 0.26, -sad_w * 0.42, z_gnd + base_t - 4.0))
        o_main.uniteWith(o_base); o_base.erase()
        o_main.uniteWith(o_web); o_web.erase()

    # 5. 4 个工艺接管 (壳程上下对角 2 个 + 前端 A 型管箱上下 2 个双管程接管)
    def _add_nozzle(x_pos, z_sign, dn_val):
        r_n, r_nf, t_nf = _std_noz_dims(dn_val)
        z_face = z_sign * (R_S + NOZ_EXT)
        pipe_h = R_S * 0.35 + NOZ_EXT - t_nf
        if z_sign > 0:
            o_p = CYLINDER(s, R=r_n, H=pipe_h + 2.0, O=0.0).translate((x_pos, 0.0, R_S * 0.65))
            o_f = CYLINDER(s, R=r_nf, H=t_nf, O=0.0).translate((x_pos, 0.0, z_face - t_nf))
        else:
            o_p = CYLINDER(s, R=r_n, H=pipe_h + 2.0, O=0.0).rotateX(180.0).translate((x_pos, 0.0, -R_S * 0.65))
            o_f = CYLINDER(s, R=r_nf, H=t_nf, O=0.0).rotateX(180.0).translate((x_pos, 0.0, z_face + t_nf))
        o_main.uniteWith(o_p); o_p.erase()
        o_main.uniteWith(o_f); o_f.erase()
        return (x_pos, 0.0, z_face)

    p_s1 = _add_nozzle(-half_l + 450.0, 1.0, NOZ_S)
    p_s2 = _add_nozzle(half_l - 450.0, -1.0, NOZ_S)
    p_t1 = _add_nozzle(-(half_l + L_BOX * 0.48), 1.0, NOZ_T)
    p_t2 = _add_nozzle(-(half_l + L_BOX * 0.48), -1.0, NOZ_T)

    s.setPoint(p_s1, (0.0, 0.0, 1.0))
    s.setPoint(p_s2, (0.0, 0.0, -1.0))
    s.setPoint(p_t1, (0.0, 0.0, 1.0))
    s.setPoint(p_t2, (0.0, 0.0, -1.0))

    s.setLinearDimension('L_TUBE', (-half_l, 0.0, R_S), (half_l, 0.0, R_S))
    s.setLinearDimension('A_SADDLE', (-A_SADDLE / 2.0, 0.0, z_gnd), (A_SADDLE / 2.0, 0.0, z_gnd))
    s.setLinearDimension('H_SADDLE', (0.0, 0.0, z_gnd), (0.0, 0.0, 0.0))
    s.setLinearDimension('D_REAR', (half_l + fl_t + L_REAR * 0.5, -R_REAR, 0.0), (half_l + fl_t + L_REAR * 0.5, R_REAR, 0.0))
