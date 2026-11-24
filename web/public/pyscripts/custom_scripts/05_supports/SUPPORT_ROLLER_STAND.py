# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"化工单滚轮管道支座",
    TooltipLong=u"化工长距离热力及工艺管廊低摩擦单滚轮支座 (Y3 型，符合 HG/T 21629，含凹弧铸钢托辊、承重主轴销、双侧立板轴承座、斜撑肋板与地脚底板)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被支承管道公称外径 (mm)")
@param(H=LENGTH, TooltipShort=u"中心高", TooltipLong=u"管道中心至滚轮支座底板底面的距离 (mm)")
@param(D_ROLL=LENGTH, TooltipShort=u"滚轮外径", TooltipLong=u"铸钢托辊两端最大外径 (mm)")
@param(W_ROLL=LENGTH, TooltipShort=u"滚轮宽度", TooltipLong=u"铸钢托辊横向宽度 (mm)")
@param(L_BASE=LENGTH, TooltipShort=u"底板长度", TooltipLong=u"支座底板横向总长 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"底板宽度", TooltipLong=u"支座底板顺管向宽度 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"支座编号", TooltipLong=u"单滚轮管道支座型号规格编码")
def SUPPORT_ROLLER_STAND(s, D=219.1, H=235.0, D_ROLL=110.0, W_ROLL=150.0, L_BASE=260.0, W_BASE=140.0, ID=u"Y3-DN200", **kw):
    D = max(57.0, float(D))
    r_pipe = D / 2.0
    D_ROLL = max(65.0, float(D_ROLL))
    r_roll = D_ROLL / 2.0
    r_waist = r_roll * 0.72
    W_ROLL = max(90.0, float(W_ROLL))
    H = max(r_pipe + r_waist + 55.0, float(H))
    L_BASE = max(W_ROLL + 85.0, float(L_BASE))
    W_BASE = max(D_ROLL + 20.0, float(W_BASE))

    z_bot = -H
    t_base = 16.0
    z_axle = -(r_pipe + r_waist)

    # 1. 底部带螺栓孔矩形底板 (H=dx=W_BASE, L=dy=L_BASE, W=dz=t_base)
    o_m = BOX(s, L=L_BASE, W=t_base, H=W_BASE).translate((0.0, 0.0, z_bot + t_base * 0.5))
    for sy in (-1.0, 1.0):
        bh = CYLINDER(s, R=9.0, H=t_base + 4.0, O=0.0).translate((0.0, sy * L_BASE * 0.38, z_bot - 2.0))
        o_m.subtractFrom(bh); bh.erase()

    # 2. 两侧轴承立板 + 外侧加劲肋板
    h_cheek = (z_axle + r_roll * 0.55) - (z_bot + t_base)
    y_cheek = W_ROLL * 0.5 + 10.0
    z_cheek_c = z_bot + t_base + h_cheek * 0.5 - 2.0
    for sy in (-1.0, 1.0):
        ch = BOX(s, L=16.0, W=h_cheek, H=W_BASE * 0.72).translate((0.0, sy * y_cheek, z_cheek_c))
        rb = BOX(s, L=32.0, W=h_cheek * 0.78, H=12.0).translate((0.0, sy * (y_cheek + 20.0), z_bot + t_base + h_cheek * 0.38))
        o_m.uniteWith(ch); ch.erase()
        o_m.uniteWith(rb); rb.erase()

    # 3. 横向主轴销 + 凹弧形铸钢滚轮
    w_axle = W_ROLL + 56.0
    o_axle = CYLINDER(s, R=r_roll * 0.32, H=w_axle, O=0.0).rotateX(-90.0).translate((0.0, -w_axle * 0.5, z_axle))
    o_m.uniteWith(o_axle); o_axle.erase()

    o_r_mid = CYLINDER(s, R=r_waist, H=W_ROLL, O=0.0).rotateX(-90.0).translate((0.0, -W_ROLL * 0.5, z_axle))
    o_r_l = CONE(s, R1=r_roll, R2=r_waist, H=W_ROLL * 0.36, E=0.0).rotateX(-90.0).translate((0.0, -W_ROLL * 0.5, z_axle))
    o_r_r = CONE(s, R1=r_waist, R2=r_roll, H=W_ROLL * 0.36, E=0.0).rotateX(-90.0).translate((0.0, W_ROLL * 0.14, z_axle))
    for p in (o_r_mid, o_r_l, o_r_r):
        o_m.uniteWith(p); p.erase()

    # 4. 顶部贴合管道的弧形鞍垫导轨块
    o_pad = CYLINDER(s, R=r_pipe + 10.0, H=W_BASE * 0.85, O=0.0).rotateY(90.0).translate((-W_BASE * 0.425, 0.0, 0.0))
    o_trim = BOX(s, L=(r_pipe + 12.0) * 2.2, W=r_pipe * 1.65, H=W_BASE).translate((0.0, 0.0, r_pipe * 0.35))
    o_pad.subtractFrom(o_trim); o_trim.erase()
    o_m.uniteWith(o_pad); o_pad.erase()

    o_cut = CYLINDER(s, R=r_pipe, H=W_BASE + 20.0, O=0.0).rotateY(90.0).translate((-(W_BASE * 0.5 + 10.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("H", (0.0, 0.0, z_bot), (0.0, 0.0, 0.0))
    s.setLinearDimension("L_BASE", (0.0, -L_BASE / 2.0, z_bot), (0.0, L_BASE / 2.0, z_bot))
