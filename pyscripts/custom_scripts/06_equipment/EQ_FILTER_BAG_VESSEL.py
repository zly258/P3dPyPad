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
          TooltipShort=u"多袋式过滤器压力容器",
          TooltipLong=u"多袋式精密过滤压力容器，含立式圆筒体、下椭圆封头、上部快开螺栓主法兰盖（含摇臂吊柱与手轮）、3 根均布支腿及侧进底出 2 个标准接管法兰",
          LengthUnit="mm",
          Ports="2")
@group("MainDimensions", TooltipLong=u"多袋式过滤器压力容器主要几何尺寸参数")
@param(D=LENGTH, TooltipShort=u"筒体直径", TooltipLong=u"过滤器筒体公称直径 DN (mm)")
@param(H_SHELL=LENGTH, TooltipShort=u"筒体直段高", TooltipLong=u"筒体圆柱段高度 (mm)", Ask4Dist=True)
@param(H_LEG=LENGTH, TooltipShort=u"支腿高度", TooltipLong=u"底封头下切线至地面高度 (mm)", Ask4Dist=True)
@param(DN_NOZ=LENGTH, TooltipShort=u"进出口通径", TooltipLong=u"侧进/底出工艺接管 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出长", TooltipLong=u"接管法兰面伸出长度 (mm)")
def EQ_FILTER_BAG_VESSEL(
    s,
    D=800.0,
    H_SHELL=1200.0,
    H_LEG=650.0,
    DN_NOZ=150.0,
    NOZ_EXT=240.0,
    ID=u"EQ_FILTER_BAG_VESSEL",
    **kw
):
    u"""多袋式过滤器压力容器 (下封头切线 Z=0, 地面 Z=-H_LEG)。"""
    D = float(D)
    if D < 1.0:
        D = 1.0
    R_V = D / 2.0
    H_SHELL = float(H_SHELL)
    if H_SHELL < 1.0:
        H_SHELL = 1.0
    H_LEG = max(350.0, float(H_LEG))
    NOZ_EXT = max(150.0, float(NOZ_EXT))
    h_head = D * 0.25
    z_gnd = -H_LEG

    # 1. 主筒体 + 下椭圆封头 + 上快开主法兰盖
    o_main = CYLINDER(s, R=R_V, H=H_SHELL, O=0.0)
    o_bot = ELLIPSOIDHEAD(s, R=R_V).rotateX(180.0)
    o_main.uniteWith(o_bot); o_bot.erase()

    r_mfl = R_V + 70.0
    o_fl1 = CYLINDER(s, R=r_mfl, H=38.0, O=0.0).translate((0.0, 0.0, H_SHELL - 38.0))
    o_fl2 = CYLINDER(s, R=r_mfl, H=38.0, O=0.0).translate((0.0, 0.0, H_SHELL))
    o_top = ELLIPSOIDHEAD(s, R=R_V).translate((0.0, 0.0, H_SHELL + 38.0))
    o_main.uniteWith(o_fl1); o_fl1.erase()
    o_main.uniteWith(o_fl2); o_fl2.erase()
    o_main.uniteWith(o_top); o_top.erase()

    # 快开吊臂转轴 + 手轮细节
    z_cap_top = H_SHELL + 38.0 + h_head
    o_post = CYLINDER(s, R=26.0, H=h_head + 160.0, O=0.0).translate((0.0, R_V + 85.0, H_SHELL - 60.0))
    o_arm = CORNERBOX(s, L=48.0, W=R_V + 100.0, H=40.0).translate((-24.0, -15.0, z_cap_top + 40.0))
    o_stem = CYLINDER(s, R=18.0, H=130.0, O=0.0).translate((0.0, 0.0, z_cap_top - 10.0))
    o_spoke = CORNERBOX(s, L=190.0, W=20.0, H=20.0).translate((-95.0, -10.0, z_cap_top + 105.0))
    o_main.uniteWith(o_spoke); o_spoke.erase()
    o_wheel = TORUS(s, R1=95.0, R2=14.0).translate((0.0, 0.0, z_cap_top + 115.0))
    o_main.uniteWith(o_post); o_post.erase()
    o_main.uniteWith(o_arm); o_arm.erase()
    o_main.uniteWith(o_stem); o_stem.erase()
    o_main.uniteWith(o_wheel); o_wheel.erase()

    # 2. 3 根均布管式支腿 + 地脚底板
    r_pcd = R_V * 0.85
    r_leg = max(42.0, D * 0.065)
    base_w = r_leg * 3.0
    for ang_deg in (30.0, 150.0, 270.0):
        rad = math.radians(ang_deg)
        lx, ly = r_pcd * math.cos(rad), r_pcd * math.sin(rad)
        o_leg = CYLINDER(s, R=r_leg, H=R_V * 0.35 - (z_gnd + 16.0), O=0.0).translate((lx, ly, z_gnd + 16.0))
        o_bp = CORNERBOX(s, L=base_w, W=base_w, H=16.0).translate((lx - base_w / 2.0, ly - base_w / 2.0, z_gnd))
        o_main.uniteWith(o_leg); o_leg.erase()
        o_main.uniteWith(o_bp); o_bp.erase()

    # 3. 侧进 (-X) + 底出 (-Z) 双标准法兰
    r_p, r_f, t_f = _std_noz_dims(DN_NOZ)
    x_in_face = -(R_V + NOZ_EXT)
    z_in = H_SHELL * 0.72
    o_p1 = CYLINDER(s, R=r_p, H=abs(x_in_face) - t_f - R_V * 0.75, O=0.0).rotateY(-90.0).translate((-R_V * 0.75, 0.0, z_in))
    o_f1 = CYLINDER(s, R=r_f, H=t_f, O=0.0).rotateY(-90.0).translate((x_in_face + t_f, 0.0, z_in))
    o_main.uniteWith(o_p1); o_p1.erase()
    o_main.uniteWith(o_f1); o_f1.erase()

    z_out_face = max(z_gnd + 110.0, -(h_head + NOZ_EXT * 0.85))
    o_p2 = CYLINDER(s, R=r_p, H=(-h_head * 0.45) - (z_out_face + t_f), O=0.0).translate((0.0, 0.0, z_out_face + t_f))
    o_f2 = CYLINDER(s, R=r_f, H=t_f, O=0.0).translate((0.0, 0.0, z_out_face))
    o_main.uniteWith(o_p2); o_p2.erase()
    o_main.uniteWith(o_f2); o_f2.erase()

    s.setPoint((x_in_face, 0.0, z_in), (-1.0, 0.0, 0.0))
    s.setPoint((0.0, 0.0, z_out_face), (0.0, 0.0, -1.0))

    s.setLinearDimension('D', (-R_V, 0.0, H_SHELL * 0.5), (R_V, 0.0, H_SHELL * 0.5))
    s.setLinearDimension('H_SHELL', (R_V + 120.0, 0.0, 0.0), (R_V + 120.0, 0.0, H_SHELL))
