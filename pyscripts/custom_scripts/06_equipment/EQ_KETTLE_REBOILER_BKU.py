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
          TooltipShort=u"BKU 釜式重沸器 (GB/T 151)",
          TooltipLong=u"GB/T 151 BKU 型卧式釜式重沸器参数化模型，含前端B型封头管箱、偏心锥形扩大段、大直径蒸发壳体、后端椭圆封头、双鞍式支座及4个工艺接管",
          LengthUnit="mm",
          Ports="4")
@group("MainDimensions", TooltipLong=u"BKU 釜式重沸器主要尺寸参数")
@param(D_BOX=LENGTH, TooltipShort=u"管箱公称直径", TooltipLong=u"前端B型管箱及小端壳体公称直径 (mm)")
@param(D_KETTLE=LENGTH, TooltipShort=u"蒸发壳体直径", TooltipLong=u"偏心扩大蒸发壳体公称直径 (mm)")
@param(L_KETTLE=LENGTH, TooltipShort=u"蒸发壳体长", TooltipLong=u"大直径蒸发壳体筒段长度 (mm)", Ask4Dist=True)
@param(L_TRANS=LENGTH, TooltipShort=u"偏心锥段长", TooltipLong=u"前端小壳体至大壳体偏心过渡锥段长度 (mm)")
@param(L_BOX=LENGTH, TooltipShort=u"前端管箱长", TooltipLong=u"前端管箱直段长度 (mm)")
@param(H_SADDLE=LENGTH, TooltipShort=u"中心高", TooltipLong=u"鞍座底板底面至管束中心线高度 H (mm)", Ask4Dist=True)
@param(A_SADDLE=LENGTH, TooltipShort=u"鞍座间距", TooltipLong=u"双鞍座中心距 A (mm)", Ask4Dist=True)
@param(NOZ_T=LENGTH, TooltipShort=u"管程接管口径", TooltipLong=u"管程加热介质进出口公称通径 DN (mm)")
@param(NOZ_LIQ=LENGTH, TooltipShort=u"壳程进液口径", TooltipLong=u"壳程底部进液口公称通径 DN (mm)")
@param(NOZ_VAP=LENGTH, TooltipShort=u"气相出口口径", TooltipLong=u"蒸发壳体顶部气相出口公称通径 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出高", TooltipLong=u"接管法兰面距外壁伸出高度 (mm)")
def EQ_KETTLE_REBOILER_BKU(
    s,
    D_BOX=700.0,
    D_KETTLE=1300.0,
    L_KETTLE=3600.0,
    L_TRANS=650.0,
    L_BOX=550.0,
    H_SADDLE=950.0,
    A_SADDLE=3000.0,
    NOZ_T=150.0,
    NOZ_LIQ=150.0,
    NOZ_VAP=300.0,
    NOZ_EXT=260.0,
    ID=u"EQ_KETTLE_REBOILER_BKU",
    **kw
):
    u"""GB/T 151 BKU 型釜式重沸器 (沿 X 轴布置，前端管箱在 -X，偏心扩大蒸发壳体向 +Z 偏心，鞍座底面 Z=-H_SADDLE)。"""
    D_BOX = float(D_BOX)
    if D_BOX < 1.0:
        D_BOX = 1.0
    D_KETTLE = float(D_KETTLE)
    if D_KETTLE < 1.0:
        D_KETTLE = 1.0
    R_B = D_BOX / 2.0
    R_K = D_KETTLE / 2.0
    L_KETTLE = float(L_KETTLE)
    if L_KETTLE < 1.0:
        L_KETTLE = 1.0
    L_TRANS = max(350.0, float(L_TRANS))
    L_BOX = max(300.0, float(L_BOX))
    dz_ecc = (R_K - R_B) * 0.72
    H_SADDLE = float(H_SADDLE)
    if H_SADDLE < 1.0:
        H_SADDLE = 1.0
    NOZ_T = max(50.0, float(NOZ_T))
    NOZ_LIQ = max(50.0, float(NOZ_LIQ))
    NOZ_VAP = max(100.0, float(NOZ_VAP))
    NOZ_EXT = max(160.0, float(NOZ_EXT))

    x_ts = 0.0
    l_stub = max(240.0, D_BOX * 0.35)
    x_trans_start = x_ts + l_stub
    x_kettle_start = x_trans_start + L_TRANS
    x_kettle_end = x_kettle_start + L_KETTLE
    fl_t = max(46.0, D_BOX * 0.065)
    r_fl_box = R_B + max(65.0, D_BOX * 0.095)
    z_gnd = -H_SADDLE

    # 1. 大直径蒸发壳体 (中心线在 Z = dz_ecc)
    o_main = CYLINDER(s, R=R_K, H=L_KETTLE, O=0.0).rotateY(90.0).translate((x_kettle_start, 0.0, dz_ecc))

    # 2. 后端 EHA 2:1 椭圆封头
    o_rh = ELLIPSOIDHEAD(s, R=R_K).rotateY(90.0).translate((x_kettle_end - 2.0, 0.0, dz_ecc))
    o_main.uniteWith(o_rh)
    o_rh.erase()

    # 3. 偏心过渡锥段 (从 X=x_trans_start, Z=0 过渡至 X=x_kettle_start, Z=dz_ecc)
    n_seg = 10
    seg_l = L_TRANS / float(n_seg)
    for i in range(n_seg):
        t0 = float(i) / float(n_seg)
        t1 = float(i + 1) / float(n_seg)
        r0 = R_B + (R_K - R_B) * t0
        r1 = R_B + (R_K - R_B) * t1
        zm = dz_ecc * (t0 + t1) * 0.5
        xs = x_trans_start + i * seg_l - 2.0
        o_sg = CONE(s, R1=r0, R2=r1, H=seg_l + 4.0).rotateY(90.0).translate((xs, 0.0, zm))
        o_main.uniteWith(o_sg)
        o_sg.erase()

    # 4. 小端壳体短节 + 管板主法兰 + 前端 B 型管箱 + 前端椭圆封头
    o_stub = CYLINDER(s, R=R_B, H=l_stub + 8.0, O=0.0).rotateY(90.0).translate((x_ts - 4.0, 0.0, 0.0))
    o_main.uniteWith(o_stub)
    o_stub.erase()

    o_tsfl = CYLINDER(s, R=r_fl_box, H=fl_t * 1.4, O=0.0).rotateY(90.0).translate((x_ts - fl_t * 0.7, 0.0, 0.0))
    o_main.uniteWith(o_tsfl)
    o_tsfl.erase()

    o_box = CYLINDER(s, R=R_B, H=L_BOX + 4.0, O=0.0).rotateY(90.0).translate((x_ts - L_BOX, 0.0, 0.0))
    o_main.uniteWith(o_box)
    o_box.erase()

    o_fh = ELLIPSOIDHEAD(s, R=R_B).rotateY(-90.0).translate((x_ts - L_BOX + 2.0, 0.0, 0.0))
    o_main.uniteWith(o_fh)
    o_fh.erase()

    # 5. 蒸发壳体后端溢流堰侧检查/排液短管 (非端口特征)
    o_weir_fl = CYLINDER(s, R=130.0, H=28.0, O=0.0).translate((x_kettle_end - 320.0, 0.0, dz_ecc - R_K - 180.0))
    o_weir_p = CYLINDER(s, R=65.0, H=220.0, O=0.0).translate((x_kettle_end - 320.0, 0.0, dz_ecc - R_K - 170.0))
    o_main.uniteWith(o_weir_p)
    o_weir_p.erase()
    o_main.uniteWith(o_weir_fl)
    o_weir_fl.erase()

    # 6. 双鞍式支座 (前鞍座位于蒸发壳体前段，后鞍座位于蒸发壳体后段)
    a_sad = min(L_KETTLE - 550.0, max(900.0, float(A_SADDLE)))
    x_mid_k = x_kettle_start + L_KETTLE * 0.5
    sad_w = max(240.0, D_KETTLE * 0.22)
    sad_b = D_KETTLE * 0.84
    base_t = max(22.0, D_KETTLE * 0.02)
    web_t = max(18.0, D_KETTLE * 0.016)
    z_sad_top = dz_ecc - R_K * 0.45
    h_web = max(120.0, z_sad_top - (z_gnd + base_t))
    for xs in (x_mid_k - a_sad * 0.5, x_mid_k + a_sad * 0.5):
        o_bp = CORNERBOX(s, L=sad_w, W=sad_b, H=base_t).translate((xs - sad_w * 0.5, -sad_b * 0.5, z_gnd))
        o_main.uniteWith(o_bp)
        o_bp.erase()
        o_wb = CORNERBOX(s, L=web_t, W=sad_b * 0.88, H=h_web).translate((xs - web_t * 0.5, -sad_b * 0.44, z_gnd + base_t - 2.0))
        o_main.uniteWith(o_wb)
        o_wb.erase()
        for ry in (-sad_b * 0.36, 0.0, sad_b * 0.36):
            o_rb = CORNERBOX(s, L=sad_w * 0.86, W=web_t, H=h_web * 0.82).translate(
                (xs - sad_w * 0.43, ry - web_t * 0.5, z_gnd + base_t - 2.0)
            )
            o_main.uniteWith(o_rb)
            o_rb.erase()

    # 7. 4 个工艺接管
    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    def _add_v_nozzle(x_pos, z_center, r_body, dn_val, up=True):
        r_p, r_f, t_f = _fl_dims(dn_val)
        embed = r_body * 0.32
        if up:
            z_face = z_center + r_body + NOZ_EXT
            z_start = z_center + r_body - embed
            o_p = CYLINDER(s, R=r_p, H=z_face - t_f - z_start + 2.0, O=0.0).translate((x_pos, 0.0, z_start))
            o_f = CYLINDER(s, R=r_f, H=t_f, O=0.0).translate((x_pos, 0.0, z_face - t_f))
            d_vec = (0.0, 0.0, 1.0)
        else:
            z_face = z_center - r_body - NOZ_EXT
            z_start = z_center - r_body + embed
            o_p = CYLINDER(s, R=r_p, H=z_start - (z_face + t_f) + 2.0, O=0.0).translate((x_pos, 0.0, z_face + t_f - 2.0))
            o_f = CYLINDER(s, R=r_f, H=t_f, O=0.0).translate((x_pos, 0.0, z_face))
            d_vec = (0.0, 0.0, -1.0)
        o_main.uniteWith(o_p)
        o_p.erase()
        o_main.uniteWith(o_f)
        o_f.erase()
        return (x_pos, 0.0, z_face), d_vec

    x_box_mid = x_ts - L_BOX * 0.55
    p_t_in, d_t_in = _add_v_nozzle(x_box_mid, 0.0, R_B, NOZ_T, up=True)
    p_t_out, d_t_out = _add_v_nozzle(x_box_mid, 0.0, R_B, NOZ_T, up=False)
    p_s_in, d_s_in = _add_v_nozzle(x_kettle_start + L_KETTLE * 0.25, dz_ecc, R_K, NOZ_LIQ, up=False)
    p_s_out, d_s_out = _add_v_nozzle(x_kettle_start + L_KETTLE * 0.55, dz_ecc, R_K, NOZ_VAP, up=True)

    # 8. 注册 4 个工艺端口
    s.setPoint(p_t_in, d_t_in)
    s.setPoint(p_t_out, d_t_out)
    s.setPoint(p_s_in, d_s_in)
    s.setPoint(p_s_out, d_s_out)

    # 9. 注册线性标注
    s.setLinearDimension('D_BOX', (x_box_mid, -R_B, 0.0), (x_box_mid, R_B, 0.0))
    s.setLinearDimension('D_KETTLE', (x_mid_k, -R_K, dz_ecc), (x_mid_k, R_K, dz_ecc))
    s.setLinearDimension('L_KETTLE', (x_kettle_start, 0.0, dz_ecc), (x_kettle_end, 0.0, dz_ecc))
    s.setLinearDimension('H_SADDLE', (x_mid_k, 0.0, z_gnd), (x_mid_k, 0.0, 0.0))
    s.setLinearDimension('A_SADDLE', (x_mid_k - a_sad * 0.5, 0.0, z_gnd), (x_mid_k + a_sad * 0.5, 0.0, z_gnd))
