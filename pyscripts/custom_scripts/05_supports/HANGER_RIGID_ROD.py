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

@activate(Group="Support",
          TooltipShort=u"刚性单吊杆吊架 (HG/T 21629 H1)",
          TooltipLong=u"刚性单吊杆吊架，含三螺栓双耳管夹、适中高度拉杆、开窗式花篮螺母与顶部生根耳板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"刚性单吊杆吊架主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被悬吊管道外径 D (mm)")
@param(H_ROD=LENGTH, TooltipShort=u"吊杆总高", TooltipLong=u"管道中心至顶部生根板顶面高度 H_ROD (mm)", Ask4Dist=True)
@param(ROD_D=LENGTH, TooltipShort=u"吊杆直径", TooltipLong=u"刚性拉杆公称直径 (mm)")
@param(CLAMP_W=LENGTH, TooltipShort=u"管夹宽度", TooltipLong=u"双耳管夹扁钢宽度 (mm)")
@param(CLAMP_T=LENGTH, TooltipShort=u"管夹厚度", TooltipLong=u"管夹扁钢厚度 (mm)")
@param(TOP_W=LENGTH, TooltipShort=u"生根板宽", TooltipLong=u"顶部方形生根底板宽度 (mm)")
def HANGER_RIGID_ROD(
    s,
    D=114.3,
    H_ROD=380.0,
    ROD_D=16.0,
    CLAMP_W=40.0,
    CLAMP_T=8.0,
    TOP_W=120.0,
    ID=u"HANGER_RIGID_ROD",
    **kw
):
    u"""刚性单吊杆吊架 (原点在管道中心线, 管道沿 X 轴, 吊杆向 +Z 延伸)。"""
    D = max(25.0, float(D))
    r_p = D / 2.0
    ROD_D = max(10.0, float(ROD_D))
    CLAMP_W = max(25.0, float(CLAMP_W))
    CLAMP_T = max(6.0, float(CLAMP_T))
    TOP_W = float(TOP_W)
    if TOP_W < 1.0:
        TOP_W = 1.0
    H_ROD = float(H_ROD)
    if H_ROD < 1.0:
        H_ROD = 1.0

    r_out = r_p + CLAMP_T
    ear_gap = max(8.0, CLAMP_T * 1.1)
    top_t = max(10.0, CLAMP_T * 1.4)
    z_top = H_ROD
    z_plt_bot = z_top - top_t

    # 1. 下部立式双半圆管夹（上下垂直双耳）
    o_main = CYLINDER(s, R=r_out, H=CLAMP_W, O=r_p).rotateY(90.0).translate((-CLAMP_W / 2.0, 0.0, 0.0))
    o_slot = CORNERBOX(s, L=CLAMP_W + 8.0, W=ear_gap, H=r_out * 2.6).translate(
        (-(CLAMP_W / 2.0 + 4.0), -ear_gap / 2.0, -r_out * 1.3))
    o_main.subtractFrom(o_slot)
    o_slot.erase()

    # 下部短耳 + 上部加长吊耳
    bot_ear_h = max(28.0, ROD_D * 1.8)
    top_ear_h = max(55.0, ROD_D * 3.4)
    for sy in (-1.0, 1.0):
        ey = (ear_gap / 2.0) if sy > 0 else -(ear_gap / 2.0 + CLAMP_T)
        o_be = CORNERBOX(s, L=CLAMP_W, W=CLAMP_T, H=bot_ear_h).translate(
            (-CLAMP_W / 2.0, ey, -(r_p + bot_ear_h)))
        o_main.uniteWith(o_be)
        o_be.erase()
        o_te = CORNERBOX(s, L=CLAMP_W, W=CLAMP_T, H=top_ear_h).translate(
            (-CLAMP_W / 2.0, ey, r_p))
        o_main.uniteWith(o_te)
        o_te.erase()

    # 上下管夹横销螺栓（底部1根 + 上部2根）
    bw = ear_gap + CLAMP_T * 2.0 + ROD_D * 1.4
    for bz in (-(r_out + bot_ear_h * 0.45), r_out + top_ear_h * 0.30, r_out + top_ear_h * 0.72):
        o_b = CYLINDER(s, R=ROD_D * 0.48, H=bw, O=0.0).rotateX(-90.0).translate((0.0, -bw / 2.0, bz))
        o_main.uniteWith(o_b)
        o_b.erase()

    # 2. 吊杆（从管夹上吊耳销孔延伸至顶部生根耳板）
    z_rod_start = r_out + top_ear_h * 0.72
    z_ear_pin = z_plt_bot - max(28.0, ROD_D * 1.8)
    o_rod = CYLINDER(s, R=ROD_D * 0.5, H=(z_ear_pin - z_rod_start) + 4.0, O=0.0).translate(
        (0.0, 0.0, z_rod_start - 2.0))
    o_main.uniteWith(o_rod)
    o_rod.erase()

    # 下端环形吊眼（包覆在管夹上销轴上）
    eye_r = max(ROD_D * 1.05, 16.0)
    o_bot_eye = CYLINDER(s, R=eye_r, H=ear_gap + 1.0, O=0.0).rotateX(-90.0).translate(
        (0.0, -(ear_gap + 1.0) / 2.0, z_rod_start))
    o_main.uniteWith(o_bot_eye)
    o_bot_eye.erase()

    # 3. 中部开窗式花篮螺母（清晰表达上下六角套筒+两侧连接肋）
    z_tb_mid = (z_rod_start + z_ear_pin) * 0.50
    tb_len = max(72.0, min(110.0, (z_ear_pin - z_rod_start) * 0.42))
    tb_r = ROD_D * 1.05
    cap_h = tb_len * 0.24
    # 上下螺母端头
    for sz in (-1.0, 1.0):
        cz = (z_tb_mid + tb_len / 2.0 - cap_h) if sz > 0 else (z_tb_mid - tb_len / 2.0)
        o_cap = CYLINDER(s, R=tb_r, H=cap_h, O=0.0).translate((0.0, 0.0, cz))
        o_main.uniteWith(o_cap)
        o_cap.erase()
    # 花篮两侧纵梁（留出中间镂空槽感，杆体穿过后外侧突出双耳轮廓）
    strap_t = max(5.0, ROD_D * 0.35)
    strap_w = ROD_D * 0.9
    for sy in (-1.0, 1.0):
        sy_pos = (tb_r - strap_t) if sy > 0 else -tb_r
        o_st = CORNERBOX(s, L=strap_w, W=strap_t, H=tb_len).translate(
            (-strap_w / 2.0, sy_pos, z_tb_mid - tb_len / 2.0))
        o_main.uniteWith(o_st)
        o_st.erase()

    # 4. 顶部生根底板 + U型双耳吊座 + 顶部销轴
    o_tplt = CORNERBOX(s, L=TOP_W, W=TOP_W, H=top_t).translate((-TOP_W / 2.0, -TOP_W / 2.0, z_plt_bot))
    o_main.uniteWith(o_tplt)
    o_tplt.erase()

    clev_h = z_plt_bot - z_ear_pin + eye_r * 0.85
    clev_l = max(44.0, ROD_D * 2.6)
    for sy in (-1.0, 1.0):
        cy = (ear_gap / 2.0) if sy > 0 else -(ear_gap / 2.0 + CLAMP_T)
        o_cl = CORNERBOX(s, L=clev_l, W=CLAMP_T, H=clev_h + 2.0).translate(
            (-clev_l / 2.0, cy, z_plt_bot - clev_h))
        o_main.uniteWith(o_cl)
        o_cl.erase()

    o_top_eye = CYLINDER(s, R=eye_r, H=ear_gap + 1.0, O=0.0).rotateX(-90.0).translate(
        (0.0, -(ear_gap + 1.0) / 2.0, z_ear_pin))
    o_main.uniteWith(o_top_eye)
    o_top_eye.erase()

    o_tpin = CYLINDER(s, R=ROD_D * 0.55, H=bw, O=0.0).rotateX(-90.0).translate((0.0, -bw / 2.0, z_ear_pin))
    o_main.uniteWith(o_tpin)
    o_tpin.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H_ROD', (0.0, 0.0, 0.0), (0.0, 0.0, z_top))
    s.setLinearDimension('TOP_W', (-TOP_W / 2.0, 0.0, z_top), (TOP_W / 2.0, 0.0, z_top))
