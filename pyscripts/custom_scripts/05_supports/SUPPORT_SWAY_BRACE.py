# -*- coding: utf-8 -*-
import math
from varmain.primitiv import *
from varmain.custom import *


@activate(
    Group="Support",
    FirstPortEndtypes="Undefined_ET",
    Ports="1",
    TooltipShort=u"双向预紧弹簧减振拉撑杆",
    TooltipLong=u"化工两相流与压缩机振动管道控制低频晃动用双向预紧弹簧减振拉撑杆 (Z1 型，符合 HG/T 21629，含双螺栓防振管夹、前铰接销耳、双向预紧弹簧圆筒罐、刻度视窗、花兰调节螺套与生根耳座)",
    LengthUnit="mm",
)
@group("MainDimensions")
@param(D=LENGTH, TooltipShort=u"管道外径", TooltipLong=u"被减振约束管道外径 (mm)")
@param(L_BRACE=LENGTH, TooltipShort=u"拉撑总长", TooltipLong=u"管道中心至尾部钢结构生根底面的总安装距离 (mm)")
@param(D_CAN=LENGTH, TooltipShort=u"弹簧筒外径", TooltipLong=u"中部双向预紧弹簧圆筒外径 (mm)")
@param(W_CLAMP=LENGTH, TooltipShort=u"管夹宽度", TooltipLong=u"管道抱箍轴向宽度 (mm)")
@param(W_BASE=LENGTH, TooltipShort=u"生根板边长", TooltipLong=u"尾部生根方形底板边长 (mm)")
@group(Name="meaningless enum")
@param(ID=STRING, TooltipShort=u"支吊架编号", TooltipLong=u"双向预紧弹簧减振杆型号规格编码")
def SUPPORT_SWAY_BRACE(s, D=219.1, L_BRACE=720.0, D_CAN=140.0, W_CLAMP=75.0, W_BASE=180.0, ID=u"Z1-DN200", **kw):
    D = max(48.0, float(D))
    r_pipe = D / 2.0
    D_CAN = max(90.0, float(D_CAN))
    r_can = D_CAN / 2.0
    L_BRACE = max(r_pipe + 420.0, float(L_BRACE))
    W_CLAMP = max(50.0, float(W_CLAMP))
    W_BASE = max(D_CAN + 30.0, float(W_BASE))

    t_cl = max(12.0, D * 0.055)
    r_cl = r_pipe + t_cl

    # 1. 管道双耳重型管夹 + +Y 方向铰接双耳座
    o_m = CYLINDER(s, R=r_cl, H=W_CLAMP, O=0.0).rotateY(90.0).translate((-W_CLAMP * 0.5, 0.0, 0.0))
    o_ears = BOX(s, L=t_cl * 2.4, W=r_cl * 2.4, H=W_CLAMP).translate((0.0, 0.0, 0.0))
    y_pin1 = r_cl + 45.0
    o_clev1 = BOX(s, L=75.0, W=D_CAN * 0.55, H=W_CLAMP * 0.65).translate((0.0, r_cl + 22.0, 0.0))
    o_pin1 = CYLINDER(s, R=14.0, H=W_CLAMP * 0.85, O=0.0).rotateY(90.0).translate((-W_CLAMP * 0.425, y_pin1, 0.0))
    for p in (o_ears, o_clev1, o_pin1):
        o_m.uniteWith(p); p.erase()

    # 2. 中心拉压连杆 + 中部双向预压弹簧筒罐 + 两侧法兰端盖 + 顶载荷位移铭牌 + 后部花兰调节螺套
    y_pin2 = L_BRACE - 45.0
    span = y_pin2 - y_pin1
    l_can = span * 0.48
    y_can0 = y_pin1 + span * 0.16

    o_rod = CYLINDER(s, R=18.0, H=span + 20.0, O=0.0).rotateX(-90.0).translate((0.0, y_pin1 - 10.0, 0.0))
    o_can = CYLINDER(s, R=r_can, H=l_can, O=0.0).rotateX(-90.0).translate((0.0, y_can0, 0.0))
    o_fl1 = CYLINDER(s, R=r_can * 1.12, H=16.0, O=0.0).rotateX(-90.0).translate((0.0, y_can0, 0.0))
    o_fl2 = CYLINDER(s, R=r_can * 1.12, H=16.0, O=0.0).rotateX(-90.0).translate((0.0, y_can0 + l_can - 16.0, 0.0))
    o_scale = BOX(s, L=l_can * 0.65, W=14.0, H=42.0).translate((0.0, y_can0 + l_can * 0.5, r_can + 2.0))
    o_tb = CYLINDER(s, R=28.0, H=span * 0.22, O=0.0).rotateX(-90.0).translate((0.0, y_can0 + l_can + span * 0.08, 0.0))
    for p in (o_rod, o_can, o_fl1, o_fl2, o_scale, o_tb):
        o_m.uniteWith(p); p.erase()

    # 3. 尾部铰接耳座与方形生根底板 (Y = L_BRACE)
    t_b = 18.0
    o_clev2 = BOX(s, L=75.0, W=D_CAN * 0.60, H=W_CLAMP * 0.65).translate((0.0, L_BRACE - 42.0, 0.0))
    o_pin2 = CYLINDER(s, R=14.0, H=W_CLAMP * 0.85, O=0.0).rotateY(90.0).translate((-W_CLAMP * 0.425, y_pin2, 0.0))
    o_base = BOX(s, L=t_b, W=W_BASE, H=W_BASE).translate((0.0, L_BRACE - t_b * 0.5, 0.0))
    for p in (o_clev2, o_pin2, o_base):
        o_m.uniteWith(p); p.erase()

    # 切除管道通孔
    o_cut = CYLINDER(s, R=r_pipe, H=W_CLAMP + 20.0, O=0.0).rotateY(90.0).translate((-(W_CLAMP * 0.5 + 10.0), 0.0, 0.0))
    o_m.subtractFrom(o_cut); o_cut.erase()

    s.setPoint((0.0, 0.0, 0.0), (0.0, 0.0, -1.0))
    s.setLinearDimension("L_BRACE", (0.0, 0.0, 0.0), (0.0, L_BRACE, 0.0))
    s.setLinearDimension("D_CAN", (0.0, y_can0, -r_can), (0.0, y_can0, r_can))
