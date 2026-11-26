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
          TooltipShort=u"精馏塔/吸收塔 (NB/T 47041)",
          TooltipLong=u"NB/T 47041 塔式容器参数化模型，含圆筒/锥形裙座、基础环与地脚螺栓座、塔体、上下封头、双人孔及 6 个工艺接管",
          LengthUnit="mm",
          Ports="6")
@group("MainDimensions", TooltipLong=u"精馏塔塔体、裙座与接管主要尺寸参数")
@param(D=LENGTH, TooltipShort=u"塔体公称直径", TooltipLong=u"塔体公称直径 DN (mm)")
@param(H_SHELL=LENGTH, TooltipShort=u"塔体直段高", TooltipLong=u"上下封头切线间塔体直段长度 (mm)", Ask4Dist=True)
@param(H_SKIRT=LENGTH, TooltipShort=u"裙座高度", TooltipLong=u"基础环底面至下封头切线高度 (mm)", Ask4Dist=True)
@param(D_SKIRT_BOT=LENGTH, TooltipShort=u"裙座底外径", TooltipLong=u"裙座下端外径，大于D时呈锥形裙座 (mm)")
@param(N_TOP=LENGTH, TooltipShort=u"塔顶气相口", TooltipLong=u"塔顶气相出口公称通径 DN (mm)")
@param(N_REF=LENGTH, TooltipShort=u"回流口通径", TooltipLong=u"塔顶回流进口公称通径 DN (mm)")
@param(N_FEED=LENGTH, TooltipShort=u"进料口通径", TooltipLong=u"中部进料接管公称通径 DN (mm)")
@param(N_REB=LENGTH, TooltipShort=u"再沸返塔口", TooltipLong=u"下部再沸器返塔口公称通径 DN (mm)")
@param(N_BOT=LENGTH, TooltipShort=u"塔底液相口", TooltipLong=u"塔底液相出口公称通径 DN (mm)")
@param(N_SIDE=LENGTH, TooltipShort=u"侧线采出口", TooltipLong=u"侧线采出或仪表口公称通径 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出长", TooltipLong=u"侧向工艺接管法兰面距塔壁伸出长度 (mm)")
def EQ_TOWER_COLUMN(
    s,
    D=1200.0,
    H_SHELL=12000.0,
    H_SKIRT=2400.0,
    D_SKIRT_BOT=1400.0,
    N_TOP=250.0,
    N_REF=100.0,
    N_FEED=150.0,
    N_REB=200.0,
    N_BOT=150.0,
    N_SIDE=100.0,
    NOZ_EXT=280.0,
    ID=u"EQ_TOWER_COLUMN",
    **kw
):
    u"""NB/T 47041 精馏塔/吸收塔 (EL 0 = 下封头切线，裙座底面 Z = -H_SKIRT，+Z 向上)。"""
    D = float(D)
    if D < 1.0:
        D = 1.0
    R_V = D / 2.0
    H_SHELL = float(H_SHELL)
    if H_SHELL < 1.0:
        H_SHELL = 1.0
    H_HEAD = R_V * 0.5
    H_SKIRT = float(H_SKIRT)
    if H_SKIRT < 1.0:
        H_SKIRT = 1.0
    D_SKIRT_BOT = float(D_SKIRT_BOT)
    if D_SKIRT_BOT < 1.0:
        D_SKIRT_BOT = 1.0
    R_SK_BOT = D_SKIRT_BOT / 2.0
    NOZ_EXT = max(150.0, float(NOZ_EXT))

    z_gnd = -H_SKIRT

    # 1. 主塔体与上下 EHA 2:1 封头
    o_main = CYLINDER(s, R=R_V, H=H_SHELL, O=0.0)

    o_th = ELLIPSOIDHEAD(s, R=R_V).translate((0.0, 0.0, H_SHELL - 2.0))
    o_main.uniteWith(o_th)
    o_th.erase()

    o_bh = ELLIPSOIDHEAD(s, R=R_V).rotateX(180.0).translate((0.0, 0.0, 2.0))
    o_main.uniteWith(o_bh)
    o_bh.erase()

    # 2. 圆筒/锥形裙座 + 基础环 + 压环 + 地脚螺栓筋板
    o_skirt = CONE(s, R1=R_SK_BOT, R2=R_V, H=H_SKIRT + 20.0).translate((0.0, 0.0, z_gnd))
    o_main.uniteWith(o_skirt)
    o_skirt.erase()

    ring_t = max(24.0, D * 0.022)
    r_base_out = R_SK_BOT + max(110.0, D * 0.09)
    o_bring = CYLINDER(s, R=r_base_out, H=ring_t, O=0.0).translate((0.0, 0.0, z_gnd))
    o_main.uniteWith(o_bring)
    o_bring.erase()

    # 盖环 (地脚螺栓座顶环)
    chair_h = max(180.0, D * 0.14)
    o_cring = CYLINDER(s, R=r_base_out - 10.0, H=ring_t * 0.75, O=0.0).translate((0.0, 0.0, z_gnd + chair_h))
    o_main.uniteWith(o_cring)
    o_cring.erase()

    # 8 组地脚螺栓筋板
    for i in range(8):
        ang = i * 45.0
        o_gus = CORNERBOX(s, L=r_base_out - R_SK_BOT + 40.0, W=18.0, H=chair_h).translate(
            (R_SK_BOT - 30.0, -9.0, z_gnd + ring_t * 0.5)
        ).rotateZ(ang)
        o_main.uniteWith(o_gus)
        o_gus.erase()

    # 2b. 分段加强圈 / 平台支撑圈 (3 处清晰工业分段环)
    stiff_t = max(22.0, D * 0.018)
    r_stiff = R_V + max(75.0, D * 0.065)
    for frac in (0.22, 0.58, 0.84):
        o_sring = CYLINDER(s, R=r_stiff, H=stiff_t, O=0.0).translate((0.0, 0.0, H_SHELL * frac))
        o_main.uniteWith(o_sring)
        o_sring.erase()

    # 3. 接管构造函数
    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    def _add_side_nozzle(z_el, deg, dn_val, ext_l, add_cover=False):
        r_p, r_f, t_f = _fl_dims(dn_val)
        rad = math.radians(deg)
        r_face = R_V + ext_l
        embed = R_V * 0.25
        pipe_l = ext_l + embed - t_f
        o_p = CYLINDER(s, R=r_p, H=pipe_l + 2.0, O=0.0).rotateY(90.0).translate((R_V - embed, 0.0, z_el)).rotateZ(deg)
        o_f = CYLINDER(s, R=r_f, H=t_f, O=0.0).rotateY(90.0).translate((r_face - t_f, 0.0, z_el)).rotateZ(deg)
        o_main.uniteWith(o_p)
        o_p.erase()
        o_main.uniteWith(o_f)
        o_f.erase()
        if add_cover:
            o_cv = CYLINDER(s, R=r_f, H=t_f * 0.85, O=0.0).rotateY(90.0).translate((r_face - 1.0, 0.0, z_el)).rotateZ(deg)
            o_main.uniteWith(o_cv)
            o_cv.erase()
        return (r_face * math.cos(rad), r_face * math.sin(rad), z_el), (math.cos(rad), math.sin(rad), 0.0)

    # 4. 塔顶气相出口 (Port 1, +Z)
    r_p1, r_f1, t_f1 = _fl_dims(N_TOP)
    z_top_face = H_SHELL + H_HEAD + NOZ_EXT
    z1_start = H_SHELL + H_HEAD * 0.65
    o_p1 = CYLINDER(s, R=r_p1, H=z_top_face - t_f1 - z1_start + 2.0, O=0.0).translate((0.0, 0.0, z1_start))
    o_f1 = CYLINDER(s, R=r_f1, H=t_f1, O=0.0).translate((0.0, 0.0, z_top_face - t_f1))
    o_main.uniteWith(o_p1)
    o_p1.erase()
    o_main.uniteWith(o_f1)
    o_f1.erase()
    p_top = (0.0, 0.0, z_top_face)

    # 5. 5 个侧向工艺口 (回流、进料、再沸返塔、塔底引出、侧线采出)
    p_ref, d_ref = _add_side_nozzle(H_SHELL * 0.90, 180.0, N_REF, NOZ_EXT)
    p_feed, d_feed = _add_side_nozzle(H_SHELL * 0.50, 0.0, N_FEED, NOZ_EXT)
    p_reb, d_reb = _add_side_nozzle(H_SHELL * 0.14, 180.0, N_REB, NOZ_EXT)
    p_side, d_side = _add_side_nozzle(H_SHELL * 0.70, 90.0, N_SIDE, NOZ_EXT)

    # 塔底液相出口 (从下封头底部弯出穿裙座至 -X 侧)
    r_pb, r_fb, t_fb = _fl_dims(N_BOT)
    z_bot_noz = -H_HEAD - max(250.0, r_fb + 80.0)
    r_bot_face = R_SK_BOT + NOZ_EXT
    o_bdrop = CYLINDER(s, R=r_pb, H=abs(z_bot_noz) - H_HEAD * 0.4 + r_pb, O=0.0).translate(
        (0.0, 0.0, z_bot_noz - r_pb)
    )
    o_main.uniteWith(o_bdrop)
    o_bdrop.erase()
    o_bhor = CYLINDER(s, R=r_pb, H=r_bot_face - t_fb + r_pb, O=0.0).rotateY(-90.0).translate((r_pb * 0.5, 0.0, z_bot_noz))
    o_main.uniteWith(o_bhor)
    o_bhor.erase()
    o_bfl = CYLINDER(s, R=r_fb, H=t_fb, O=0.0).rotateY(-90.0).translate((-r_bot_face + t_fb, 0.0, z_bot_noz))
    o_main.uniteWith(o_bfl)
    o_bfl.erase()
    p_bot = (-r_bot_face, 0.0, z_bot_noz)

    # 6. 双人孔 (非端口附件，带盲盖，位于塔下部与上部 +X/-Y 侧)
    _add_side_nozzle(H_SHELL * 0.28, -90.0, 450.0, NOZ_EXT + 40.0, add_cover=True)
    _add_side_nozzle(H_SHELL * 0.78, -90.0, 450.0, NOZ_EXT + 40.0, add_cover=True)

    # 7. 注册 6 个工艺端口
    s.setPoint(p_top, (0.0, 0.0, 1.0))
    s.setPoint(p_ref, d_ref)
    s.setPoint(p_feed, d_feed)
    s.setPoint(p_reb, d_reb)
    s.setPoint(p_bot, (-1.0, 0.0, 0.0))
    s.setPoint(p_side, d_side)

    # 8. 注册线性标注
    s.setLinearDimension('D', (-R_V, 0.0, 0.0), (R_V, 0.0, 0.0))
    s.setLinearDimension('H_SHELL', (-R_V, 0.0, 0.0), (-R_V, 0.0, H_SHELL))
    s.setLinearDimension('H_SKIRT', (-R_SK_BOT, 0.0, z_gnd), (-R_SK_BOT, 0.0, 0.0))
    s.setLinearDimension('D_SKIRT_BOT', (-R_SK_BOT, 0.0, z_gnd), (R_SK_BOT, 0.0, z_gnd))
