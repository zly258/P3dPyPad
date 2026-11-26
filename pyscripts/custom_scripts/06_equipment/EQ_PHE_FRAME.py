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
          TooltipShort=u"板式换热器 (NB/T 47004)",
          TooltipLong=u"NB/T 47004 可拆式板式热交换器参数化模型，含固定压紧板、传热板片束、活动压紧板、上下导杆、夹紧螺栓、后端支柱及前端 4 个法兰口",
          LengthUnit="mm",
          Ports="4")
@group("MainDimensions", TooltipLong=u"板式换热器框架、板片束与接管主要尺寸参数")
@param(DN=LENGTH, TooltipShort=u"接口公称通径", TooltipLong=u"前端4个工艺接口公称通径 DN (mm)")
@param(L_TOTAL=LENGTH, TooltipShort=u"框架总长", TooltipLong=u"固定压紧板外侧面至后支柱外缘总长 L (mm)", Ask4Dist=True)
@param(W_PLATE=LENGTH, TooltipShort=u"压紧板宽度", TooltipLong=u"固定/活动压紧板宽度 W (mm)")
@param(H_PLATE=LENGTH, TooltipShort=u"压紧板总高", TooltipLong=u"地面至固定压紧板顶部总高度 H (mm)", Ask4Dist=True)
@param(L_PACK=LENGTH, TooltipShort=u"板片束夹紧长", TooltipLong=u"传热板片束夹紧厚度 (mm)", Ask4Dist=True)
@param(Y_PORT=LENGTH, TooltipShort=u"左右口中心距", TooltipLong=u"前端左右两列法兰口水平中心距 (mm)")
@param(Z_PORT=LENGTH, TooltipShort=u"上下口中心距", TooltipLong=u"前端上下两排法兰口垂直中心距 (mm)")
def EQ_PHE_FRAME(
    s,
    DN=100.0,
    L_TOTAL=1350.0,
    W_PLATE=520.0,
    H_PLATE=1420.0,
    L_PACK=460.0,
    Y_PORT=240.0,
    Z_PORT=920.0,
    ID=u"EQ_PHE_FRAME",
    **kw
):
    u"""NB/T 47004 板式换热器 (底面 Z=0，固定压紧板外侧面在 X=0，板片束沿 +X 延伸，4 个法兰口在 -X 侧)。"""
    DN = max(32.0, float(DN))
    L_TOTAL = float(L_TOTAL)
    if L_TOTAL < 1.0:
        L_TOTAL = 1.0
    W_PLATE = float(W_PLATE)
    if W_PLATE < 1.0:
        W_PLATE = 1.0
    H_PLATE = float(H_PLATE)
    if H_PLATE < 1.0:
        H_PLATE = 1.0
    T_FIX = max(40.0, W_PLATE * 0.09)
    T_MOV = max(36.0, W_PLATE * 0.08)
    L_PACK = min(L_TOTAL - T_FIX - T_MOV - 160.0, max(120.0, float(L_PACK)))
    Y_PORT = min(W_PLATE - 140.0, max(100.0, float(Y_PORT)))
    Z_PORT = min(H_PLATE - 280.0, max(300.0, float(Z_PORT)))

    foot_h = max(80.0, H_PLATE * 0.07)
    plate_h = H_PLATE - foot_h

    # 1. 固定压紧板 (X: 0 -> T_FIX, Z: foot_h -> H_PLATE) + 底部双支脚
    o_main = CORNERBOX(s, L=T_FIX, W=W_PLATE, H=plate_h).translate((0.0, -W_PLATE / 2.0, foot_h))
    foot_l = T_FIX + 110.0
    foot_w = max(80.0, W_PLATE * 0.22)
    for sy in (-1.0, 1.0):
        o_ft = CORNERBOX(s, L=foot_l, W=foot_w, H=foot_h + 15.0).translate(
            (-30.0, sy * (W_PLATE / 2.0 - foot_w / 2.0) - foot_w / 2.0, 0.0)
        )
        o_main.uniteWith(o_ft)
        o_ft.erase()

    # 2. 传热板片束 (带压紧波纹阶梯特征，位于固定板与活动板之间)
    pack_w = W_PLATE * 0.84
    pack_h = plate_h * 0.90
    z_pack0 = foot_h + (plate_h - pack_h) / 2.0
    o_pack = CORNERBOX(s, L=L_PACK + 8.0, W=pack_w, H=pack_h).translate(
        (T_FIX - 4.0, -pack_w / 2.0, z_pack0)
    )
    o_main.uniteWith(o_pack)
    o_pack.erase()

    # 3. 活动压紧板
    x_mov = T_FIX + L_PACK
    o_mov = CORNERBOX(s, L=T_MOV, W=W_PLATE, H=plate_h).translate((x_mov, -W_PLATE / 2.0, foot_h))
    o_main.uniteWith(o_mov)
    o_mov.erase()

    # 4. 后端支柱 + 底板 (X = L_TOTAL - col_l .. L_TOTAL)
    col_l = max(75.0, T_FIX * 1.4)
    col_w = max(90.0, W_PLATE * 0.22)
    x_col = L_TOTAL - col_l
    o_col = CORNERBOX(s, L=col_l, W=col_w, H=H_PLATE).translate((x_col, -col_w / 2.0, 0.0))
    o_cbase = CORNERBOX(s, L=col_l + 80.0, W=W_PLATE * 0.65, H=24.0).translate(
        (x_col - 40.0, -W_PLATE * 0.325, 0.0)
    )
    o_main.uniteWith(o_col)
    o_col.erase()
    o_main.uniteWith(o_cbase)
    o_cbase.erase()

    # 5. 上承重导杆 + 下导向杆 (贯穿固定板、活动板至后支柱)
    bar_l = L_TOTAL - T_FIX * 0.4
    top_bar_w = max(55.0, W_PLATE * 0.13)
    top_bar_h = max(70.0, H_PLATE * 0.055)
    o_tbar = CORNERBOX(s, L=bar_l, W=top_bar_w, H=top_bar_h).translate(
        (T_FIX * 0.3, -top_bar_w / 2.0, H_PLATE - top_bar_h - 15.0)
    )
    o_main.uniteWith(o_tbar)
    o_tbar.erase()

    r_bbar = max(22.0, W_PLATE * 0.045)
    o_bbar = CYLINDER(s, R=r_bbar, H=bar_l, O=0.0).rotateY(90.0).translate(
        (T_FIX * 0.3, 0.0, foot_h + r_bbar + 18.0)
    )
    o_main.uniteWith(o_bbar)
    o_bbar.erase()

    # 6. 两侧 4 根夹紧拉杆螺栓 (贯穿固定板至活动板外侧)
    r_bolt = max(14.0, W_PLATE * 0.028)
    bolt_l = T_FIX + L_PACK + T_MOV + 110.0
    for sy in (-1.0, 1.0):
        by = sy * (W_PLATE * 0.43)
        for sz in (0.24, 0.76):
            bz = foot_h + plate_h * sz
            o_bolt = CYLINDER(s, R=r_bolt, H=bolt_l, O=0.0).rotateY(90.0).translate((-30.0, by, bz))
            o_main.uniteWith(o_bolt)
            o_bolt.erase()

    # 7. 前端 4 个法兰工艺口 (-X 侧)
    r_p, r_f, t_f = _std_noz_dims(DN)
    noz_ext = max(110.0, DN * 0.9 + 50.0)
    x_face = -noz_ext

    z_mid = foot_h + plate_h * 0.5
    z_hi = z_mid + Z_PORT / 2.0
    z_lo = z_mid - Z_PORT / 2.0
    y_l = -Y_PORT / 2.0
    y_r = Y_PORT / 2.0

    port_coords = [(x_face, y_l, z_hi), (x_face, y_r, z_hi), (x_face, y_l, z_lo), (x_face, y_r, z_lo)]
    for px, py, pz in port_coords:
        o_np = CYLINDER(s, R=r_p, H=noz_ext + 20.0, O=0.0).rotateY(-90.0).translate((15.0, py, pz))
        o_nf = CYLINDER(s, R=r_f, H=t_f, O=0.0).rotateY(-90.0).translate((x_face + t_f, py, pz))
        o_main.uniteWith(o_np)
        o_np.erase()
        o_main.uniteWith(o_nf)
        o_nf.erase()
        s.setPoint((px, py, pz), (-1.0, 0.0, 0.0))

    # 8. 注册线性标注
    s.setLinearDimension('L_TOTAL', (0.0, -W_PLATE / 2.0, 0.0), (L_TOTAL, -W_PLATE / 2.0, 0.0))
    s.setLinearDimension('W_PLATE', (0.0, -W_PLATE / 2.0, H_PLATE), (0.0, W_PLATE / 2.0, H_PLATE))
    s.setLinearDimension('H_PLATE', (0.0, -W_PLATE / 2.0, 0.0), (0.0, -W_PLATE / 2.0, H_PLATE))
    s.setLinearDimension('L_PACK', (T_FIX, 0.0, H_PLATE), (T_FIX + L_PACK, 0.0, H_PLATE))
