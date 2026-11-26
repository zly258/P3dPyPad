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
          TooltipShort=u"可变弹簧吊架 (NB/T 47039 VS)",
          TooltipLong=u"可变弹簧吊架，含下部重型管夹、下吊杆、带载荷标尺槽圆柱弹簧筒、上拉杆与顶部生根耳板",
          LengthUnit="mm",
          Ports="1")
@group("MainDimensions", TooltipLong=u"可变弹簧吊架主要几何参数")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被悬吊管道外径 D (mm)")
@param(H_TOT=LENGTH, TooltipShort=u"安装总高", TooltipLong=u"管道中心至顶部生根板顶面总高度 H_TOT (mm)", Ask4Dist=True)
@param(D_CASING=LENGTH, TooltipShort=u"弹簧筒外径", TooltipLong=u"可变弹簧圆柱外壳外径 (mm)")
@param(H_CASING=LENGTH, TooltipShort=u"弹簧筒高度", TooltipLong=u"弹簧圆柱筒体高度 (mm)")
@param(ROD_D=LENGTH, TooltipShort=u"吊杆直径", TooltipLong=u"上下吊杆公称直径 (mm)")
@param(CLAMP_W=LENGTH, TooltipShort=u"管夹宽度", TooltipLong=u"下部重型管夹扁钢宽度 (mm)")
def HANGER_VAR_SPRING(
    s,
    D=168.3,
    H_TOT=480.0,
    D_CASING=130.0,
    H_CASING=180.0,
    ROD_D=18.0,
    CLAMP_W=45.0,
    ID=u"HANGER_VAR_SPRING",
    **kw
):
    u"""可变弹簧吊架 (原点在管道中心线, 管道沿 X 轴, 弹簧组件向 +Z 延伸)。"""
    D = max(32.0, float(D))
    r_p = D / 2.0
    D_CASING = float(D_CASING)
    if D_CASING < 1.0:
        D_CASING = 1.0
    H_CASING = max(110.0, float(H_CASING))
    ROD_D = max(12.0, float(ROD_D))
    CLAMP_W = max(30.0, float(CLAMP_W))
    H_TOT = float(H_TOT)
    if H_TOT < 1.0:
        H_TOT = 1.0

    clamp_t = max(8.0, CLAMP_W * 0.20)
    r_out = r_p + clamp_t
    ear_gap = max(10.0, clamp_t * 1.1)
    top_t = max(12.0, clamp_t * 1.3)
    z_top = H_TOT
    z_tplt_bot = z_top - top_t

    # 1. 下部立式重型双耳管夹
    o_main = CYLINDER(s, R=r_out, H=CLAMP_W, O=r_p).rotateY(90.0).translate((-CLAMP_W / 2.0, 0.0, 0.0))
    o_slot = CORNERBOX(s, L=CLAMP_W + 8.0, W=ear_gap, H=r_out * 2.6).translate(
        (-(CLAMP_W / 2.0 + 4.0), -ear_gap / 2.0, -r_out * 1.3))
    o_main.subtractFrom(o_slot)
    o_slot.erase()

    bot_ear_h = max(30.0, ROD_D * 1.7)
    top_ear_h = max(55.0, ROD_D * 3.0)
    for sy in (-1.0, 1.0):
        ey = (ear_gap / 2.0) if sy > 0 else -(ear_gap / 2.0 + clamp_t)
        o_be = CORNERBOX(s, L=CLAMP_W, W=clamp_t, H=bot_ear_h).translate((-CLAMP_W / 2.0, ey, -(r_p + bot_ear_h)))
        o_main.uniteWith(o_be)
        o_be.erase()
        o_te = CORNERBOX(s, L=CLAMP_W, W=clamp_t, H=top_ear_h).translate((-CLAMP_W / 2.0, ey, r_p))
        o_main.uniteWith(o_te)
        o_te.erase()

    bw = ear_gap + clamp_t * 2.0 + ROD_D * 1.4
    z_pin_bot = r_out + top_ear_h * 0.72
    for bz in (-(r_out + bot_ear_h * 0.45), r_out + top_ear_h * 0.28, z_pin_bot):
        o_b = CYLINDER(s, R=ROD_D * 0.48, H=bw, O=0.0).rotateX(-90.0).translate((0.0, -bw / 2.0, bz))
        o_main.uniteWith(o_b)
        o_b.erase()

    # 2. 中心拉杆贯通（下吊杆 + 穿过弹簧筒 + 上拉杆）
    z_pin_top = z_tplt_bot - max(30.0, ROD_D * 1.7)
    o_rod = CYLINDER(s, R=ROD_D * 0.5, H=(z_pin_top - z_pin_bot) + 4.0, O=0.0).translate(
        (0.0, 0.0, z_pin_bot - 2.0))
    o_main.uniteWith(o_rod)
    o_rod.erase()

    # 3. 圆柱可变弹簧筒体（位于中上段，带上下端盖法兰、载荷标尺牌与防松螺母）
    z_cas_mid = (z_pin_bot + z_pin_top) * 0.54
    z_cas_bot = z_cas_mid - H_CASING / 2.0
    z_cas_top = z_cas_mid + H_CASING / 2.0
    r_cas = D_CASING / 2.0
    fl_t = max(10.0, D_CASING * 0.09)
    r_fl = r_cas + max(10.0, D_CASING * 0.09)

    o_cas = CYLINDER(s, R=r_cas, H=H_CASING, O=0.0).translate((0.0, 0.0, z_cas_bot))
    o_main.uniteWith(o_cas)
    o_cas.erase()

    # 上下圆形端盖法兰
    for fz in (z_cas_bot, z_cas_top - fl_t):
        o_fl = CYLINDER(s, R=r_fl, H=fl_t, O=0.0).translate((0.0, 0.0, fz))
        o_main.uniteWith(o_fl)
        o_fl.erase()

    # 前侧垂直载荷刻度标尺槽盖板 + 红色指针凸块轮廓
    scale_w = max(24.0, D_CASING * 0.22)
    scale_h = H_CASING * 0.72
    o_scale = CORNERBOX(s, L=12.0, W=scale_w, H=scale_h).translate(
        (r_cas - 4.0, -scale_w / 2.0, z_cas_mid - scale_h / 2.0))
    o_main.uniteWith(o_scale)
    o_scale.erase()
    o_ptr = CORNERBOX(s, L=10.0, W=scale_w * 0.6, H=10.0).translate(
        (r_cas + 6.0, -scale_w * 0.3, z_cas_mid - 5.0))
    o_main.uniteWith(o_ptr)
    o_ptr.erase()

    # 下端螺纹调节长螺母
    o_adj = CYLINDER(s, R=ROD_D * 1.0, H=ROD_D * 2.2, O=0.0).translate((0.0, 0.0, z_cas_bot - ROD_D * 2.1))
    o_main.uniteWith(o_adj)
    o_adj.erase()

    # 4. 顶部生根底板 + 吊耳座
    top_w = max(130.0, D_CASING * 1.05)
    o_tplt = CORNERBOX(s, L=top_w, W=top_w, H=top_t).translate((-top_w / 2.0, -top_w / 2.0, z_tplt_bot))
    o_main.uniteWith(o_tplt)
    o_tplt.erase()

    clev_h = z_tplt_bot - z_pin_top + ROD_D * 1.1
    clev_l = max(48.0, ROD_D * 2.8)
    for sy in (-1.0, 1.0):
        cy = (ear_gap / 2.0) if sy > 0 else -(ear_gap / 2.0 + clamp_t)
        o_cl = CORNERBOX(s, L=clev_l, W=clamp_t, H=clev_h + 2.0).translate((-clev_l / 2.0, cy, z_tplt_bot - clev_h))
        o_main.uniteWith(o_cl)
        o_cl.erase()

    o_tpin = CYLINDER(s, R=ROD_D * 0.55, H=bw, O=0.0).rotateX(-90.0).translate((0.0, -bw / 2.0, z_pin_top))
    o_main.uniteWith(o_tpin)
    o_tpin.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))
    s.setLinearDimension('H_TOT', (0.0, 0.0, 0.0), (0.0, 0.0, z_top))
    s.setLinearDimension('D_CASING', (0.0, -r_cas, z_cas_mid), (0.0, r_cas, z_cas_mid))
