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
          TooltipShort=u"卧式储罐/分离器 (NB/T 47042)",
          TooltipLong=u"NB/T 47042 卧式压力容器与气液分离器参数化模型，含卧式筒体、双 EHA 2:1 椭圆形封头、双鞍式支座、顶部人孔及 4 个工艺接管",
          LengthUnit="mm",
          Ports="5")
@group("MainDimensions", TooltipLong=u"卧式储罐主体、鞍座与接管主要尺寸参数")
@param(D=LENGTH, TooltipShort=u"筒体公称直径", TooltipLong=u"卧式筒体公称直径 DN (mm)")
@param(L_SHELL=LENGTH, TooltipShort=u"筒体直段长度", TooltipLong=u"两封头切线间筒体直段长度 L (mm)", Ask4Dist=True)
@param(H_SADDLE=LENGTH, TooltipShort=u"设备中心高", TooltipLong=u"鞍座底板底面至筒体中心线高度 H (mm)", Ask4Dist=True)
@param(A_SADDLE=LENGTH, TooltipShort=u"鞍座中心距", TooltipLong=u"双鞍座中心距 A (mm)", Ask4Dist=True)
@param(N_MH=LENGTH, TooltipShort=u"顶部人孔通径", TooltipLong=u"顶部人孔公称通径 DN (mm)")
@param(N_IN=LENGTH, TooltipShort=u"进料口通径", TooltipLong=u"顶部进料接管公称通径 DN (mm)")
@param(N_GAS=LENGTH, TooltipShort=u"气相口通径", TooltipLong=u"顶部气相出口公称通径 DN (mm)")
@param(N_LIQ=LENGTH, TooltipShort=u"液相口通径", TooltipLong=u"底部液相出口公称通径 DN (mm)")
@param(N_DRN=LENGTH, TooltipShort=u"排污口通径", TooltipLong=u"底部排污接管公称通径 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出高", TooltipLong=u"工艺接管法兰面距筒体外壁伸出高度 (mm)")
def EQ_HORIZONTAL_VESSEL(
    s,
    D=1600.0,
    L_SHELL=4000.0,
    H_SADDLE=1200.0,
    A_SADDLE=2800.0,
    N_MH=450.0,
    N_IN=150.0,
    N_GAS=150.0,
    N_LIQ=100.0,
    N_DRN=50.0,
    NOZ_EXT=250.0,
    ID=u"EQ_HORIZONTAL_VESSEL",
    **kw
):
    u"""NB/T 47042 卧式储罐/分离器 (筒体沿 X 轴对称，中心线 Y=0, Z=0，鞍座底面 Z=-H_SADDLE)。"""
    D = float(D)
    if D < 1.0:
        D = 1.0
    R_V = D / 2.0
    L_SHELL = float(L_SHELL)
    if L_SHELL < 1.0:
        L_SHELL = 1.0
    H_SADDLE = float(H_SADDLE)
    if H_SADDLE < 1.0:
        H_SADDLE = 1.0
    A_SADDLE = min(L_SHELL - 400.0, max(500.0, float(A_SADDLE)))
    NOZ_EXT = max(120.0, float(NOZ_EXT))

    half_l = L_SHELL / 2.0
    z_gnd = -H_SADDLE

    # 1. 卧式筒体 + 双 EHA 2:1 椭圆形封头
    o_main = CYLINDER(s, R=R_V, H=L_SHELL, O=0.0).rotateY(90.0).translate((-half_l, 0.0, 0.0))

    o_hl = ELLIPSOIDHEAD(s, R=R_V).rotateY(-90.0).translate((-half_l + 2.0, 0.0, 0.0))
    o_main.uniteWith(o_hl)
    o_hl.erase()

    o_hr = ELLIPSOIDHEAD(s, R=R_V).rotateY(90.0).translate((half_l - 2.0, 0.0, 0.0))
    o_main.uniteWith(o_hr)
    o_hr.erase()

    # 2. 双鞍式支座 (含120度弧形垫板、腹板、筋板、底板)
    sad_w = D * 0.866
    sad_l = max(220.0, D * 0.20)
    base_t = max(16.0, D * 0.015)
    web_t = max(14.0, D * 0.012)
    rib_t = max(12.0, D * 0.010)
    pad_t = max(12.0, D * 0.010)
    pad_l = sad_l + 60.0
    z_cradle_top = -R_V * 0.5  # 120°包角顶边高度

    for sx in (-1.0, 1.0):
        xc = sx * (A_SADDLE / 2.0)
        # 鞍座底板
        o_base = CORNERBOX(s, L=sad_l, W=sad_w, H=base_t).translate(
            (xc - sad_l / 2.0, -sad_w / 2.0, z_gnd)
        )
        o_main.uniteWith(o_base)
        o_base.erase()

        # 鞍座中间腹板 (向上深入筒体10mm确保无缝融合)
        web_h = (z_cradle_top + R_V * 0.12) - (z_gnd + base_t)
        o_web = CORNERBOX(s, L=web_t, W=sad_w * 0.92, H=web_h + 10.0).translate(
            (xc - web_t / 2.0, -sad_w * 0.46, z_gnd + base_t - 5.0)
        )
        # 用略小于筒体的弧面辅助或直接与筒体并集
        o_main.uniteWith(o_web)
        o_web.erase()

        # 3道纵向筋板 (中、左、右)
        for ry in (-sad_w * 0.36, 0.0, sad_w * 0.36):
            rib_h = max(80.0, (-math.sqrt(max(1.0, R_V * R_V - ry * ry)) + 25.0) - (z_gnd + base_t))
            o_rib = CORNERBOX(s, L=sad_l * 0.88, W=rib_t, H=rib_h).translate(
                (xc - sad_l * 0.44, ry - rib_t / 2.0, z_gnd + base_t - 4.0)
            )
            o_main.uniteWith(o_rib)
            o_rib.erase()

        # 120度弧形包角垫板 (圆柱环与矩形框求交)
        o_pad_cyl = CYLINDER(s, R=R_V + pad_t, H=pad_l, O=R_V - 15.0).rotateY(90.0).translate(
            (xc - pad_l / 2.0, 0.0, 0.0)
        )
        o_pad_clip = CORNERBOX(s, L=pad_l + 20.0, W=sad_w, H=R_V * 0.65).translate(
            (xc - pad_l / 2.0 - 10.0, -sad_w / 2.0, -R_V - pad_t - 10.0)
        )
        o_pad_cyl.intersectWith(o_pad_clip)
        o_pad_clip.erase()
        o_main.uniteWith(o_pad_cyl)
        o_pad_cyl.erase()

    # 3. 辅助接管构造函数
    def _add_vert_nozzle(x_pos, z_sign, dn_val, ext_h):
        r_p, r_f, t_f = _std_noz_dims(dn_val)
        z_face = z_sign * (R_V + ext_h)
        embed = R_V * 0.25
        pipe_h = ext_h + embed - t_f
        if z_sign > 0:
            o_p = CYLINDER(s, R=r_p, H=pipe_h + 2.0, O=0.0).translate((x_pos, 0.0, R_V - embed))
            o_f = CYLINDER(s, R=r_f, H=t_f, O=0.0).translate((x_pos, 0.0, z_face - t_f))
        else:
            o_p = CYLINDER(s, R=r_p, H=pipe_h + 2.0, O=0.0).rotateX(180.0).translate((x_pos, 0.0, -R_V + embed))
            o_f = CYLINDER(s, R=r_f, H=t_f, O=0.0).rotateX(180.0).translate((x_pos, 0.0, z_face + t_f))
        o_main.uniteWith(o_p)
        o_p.erase()
        o_main.uniteWith(o_f)
        o_f.erase()
        return (x_pos, 0.0, z_face)

    # 4. 顶部人孔 + 4 工艺接管 (共 5 个端口)
    p_mh = _add_vert_nozzle(0.0, 1.0, N_MH, NOZ_EXT + 50.0)
    p_in = _add_vert_nozzle(-half_l * 0.65, 1.0, N_IN, NOZ_EXT)
    p_gas = _add_vert_nozzle(half_l * 0.65, 1.0, N_GAS, NOZ_EXT)
    p_liq = _add_vert_nozzle(half_l * 0.55, -1.0, N_LIQ, NOZ_EXT)
    p_drn = _add_vert_nozzle(-half_l * 0.55, -1.0, N_DRN, NOZ_EXT * 0.85)

    # 5. 注册 5 个端口
    s.setPoint(p_in, (0.0, 0.0, 1.0))
    s.setPoint(p_gas, (0.0, 0.0, 1.0))
    s.setPoint(p_mh, (0.0, 0.0, 1.0))
    s.setPoint(p_liq, (0.0, 0.0, -1.0))
    s.setPoint(p_drn, (0.0, 0.0, -1.0))

    # 6. 注册线性标注 (严格 3 位置参数)
    s.setLinearDimension('D', (0.0, -R_V, 0.0), (0.0, R_V, 0.0))
    s.setLinearDimension('L_SHELL', (-half_l, 0.0, R_V), (half_l, 0.0, R_V))
    s.setLinearDimension('A_SADDLE', (-A_SADDLE / 2.0, 0.0, z_gnd), (A_SADDLE / 2.0, 0.0, z_gnd))
    s.setLinearDimension('H_SADDLE', (0.0, 0.0, z_gnd), (0.0, 0.0, 0.0))
