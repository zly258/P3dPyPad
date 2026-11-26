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
          TooltipShort=u"套管式换热器 (双层U形)",
          TooltipLong=u"上下双层U形套管式换热器参数化模型，含双层平行外套管、后端180度回弯盒、上下层联通短管、双组钢结构支架及4个法兰工艺口",
          LengthUnit="mm",
          Ports="4")
@group("MainDimensions", TooltipLong=u"套管式换热器主要尺寸参数")
@param(DN_OUT=LENGTH, TooltipShort=u"外套管公称直径", TooltipLong=u"外套管公称通径 DN (mm)")
@param(DN_IN=LENGTH, TooltipShort=u"内管公称直径", TooltipLong=u"内换热管公称通径 DN (mm)")
@param(L_STRAIGHT=LENGTH, TooltipShort=u"直管段长度", TooltipLong=u"套管直段有效长度 L (mm)", Ask4Dist=True)
@param(PITCH_Y=LENGTH, TooltipShort=u"U形中心距", TooltipLong=u"同层左右两根套管中心距 (mm)")
@param(PITCH_Z=LENGTH, TooltipShort=u"上下层间距", TooltipLong=u"上下两层U形套管中心高差 (mm)")
@param(H_BASE=LENGTH, TooltipShort=u"底层中心高", TooltipLong=u"支架底面至底层套管中心线高度 (mm)", Ask4Dist=True)
@param(NOZ_S=LENGTH, TooltipShort=u"壳程接口口径", TooltipLong=u"外套管环隙介质进出口通径 DN (mm)")
@param(NOZ_T=LENGTH, TooltipShort=u"管程接口口径", TooltipLong=u"内管介质进出口通径 DN (mm)")
@param(NOZ_EXT=LENGTH, TooltipShort=u"接管伸出高", TooltipLong=u"法兰面距外壁伸出高度 (mm)")
def EQ_DOUBLE_PIPE_HX(
    s,
    DN_OUT=150.0,
    DN_IN=80.0,
    L_STRAIGHT=3000.0,
    PITCH_Y=340.0,
    PITCH_Z=380.0,
    H_BASE=560.0,
    NOZ_S=80.0,
    NOZ_T=80.0,
    NOZ_EXT=180.0,
    ID=u"EQ_DOUBLE_PIPE_HX",
    **kw
):
    u"""上下双层 U 形套管式换热器 (沿 X 轴布置，前端法兰在 X=0 附近，后端 U 形回弯盒在 +X，支架底面 Z=0)。"""
    DN_OUT = max(80.0, float(DN_OUT))
    DN_IN = max(40.0, min(DN_OUT * 0.65, float(DN_IN)))
    L_STRAIGHT = float(L_STRAIGHT)
    if L_STRAIGHT < 1.0:
        L_STRAIGHT = 1.0
    R_OUT = (DN_OUT * 1.08 + 10.0) / 2.0
    R_IN = (DN_IN * 1.08 + 8.0) / 2.0
    PITCH_Y = float(PITCH_Y)
    if PITCH_Y < 1.0:
        PITCH_Y = 1.0
    PITCH_Z = float(PITCH_Z)
    if PITCH_Z < 1.0:
        PITCH_Z = 1.0
    H_BASE = float(H_BASE)
    if H_BASE < 1.0:
        H_BASE = 1.0
    NOZ_S = max(40.0, float(NOZ_S))
    NOZ_T = max(40.0, float(NOZ_T))
    NOZ_EXT = max(120.0, float(NOZ_EXT))

    y_l = -PITCH_Y * 0.5
    y_r = PITCH_Y * 0.5
    z_lo = H_BASE
    z_hi = H_BASE + PITCH_Z
    fl_t = max(22.0, R_OUT * 0.28)
    r_fl_out = R_OUT + max(42.0, R_OUT * 0.42)

    def _fl_dims(dn_val):
        return _std_noz_dims(dn_val)

    # 1. 上下两层共 4 根主外套管 + 前端法兰 + 后端回弯法兰盒
    o_main = None
    for z_lvl in (z_lo, z_hi):
        for y_pos in (y_l, y_r):
            o_p = CYLINDER(s, R=R_OUT, H=L_STRAIGHT, O=0.0).rotateY(90.0).translate((0.0, y_pos, z_lvl))
            if o_main is None:
                o_main = o_p
            else:
                o_main.uniteWith(o_p)
                o_p.erase()
            # 前端套管密封法兰
            o_ff = CYLINDER(s, R=r_fl_out, H=fl_t, O=0.0).rotateY(90.0).translate((0.0, y_pos, z_lvl))
            o_main.uniteWith(o_ff)
            o_ff.erase()
            # 后端回弯法兰
            o_rf = CYLINDER(s, R=r_fl_out, H=fl_t, O=0.0).rotateY(90.0).translate((L_STRAIGHT - fl_t, y_pos, z_lvl))
            o_main.uniteWith(o_rf)
            o_rf.erase()

        # 后端 U 形回弯罩盒 + 联通管
        box_l = PITCH_Y * 0.55 + R_OUT
        box_w = PITCH_Y + R_OUT * 2.1
        box_h = R_OUT * 2.15
        o_ubox = CORNERBOX(s, L=box_l, W=box_w, H=box_h).translate(
            (L_STRAIGHT - 6.0, -box_w * 0.5, z_lvl - box_h * 0.5)
        )
        o_main.uniteWith(o_ubox)
        o_ubox.erase()
        # 后端外套管水平联通短节
        o_xov = CYLINDER(s, R=R_OUT * 0.62, H=PITCH_Y, O=0.0).rotateX(-90.0).translate((L_STRAIGHT - 180.0, y_l, z_lvl))
        o_main.uniteWith(o_xov)
        o_xov.erase()

    # 2. 上下层间管程与壳程串联短管 (右侧 y_r 串联)
    o_s_link = CYLINDER(s, R=R_OUT * 0.58, H=PITCH_Z + 10.0, O=0.0).translate((260.0, y_r, z_lo - 5.0))
    o_main.uniteWith(o_s_link)
    o_s_link.erase()

    # 前端右侧内管 U 形串联回弯
    o_t_st1 = CYLINDER(s, R=R_IN, H=200.0, O=0.0).rotateY(-90.0).translate((20.0, y_r, z_lo))
    o_t_st2 = CYLINDER(s, R=R_IN, H=200.0, O=0.0).rotateY(-90.0).translate((20.0, y_r, z_hi))
    o_t_v = CYLINDER(s, R=R_IN, H=PITCH_Z + R_IN * 1.4, O=0.0).translate((-170.0, y_r, z_lo - R_IN * 0.7))
    for ob in (o_t_st1, o_t_st2, o_t_v):
        o_main.uniteWith(ob)
        ob.erase()

    # 3. 双组门式钢结构支架 (底座板 + 立柱 + 上下托梁)
    col_w = max(60.0, R_OUT * 0.65)
    bp_l = col_w * 2.4
    bp_w = PITCH_Y + R_OUT * 3.0
    bp_t = 18.0
    for xs in (L_STRAIGHT * 0.24, L_STRAIGHT * 0.76):
        o_bp = CORNERBOX(s, L=bp_l, W=bp_w, H=bp_t).translate((xs - bp_l * 0.5, -bp_w * 0.5, 0.0))
        o_main.uniteWith(o_bp)
        o_bp.erase()
        for sy in (-1.0, 1.0):
            yc = sy * (PITCH_Y * 0.5 + R_OUT + col_w * 0.4)
            o_col = CORNERBOX(s, L=col_w, W=col_w, H=z_hi + R_OUT * 0.3).translate(
                (xs - col_w * 0.5, yc - col_w * 0.5, bp_t - 2.0)
            )
            o_main.uniteWith(o_col)
            o_col.erase()
        for z_lvl in (z_lo, z_hi):
            o_bm = CORNERBOX(s, L=col_w, W=bp_w * 0.96, H=col_w * 0.85).translate(
                (xs - col_w * 0.5, -bp_w * 0.48, z_lvl - R_OUT - col_w * 0.55)
            )
            o_main.uniteWith(o_bm)
            o_bm.erase()

    # 4. 4 个法兰工艺口
    r_pt, r_ft, t_ft = _fl_dims(NOZ_T)
    x_t_face = -(NOZ_EXT + 60.0)
    # Port 1: 上层左侧管程进口 (-X)
    o_t1p = CYLINDER(s, R=r_pt, H=abs(x_t_face) - t_ft + 40.0, O=0.0).rotateY(-90.0).translate((35.0, y_l, z_hi))
    o_t1f = CYLINDER(s, R=r_ft, H=t_ft, O=0.0).rotateY(-90.0).translate((x_t_face + t_ft, y_l, z_hi))
    o_main.uniteWith(o_t1p)
    o_t1p.erase()
    o_main.uniteWith(o_t1f)
    o_t1f.erase()
    p_t_in = (x_t_face, y_l, z_hi)

    # Port 2: 下层左侧管程出口 (-X)
    o_t2p = CYLINDER(s, R=r_pt, H=abs(x_t_face) - t_ft + 40.0, O=0.0).rotateY(-90.0).translate((35.0, y_l, z_lo))
    o_t2f = CYLINDER(s, R=r_ft, H=t_ft, O=0.0).rotateY(-90.0).translate((x_t_face + t_ft, y_l, z_lo))
    o_main.uniteWith(o_t2p)
    o_t2p.erase()
    o_main.uniteWith(o_t2f)
    o_t2f.erase()
    p_t_out = (x_t_face, y_l, z_lo)

    # Port 3: 上层左侧壳程进口 (+Z)
    r_ps, r_fs, t_fs = _fl_dims(NOZ_S)
    x_s_noz = 260.0
    z_s_top = z_hi + R_OUT + NOZ_EXT
    o_s1p = CYLINDER(s, R=r_ps, H=NOZ_EXT - t_fs + R_OUT * 0.5, O=0.0).translate((x_s_noz, y_l, z_hi + R_OUT * 0.5))
    o_s1f = CYLINDER(s, R=r_fs, H=t_fs, O=0.0).translate((x_s_noz, y_l, z_s_top - t_fs))
    o_main.uniteWith(o_s1p)
    o_s1p.erase()
    o_main.uniteWith(o_s1f)
    o_s1f.erase()
    p_s_in = (x_s_noz, y_l, z_s_top)

    # Port 4: 下层左侧壳程出口 (-Z)
    z_s_bot = z_lo - R_OUT - NOZ_EXT
    o_s2p = CYLINDER(s, R=r_ps, H=NOZ_EXT - t_fs + R_OUT * 0.5, O=0.0).translate((x_s_noz, y_l, z_s_bot + t_fs - 2.0))
    o_s2f = CYLINDER(s, R=r_fs, H=t_fs, O=0.0).translate((x_s_noz, y_l, z_s_bot))
    o_main.uniteWith(o_s2p)
    o_s2p.erase()
    o_main.uniteWith(o_s2f)
    o_s2f.erase()
    p_s_out = (x_s_noz, y_l, z_s_bot)

    # 5. 注册 4 个工艺端口
    s.setPoint(p_t_in, (-1.0, 0.0, 0.0))
    s.setPoint(p_t_out, (-1.0, 0.0, 0.0))
    s.setPoint(p_s_in, (0.0, 0.0, 1.0))
    s.setPoint(p_s_out, (0.0, 0.0, -1.0))

    # 6. 注册线性标注
    s.setLinearDimension('L_STRAIGHT', (0.0, y_l, z_lo), (L_STRAIGHT, y_l, z_lo))
    s.setLinearDimension('PITCH_Y', (0.0, y_l, z_lo), (0.0, y_r, z_lo))
    s.setLinearDimension('PITCH_Z', (0.0, y_l, z_lo), (0.0, y_l, z_hi))
    s.setLinearDimension('H_BASE', (L_STRAIGHT * 0.24, 0.0, 0.0), (L_STRAIGHT * 0.24, 0.0, z_lo))
