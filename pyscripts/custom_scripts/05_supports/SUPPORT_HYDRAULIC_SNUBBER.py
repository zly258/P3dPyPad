# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"动载管道液压阻尼器总成",
    TooltipLong=u"化工往复压缩机/安全阀泄放动载管道液压阻尼器减振总成 (符合 HG/T 21629，含重型防振管抱箍、关节轴承销耳、伸缩活塞杆、主液压缸筒、储油补偿副缸与尾部梁生根支座)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被减振保护管道公称外径 (mm)")
@param(L_SNUB=LENGTH, TooltipShort=u"阻尼器总长", TooltipLong=u"管道中心至尾部生根底板的水平总安装距离 (mm)")
@param(D_CYL=LENGTH, TooltipShort=u"主油缸外径", TooltipLong=u"液压阻尼器主工作油缸外径 (mm)")
@param(W_CLAMP=LENGTH, TooltipShort=u"防振管夹宽", TooltipLong=u"重型双螺栓防振管抱箍轴向宽度 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"生根底板宽", TooltipLong=u"尾部钢结构生根底板边长 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"阻尼器编号", TooltipLong=u"液压阻尼器总成型号规格编码")
def SUPPORT_HYDRAULIC_SNUBBER(s, D=219.1, L_SNUB=650.0, D_CYL=115.0, W_CLAMP=80.0, W_BASE=180.0, ID=u"HS-DN200-50kN", **kw):
    D = max(48.0, float(D))
    r_pipe = D / 2.0
    D_CYL = max(70.0, float(D_CYL))
    r_cyl = D_CYL / 2.0
    L_SNUB = max(r_pipe + 380.0, float(L_SNUB))
    W_CLAMP = max(50.0, float(W_CLAMP))
    W_BASE = max(D_CYL + 50.0, float(W_BASE))

    t_cl = max(12.0, D * 0.06)
    r_cl = r_pipe + t_cl

    # 1. 管道重型防振管抱箍 + +Y 方向双耳铰接座 (BOX: H=dx, L=dy, W=dz)
    o_m = CYLINDER(s, R=r_cl, H=W_CLAMP, O=0.0).rotateY(90.0).translate((-W_CLAMP * 0.5, 0.0, 0.0))
    o_fl = BOX(s, L=t_cl * 2.4, W=r_cl * 2.45, H=W_CLAMP).translate((0.0, 0.0, 0.0))
    o_m.uniteWith(o_fl); o_fl.erase()

    y_pin1 = r_cl + 48.0
    o_clevis1 = BOX(s, L=75.0, W=D_CYL * 0.68, H=W_CLAMP * 0.65).translate((0.0, r_cl + 22.0, 0.0))
    o_pin1 = CYLINDER(s, R=16.0, H=W_CLAMP * 0.85, O=0.0).rotateY(90.0).translate((-W_CLAMP * 0.425, y_pin1, 0.0))
    o_m.uniteWith(o_clevis1); o_clevis1.erase()
    o_m.uniteWith(o_pin1); o_pin1.erase()

    # 2. 伸缩活塞杆 + 主液压工作油缸筒 + 顶部透明油位补偿副储油筒
    y_pin2 = L_SNUB - 48.0
    span_pins = y_pin2 - y_pin1
    l_cyl = span_pins * 0.58
    y_cyl_start = y_pin1 + span_pins * 0.30

    o_rod = CYLINDER(s, R=r_cyl * 0.36, H=span_pins + 20.0, O=0.0).rotateX(-90.0).translate((0.0, y_pin1 - 10.0, 0.0))
    o_cyl = CYLINDER(s, R=r_cyl, H=l_cyl, O=0.0).rotateX(-90.0).translate((0.0, y_cyl_start, 0.0))
    o_cap_f = BOX(s, L=24.0, W=D_CYL * 1.12, H=D_CYL * 1.12).translate((0.0, y_cyl_start + 12.0, 0.0))
    o_cap_r = BOX(s, L=24.0, W=D_CYL * 1.12, H=D_CYL * 1.12).translate((0.0, y_cyl_start + l_cyl - 12.0, 0.0))
    for p in (o_rod, o_cyl, o_cap_f, o_cap_r):
        o_m.uniteWith(p); p.erase()

    # 顶部控制阀块与副储油筒
    h_vblk = r_cyl + 35.0
    o_vblk = BOX(s, L=l_cyl * 0.72, W=h_vblk, H=D_CYL * 0.65).translate((0.0, y_cyl_start + l_cyl * 0.5, h_vblk * 0.5))
    o_res = CYLINDER(s, R=r_cyl * 0.48, H=l_cyl * 0.78, O=0.0).rotateX(-90.0).translate((0.0, y_cyl_start + l_cyl * 0.11, r_cyl + 32.0))
    o_m.uniteWith(o_vblk); o_vblk.erase()
    o_m.uniteWith(o_res); o_res.erase()

    # 3. 尾部钢结构铰接耳座与四孔安装底板 (Y = L_SNUB)
    t_base = 18.0
    o_clevis2 = BOX(s, L=75.0, W=D_CYL * 0.75, H=W_CLAMP * 0.65).translate((0.0, L_SNUB - 42.0, 0.0))
    o_pin2 = CYLINDER(s, R=16.0, H=W_CLAMP * 0.85, O=0.0).rotateY(90.0).translate((-W_CLAMP * 0.425, y_pin2, 0.0))
    o_base = BOX(s, L=t_base, W=W_BASE, H=W_BASE).translate((0.0, L_SNUB - t_base * 0.5, 0.0))
    for p in (o_clevis2, o_pin2, o_base):
        o_m.uniteWith(p); p.erase()

    # 切除管道通孔
    o_cut = CYLINDER(s, R=r_pipe, H=W_CLAMP + 20.0, O=0.0).rotateY(90.0).translate((-(W_CLAMP * 0.5 + 10.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("L_SNUB", (0.0, 0.0, 0.0), (0.0, L_SNUB, 0.0))
    s.setLinearDimension("W_BASE", (-W_BASE / 2.0, L_SNUB, -W_BASE / 2.0), (W_BASE / 2.0, L_SNUB, -W_BASE / 2.0))
