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
          TooltipShort=u"厢式/板框压滤机",
          TooltipLong=u"自动液压厢式/板框压滤机，含前后立柱支架、双侧水平主梁、液压压紧油缸及油缸座、多片厢式滤板组、活动压紧板、止推板及进料/滤液 2 个标准法兰",
          LengthUnit="mm",
          Ports="2")
@group("MainDimensions", TooltipLong=u"厢式/板框压滤机主要外形尺寸参数")
@param(DN_FEED=LENGTH, TooltipShort=u"进料口通径", TooltipLong=u"止推板中心进料口 DN (mm)")
@param(DN_FILT=LENGTH, TooltipShort=u"滤液出口", TooltipLong=u"滤液收集总管出口 DN (mm)")
@param(L_TOTAL=LENGTH, TooltipShort=u"设备总长", TooltipLong=u"压滤机整体长度 (mm)", Ask4Dist=True)
@param(W_PLATE=LENGTH, TooltipShort=u"滤板宽度", TooltipLong=u"方形滤板外形宽度 (mm)")
@param(H_PLATE=LENGTH, TooltipShort=u"滤板高度", TooltipLong=u"方形滤板外形高度 (mm)")
@param(N_PLATES=INT, TooltipShort=u"滤板片数", TooltipLong=u"滤板组视觉分段数 (片)")
def EQ_FILTER_PRESS_PLATE(
    s,
    DN_FEED=100.0,
    DN_FILT=80.0,
    L_TOTAL=4600.0,
    W_PLATE=1250.0,
    H_PLATE=1250.0,
    N_PLATES=14,
    ID=u"EQ_FILTER_PRESS_PLATE",
    **kw
):
    u"""厢式/板框压滤机 (底面 Z=0, 主梁沿 X 轴)。"""
    L_TOTAL = float(L_TOTAL)
    if L_TOTAL < 1.0:
        L_TOTAL = 1.0
    W_PLATE = float(W_PLATE)
    if W_PLATE < 1.0:
        W_PLATE = 1.0
    H_PLATE = max(650.0, float(H_PLATE))
    N_PLATES = max(6, min(24, int(N_PLATES)))

    z_beam = H_PLATE * 0.52 + 320.0
    w_frame = W_PLATE + 320.0

    # 1. 前后立柱支架 + 双侧主梁
    x_head = -L_TOTAL * 0.44
    x_tail = L_TOTAL * 0.46
    o_main = CORNERBOX(s, L=180.0, W=w_frame, H=z_beam + H_PLATE * 0.55).translate((x_head, -w_frame / 2.0, 0.0))
    o_tail_st = CORNERBOX(s, L=200.0, W=w_frame, H=z_beam + 260.0).translate((x_tail - 200.0, -w_frame / 2.0, 0.0))
    o_main.uniteWith(o_tail_st); o_tail_st.erase()

    for sy in (-1.0, 1.0):
        y_bm = sy * (W_PLATE / 2.0 + 70.0)
        o_bm = CORNERBOX(s, L=x_tail - x_head, W=90.0, H=220.0).translate((x_head, y_bm - 45.0, z_beam - 110.0))
        o_main.uniteWith(o_bm); o_bm.erase()

    # 2. 止推板 (-X 侧) + 厢式滤板组 + 活动压紧板
    x_pack0 = x_head + 180.0
    l_pack = L_TOTAL * 0.52
    pitch = l_pack / float(N_PLATES)
    for idx in range(N_PLATES):
        xp = x_pack0 + idx * pitch
        o_pl = CORNERBOX(s, L=pitch * 0.68, W=W_PLATE, H=H_PLATE).translate((xp, -W_PLATE / 2.0, z_beam - H_PLATE * 0.5))
        # 两侧搭接主梁的把手耳
        o_ear = CORNERBOX(s, L=pitch * 0.68, W=W_PLATE + 240.0, H=90.0).translate((xp, -(W_PLATE + 240.0) / 2.0, z_beam + 10.0))
        o_main.uniteWith(o_pl); o_pl.erase()
        o_main.uniteWith(o_ear); o_ear.erase()

    o_core = CYLINDER(s, R=65.0, H=l_pack + 180.0, O=0.0).rotateY(90.0).translate((x_head + 160.0, 0.0, z_beam))
    o_main.uniteWith(o_core); o_core.erase()
    x_press = x_pack0 + l_pack
    o_press = CORNERBOX(s, L=140.0, W=W_PLATE + 80.0, H=H_PLATE + 60.0).translate((x_press, -(W_PLATE + 80.0) / 2.0, z_beam - H_PLATE * 0.5 - 30.0))
    o_main.uniteWith(o_press); o_press.erase()

    # 3. 尾端液压压紧油缸 + 活塞杆
    r_cyl = max(110.0, W_PLATE * 0.14)
    l_cyl = (x_tail - 200.0) - (x_press + 140.0)
    o_rod = CYLINDER(s, R=r_cyl * 0.58, H=l_cyl + 40.0, O=0.0).rotateY(90.0).translate((x_press + 120.0, 0.0, z_beam))
    o_hcyl = CYLINDER(s, R=r_cyl, H=l_cyl * 0.85, O=0.0).rotateY(90.0).translate((x_tail - 200.0, 0.0, z_beam))
    o_main.uniteWith(o_rod); o_rod.erase()
    o_main.uniteWith(o_hcyl); o_hcyl.erase()

    # 4. 两个标准接口: 止推板中心进料口 (-X) 与 滤液收集出口 (+Y)
    r_pf, r_ff, t_ff = _std_noz_dims(DN_FEED)
    x_feed = x_head - 220.0
    o_fp = CYLINDER(s, R=r_pf, H=abs(x_feed - x_head) - t_ff + 20.0, O=0.0).rotateY(-90.0).translate((x_head + 10.0, 0.0, z_beam))
    o_ff = CYLINDER(s, R=r_ff, H=t_ff, O=0.0).rotateY(-90.0).translate((x_feed + t_ff, 0.0, z_beam))
    o_main.uniteWith(o_fp); o_fp.erase()
    o_main.uniteWith(o_ff); o_ff.erase()

    r_pl, r_fl, t_fl = _std_noz_dims(DN_FILT)
    y_filt = W_PLATE / 2.0 + 260.0
    z_filt = z_beam - H_PLATE * 0.42
    o_lp = CYLINDER(s, R=r_pl, H=y_filt - t_fl - W_PLATE * 0.45, O=0.0).rotateX(-90.0).translate((x_head + 90.0, W_PLATE * 0.45, z_filt))
    o_lf = CYLINDER(s, R=r_fl, H=t_fl, O=0.0).rotateX(-90.0).translate((x_head + 90.0, y_filt - t_fl, z_filt))
    o_main.uniteWith(o_lp); o_lp.erase()
    o_main.uniteWith(o_lf); o_lf.erase()

    s.setPoint((x_feed, 0.0, z_beam), (-1.0, 0.0, 0.0))
    s.setPoint((x_head + 90.0, y_filt, z_filt), (0.0, 1.0, 0.0))

    s.setLinearDimension('L_TOTAL', (x_head, -w_frame / 2.0, 0.0), (x_tail, -w_frame / 2.0, 0.0))
    s.setLinearDimension('W_PLATE', (x_pack0, -W_PLATE / 2.0, z_beam), (x_pack0, W_PLATE / 2.0, z_beam))
