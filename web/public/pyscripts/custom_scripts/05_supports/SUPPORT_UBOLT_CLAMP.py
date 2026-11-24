# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding("utf-8")
except (NameError, AttributeError):
    pass
from varmain.primitiv import *
from varmain.custom import *
from aqa.math import *
import math

def _hex_z(s, af, h):
    rc = float(af) / math.sqrt(3.0)
    b0 = BOX(s, L=af, W=h, H=rc).translate((0.0, 0.0, h * 0.5))
    b1 = BOX(s, L=af, W=h, H=rc).rotateZ(60.0).translate((0.0, 0.0, h * 0.5))
    b2 = BOX(s, L=af, W=h, H=rc).rotateZ(120.0).translate((0.0, 0.0, h * 0.5))
    b0.uniteWith(b1); b1.erase()
    b0.uniteWith(b2); b2.erase()
    return b0

@activate(Group="Support", Ports=1, TooltipShort=u"化工带衬板U形螺栓管夹 (HG/T 21629 A2)", TooltipLong=u"化工行业标准 HG/T 21629-2021 A1/A2 带弧形衬板与承重槽钢横梁的U形螺栓管架 (U-Bolt Pipe Clamp with Pad & Beam)，含圆钢U形螺栓、弧形护管衬板、槽钢横梁及梁顶梁底四颗六角锁紧螺母", LengthUnit="mm")
@group("MainDimensions", TooltipLong=u"支吊架主要结构尺寸：管道口径、结构与型钢规格")
@param(D=LENGTH, TooltipShort=u"管道外径 OD", Ask4Dist=True, TooltipLong=u"管道外径 OD")
@param(ROD_D=LENGTH, TooltipShort=u"U形螺栓杆径 d", TooltipLong=u"U形螺栓杆径 d")
@param(C=LENGTH, TooltipShort=u"U形螺栓中心距 C", TooltipLong=u"U形螺栓中心距 C")
@param(H_EXT=LENGTH, TooltipShort=u"螺纹伸出梁底长 H1", TooltipLong=u"螺纹伸出梁底长 H1")
@param(BEAM_H=LENGTH, TooltipShort=u"支承槽钢高 H", TooltipLong=u"支承槽钢高 H")
@param(BEAM_B=LENGTH, TooltipShort=u"支承槽钢宽 B", TooltipLong=u"支承槽钢宽 B")
@param(BEAM_L=LENGTH, TooltipShort=u"支承槽钢长 L", Ask4Dist=True, TooltipLong=u"支承槽钢长 L")
@param(ID=STRING, TooltipShort=u"管夹代号", TooltipLong=u"安装位号，用于图纸标注与材料表")
def SUPPORT_UBOLT_CLAMP(s, D=114.3, ROD_D=16.0, C=135.0, H_EXT=55.0, BEAM_H=100.0, BEAM_B=48.0, BEAM_L=320.0, ID="A2-DN100", **kw):
    D = max(20.0, float(D))
    r_pipe = D / 2.0
    ROD_D = max(10.0, float(ROD_D))
    r_rod = ROD_D / 2.0
    C = max(D + ROD_D + 2.0, float(C))
    r_arc = C / 2.0
    H_EXT = max(35.0, float(H_EXT))
    BEAM_H = max(60.0, float(BEAM_H))
    BEAM_B = max(38.0, float(BEAM_B))
    BEAM_L = max(C + 100.0, float(BEAM_L))

    t_pad = 8.0
    z_beam_top = -(r_pipe + t_pad)
    tf = max(7.5, BEAM_H * 0.085)
    tw = max(5.3, BEAM_H * 0.055)

    # 1. 底部弧形护管衬垫 (120° Curved Saddle Pad between pipe and channel beam)
    w_pad_x = max(60.0, BEAM_B * 1.25)
    o_sup = CYLINDER(s, R=r_pipe + t_pad, H=w_pad_x, O=0.0).rotateY(90.0).translate((-w_pad_x * 0.5, 0.0, 0.0))
    o_cut_top = BOX(s, L=2.0 * (r_pipe + t_pad) + 20.0, W=2.0 * r_pipe + 20.0, H=w_pad_x + 10.0).translate((0.0, 0.0, r_pipe * 0.45))
    o_sup.subtractFrom(o_cut_top); o_cut_top.erase()
    o_pipe_cut = CYLINDER(s, R=r_pipe, H=w_pad_x + 20.0, O=0.0).rotateY(90.0).translate((-(w_pad_x * 0.5 + 10.0), 0.0, 0.0))
    o_sup.subtractFrom(o_pipe_cut); o_pipe_cut.erase()

    # 2. 下方承重槽钢横梁 (沿 Y 方向横跨管道下方，z in [z_beam_top - BEAM_H, z_beam_top])
    o_fl_top = BOX(s, L=BEAM_L, W=tf, H=BEAM_B).translate((0.0, 0.0, z_beam_top - tf * 0.5))
    o_fl_bot = BOX(s, L=BEAM_L, W=tf, H=BEAM_B).translate((0.0, 0.0, z_beam_top - BEAM_H + tf * 0.5))
    o_web = BOX(s, L=BEAM_L, W=BEAM_H, H=tw).translate((-BEAM_B * 0.5 + tw * 0.5, 0.0, z_beam_top - BEAM_H * 0.5))
    o_sup.uniteWith(o_fl_top); o_fl_top.erase()
    o_sup.uniteWith(o_fl_bot); o_fl_bot.erase()
    o_sup.uniteWith(o_web); o_web.erase()

    # 3. U 形圆钢螺栓 (位于 YZ 平面，跨在沿 X 轴延伸的管道上方！)
    # TORUS 默认在 XY 平面从 0..180° (+Z 拱起需 rotateY(90)):
    # TORUS(A=180) 绕 Y 旋转 -90° 后位于 YZ 平面，拱顶在 +Z！
    o_arch = TORUS(s, R1=r_arc, R2=r_rod, A=180.0).rotateX(90.0).rotateZ(90.0)
    o_sup.uniteWith(o_arch); o_arch.erase()

    z_leg_bot = z_beam_top - tf - H_EXT
    leg_h = -z_leg_bot + 2.0
    nut_af = ROD_D * 1.65
    nut_h = ROD_D * 0.85
    wash_r = ROD_D * 1.15
    wash_t = 3.5

    for sy in (-1.0, 1.0):
        yl = sy * r_arc
        leg = CYLINDER(s, R=r_rod, H=leg_h, O=0.0).translate((0.0, yl, z_leg_bot))
        o_sup.uniteWith(leg); leg.erase()
        # 槽钢上翼缘顶面调节螺母 + 垫圈
        w_up = CYLINDER(s, R=wash_r, H=wash_t, O=0.0).translate((0.0, yl, z_beam_top))
        n_up = _hex_z(s, nut_af, nut_h).translate((0.0, yl, z_beam_top + wash_t))
        o_sup.uniteWith(w_up); w_up.erase()
        o_sup.uniteWith(n_up); n_up.erase()
        # 槽钢上翼缘底面双锁紧螺母 + 垫圈
        w_dn = CYLINDER(s, R=wash_r, H=wash_t, O=0.0).translate((0.0, yl, z_beam_top - tf - wash_t))
        n_dn1 = _hex_z(s, nut_af, nut_h).translate((0.0, yl, z_beam_top - tf - wash_t - nut_h))
        n_dn2 = _hex_z(s, nut_af, nut_h * 0.85).translate((0.0, yl, z_beam_top - tf - wash_t - 1.85 * nut_h))
        o_sup.uniteWith(w_dn); w_dn.erase()
        o_sup.uniteWith(n_dn1); n_dn1.erase()
        o_sup.uniteWith(n_dn2); n_dn2.erase()

    s.setPoint((0.0, 0.0, 0.0), (-1.0, 0.0, 0.0))

    s.setLinearDimension("C", (0.0, -r_arc, r_arc), (0.0, r_arc, r_arc))
    s.setLinearDimension("BEAM_L", (0.0, -BEAM_L * 0.5, z_beam_top - BEAM_H), (0.0, BEAM_L * 0.5, z_beam_top - BEAM_H))
    s.setLinearDimension("D", (0.0, 0.0, -r_pipe), (0.0, 0.0, r_pipe))
