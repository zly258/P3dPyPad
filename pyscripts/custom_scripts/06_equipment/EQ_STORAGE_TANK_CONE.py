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
          TooltipShort=u"常压锥顶立式储罐 (NB/T 47003.1)",
          TooltipLong=u"NB/T 47003.1 常压固定锥顶立式储罐参数化模型，含平底边缘环、大筒体、锥顶、侧人孔、顶呼吸阀口及进出口接管",
          LengthUnit="mm",
          Ports="4")
@group("MainDimensions", TooltipLong=u"常压锥顶储罐罐体、锥顶与接管尺寸参数")
@param(D=LENGTH, TooltipShort=u"储罐公称直径", TooltipLong=u"立式储罐罐体公称直径 DN (mm)")
@param(H_SHELL=LENGTH, TooltipShort=u"罐壁高度", TooltipLong=u"罐底至顶包边角钢罐壁高度 H (mm)", Ask4Dist=True)
@param(H_CONE=LENGTH, TooltipShort=u"锥顶高度", TooltipLong=u"锥顶中心高度 (mm)", Ask4Dist=True)
@param(N_VENT=LENGTH, TooltipShort=u"呼吸阀口通径", TooltipLong=u"罐顶呼吸阀/通气口公称通径 DN (mm)")
@param(N_IN=LENGTH, TooltipShort=u"进料口通径", TooltipLong=u"上部进料口公称通径 DN (mm)")
@param(N_OUT=LENGTH, TooltipShort=u"出料口通径", TooltipLong=u"下部出料口公称通径 DN (mm)")
@param(N_DRN=LENGTH, TooltipShort=u"排污口通径", TooltipLong=u"底部排污口公称通径 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出长", TooltipLong=u"侧向接管法兰面距罐壁伸出长度 (mm)")
def EQ_STORAGE_TANK_CONE(
    s,
    D=4000.0,
    H_SHELL=4500.0,
    H_CONE=500.0,
    N_VENT=150.0,
    N_IN=100.0,
    N_OUT=150.0,
    N_DRN=80.0,
    NOZ_EXT=280.0,
    ID=u"EQ_STORAGE_TANK_CONE",
    **kw
):
    u"""NB/T 47003.1 常压锥顶立式储罐 (罐底平置 Z=0，+Z 向上)。"""
    D = float(D)
    if D < 1.0:
        D = 1.0
    R_V = D / 2.0
    H_SHELL = float(H_SHELL)
    if H_SHELL < 1.0:
        H_SHELL = 1.0
    H_CONE = float(H_CONE)
    if H_CONE < 1.0:
        H_CONE = 1.0
    NOZ_EXT = max(150.0, float(NOZ_EXT))

    # 1. 底边缘环 + 主罐壁筒体 + 顶包边加强环 + 固定锥顶
    o_main = CYLINDER(s, R=R_V + 60.0, H=24.0, O=0.0)

    o_shell = CYLINDER(s, R=R_V, H=H_SHELL, O=0.0).translate((0.0, 0.0, 10.0))
    o_main.uniteWith(o_shell)
    o_shell.erase()

    o_curb = CYLINDER(s, R=R_V + 35.0, H=65.0, O=0.0).translate((0.0, 0.0, H_SHELL - 45.0))
    o_main.uniteWith(o_curb)
    o_curb.erase()

    o_cone = CONE(s, R1=R_V + 25.0, R2=max(80.0, float(N_VENT) * 0.8), H=H_CONE).translate((0.0, 0.0, H_SHELL + 10.0))
    o_main.uniteWith(o_cone)
    o_cone.erase()

    # 2. 接管构造函数
    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    def _add_side_noz(z_el, deg, dn_val, ext_l, blind=False):
        r_p, r_f, t_f = _fl_dims(dn_val)
        rad = math.radians(deg)
        r_face = R_V + ext_l
        embed = 150.0
        pipe_l = ext_l + embed - t_f
        o_p = CYLINDER(s, R=r_p, H=pipe_l + 2.0, O=0.0).rotateY(90.0).translate((R_V - embed, 0.0, z_el)).rotateZ(deg)
        o_f = CYLINDER(s, R=r_f, H=t_f, O=0.0).rotateY(90.0).translate((r_face - t_f, 0.0, z_el)).rotateZ(deg)
        o_main.uniteWith(o_p)
        o_p.erase()
        o_main.uniteWith(o_f)
        o_f.erase()
        if blind:
            o_cv = CYLINDER(s, R=r_f, H=t_f * 0.85, O=0.0).rotateY(90.0).translate((r_face - 1.0, 0.0, z_el)).rotateZ(deg)
            o_main.uniteWith(o_cv)
            o_cv.erase()
        return (r_face * math.cos(rad), r_face * math.sin(rad), z_el), (math.cos(rad), math.sin(rad), 0.0)

    # 3. 顶部呼吸阀口 (Port 1, 锥顶中心 +Z)
    r_pv, r_fv, t_fv = _fl_dims(N_VENT)
    z_vent_face = H_SHELL + H_CONE + 260.0
    z_vent_start = H_SHELL + H_CONE * 0.65
    o_nv_p = CYLINDER(s, R=r_pv, H=z_vent_face - t_fv - z_vent_start + 2.0, O=0.0).translate((0.0, 0.0, z_vent_start))
    o_nv_f = CYLINDER(s, R=r_fv, H=t_fv, O=0.0).translate((0.0, 0.0, z_vent_face - t_fv))
    o_main.uniteWith(o_nv_p)
    o_nv_p.erase()
    o_main.uniteWith(o_nv_f)
    o_nv_f.erase()
    p_vent = (0.0, 0.0, z_vent_face)

    # 4. 上部进料口 (Port 2)、下部出料口 (Port 3)、底部排污口 (Port 4)
    p_in, d_in = _add_side_noz(H_SHELL - 450.0, 180.0, N_IN, NOZ_EXT)
    p_out, d_out = _add_side_noz(450.0, 180.0, N_OUT, NOZ_EXT)
    p_drn, d_drn = _add_side_noz(260.0, 90.0, N_DRN, NOZ_EXT)

    # 5. 下部侧人孔 (DN600, 带盲盖，0度 +X 侧，非工艺端口附件)
    _add_side_noz(750.0, 0.0, 600.0, NOZ_EXT + 60.0, blind=True)

    # 6. 注册 4 个端口
    s.setPoint(p_vent, (0.0, 0.0, 1.0))
    s.setPoint(p_in, d_in)
    s.setPoint(p_out, d_out)
    s.setPoint(p_drn, d_drn)

    # 7. 注册线性标注
    s.setLinearDimension('D', (-R_V, 0.0, 0.0), (R_V, 0.0, 0.0))
    s.setLinearDimension('H_SHELL', (-R_V, 0.0, 0.0), (-R_V, 0.0, H_SHELL))
    s.setLinearDimension('H_CONE', (0.0, 0.0, H_SHELL), (0.0, 0.0, H_SHELL + H_CONE))
