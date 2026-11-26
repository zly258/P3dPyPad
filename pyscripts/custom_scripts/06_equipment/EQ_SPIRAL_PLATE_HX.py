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
          TooltipShort=u"螺旋板换热器 (GB/T 28712)",
          TooltipLong=u"GB/T 28712 卧式可拆型螺旋板换热器参数化模型，含扁圆柱螺旋主体、双端重型法兰端盖、双支腿底板及4个轴向/切向工艺接管",
          LengthUnit="mm",
          Ports="4")
@group("MainDimensions", TooltipLong=u"螺旋板换热器主要尺寸参数")
@param(D_BODY=LENGTH, TooltipShort=u"主体外径", TooltipLong=u"螺旋板换热器扁圆柱主体公称直径 D (mm)")
@param(W_BODY=LENGTH, TooltipShort=u"板宽筒厚", TooltipLong=u"螺旋体有效轴向宽度 W (mm)", Ask4Dist=True)
@param(H_CL=LENGTH, TooltipShort=u"中心安装高", TooltipLong=u"支腿底板底面至螺旋体中心线高度 H (mm)", Ask4Dist=True)
@param(NOZ_A=LENGTH, TooltipShort=u"热介质接口", TooltipLong=u"热介质通道进出口公称通径 DN (mm)")
@param(NOZ_B=LENGTH, TooltipShort=u"冷介质接口", TooltipLong=u"冷介质通道进出口公称通径 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出高", TooltipLong=u"工艺接管法兰面伸出高度 (mm)")
def EQ_SPIRAL_PLATE_HX(
    s,
    D_BODY=1200.0,
    W_BODY=600.0,
    H_CL=950.0,
    NOZ_A=150.0,
    NOZ_B=150.0,
    NOZ_EXT=220.0,
    ID=u"EQ_SPIRAL_PLATE_HX",
    **kw
):
    u"""GB/T 28712 卧式螺旋板换热器 (扁圆柱轴线沿 X 轴，中心在原点，支腿底面 Z=-H_CL)。"""
    D_BODY = float(D_BODY)
    if D_BODY < 1.0:
        D_BODY = 1.0
    R_B = D_BODY / 2.0
    W_BODY = float(W_BODY)
    if W_BODY < 1.0:
        W_BODY = 1.0
    H_CL = float(H_CL)
    if H_CL < 1.0:
        H_CL = 1.0
    NOZ_A = max(50.0, float(NOZ_A))
    NOZ_B = max(50.0, float(NOZ_B))
    NOZ_EXT = max(140.0, float(NOZ_EXT))

    half_w = W_BODY * 0.5
    fl_t = max(32.0, D_BODY * 0.03)
    cov_t = max(36.0, D_BODY * 0.034)
    r_fl = R_B + max(65.0, D_BODY * 0.065)
    z_gnd = -H_CL

    # 1. 扁圆柱螺旋体主壳
    o_main = CYLINDER(s, R=R_B, H=W_BODY, O=0.0).rotateY(90.0).translate((-half_w, 0.0, 0.0))

    # 2. 双端法兰环 + 可拆端盖 (含阶梯外轮廓与微拱封盖)
    for sx in (-1.0, 1.0):
        x_fl = -half_w if sx < 0 else half_w - fl_t
        o_fl = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).rotateY(90.0).translate((x_fl, 0.0, 0.0))
        o_main.uniteWith(o_fl)
        o_fl.erase()

        x_cov = -half_w - cov_t + 2.0 if sx < 0 else half_w - 2.0
        o_cv = CYLINDER(s, R=r_fl, H=cov_t, O=0.0).rotateY(90.0).translate((x_cov, 0.0, 0.0))
        o_main.uniteWith(o_cv)
        o_cv.erase()

        # 端盖中心加强凸台
        x_boss = -half_w - cov_t - 26.0 if sx < 0 else half_w + cov_t - 4.0
        o_bs = CYLINDER(s, R=R_B * 0.52, H=30.0, O=0.0).rotateY(90.0).translate((x_boss, 0.0, 0.0))
        o_main.uniteWith(o_bs)
        o_bs.erase()

    # 3. 底部双支腿与底板
    leg_span_y = D_BODY * 0.62
    leg_w_x = W_BODY * 0.72
    leg_t_y = max(140.0, D_BODY * 0.14)
    bp_t = max(20.0, D_BODY * 0.02)
    z_leg_top = -R_B * 0.55
    h_leg = max(160.0, z_leg_top - (z_gnd + bp_t))
    for sy in (-1.0, 1.0):
        yc = sy * leg_span_y * 0.5
        o_bp = CORNERBOX(s, L=leg_w_x + 80.0, W=leg_t_y + 80.0, H=bp_t).translate(
            (-(leg_w_x + 80.0) * 0.5, yc - (leg_t_y + 80.0) * 0.5, z_gnd)
        )
        o_main.uniteWith(o_bp)
        o_bp.erase()
        o_lg = CORNERBOX(s, L=leg_w_x, W=leg_t_y, H=h_leg).translate(
            (-leg_w_x * 0.5, yc - leg_t_y * 0.5, z_gnd + bp_t - 2.0)
        )
        o_main.uniteWith(o_lg)
        o_lg.erase()

    # 4. 4 个工艺接管 (2 个轴向中心口 + 2 个外缘切向/径向口)
    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    # Port 1: +X 端盖中心热介质进口
    r_pa, r_fa, t_fa = _fl_dims(NOZ_A)
    x_p1 = half_w + cov_t + NOZ_EXT
    o_p1 = CYLINDER(s, R=r_pa, H=NOZ_EXT - t_fa + 40.0, O=0.0).rotateY(90.0).translate((half_w + cov_t - 35.0, 0.0, 0.0))
    o_f1 = CYLINDER(s, R=r_fa, H=t_fa, O=0.0).rotateY(90.0).translate((x_p1 - t_fa, 0.0, 0.0))
    o_main.uniteWith(o_p1)
    o_p1.erase()
    o_main.uniteWith(o_f1)
    o_f1.erase()
    p1 = (x_p1, 0.0, 0.0)

    # Port 2: 顶部外缘热介质出口 (+Z, 切向偏移 -Y)
    y_t2 = -R_B * 0.42
    z_p2 = R_B + NOZ_EXT
    o_p2 = CYLINDER(s, R=r_pa, H=z_p2 - t_fa - R_B * 0.55 + 2.0, O=0.0).translate((W_BODY * 0.14, y_t2, R_B * 0.55))
    o_f2 = CYLINDER(s, R=r_fa, H=t_fa, O=0.0).translate((W_BODY * 0.14, y_t2, z_p2 - t_fa))
    o_main.uniteWith(o_p2)
    o_p2.erase()
    o_main.uniteWith(o_f2)
    o_f2.erase()
    p2 = (W_BODY * 0.14, y_t2, z_p2)

    # Port 3: -X 端盖中心冷介质出口
    r_pb, r_fb, t_fb = _fl_dims(NOZ_B)
    x_p3 = -(half_w + cov_t + NOZ_EXT)
    o_p3 = CYLINDER(s, R=r_pb, H=NOZ_EXT - t_fb + 40.0, O=0.0).rotateY(-90.0).translate((-(half_w + cov_t - 35.0), 0.0, 0.0))
    o_f3 = CYLINDER(s, R=r_fb, H=t_fb, O=0.0).rotateY(-90.0).translate((x_p3 + t_fb, 0.0, 0.0))
    o_main.uniteWith(o_p3)
    o_p3.erase()
    o_main.uniteWith(o_f3)
    o_f3.erase()
    p3 = (x_p3, 0.0, 0.0)

    # Port 4: 侧面外缘冷介质进口 (+Y, 位于下半圆避开支腿)
    y_p4 = R_B + NOZ_EXT
    z_t4 = R_B * 0.35
    o_p4 = CYLINDER(s, R=r_pb, H=y_p4 - t_fb - R_B * 0.55 + 2.0, O=0.0).rotateX(-90.0).translate((-W_BODY * 0.14, R_B * 0.55, z_t4))
    o_f4 = CYLINDER(s, R=r_fb, H=t_fb, O=0.0).rotateX(-90.0).translate((-W_BODY * 0.14, y_p4 - t_fb, z_t4))
    o_main.uniteWith(o_p4)
    o_p4.erase()
    o_main.uniteWith(o_f4)
    o_f4.erase()
    p4 = (-W_BODY * 0.14, y_p4, z_t4)

    # 5. 注册 4 个工艺端口
    s.setPoint(p1, (1.0, 0.0, 0.0))
    s.setPoint(p2, (0.0, 0.0, 1.0))
    s.setPoint(p3, (-1.0, 0.0, 0.0))
    s.setPoint(p4, (0.0, 1.0, 0.0))

    # 6. 注册线性标注
    s.setLinearDimension('D_BODY', (0.0, -R_B, 0.0), (0.0, R_B, 0.0))
    s.setLinearDimension('W_BODY', (-half_w, 0.0, 0.0), (half_w, 0.0, 0.0))
    s.setLinearDimension('H_CL', (0.0, 0.0, z_gnd), (0.0, 0.0, 0.0))
