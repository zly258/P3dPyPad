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
          TooltipShort=u"螺杆式冷冻机组撬块",
          TooltipLong=u"工业水冷螺杆式冷冻机组撬块，含公共底座、双螺杆压缩机、卧式蒸发器、卧式冷凝器、电控柜及 4 个冷媒/冷却水接管法兰",
          LengthUnit="mm",
          Ports="4")
@group("MainDimensions", TooltipLong=u"螺杆式冷冻机组撬块主要几何尺寸参数")
@param(DN_CHW=LENGTH, TooltipShort=u"冷冻水口径", TooltipLong=u"蒸发器冷冻水进出口 DN (mm)")
@param(DN_CW=LENGTH, TooltipShort=u"冷却水口径", TooltipLong=u"冷凝器冷却水进出口 DN (mm)")
@param(L_SKID=LENGTH, TooltipShort=u"机组长度", TooltipLong=u"公共底座总长 (mm)", Ask4Dist=True)
@param(W_SKID=LENGTH, TooltipShort=u"机组宽度", TooltipLong=u"公共底座总宽 (mm)", Ask4Dist=True)
@param(H_SKID=LENGTH, TooltipShort=u"底座高度", TooltipLong=u"槽钢底座高度 (mm)")
@param(D_EVAP=LENGTH, TooltipShort=u"蒸发器外径", TooltipLong=u"下部卧式蒸发器壳径 (mm)")
@param(D_COND=LENGTH, TooltipShort=u"冷凝器外径", TooltipLong=u"下部卧式冷凝器壳径 (mm)")
def EQ_CHILLER_SCREW_SKID(
    s,
    DN_CHW=150.0,
    DN_CW=150.0,
    L_SKID=3600.0,
    W_SKID=1750.0,
    H_SKID=200.0,
    D_EVAP=620.0,
    D_COND=660.0,
    ID=u"EQ_CHILLER_SCREW_SKID",
    **kw
):
    u"""螺杆式冷冻机组撬块 (底面 Z=0, 壳体沿 X 轴平行布置)。"""
    L_SKID = float(L_SKID)
    if L_SKID < 1.0:
        L_SKID = 1.0
    W_SKID = float(W_SKID)
    if W_SKID < 1.0:
        W_SKID = 1.0
    H_SKID = max(150.0, float(H_SKID))
    D_EVAP = max(400.0, float(D_EVAP))
    D_COND = max(420.0, float(D_COND))
    R_EV = D_EVAP / 2.0
    R_CD = D_COND / 2.0

    # 1. 公共钢结构底座
    o_main = CORNERBOX(s, L=L_SKID, W=W_SKID, H=H_SKID).translate((-L_SKID / 2.0, -W_SKID / 2.0, 0.0))

    # 2. 卧式蒸发器 (-Y 侧) 与 卧式冷凝器 (+Y 侧)
    l_hx = L_SKID * 0.84
    y_ev = -W_SKID * 0.24
    y_cd = W_SKID * 0.24
    z_hx = H_SKID + max(R_EV, R_CD) + 120.0

    for y_pos, r_h in ((y_ev, R_EV), (y_cd, R_CD)):
        o_sh = CYLINDER(s, R=r_h, H=l_hx, O=0.0).rotateY(90.0).translate((-l_hx / 2.0, y_pos, z_hx))
        o_main.uniteWith(o_sh); o_sh.erase()
        for sx in (-1.0, 1.0):
            o_fl = CYLINDER(s, R=r_h + 45.0, H=34.0, O=0.0).rotateY(90.0).translate((sx * l_hx / 2.0 - 17.0, y_pos, z_hx))
            o_box = CYLINDER(s, R=r_h, H=240.0, O=0.0).rotateY(90.0).translate((sx * (l_hx / 2.0) - (240.0 if sx < 0 else 0.0), y_pos, z_hx))
            o_hd = ELLIPSOIDHEAD(s, R=r_h).rotateY(-90.0 if sx < 0 else 90.0).translate((sx * (l_hx / 2.0 + 240.0), y_pos, z_hx))
            o_sad = CORNERBOX(s, L=160.0, W=r_h * 1.4, H=z_hx - H_SKID).translate((sx * l_hx * 0.34 - 80.0, y_pos - r_h * 0.7, H_SKID))
            o_main.uniteWith(o_fl); o_fl.erase()
            o_main.uniteWith(o_box); o_box.erase()
            o_main.uniteWith(o_hd); o_hd.erase()
            o_main.uniteWith(o_sad); o_sad.erase()

    # 3. 顶部双螺杆压缩机总成 (跨坐于两壳体上方)
    z_comp = z_hx + max(R_EV, R_CD) + 320.0
    r_comp = max(210.0, W_SKID * 0.14)
    l_comp = L_SKID * 0.44
    o_comp = CYLINDER(s, R=r_comp, H=l_comp, O=0.0).rotateY(90.0).translate((-l_comp * 0.55, 0.0, z_comp))
    o_oil = CYLINDER(s, R=r_comp * 0.78, H=l_comp * 0.45, O=0.0).rotateY(90.0).translate((l_comp * 0.35, 0.0, z_comp + r_comp * 0.2))
    o_cbox = CORNERBOX(s, L=240.0, W=260.0, H=220.0).translate((-l_comp * 0.35, -130.0, z_comp + r_comp * 0.6))
    o_main.uniteWith(o_comp); o_comp.erase()
    o_main.uniteWith(o_oil); o_oil.erase()
    o_main.uniteWith(o_cbox); o_cbox.erase()
    for sx in (-0.35, 0.25):
        o_br = CORNERBOX(s, L=140.0, W=abs(y_cd - y_ev), H=z_comp - z_hx).translate((sx * l_comp - 70.0, y_ev, z_hx))
        o_main.uniteWith(o_br); o_br.erase()

    # 4. 侧面工业电控柜 (-Y 侧前部)
    cab_l, cab_w, cab_h = 720.0, 360.0, 1450.0
    o_cab = CORNERBOX(s, L=cab_l, W=cab_w, H=cab_h).translate((-L_SKID * 0.38, -W_SKID / 2.0 + 30.0, H_SKID))
    o_main.uniteWith(o_cab); o_cab.erase()

    # 5. 4 个水系统接管法兰 (冷冻水进/出 + 冷却水进/出)
    def _add_top_noz(x_p, y_p, z_base, r_body, dn_v):
        rp, rf, tf = _std_noz_dims(dn_v)
        zf = z_base + r_body + 240.0
        op = CYLINDER(s, R=rp, H=zf - tf - z_base, O=0.0).translate((x_p, y_p, z_base))
        of = CYLINDER(s, R=rf, H=tf, O=0.0).translate((x_p, y_p, zf - tf))
        o_main.uniteWith(op); op.erase()
        o_main.uniteWith(of); of.erase()
        return (x_p, y_p, zf)

    p1 = _add_top_noz(-l_hx * 0.36, y_ev, z_hx, R_EV, DN_CHW)
    p2 = _add_top_noz(l_hx * 0.36, y_ev, z_hx, R_EV, DN_CHW)
    p3 = _add_top_noz(-l_hx * 0.36, y_cd, z_hx, R_CD, DN_CW)
    p4 = _add_top_noz(l_hx * 0.36, y_cd, z_hx, R_CD, DN_CW)

    for pt in (p1, p2, p3, p4):
        s.setPoint(pt, (0.0, 0.0, 1.0))

    s.setLinearDimension('L_SKID', (-L_SKID / 2.0, -W_SKID / 2.0, 0.0), (L_SKID / 2.0, -W_SKID / 2.0, 0.0))
    s.setLinearDimension('W_SKID', (L_SKID / 2.0, -W_SKID / 2.0, 0.0), (L_SKID / 2.0, W_SKID / 2.0, 0.0))
