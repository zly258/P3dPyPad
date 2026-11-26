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
          TooltipShort=u"旋风分离器 (切向矩形入口)",
          TooltipLong=u"工业气固旋风分离器参数化模型，含主圆柱段、长锥体、切向矩形入口风道与矩形法兰、顶部溢流排气筒、底部卸料法兰及4个耳式支座",
          LengthUnit="mm",
          Ports="3")
@group("MainDimensions", TooltipLong=u"旋风分离器主要尺寸参数")
@param(D_CYL=LENGTH, TooltipShort=u"筒体直径", TooltipLong=u"旋风分离器主圆柱段外径 D (mm)")
@param(H_CYL=LENGTH, TooltipShort=u"圆柱段高", TooltipLong=u"主圆柱段高度 (mm)", Ask4Dist=True)
@param(H_CONE=LENGTH, TooltipShort=u"长锥体高", TooltipLong=u"下部倒锥体高度 (mm)", Ask4Dist=True)
@param(D_VORTEX=LENGTH, TooltipShort=u"溢流管径", TooltipLong=u"顶部溢流排气管公称通径 DN (mm)")
@param(H_TOP=LENGTH, TooltipShort=u"溢流管伸出高", TooltipLong=u"顶部溢流管法兰面距顶盖高度 (mm)")
@param(W_IN=LENGTH, TooltipShort=u"切向入口宽", TooltipLong=u"切向矩形入口风道宽度 (mm)")
@param(H_IN=LENGTH, TooltipShort=u"切向入口高", TooltipLong=u"切向矩形入口风道高度 (mm)")
@param(L_IN=LENGTH, TooltipShort=u"入口伸出长", TooltipLong=u"切向入口法兰面距筒体中心线水平距离 (mm)")
@param(D_DIS=LENGTH, TooltipShort=u"底卸料口径", TooltipLong=u"锥底固体卸料口公称通径 DN (mm)")
@param(H_DIS=LENGTH, TooltipShort=u"底卸料管长", TooltipLong=u"底部卸料管法兰面距锥底伸出长度 (mm)")
def EQ_CYCLONE_SEPARATOR(
    s,
    D_CYL=1000.0,
    H_CYL=1500.0,
    H_CONE=2200.0,
    D_VORTEX=500.0,
    H_TOP=750.0,
    W_IN=260.0,
    H_IN=520.0,
    L_IN=750.0,
    D_DIS=250.0,
    H_DIS=380.0,
    ID=u"EQ_CYCLONE_SEPARATOR",
    **kw
):
    u"""工业旋风分离器 (柱锥交界面 Z=0，圆柱向上至 H_CYL，长锥向下至 -H_CONE，切向矩形入口位于 -X/+Y 侧)。"""
    D_CYL = float(D_CYL)
    if D_CYL < 1.0:
        D_CYL = 1.0
    R_C = D_CYL / 2.0
    H_CYL = float(H_CYL)
    if H_CYL < 1.0:
        H_CYL = 1.0
    H_CONE = float(H_CONE)
    if H_CONE < 1.0:
        H_CONE = 1.0
    D_VORTEX = min(D_CYL * 0.72, max(150.0, float(D_VORTEX)))
    H_TOP = max(250.0, float(H_TOP))
    W_IN = min(R_C * 0.85, max(100.0, float(W_IN)))
    H_IN = min(H_CYL * 0.75, max(180.0, float(H_IN)))
    L_IN = max(R_C + 200.0, float(L_IN))
    D_DIS = min(D_CYL * 0.45, max(100.0, float(D_DIS)))
    H_DIS = max(180.0, float(H_DIS))

    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    r_pd, r_fd, t_fd = _fl_dims(D_DIS)

    # 1. 主圆柱段 + 顶盖法兰边 + 柱锥过渡法兰环
    o_main = CYLINDER(s, R=R_C, H=H_CYL, O=0.0)
    ring_t = max(24.0, D_CYL * 0.025)
    o_top_rim = CYLINDER(s, R=R_C + 45.0, H=ring_t, O=0.0).translate((0.0, 0.0, H_CYL - ring_t))
    o_mid_rim = CYLINDER(s, R=R_C + 38.0, H=ring_t, O=0.0).translate((0.0, 0.0, -ring_t * 0.4))
    o_main.uniteWith(o_top_rim)
    o_top_rim.erase()
    o_main.uniteWith(o_mid_rim)
    o_mid_rim.erase()

    # 2. 长倒锥体
    o_cone = CONE(s, R1=max(r_pd + 12.0, R_C * 0.28), R2=R_C, H=H_CONE + 6.0).translate((0.0, 0.0, -H_CONE))
    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 3. 顶部溢流排气管与法兰 (Port 1, +Z)
    r_pv, r_fv, t_fv = _fl_dims(D_VORTEX)
    z_top_face = H_CYL + H_TOP
    o_vp = CYLINDER(s, R=r_pv, H=H_TOP - t_fv + 40.0, O=0.0).translate((0.0, 0.0, H_CYL - 35.0))
    o_vf = CYLINDER(s, R=r_fv, H=t_fv, O=0.0).translate((0.0, 0.0, z_top_face - t_fv))
    o_main.uniteWith(o_vp)
    o_vp.erase()
    o_main.uniteWith(o_vf)
    o_vf.erase()
    p_top = (0.0, 0.0, z_top_face)

    # 4. 切向矩形入口风道与矩形法兰 (Port 2, -X 方向，外壁与筒体 +Y 切线齐平)
    y_in_outer = R_C
    y_in_inner = R_C - W_IN
    y_in_mid = (y_in_outer + y_in_inner) * 0.5
    z_in_top = H_CYL - ring_t - 20.0
    z_in_bot = z_in_top - H_IN
    z_in_mid = (z_in_top + z_in_bot) * 0.5
    fl_rect_t = 24.0
    fl_rect_pad = 48.0
    x_in_face = -L_IN
    duct_len = L_IN + R_C * 0.35 - fl_rect_t
    o_duct = CORNERBOX(s, L=duct_len, W=W_IN, H=H_IN).translate((x_in_face + fl_rect_t - 2.0, y_in_inner, z_in_bot))
    o_rfl = CORNERBOX(s, L=fl_rect_t, W=W_IN + fl_rect_pad * 2.0, H=H_IN + fl_rect_pad * 2.0).translate(
        (x_in_face, y_in_inner - fl_rect_pad, z_in_bot - fl_rect_pad)
    )
    o_main.uniteWith(o_duct)
    o_duct.erase()
    o_main.uniteWith(o_rfl)
    o_rfl.erase()
    p_in = (x_in_face, y_in_mid, z_in_mid)

    # 5. 底部固体卸料管与法兰 (Port 3, -Z)
    z_dis_face = -H_CONE - H_DIS
    o_dp = CYLINDER(s, R=r_pd, H=H_DIS - t_fd + 35.0, O=0.0).translate((0.0, 0.0, z_dis_face + t_fd - 2.0))
    o_df = CYLINDER(s, R=r_fd, H=t_fd, O=0.0).translate((0.0, 0.0, z_dis_face))
    o_main.uniteWith(o_dp)
    o_dp.erase()
    o_main.uniteWith(o_df)
    o_df.erase()
    p_dis = (0.0, 0.0, z_dis_face)

    # 6. 4 个耳式安装支座 (位于柱锥交界处上方)
    lug_l = max(130.0, D_CYL * 0.14)
    lug_w = max(140.0, D_CYL * 0.15)
    lug_h = max(200.0, D_CYL * 0.22)
    for i in range(4):
        ang = 45.0 + i * 90.0
        o_lg_bp = CORNERBOX(s, L=lug_l + 30.0, W=lug_w, H=20.0).translate((R_C - 25.0, -lug_w * 0.5, 40.0)).rotateZ(ang)
        o_lg_wb = CORNERBOX(s, L=lug_l + 20.0, W=18.0, H=lug_h).translate((R_C - 25.0, -9.0, 56.0)).rotateZ(ang)
        o_main.uniteWith(o_lg_bp)
        o_lg_bp.erase()
        o_main.uniteWith(o_lg_wb)
        o_lg_wb.erase()

    # 7. 注册 3 个工艺端口
    s.setPoint(p_top, (0.0, 0.0, 1.0))
    s.setPoint(p_in, (-1.0, 0.0, 0.0))
    s.setPoint(p_dis, (0.0, 0.0, -1.0))

    # 8. 注册线性标注
    s.setLinearDimension('D_CYL', (-R_C, 0.0, H_CYL * 0.5), (R_C, 0.0, H_CYL * 0.5))
    s.setLinearDimension('H_CYL', (R_C, 0.0, 0.0), (R_C, 0.0, H_CYL))
    s.setLinearDimension('H_CONE', (R_C, 0.0, -H_CONE), (R_C, 0.0, 0.0))
